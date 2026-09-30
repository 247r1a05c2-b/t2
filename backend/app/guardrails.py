SAFE={"check_logs","check_database","check_metrics","inspect_deployment"}
APPROVAL={"restart_service","rollback_deployment","scale_service"}

def classify_action(action):
    a=action.strip().lower()
    if a in SAFE: return {"action":a,"risk":"SAFE","status":"SAFE","reason":"Read-only diagnostic action."}
    if a in APPROVAL: return {"action":a,"risk":"APPROVAL","status":"PENDING_APPROVAL","reason":"Production-changing action requires explicit human approval."}
    return {"action":a,"risk":"BLOCKED","status":"BLOCKED","reason":"Action is not on the allow-list."}
