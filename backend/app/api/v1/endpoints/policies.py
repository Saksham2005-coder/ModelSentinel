from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.api import deps
from app.models.policy import ReliabilityPolicy, PolicyEvaluation
from app.services.policy_service import PolicyEvaluationService
import datetime

router = APIRouter()

class PolicyRuleSchema(BaseModel):
    type: str
    operator: str = "="
    value: Any
    severity: str = "REVIEW_REQUIRED" # or "BLOCK"

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
def get_policies(db: Session = Depends(deps.get_db)):
    return db.query(ReliabilityPolicy).all()

@router.get("/{policy_id}")
def get_policy(policy_id: str, db: Session = Depends(deps.get_db)):
    policy = db.query(ReliabilityPolicy).filter(ReliabilityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    recent_evaluations = db.query(PolicyEvaluation).filter(PolicyEvaluation.policy_id == policy_id).order_by(PolicyEvaluation.evaluated_at.desc()).limit(10).all()
    
    return {
        "policy": policy,
        "recent_evaluations": recent_evaluations
    }

@router.post("/")
def create_policy(policy_in: PolicyCreateSchema, db: Session = Depends(deps.get_db)):
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
def update_policy(policy_id: str, policy_in: PolicyUpdateSchema, db: Session = Depends(deps.get_db)):
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
def delete_policy(policy_id: str, db: Session = Depends(deps.get_db)):
    policy = db.query(ReliabilityPolicy).filter(ReliabilityPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    db.delete(policy)
    db.commit()
    return {"status": "ok"}

@router.post("/evaluate")
def evaluate_policy(request: EvaluateRequestSchema, db: Session = Depends(deps.get_db)):
    svc = PolicyEvaluationService(db)
    return svc.evaluate_action(
        target_type=request.target_type,
        target_id=request.target_id,
        environment=request.environment,
        model_id=request.model_id,
        context=request.context
    )
