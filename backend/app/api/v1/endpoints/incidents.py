from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.models.incident import Incident
from app.schemas.incident import IncidentResponse, IncidentDetailResponse, IncidentResolution
from app.incidents.service import IncidentService

from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    model_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None
):
    query = db.query(Incident)
    
    if model_id:
        query = query.filter(Incident.model_id == model_id)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if category:
        query = query.filter(Incident.category == category)
        
    incidents = query.order_by(desc(Incident.detected_at)).offset(skip).limit(limit).all()
    return incidents

@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{incident_id}/acknowledge", response_model=IncidentResponse)
def acknowledge_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentService.acknowledge(db, incident)

@router.post("/{incident_id}/start-investigation", response_model=IncidentResponse)
def start_investigation(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentService.start_investigation(db, incident)

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(incident_id: str, payload: IncidentResolution, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentService.resolve(db, incident, payload.resolution_note)

@router.post("/{incident_id}/suppress", response_model=IncidentResponse)
def suppress_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentService.suppress(db, incident)

@router.get("/{incident_id}/repository-context")
def get_incident_repository_context(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    from app.repository.service import RepositoryService
    svc = RepositoryService(db)
    
    return svc.get_context_for_incident(incident)
