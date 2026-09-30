import hashlib, hmac, os, time, base64, json
EMAIL=os.getenv("DEMO_ENGINEER_EMAIL","engineer@tracegaurd.ai").lower(); PASSWORD=os.getenv("DEMO_ENGINEER_PASSWORD","TraceGaurd@123"); SECRET=os.getenv("TRACEGAURD_SECRET","change-me")
def verify_credentials(email,password): return hmac.compare_digest(email.lower(),EMAIL) and hmac.compare_digest(password,PASSWORD)
def issue_token(email):
    payload=base64.urlsafe_b64encode(json.dumps({"sub":email.lower(),"exp":int(time.time())+28800}).encode()).decode().rstrip("="); sig=hmac.new(SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest(); return payload+"."+sig
def verify_token(token):
    try:
        payload,sig=token.split(".",1); expected=hmac.new(SECRET.encode(),payload.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig,expected): return None
        data=json.loads(base64.urlsafe_b64decode(payload+"="*((4-len(payload)%4)%4))); return data["sub"] if data["exp"]>=int(time.time()) else None
    except Exception: return None
