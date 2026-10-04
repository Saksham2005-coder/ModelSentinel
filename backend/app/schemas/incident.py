from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class IncidentSignalResponse(BaseModel):
    id: str
    incident_id: str
    source_type: str
    source_id: Optional[str]
    signal_name: str
    observed_value: Optional[float]
    threshold: Optional[float]
    comparison: Optional[str]
    status: str
    explanation: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class IncidentEventResponse(BaseModel):
    id: str
    incident_id: str
    event_type: str
    message: str
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class IncidentEvidenceResponse(BaseModel):
    id: str
    incident_id: str
    monitoring_run_id: str
    snapshot: Dict[str, Any]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class IncidentBase(BaseModel):
    incident_key: str
    model_id: str
    model_version_id: str
    title: str
    summary: Optional[str]
    severity: str
    status: str
    category: str
    detected_at: datetime
    last_seen_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class IncidentResponse(IncidentBase):
    id: str

class IncidentDetailResponse(IncidentResponse):
    signals: List[IncidentSignalResponse] = []
    events: List[IncidentEventResponse] = []
    evidence: Optional[IncidentEvidenceResponse] = None

class IncidentResolution(BaseModel):
    resolution_note: Optional[str] = None
