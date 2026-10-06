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
from app.services.deployment_verification_service import DeploymentVerificationService
from pydantic import BaseModel
from typing import Any, Optional
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
            "deployed_at": d.deployed_at,
            "environment": d.environment,
            "deployment_source": d.deployment_source,
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

class RecordDeploymentRequest(BaseModel):
    environment: str
    deployment_source: str
    deployed_by: Optional[str] = None

@router.post("/{id}/record")
def record_deployment(id: str, req: RecordDeploymentRequest, db: Session = Depends(get_db)):
    try:
        dep = DeploymentVerificationService.record_deployment(
            db, id, req.environment, req.deployment_source, req.deployed_by
        )
        return {"status": dep.status, "deployed_at": dep.deployed_at}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/verify/start")
def start_verification(id: str, db: Session = Depends(get_db)):
    try:
        verif = DeploymentVerificationService.start_verification(db, id)
        return {"status": verif.status, "verification_id": verif.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/verify/evaluate")
def evaluate_health(id: str, db: Session = Depends(get_db)):
    try:
        verif = DeploymentVerificationService.evaluate_health(db, id)
        return {
            "status": verif.status,
            "summary": verif.summary,
            "failure_reason": verif.failure_reason,
            "observations": verif.post_deployment_observation
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}")
def get_deployment(id: str, db: Session = Depends(get_db)):
    d = db.query(Deployment).filter(Deployment.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    verifications = d.deployment_verifications if hasattr(d, 'deployment_verifications') else []
    # Actually, we didn't add back_populates in DeploymentVerification for the list of verifications on Deployment,
    # let's just query it directly.
    from app.models.deployment_verification import DeploymentVerification
    verifs = db.query(DeploymentVerification).filter(DeploymentVerification.deployment_id == id).order_by(DeploymentVerification.started_at.desc()).all()
    
    return {
        "id": d.id,
        "pull_request_id": d.pull_request_id,
        "incident_id": d.incident_id,
        "commit_sha": d.commit_sha,
        "status": d.status,
        "gate_result": json.loads(d.gate_result) if d.gate_result else {},
        "block_reason": d.block_reason,
        "deployed_at": d.deployed_at,
        "environment": d.environment,
        "deployment_source": d.deployment_source,
        "created_at": d.created_at,
        "verifications": [
            {
                "id": v.id,
                "status": v.status,
                "summary": v.summary,
                "failure_reason": v.failure_reason,
                "started_at": v.started_at,
                "completed_at": v.completed_at,
                "observations": v.post_deployment_observation,
                "baseline": v.baseline_reference
            } for v in verifs
        ]
    }
