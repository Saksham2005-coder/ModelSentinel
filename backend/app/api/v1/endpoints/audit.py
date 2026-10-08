from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.models.audit import AuditEvent

router = APIRouter()

@router.get("", dependencies=[Depends(deps.RequirePermissions(["audit.read"]))])
def list_audit_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user)
) -> Any:
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return events
