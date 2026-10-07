from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class WorkflowStepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"

class WorkflowApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class WorkflowStepRunBase(BaseModel):
    name: str
    step_type: str
    order: int
    is_automatic: bool = True
    requires_approval: bool = False
    status: WorkflowStepStatus
    attempt_count: int
    max_attempts: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_reference_type: Optional[str] = None
    output_reference_id: Optional[str] = None

class WorkflowStepRunSchema(WorkflowStepRunBase):
    id: str
    workflow_run_id: str

    model_config = {"from_attributes": True}

class WorkflowRunBase(BaseModel):
    name: str
    workflow_type: str
    description: Optional[str] = None
    status: WorkflowStatus
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

class WorkflowRunSchema(WorkflowRunBase):
    id: str
    steps: List[WorkflowStepRunSchema] = []

    model_config = {"from_attributes": True}

class WorkflowApprovalSchema(BaseModel):
    id: str
    workflow_step_run_id: str
    status: WorkflowApprovalStatus
    requested_at: datetime
    responded_at: Optional[datetime] = None
    comments: Optional[str] = None
    reviewer: Optional[str] = None

    model_config = {"from_attributes": True}

class WorkflowActionRequest(BaseModel):
    comments: Optional[str] = None

class StepResult(BaseModel):
    status: WorkflowStepStatus
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    message: Optional[str] = None
    
