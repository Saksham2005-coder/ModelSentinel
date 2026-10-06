from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.models.deployment import Deployment
from app.services.deployment_gate_service import DeploymentGateService
from typing import Any
import json

router = APIRouter()

@router.get("/")
def list_deployments(db: Session = Depends(get_db)) -> Any:
    deps = db.query(Deployment).order_by(Deployment.created_at.desc()).all()
    # parse gate_result for frontend
    res = []
    for d in deps:
        d_dict = {
            "id": d.id,
            "pull_request_id": d.pull_request_id,
            "incident_id": d.incident_id,
            "commit_sha": d.commit_sha,
            "status": d.status,
            "gate_result": json.loads(d.gate_result) if d.gate_result else {},
            "block_reason": d.block_reason,
            "approved_by": d.approved_by,
            "created_at": d.created_at
        }
        res.append(d_dict)
    return res

@router.post("/{pr_id}/evaluate")
def evaluate_deployment_gate(pr_id: str, db: Session = Depends(get_db)) -> Any:
    svc = DeploymentGateService(db)
    try:
        deployment = svc.evaluate_gate(pr_id)
        return {
            "id": deployment.id,
            "pull_request_id": deployment.pull_request_id,
            "incident_id": deployment.incident_id,
            "commit_sha": deployment.commit_sha,
            "status": deployment.status,
            "gate_result": json.loads(deployment.gate_result) if deployment.gate_result else {},
            "block_reason": deployment.block_reason,
            "created_at": deployment.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
