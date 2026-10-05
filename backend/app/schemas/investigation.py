from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class InvestigationEventBase(BaseModel):
    event_type: str
    title: str
    message: str
    tool_name: Optional[str] = None
    status: str
    metadata_json: Optional[Dict[str, Any]] = None

class InvestigationEventResponse(InvestigationEventBase):
    id: str
    investigation_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class InvestigationEvidenceBase(BaseModel):
    evidence_type: str
    source_type: str
    source_id: Optional[str] = None
    title: str
    value_json: Optional[Dict[str, Any]] = None
    relationship_type: str # supports, contradicts, neutral, context
    explanation: str

class InvestigationEvidenceResponse(InvestigationEvidenceBase):
    id: str
    investigation_id: str
    hypothesis_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InvestigationHypothesisBase(BaseModel):
    title: str
    description: str
    status: str
    rank: Optional[int] = None
    evidence_strength: str

class InvestigationHypothesisResponse(InvestigationHypothesisBase):
    id: str
    investigation_id: str
    created_at: datetime
    updated_at: datetime
    evidence_items: List[InvestigationEvidenceResponse] = []

    class Config:
        from_attributes = True

class InvestigationBase(BaseModel):
    incident_id: str
    summary: Optional[str] = None
    current_step: Optional[str] = None

class InvestigationResponse(InvestigationBase):
    id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    primary_hypothesis_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InvestigationDetailResponse(InvestigationResponse):
    events: List[InvestigationEventResponse] = []
    hypotheses: List[InvestigationHypothesisResponse] = []
    evidence: List[InvestigationEvidenceResponse] = []
