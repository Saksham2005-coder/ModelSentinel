from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Any

from app.db.session import SessionLocal
from app.services.reliability_analytics_service import ReliabilityAnalyticsService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None),
    model_id: Optional[str] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_overview_metrics(db, time_range_days, model_id)

@router.get("/incidents")
def get_incident_analytics(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_incident_analytics(db, time_range_days)

@router.get("/models")
def get_model_reliability(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_model_reliability(db, time_range_days)

@router.get("/models/{model_id}")
def get_model_analytics_detail(
    model_id: str,
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    # Get model-specific overview + detail
    overview = ReliabilityAnalyticsService.get_overview_metrics(db, time_range_days, model_id=model_id)
    return overview

@router.get("/root-causes")
def get_root_causes(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_root_cause_trends(db, time_range_days)

@router.get("/deployments")
def get_deployments(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_deployment_health(db, time_range_days)

@router.get("/fix-effectiveness")
def get_fix_effectiveness(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_fix_effectiveness(db, time_range_days)

@router.get("/policies")
def get_policy_metrics(
    db: Session = Depends(get_db),
    time_range_days: Optional[int] = Query(None)
) -> Any:
    return ReliabilityAnalyticsService.get_policy_metrics(db, time_range_days)
