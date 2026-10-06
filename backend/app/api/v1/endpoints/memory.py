from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List, Dict
from pydantic import BaseModel
import datetime

from app.db.session import SessionLocal
from app.services.incident_memory_service import IncidentMemoryService
from app.services.similarity_service import SimilarityService
from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MemoryCreatePayload(BaseModel):
    title: str = None
    summary: str = None
    root_cause: str = None
    root_cause_category: str = None
    affected_metrics: List[str] = []
    affected_features: List[str] = []
    affected_segments: List[str] = []
    signal_families: List[str] = []
    resolution_summary: str = None

@router.get("/memories")
def list_memories(db: Session = Depends(get_db)):
    memories = db.query(IncidentMemory).order_by(IncidentMemory.created_at.desc()).all()
    # Simple dictionary serialization for frontend
    return [
        {
            "id": m.id,
            "incident_id": m.incident_id,
            "title": m.title,
            "root_cause": m.root_cause,
            "root_cause_category": m.root_cause_category,
            "model_id": m.model_id,
            "affected_segments": m.affected_segments,
            "resolution_summary": m.resolution_summary,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in memories
    ]

@router.get("/incidents/{incident_id}/memory/eligibility")
def check_eligibility(incident_id: str, db: Session = Depends(get_db)):
    svc = IncidentMemoryService(db)
    res = svc.check_eligibility(incident_id)
    if res["eligible"]:
        return {"eligible": True, "reason": "Eligible for memory"}
    return {"eligible": False, "reason": res["reason"]}

@router.post("/incidents/{incident_id}/memory")
def create_memory(incident_id: str, payload: MemoryCreatePayload, db: Session = Depends(get_db)):
    svc = IncidentMemoryService(db)
    try:
        mem = svc.create_memory(incident_id, payload.dict(exclude_unset=True))
        return {"id": mem.id, "status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/incidents/{incident_id}/similar")
def get_similar_incidents(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    svc = SimilarityService(db)
    results = svc.find_similar_memories_for_incident(incident)
    
    # Format for frontend
    out = []
    for r in results:
        mem = r["memory"]
        out.append({
            "incident_id": mem.incident_id,
            "memory_id": mem.id,
            "title": mem.title,
            "similarity_score": r["similarity_score"],
            "reasons": r["reasons"],
            "root_cause": mem.root_cause,
            "resolution_summary": mem.resolution_summary
        })
    return out
