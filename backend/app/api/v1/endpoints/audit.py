from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api import deps
from app.models.audit import AuditEvent

router = APIRouter()

class AuditEventResponse(BaseModel):
    id: str
    timestamp: datetime
    action: str
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    result: Optional[str] = None

@router.get("", response_model=List[AuditEventResponse], dependencies=[Depends(deps.RequirePermissions(["audit.read"]))])
def list_audit_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user)
) -> Any:
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        AuditEventResponse(
            id=e.id,
            timestamp=e.timestamp or datetime.utcnow(),
            action=e.action or "",
            user_id=e.actor_id or "system",
            user_role=e.actor_type or "SYSTEM",
            resource_type=e.resource_type or "system",
            resource_id=e.resource_id or "",
            result=e.result or "SUCCESS"
        )
        for e in events
    ]

