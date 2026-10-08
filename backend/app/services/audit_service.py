from sqlalchemy.orm import Session
from app.models.audit import AuditEvent
import logging

logger = logging.getLogger(__name__)

def record_event(
    db: Session,
    actor_id: str,
    actor_type: str,
    action: str,
    resource_type: str,
    resource_id: str,
    result: str,
    metadata: dict = None
) -> AuditEvent:
    """
    Creates an immutable audit event in the database.
    """
    if metadata is None:
        metadata = {}
    
    event = AuditEvent(
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        event_metadata=metadata
    )
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to record audit event: {str(e)}")
        # In a real high-security system we might raise or halt execution, 
        # but for this we'll log it if the DB fails.
    
    return event
