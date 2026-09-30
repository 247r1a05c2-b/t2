from enum import Enum
from pydantic import BaseModel, Field

class Severity(str, Enum):
    info="info"
    warning="warning"
    critical="critical"

class Event(BaseModel):
    incident_id: str
    service: str
    source: str
    message: str
    severity: Severity = Severity.warning
    timestamp: str
    metadata: dict = Field(default_factory=dict)

class IngestRequest(BaseModel):
    events: list[dict]

class IngestResponse(BaseModel):
    accepted: int
    incident_ids: list[str]

class IncidentSummary(BaseModel):
    incident_id: str
    title: str
    status: str
    severity: Severity
    event_count: int
