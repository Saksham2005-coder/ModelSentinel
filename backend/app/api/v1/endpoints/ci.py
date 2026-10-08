from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from app.db.session import SessionLocal
from app.models.integration import ExternalCheck

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status/{check_id}")
def get_ci_status(check_id: str, db: Session = Depends(get_db)) -> Any:
    check = db.query(ExternalCheck).filter(ExternalCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="CI check not found")
    return check

@router.get("/runs/{repository_id}")
def get_ci_runs(repository_id: str, db: Session = Depends(get_db)) -> Any:
    # Get recent CI runs for repository by joining PR -> external checks
    from app.models.pull_request import PullRequest
    checks = db.query(ExternalCheck).join(PullRequest).filter(PullRequest.repository_id == repository_id).order_by(ExternalCheck.started_at.desc()).limit(100).all()
    return checks
