import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"
    
    id = Column(String, primary_key=True, default=lambda: f"wf-{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    workflow_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    steps = relationship("WorkflowStepRun", back_populates="workflow_run", order_by="WorkflowStepRun.order", cascade="all, delete-orphan")

class WorkflowStepRun(Base):
    __tablename__ = "workflow_step_runs"
    
    id = Column(String, primary_key=True, default=lambda: f"wfs-{uuid.uuid4().hex[:8]}")
    workflow_run_id = Column(String, ForeignKey("workflow_runs.id"), nullable=False)
    
    name = Column(String, nullable=False)
    step_type = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    
    is_automatic = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    status = Column(String, nullable=False, default="PENDING")
    
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=1)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    error_message = Column(String, nullable=True)
    
    output_reference_type = Column(String, nullable=True)
    output_reference_id = Column(String, nullable=True)
    
    workflow_run = relationship("WorkflowRun", back_populates="steps")

class WorkflowApproval(Base):
    __tablename__ = "workflow_approvals"
    
    id = Column(String, primary_key=True, default=lambda: f"wfa-{uuid.uuid4().hex[:8]}")
    workflow_step_run_id = Column(String, ForeignKey("workflow_step_runs.id"), nullable=False)
    
    status = Column(String, nullable=False, default="PENDING") # PENDING, APPROVED, REJECTED
    requested_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    responded_at = Column(DateTime, nullable=True)
    
    comments = Column(String, nullable=True)
    reviewer = Column(String, nullable=True)
    
    step_run = relationship("WorkflowStepRun")
