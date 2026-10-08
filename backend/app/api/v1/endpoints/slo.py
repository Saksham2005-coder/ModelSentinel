from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models.user import User
from app.models.slo import ReliabilityObjective, SLOEvaluation, AlertRule
from app.schemas.slo import (
    ReliabilityObjectiveCreate, ReliabilityObjective as ReliabilityObjectiveSchema, ReliabilityObjectiveUpdate,
    SLOEvaluation as SLOEvaluationSchema,
    AlertRuleCreate, AlertRule as AlertRuleSchema, AlertRuleUpdate
)
from app.services.slo_service import slo_service, SLOError

router = APIRouter()

@router.post("/objectives", response_model=ReliabilityObjectiveSchema)
def create_objective(
    *,
    db: Session = Depends(deps.get_db),
    objective_in: ReliabilityObjectiveCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> ReliabilityObjective:
    if current_user.role not in ["ADMIN", "ENGINEER"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    try:
        obj = slo_service.create_objective(db=db, obj_in=objective_in, current_user=current_user)
        return obj
    except SLOError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/objectives", response_model=List[ReliabilityObjectiveSchema])
def list_objectives(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    model_id: str = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    query = db.query(ReliabilityObjective)
    if model_id:
        query = query.filter(ReliabilityObjective.model_id == model_id)
    return query.offset(skip).limit(limit).all()

@router.post("/objectives/{objective_id}/evaluate", response_model=SLOEvaluationSchema)
def evaluate_objective(
    objective_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    try:
        evaluation = slo_service.evaluate_objective(db=db, objective_id=objective_id)
        # also evaluate alerts
        slo_service.evaluate_alert_rules(db=db, objective_id=objective_id, evaluation=evaluation)
        return evaluation
    except SLOError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/objectives/{objective_id}/evaluations", response_model=List[SLOEvaluationSchema])
def list_evaluations(
    objective_id: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    return db.query(SLOEvaluation).filter(SLOEvaluation.objective_id == objective_id).order_by(SLOEvaluation.evaluated_at.desc()).offset(skip).limit(limit).all()

@router.post("/alert-rules", response_model=AlertRuleSchema)
def create_alert_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_in: AlertRuleCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    if current_user.role not in ["ADMIN", "ENGINEER"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_obj = AlertRule(
        objective_id=rule_in.objective_id,
        name=rule_in.name,
        enabled=rule_in.enabled,
        severity=rule_in.severity,
        condition_type=rule_in.condition_type,
        threshold=rule_in.threshold,
        short_window=rule_in.short_window,
        long_window=rule_in.long_window,
        cooldown_seconds=rule_in.cooldown_seconds,
        auto_create_incident=rule_in.auto_create_incident,
        created_by=current_user.id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/alert-rules", response_model=List[AlertRuleSchema])
def list_alert_rules(
    db: Session = Depends(deps.get_db),
    objective_id: str = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    query = db.query(AlertRule)
    if objective_id:
        query = query.filter(AlertRule.objective_id == objective_id)
    return query.all()
