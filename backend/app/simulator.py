from datetime import datetime, timezone
SCENARIOS={"payment-db-timeout":[
{"incident_id":"INC-1001","service":"payment-api","source":"application-log","message":"Database connection timeout detected","severity":"critical"},
{"incident_id":"INC-1001","service":"payment-api","source":"monitoring","message":"API latency increased above 2 seconds","severity":"critical"},
{"incident_id":"INC-1001","service":"payment-api","source":"deployment","message":"payment-service deployment completed recently","severity":"warning"},
{"incident_id":"INC-1001","service":"payment-api","source":"alert","message":"High error rate detected","severity":"critical"}],"deployment-regression":[
{"incident_id":"INC-1002","service":"checkout-api","source":"deployment","message":"checkout version 4.2 deployed 8 minutes ago","severity":"warning"},
{"incident_id":"INC-1002","service":"checkout-api","source":"monitoring","message":"Checkout latency and error rate increased","severity":"critical"}]}

def available_scenarios(): return list(SCENARIOS)
def generate_scenario(name):
    if name not in SCENARIOS: raise ValueError("Unknown scenario")
    now=datetime.now(timezone.utc).isoformat(); return [{**e,"timestamp":now} for e in SCENARIOS[name]]
