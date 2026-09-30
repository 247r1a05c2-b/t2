from collections import Counter
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
load_dotenv()
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from .agents import run_agents
from .database import ClientRecord, UserRecord, database_status, SessionLocal, ApprovalRecord, RemediationExecutionRecord
from .guardrails import classify_action
from .models import IncidentSummary, IngestRequest, IngestResponse
from .monitoring import audit_log, clients, execute_approved_action, execution_log, heartbeat, record_audit, register_client
from .normalizer import normalize_events
from .security import issue_token, verify_credentials, verify_token
from .simulator import available_scenarios, generate_scenario
from .store import add_many, get, incidents

app=FastAPI(title="TraceGaurd API",version="4.0.0",description="Multi-agent AI incident commander")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
bearer=HTTPBearer(auto_error=False)
class LoginRequest(BaseModel): email:str; password:str
class ClientRequest(BaseModel): name:str=Field(min_length=2); environment:str="production"; service:str=Field(min_length=2)
class ApprovalRequest(BaseModel): action:str; approved:bool
class ExecuteRequest(BaseModel): action:str; approval_id:str
def engineer(credentials:HTTPAuthorizationCredentials|None=Depends(bearer)):
 if not credentials: raise HTTPException(401,"Engineer login required")
 email=verify_token(credentials.credentials)
 if not email: raise HTTPException(401,"Session expired or invalid")
 return email
@app.get("/health")
def health(): return {"status":"ok","service":"tracegaurd-api","version":"4.0.0","database":database_status()}
@app.post("/api/v1/auth/login")
def login(r:LoginRequest):
 if not verify_credentials(r.email,r.password): raise HTTPException(401,"Invalid engineer credentials")
 with SessionLocal() as s:
  if s.get(UserRecord,r.email.lower()) is None: s.add(UserRecord(email=r.email.lower())); s.commit()
 record_audit("LOGIN",r.email,{})
 return {"access_token":issue_token(r.email),"token_type":"bearer","engineer":r.email.lower()}
@app.get("/api/v1/auth/me")
def me(user=Depends(engineer)): return {"email":user,"role":"SOFTWARE_ENGINEER","permissions":["MONITOR","ANALYZE","APPROVE","EXECUTE_APPROVED_ACTIONS"]}
@app.get("/api/v1/scenarios")
def scenarios(user=Depends(engineer)): return available_scenarios()
@app.get("/api/v1/clients")
def list_clients(user=Depends(engineer)): return list(clients.values())
@app.post("/api/v1/clients")
def add_client(r:ClientRequest,user=Depends(engineer)):
 c=register_client(r.name,r.environment,r.service)
 with SessionLocal() as s: s.merge(ClientRecord(id=c["client_id"],name=c["name"],environment=c["environment"],service=c["service"])); s.commit()
 record_audit("CLIENT_REGISTERED",user,c); return c
@app.post("/api/v1/clients/{client_id}/heartbeat")
def client_heartbeat(client_id,user=Depends(engineer)):
 try:return heartbeat(client_id)
 except KeyError:raise HTTPException(404,"Client not found")
@app.post("/api/v1/simulate/{scenario}",response_model=IngestResponse)
def simulate(scenario,user=Depends(engineer)):
 try: events=normalize_events(generate_scenario(scenario))
 except ValueError as e: raise HTTPException(404,str(e))
 add_many(events); record_audit("INCIDENT_INGESTED",user,{"scenario":scenario,"events":len(events)}); return {"accepted":len(events),"incident_ids":sorted({e.incident_id for e in events})}
@app.post("/api/v1/events",response_model=IngestResponse)
def ingest(r:IngestRequest,user=Depends(engineer)):
 events=normalize_events(r.events); add_many(events); record_audit("EVENTS_INGESTED",user,{"events":len(events)}); return {"accepted":len(events),"incident_ids":sorted({e.incident_id for e in events})}
