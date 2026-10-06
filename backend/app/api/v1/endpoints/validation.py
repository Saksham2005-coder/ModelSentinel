from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.patch import PatchProposal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.models.validation import ValidationRun, ValidationCheck, ValidationMetric, ValidationArtifact
from app.validation.runner import ValidationRunner

router = APIRouter()

@router.post("/patches/{patch_id}/validation", response_model=dict)
def start_validation(
    patch_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """Start an isolated validation run for a patch proposal asynchronously."""
    patch = db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch proposal not found")
        
    if patch.status != "approved":
        raise HTTPException(status_code=400, detail="Patch must be approved before validation")

    runner = ValidationRunner(db, patch_id)
    # We create the run synchronously so we can return its ID immediately
    run = runner._create_run()
    
    # Actually run it in the background
    background_tasks.add_task(runner.execute)
    
    return {"validation_id": run.id, "status": run.status}

@router.get("/patches/{patch_id}/validation", response_model=List[dict])
def get_validation_runs(
    patch_id: str,
    db: Session = Depends(get_db)
) -> Any:
    runs = db.query(ValidationRun).filter(ValidationRun.patch_proposal_id == patch_id).order_by(ValidationRun.created_at.desc()).all()
    return [{"id": r.id, "status": r.status, "verdict": r.verdict, "created_at": r.created_at, "summary": r.summary} for r in runs]

@router.get("/validation/{validation_id}", response_model=dict)
def get_validation_details(
    validation_id: str,
    db: Session = Depends(get_db)
) -> Any:
    run = db.query(ValidationRun).filter(ValidationRun.id == validation_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Validation run not found")
        
    return {
        "id": run.id,
        "status": run.status,
        "verdict": run.verdict,
        "summary": run.summary,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "duration_ms": run.duration_ms
    }

@router.get("/validation/{validation_id}/checks", response_model=List[dict])
def get_validation_checks(
    validation_id: str,
    db: Session = Depends(get_db)
) -> Any:
    checks = db.query(ValidationCheck).filter(ValidationCheck.validation_run_id == validation_id).order_by(ValidationCheck.created_at.asc()).all()
    return [{"id": c.id, "check_type": c.check_type, "name": c.name, "status": c.status, "summary": c.summary, "details": c.details} for c in checks]

@router.get("/validation/{validation_id}/metrics", response_model=List[dict])
def get_validation_metrics(
    validation_id: str,
    db: Session = Depends(get_db)
) -> Any:
    metrics = db.query(ValidationMetric).filter(ValidationMetric.validation_run_id == validation_id).all()
    return [{"id": m.id, "metric_name": m.metric_name, "baseline_value": m.baseline_value, "current_value": m.current_value, "patched_value": m.patched_value, "delta": m.delta, "status": m.status, "segment_name": m.segment_name} for m in metrics]

@router.post("/validation/{validation_id}/cancel", response_model=dict)
def cancel_validation(
    validation_id: str,
    db: Session = Depends(get_db)
) -> Any:
    run = db.query(ValidationRun).filter(ValidationRun.id == validation_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Validation run not found")
        
    if run.status in ["completed", "failed", "cancelled", "timed_out"]:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed run")
        
    run.status = "cancelled"
    db.commit()
    return {"id": run.id, "status": run.status}
