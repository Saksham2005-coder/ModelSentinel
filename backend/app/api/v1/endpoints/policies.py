from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.models.policy import ReliabilityPolicy, PolicyEvaluation
from app.models.patch import PatchProposal, PatchReview
from app.models.change_risk import ChangeRiskAssessment
from app.models.pull_request import PullRequest
from app.models.validation import ValidationRun
from app.models.regression import RegressionRun
from app.services.policy_service import PolicyEvaluationService
import datetime

router = APIRouter()

class PolicyRuleSchema(BaseModel):
    type: str
    operator: str = "="
    value: Any
    severity: str = "REVIEW_REQUIRED" # or "BLOCK"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PolicyCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    scope: str
    environment: Optional[str] = None
    model_id: Optional[str] = None
    enabled: bool = True
    priority: int = 0
    rules: List[PolicyRuleSchema]

class PolicyUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    rules: Optional[List[PolicyRuleSchema]] = None

class EvaluateRequestSchema(BaseModel):
    target_type: str
    target_id: str
    environment: Optional[str] = None
    model_id: Optional[str] = None
    context: Dict[str, Any]

@router.get("/")
def get_policies(db: Session = Depends(get_db)):
    return db.query(ReliabilityPolicy).all()

@router.get("/{policy_id}")
def get_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(ReliabilityPolicy).filter(ReliabilityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    recent_evaluations = db.query(PolicyEvaluation).filter(PolicyEvaluation.policy_id == policy_id).order_by(PolicyEvaluation.evaluated_at.desc()).limit(10).all()
    
    return {
        "policy": policy,
        "recent_evaluations": recent_evaluations
    }

@router.post("/")
def create_policy(policy_in: PolicyCreateSchema, db: Session = Depends(get_db)):
    policy = ReliabilityPolicy(
        name=policy_in.name,
        description=policy_in.description,
        scope=policy_in.scope,
        environment=policy_in.environment,
        model_id=policy_in.model_id,
        enabled=policy_in.enabled,
        priority=policy_in.priority,
        rules=[r.dict() for r in policy_in.rules]
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy

@router.patch("/{policy_id}")
def update_policy(policy_id: str, policy_in: PolicyUpdateSchema, db: Session = Depends(get_db)):
    policy = db.query(ReliabilityPolicy).filter(ReliabilityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    update_data = policy_in.dict(exclude_unset=True)
    if "rules" in update_data:
        update_data["rules"] = [r.dict() if hasattr(r, 'dict') else r for r in update_data["rules"]]
        
    for field, value in update_data.items():
        setattr(policy, field, value)
        
    db.commit()
    db.refresh(policy)
    return policy

@router.delete("/{policy_id}")
def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(ReliabilityPolicy).filter(ReliabilityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(policy)
    db.commit()
    return {"status": "ok"}

@router.post("/evaluate")
def evaluate_policy(request: EvaluateRequestSchema, db: Session = Depends(get_db)):
    svc = PolicyEvaluationService(db)
    return svc.evaluate_action(
        target_type=request.target_type,
        target_id=request.target_id,
        environment=request.environment,
        model_id=request.model_id,
        context=request.context
    )

@router.post("/evaluate-patch/{patch_id}")
def evaluate_patch_policy(patch_id: str, db: Session = Depends(get_db)):
    patch = db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
        
    risk = db.query(ChangeRiskAssessment).filter(ChangeRiskAssessment.patch_proposal_id == patch_id).first()
    
    # We will assume human approval is PASS if it is approved
    approval_status = "PASS" if patch.status == "approved" else "FAIL"
    
    context = {
        "risk_level": risk.risk_level if risk else "UNKNOWN",
        "human_approval": approval_status,
        "validation_status": "PENDING", # usually unknown until validated
        "regression_status": "PENDING",
        "ci_status": "PENDING"
    }
    
    svc = PolicyEvaluationService(db)
    return svc.evaluate_action(
        target_type="PATCH",
        target_id=patch_id,
        context=context
    )

@router.post("/evaluate-deployment/{deployment_id}")
def evaluate_deployment_policy(deployment_id: str, db: Session = Depends(get_db)):
    from app.models.deployment import Deployment
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    pr = db.query(PullRequest).filter(PullRequest.id == deployment.pull_request_id).first()
    patch = db.query(PatchProposal).filter(PatchProposal.id == pr.patch_proposal_id).first()
    val_run = db.query(ValidationRun).filter(ValidationRun.id == pr.validation_run_id).first()
    
    regression_runs = db.query(RegressionRun).filter(RegressionRun.validation_run_id == pr.validation_run_id).all()
    regression_passed = all([r.status == 'PASS' for r in regression_runs]) if regression_runs else False
    
    risk = db.query(ChangeRiskAssessment).filter(ChangeRiskAssessment.patch_proposal_id == patch.id).first()
    
    context = {
        "risk_level": risk.risk_level if risk else "UNKNOWN",
        "human_approval": "PASS" if patch.status == "approved" else "FAIL",
        "validation_status": "PASS" if (val_run and val_run.verdict == "PASS") else "FAIL",
        "regression_status": "PASS" if regression_passed else "FAIL",
        "ci_status": "PASS" if pr.status in ["PASSED", "MERGED"] else "FAIL",
        "deployment_health": "HEALTHY" # assume healthy pre-deployment
    }
    
    svc = PolicyEvaluationService(db)
    res = svc.evaluate_action(
        target_type="DEPLOYMENT",
        target_id=deployment_id,
        context=context
    )
    
    # Update deployment record
    import json
    deployment.policy_result = json.dumps(res)
    db.commit()
    
    return res