@app.get("/api/v1/incidents",response_model=list[IncidentSummary])
def list_incidents(user=Depends(engineer)):
 order={"info":0,"warning":1,"critical":2}; out=[]
 for iid in incidents():
  ev=get(iid); sev=max(ev,key=lambda x:order[x.severity.value]).severity; out.append(IncidentSummary(incident_id=iid,title=f"Incident {iid}",status="OPEN",severity=sev,event_count=len(ev)))
 return out
@app.get("/api/v1/incidents/{incident_id}/events")
def events(incident_id,user=Depends(engineer)):
 ev=get(incident_id)
 if not ev: raise HTTPException(404,"Incident not found")
 return ev
@app.get("/api/v1/incidents/{incident_id}/analysis")
def analysis(incident_id,user=Depends(engineer)):
 ev=get(incident_id)
 if not ev: raise HTTPException(404,"Incident not found")
 result=run_agents(ev); result["evaluation"]={"root_cause_confidence":result["confidence"],"evidence_coverage":min(100,len(result["evidence"])*20),"workflow_completeness":min(100,len(result["agent_trace"])*12),"diagnosis_quality":min(100,round(result["confidence"]*.6+min(100,len(result["evidence"])*20)*.2+min(100,len(result["agent_trace"])*12)*.2))}; result["approval_state"]="PENDING_HUMAN_REVIEW" if any(a["risk"]=="APPROVAL" for a in result["actions"]) else "SAFE"; return result
@app.post("/api/v1/incidents/{incident_id}/approve")
def approve(incident_id,r:ApprovalRequest,user=Depends(engineer)):
 if not get(incident_id): raise HTTPException(404,"Incident not found")
 g=classify_action(r.action)
 if g["risk"]=="BLOCKED": raise HTTPException(403,"Guardrail blocked this action")
 aid=f"approval-{len(audit_log)+1}"; state="APPROVED" if r.approved else "REJECTED"
 with SessionLocal() as s: s.add(ApprovalRecord(id=aid,incident_id=incident_id,action=r.action,engineer=user,state=state)); s.commit()
 record_audit("HUMAN_APPROVAL",user,{"incident_id":incident_id,"action":r.action,"state":state,"approval_id":aid}); return {"approval_id":aid,"state":state,"guardrail":g}
@app.post("/api/v1/incidents/{incident_id}/execute")
def execute(incident_id,r:ExecuteRequest,user=Depends(engineer)):
 if not get(incident_id): raise HTTPException(404,"Incident not found")
 with SessionLocal() as s: approved=s.get(ApprovalRecord,r.approval_id)
 if not approved or approved.incident_id!=incident_id or approved.action!=r.action or approved.state!="APPROVED": raise HTTPException(403,"Explicit human approval is required before execution")
 result=execute_approved_action(incident_id,r.action,user)
 with SessionLocal() as s: s.add(RemediationExecutionRecord(incident_id=incident_id,action=r.action,engineer=user,status=result["status"],verification=json.dumps(result["verification"]))); s.commit()
 return result
@app.get("/api/v1/incidents/{incident_id}/remediation")
def remediation(incident_id,user=Depends(engineer)): return {"incident_id":incident_id,"executions":[x for x in execution_log if x["incident_id"]==incident_id]}
@app.post("/api/v1/guardrails/check")
def guardrail(payload:dict,user=Depends(engineer)): return classify_action(payload.get("action",""))
@app.get("/api/v1/metrics")
def metrics(user=Depends(engineer)):
 return {"active_incidents":len(incidents()),"clients_monitored":len(clients),"actions_executed":len(execution_log),"human_approvals":sum(x.get("details",{}).get("state")=="APPROVED" for x in audit_log if x["event"]=="HUMAN_APPROVAL"),"audit_events":len(audit_log),"uptime_status":"OPERATIONAL","database":database_status(),"timestamp":datetime.now(timezone.utc).isoformat()}
@app.get("/api/v1/audit")
def audit(user=Depends(engineer)): return list(reversed(audit_log[-100:]))
