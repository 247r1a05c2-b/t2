RUNBOOKS={
"database":["Check database availability","Check connection-pool saturation","Review timeout and connection errors","Compare recent DB configuration changes"],
"deployment":["Identify the latest deployment","Compare current and previous versions","Review deployment logs","Rollback only after human approval"],
"latency":["Check API latency by endpoint","Inspect downstream dependency latency","Review slow database queries","Compare traffic with baseline"]}

def retrieve_context(events):
    text=" ".join(e.message.lower() for e in events); out=[]
    if "database" in text or "connection" in text or "timeout" in text: out += RUNBOOKS["database"]
    if "deploy" in text or "release" in text: out += RUNBOOKS["deployment"]
    if "latency" in text or "slow" in text: out += RUNBOOKS["latency"]
    return list(dict.fromkeys(out))
