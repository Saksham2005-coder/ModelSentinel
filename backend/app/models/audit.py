import uuid
import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.db.base_class import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    actor_id = Column(String, index=True)
    actor_type = Column(String)  # USER, SYSTEM, INTEGRATION
    action = Column(String, index=True)
    resource_type = Column(String, index=True)
    resource_id = Column(String, index=True)
    result = Column(String)  # SUCCESS, DENIED, FAILED
    event_metadata = Column(JSON, default=dict)  # request/correlation id, IP, etc. (no secrets)
    source = Column(String)
