from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.models.pull_request import PullRequest
from app.services.pull_request_service import PullRequestService
from app.services.git_provider import GitHubProvider
from typing import Any

router = APIRouter()

@router.get("/")
def list_pull_requests(db: Session = Depends(get_db)) -> Any:
    prs = db.query(PullRequest).order_by(PullRequest.created_at.desc()).all()
    return prs

@router.get("/{pr_id}")
def get_pull_request(pr_id: str, db: Session = Depends(get_db)) -> Any:
    pr = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    
    # Sync status
    provider = GitHubProvider()
    svc = PullRequestService(db, provider)
    svc.sync_pr_status(pr.id)
    
    return pr

@router.post("/")
def create_pull_request(incident_id: str, patch_id: str, validation_run_id: str, db: Session = Depends(get_db)) -> Any:
    provider = GitHubProvider()
    svc = PullRequestService(db, provider)
    try:
        pr = svc.create_pull_request(incident_id, patch_id, validation_run_id)
        return pr
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{pr_id}/checks")
def get_pull_request_checks(pr_id: str, db: Session = Depends(get_db)) -> Any:
    from app.models.integration import ExternalCheck
    checks = db.query(ExternalCheck).filter(ExternalCheck.pull_request_id == pr_id).order_by(ExternalCheck.started_at.desc()).all()
    return checks
