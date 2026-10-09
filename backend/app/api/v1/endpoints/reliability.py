from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import SessionLocal
from app.services.reliability_service import reliability_service
from app.models.reliability import ReliabilityEvent, ReliabilityEdge
from pydantic import BaseModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

class ReliabilityEventResponse(BaseModel):
    id: str
    model_id: str
    model_version_id: Optional[str]
    event_type: str
    source_type: str
    source_id: str
    title: str
    severity: Optional[str]
    status: Optional[str]
    summary: Optional[str]
    metadata_json: Dict[str, Any]
    occurred_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/timeline", response_model=List[ReliabilityEventResponse])
def get_timeline(
    model_id: str,
    model_version_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get the sequential timeline of all reliability events for a given model.
    """
    events = reliability_service.get_timeline(
        db,
        model_id=model_id,
        model_version_id=model_version_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    return events

class CausalGraphResponse(BaseModel):
    nodes: List[ReliabilityEventResponse]
    edges: List[Dict[str, Any]]

@router.get("/incidents/{incident_id}/graph", response_model=CausalGraphResponse)
def get_incident_graph_by_incident_id(
    model_id: str,
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the causal graph centered around a specific incident.
    """
    event = db.query(ReliabilityEvent).filter(
        ReliabilityEvent.source_type == 'incident',
        ReliabilityEvent.source_id == incident_id
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Incident Reliability Event not found")
        
    return reliability_service.get_incident_graph(db, event.id)

@router.get("/graph/{incident_event_id}", response_model=CausalGraphResponse)
def get_incident_graph(
    model_id: str,
    incident_event_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the causal graph centered around a specific incident event (or any event).
    """
    event = db.query(ReliabilityEvent).filter(ReliabilityEvent.id == incident_event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    return reliability_service.get_incident_graph(db, incident_event_id)
