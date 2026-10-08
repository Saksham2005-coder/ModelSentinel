from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
import datetime
import uuid
from app.db.base_class import Base

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String, nullable=False, index=True) # e.g., 'github'
    type = Column(String, nullable=False) # e.g., 'repository', 'ci'
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="CONNECTED")
    config = Column(JSON, nullable=True) # For non-secret configuration
    created_by = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String, nullable=False, index=True)
    delivery_id = Column(String, nullable=False, index=True, unique=True)
    event_type = Column(String, nullable=False, index=True)
    processing_status = Column(String, nullable=False, default="PENDING") # PENDING, PROCESSED, FAILED, IGNORED
    
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=True)
    pull_request_id = Column(String, ForeignKey("pull_requests.id"), nullable=True)
    workflow_id = Column(String, ForeignKey("workflow_runs.id"), nullable=True)
    
    payload = Column(JSON, nullable=True)
    error_summary = Column(String, nullable=True)

    received_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

class ExternalCheck(Base):
    __tablename__ = "external_checks"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String, nullable=False, index=True)
    external_id = Column(String, nullable=False, index=True)
    pull_request_id = Column(String, ForeignKey("pull_requests.id"), nullable=True)
    
    name = Column(String, nullable=False)
    status = Column(String, nullable=False) # QUEUED, IN_PROGRESS, COMPLETED
    conclusion = Column(String, nullable=True) # SUCCESS, FAILURE, NEUTRAL, CANCELLED, SKIPPED, ACTION_REQUIRED
    commit_sha = Column(String, nullable=False, index=True)
    url = Column(String, nullable=True)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    pull_request = relationship("PullRequest")
