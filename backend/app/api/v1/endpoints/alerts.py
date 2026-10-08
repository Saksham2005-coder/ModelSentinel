from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.api import deps
from app.models.user import User
from app.models.slo import Alert
from app.schemas.slo import Alert as AlertSchema
from app.services.audit_service import record_event as audit_record_event
from app.services.reliability_service import reliability_service

router = APIRouter()

@router.get("/", response_model=List[AlertSchema])
def list_alerts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    model_id: str = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status)
    if model_id:
        query = query.filter(Alert.model_id == model_id)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertSchema)
def get_alert(
    alert_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/{alert_id}/acknowledge", response_model=AlertSchema)
def acknowledge_alert(
    alert_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if current_user.role not in ["ADMIN", "ENGINEER", "REVIEWER"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    if alert.status != "OPEN":
        raise HTTPException(status_code=400, detail="Alert is not OPEN")
        
    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = current_user.id
    db.commit()
    db.refresh(alert)
    
    audit_record_event(db, current_user.id, "USER", "ALERT_ACKNOWLEDGED", "ALERT", alert.id, "SUCCESS")
    reliability_service.emit_event(
        db, alert.model_id, "ALERT_ACKNOWLEDGED", "alert", alert.id, f"Alert acknowledged by {current_user.email}", 
        summary="Alert state moved to ACKNOWLEDGED", severity="info"
    )
    
    return alert

@router.post("/{alert_id}/resolve", response_model=AlertSchema)
def resolve_alert(
    alert_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if current_user.role not in ["ADMIN", "ENGINEER", "REVIEWER"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    if alert.status in ["RESOLVED", "SUPPRESSED"]:
        raise HTTPException(status_code=400, detail="Alert is already closed")
        
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = current_user.id
    db.commit()
    db.refresh(alert)
    
    audit_record_event(db, current_user.id, "USER", "ALERT_RESOLVED", "ALERT", alert.id, "SUCCESS")
    reliability_service.emit_event(
        db, alert.model_id, "ALERT_RESOLVED", "alert", alert.id, f"Alert resolved manually by {current_user.email}", 
        summary="Alert state moved to RESOLVED", severity="info"
    )
    
    return alert

@router.post("/{alert_id}/suppress", response_model=AlertSchema)
def suppress_alert(
    alert_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if current_user.role not in ["ADMIN", "ENGINEER"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    alert.status = "SUPPRESSED"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by = current_user.id
    db.commit()
    db.refresh(alert)
    
    audit_record_event(db, current_user.id, "USER", "ALERT_SUPPRESSED", "ALERT", alert.id, "SUCCESS")
    return alert
