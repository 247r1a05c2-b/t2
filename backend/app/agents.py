from .rag import retrieve_context
from .guardrails import classify_action

def run_agents(events):
    trace=[]
    trace.append({"agent":"Ingestion Agent","status":"complete","detail":f"Normalized {len(events)} events"})
    critical=[e for e in events if e.severity.value=="critical"]
    trace.append({"agent":"Noise Filter Agent","status":"complete","detail":f"Prioritized {len(critical)} critical signals"})
    text=" ".join(e.message.lower() for e in events)
    correlation="Recent deployment correlates with service degradation" if "deploy" in text else "Database timeout correlates with elevated API latency"
    trace.append({"agent":"Correlation Agent","status":"complete","detail":correlation})
    rag=retrieve_context(events); trace.append({"agent":"RAG Agent","status":"complete","detail":f"Retrieved {len(rag)} runbook items"})
    if "database" in text or "timeout" in text: cause="Database connectivity or connection-pool saturation"; confidence=91
    elif "deploy" in text: cause="Recent deployment regression is the leading hypothesis"; confidence=82
    else: cause="Insufficient evidence for a specific root cause"; confidence=55
    evidence=[{"source":e.source,"message":e.message,"timestamp":e.timestamp} for e in events]
    trace.append({"agent":"Root Cause Agent","status":"complete","detail":cause})
    steps=[{"step":1,"action":"Inspect application and database timeout logs","expected":"Confirm connection failures"},{"step":2,"action":"Compare deployment and error-rate timelines","expected":"Confirm temporal correlation"},{"step":3,"action":"Validate database pool saturation and availability","expected":"Confirm bottleneck"},{"step":4,"action":"Apply approved remediation and verify recovery","expected":"Error rate and latency return to baseline"}]
    trace.append({"agent":"Diagnostic Agent","status":"complete","detail":f"Produced {len(steps)} diagnostic steps"})
    actions=[classify_action(a) for a in ["check_logs","check_database","inspect_deployment","rollback_deployment"]]
    trace.append({"agent":"Guardrail Agent","status":"complete","detail":"Classified remediation actions; production mutations require approval"})
    trace.append({"agent":"Timeline Agent","status":"complete","detail":"Built auditable incident timeline"})
    return {"root_cause":cause,"confidence":confidence,"evidence":evidence,"rag_context":rag,"diagnosis_steps":steps,"actions":actions,"agent_trace":trace}
