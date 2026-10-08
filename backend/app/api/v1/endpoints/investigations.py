import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
import json

from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.models.investigation import Investigation, InvestigationEvent, InvestigationHypothesis, InvestigationEvidence
from app.schemas.investigation import (
    InvestigationResponse, InvestigationDetailResponse, 
    InvestigationEventResponse, InvestigationHypothesisResponse,
    InvestigationEvidenceResponse
)
from app.investigation.orchestrator import InvestigationOrchestrator

router = APIRouter()

@router.post("/incidents/{incident_id}/investigations", response_model=InvestigationResponse)
def create_investigation(
    incident_id: str,
    db: Session = Depends(get_db)
):
    inv = Investigation(incident_id=incident_id)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/incidents/{incident_id}/investigations", response_model=List[InvestigationResponse])
def list_incident_investigations(
    incident_id: str,
    db: Session = Depends(get_db)
):
    return db.query(Investigation).filter(Investigation.incident_id == incident_id).order_by(Investigation.created_at.desc()).all()

@router.get("/investigations", response_model=List[InvestigationResponse])
def list_all_investigations(
    db: Session = Depends(get_db)
):
    return db.query(Investigation).order_by(Investigation.created_at.desc()).all()

@router.get("/investigations/{investigation_id}", response_model=InvestigationDetailResponse)
def get_investigation(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

@router.post("/investigations/{investigation_id}/start")
def start_investigation(
    investigation_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    if inv.status in ["running", "completed"]:
        raise HTTPException(status_code=400, detail=f"Investigation is {inv.status}")
    
    # Run orchestrator in background
    def run_orchestrator(inv_id: str):
        # We need a new session for background task
        bg_db = next(get_db())
        try:
            orch = InvestigationOrchestrator(bg_db, inv_id)
            orch.run()
        finally:
            bg_db.close()
            
    background_tasks.add_task(run_orchestrator, investigation_id)
    
    # Pre-emptively update status
    inv.status = "queued"
    db.commit()
    return {"message": "Investigation started"}

@router.post("/investigations/{investigation_id}/cancel")
def cancel_investigation(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    if inv.status in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel finished investigation")
    inv.status = "cancelled"
    db.commit()
    return {"message": "Investigation cancelled"}

@router.get("/investigations/{investigation_id}/stream")
async def stream_investigation_events(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    async def event_generator():
        last_event_id = None
        # We use a simple polling mechanism for the SSE stream since we are not using Redis
        # Polling DB every 1 second
        while True:
            # Re-fetch session data (note: in real async app we'd use async session or separate connection)
            # This is a hacky polling approach for synchronous sqlalchemy in a streaming endpoint.
            # Best practice is async db driver, but we'll use a new session to avoid blocking.
            db_stream = next(deps.get_db())
            try:
                query = db_stream.query(InvestigationEvent).filter(InvestigationEvent.investigation_id == investigation_id).order_by(InvestigationEvent.created_at)
                events = query.all()
                
                # yield new events
                for event in events:
                    if last_event_id is None or event.created_at > last_event_id:
                        data = {
                            "id": event.id,
                            "event_type": event.event_type,
                            "title": event.title,
                            "message": event.message,
                            "status": event.status,
                            "metadata_json": event.metadata_json,
                            "created_at": event.created_at.isoformat()
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                        last_event_id = event.created_at
                
                curr_inv = db_stream.query(Investigation).filter(Investigation.id == investigation_id).first()
                if curr_inv and curr_inv.status in ["completed", "failed", "cancelled"]:
                    break
            finally:
                db_stream.close()
            
            await asyncio.sleep(1.0)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
