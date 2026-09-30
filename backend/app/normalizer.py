from datetime import datetime, timezone
from .models import Event, Severity

def normalize_events(events):
    out=[]
    for e in events:
        sev=str(e.get("severity","warning")).lower()
        if sev not in {"info","warning","critical"}: sev="warning"
        out.append(Event(incident_id=str(e.get("incident_id","INC-1001")),service=str(e.get("service","unknown")),source=str(e.get("source","unknown")),message=str(e.get("message","")),severity=Severity(sev),timestamp=e.get("timestamp") or datetime.now(timezone.utc).isoformat(),metadata=e.get("metadata") or {}))
    return out
