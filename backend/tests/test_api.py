from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def auth():
    r=c.post('/api/v1/auth/login',json={'email':'engineer@tracegaurd.ai','password':'TraceGaurd@123'})
    assert r.status_code==200
    return {'Authorization':f"Bearer {r.json()['access_token']}"}
def test_health(): assert c.get('/health').status_code==200
def test_protected_and_approval_gate():
    h=auth(); assert c.get('/api/v1/clients',headers=h).status_code==200
    c.post('/api/v1/simulate/payment-db-timeout',headers=h)
    iid=c.get('/api/v1/incidents',headers=h).json()[0]['incident_id']
    blocked=c.post(f'/api/v1/incidents/{iid}/execute',headers=h,json={'action':'rollback_deployment','approval_id':'bad'})
    assert blocked.status_code==403
