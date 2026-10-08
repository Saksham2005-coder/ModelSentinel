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
    res = []
    for pr in prs:
        res.append({
            "id": pr.id,
            "incident_id": pr.incident_id,
            "patch_proposal_id": pr.patch_proposal_id,
            "validation_run_id": pr.validation_run_id,
            "repository_id": pr.repository_id,
            "repository_snapshot_id": pr.repository_snapshot_id,
            "branch_name": pr.branch_name,
            "commit_sha": pr.commit_sha,
            "provider": pr.provider,
            "provider_pr_id": pr.provider_pr_id,
            "pr_url": pr.pr_url,
            "title": pr.title,
            "description": pr.description,
            "status": pr.status,
            "created_at": pr.created_at,
            "updated_at": pr.updated_at
        })
    return res

@router.get("/{pr_id}")
def get_pull_request(pr_id: str, db: Session = Depends(get_db)) -> Any:
    pr = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    
    # Sync status
    provider = GitHubProvider()
    svc = PullRequestService(db, provider)
    svc.sync_pr_status(pr.id)
    
    return {
        "id": pr.id,
        "incident_id": pr.incident_id,
        "patch_proposal_id": pr.patch_proposal_id,
        "validation_run_id": pr.validation_run_id,
        "repository_id": pr.repository_id,
        "repository_snapshot_id": pr.repository_snapshot_id,
        "branch_name": pr.branch_name,
        "commit_sha": pr.commit_sha,
        "provider": pr.provider,
        "provider_pr_id": pr.provider_pr_id,
        "pr_url": pr.pr_url,
        "title": pr.title,
        "description": pr.description,
        "status": pr.status,
        "created_at": pr.created_at,
        "updated_at": pr.updated_at
    }

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
