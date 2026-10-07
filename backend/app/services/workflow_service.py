import datetime
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.models.workflow import WorkflowRun, WorkflowStepRun, WorkflowApproval
from app.schemas.workflow import WorkflowStatus, WorkflowStepStatus, WorkflowApprovalStatus

class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def _create_incident_recovery_steps(self, workflow_run_id: str) -> List[WorkflowStepRun]:
        steps = [
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Investigation", step_type="INVESTIGATION", order=1, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Patch Proposal", step_type="PATCH_PROPOSAL", order=2, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Change Intelligence", step_type="CHANGE_INTELLIGENCE", order=3, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Change Risk", step_type="CHANGE_RISK", order=4, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Policy Evaluation", step_type="POLICY_EVALUATION", order=5, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Validation", step_type="VALIDATION", order=6, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Human Approval", step_type="HUMAN_APPROVAL", order=7, is_automatic=False, requires_approval=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Pull Request", step_type="PULL_REQUEST", order=8, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Deployment Gate", step_type="DEPLOYMENT_GATE", order=9, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Deployment", step_type="DEPLOYMENT", order=10, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Verification", step_type="VERIFICATION", order=11, is_automatic=True),
            WorkflowStepRun(workflow_run_id=workflow_run_id, name="Resolution Memory", step_type="RESOLUTION_MEMORY", order=12, is_automatic=True),
        ]
        return steps

    def create_workflow(self, name: str, workflow_type: str, entity_type: str, entity_id: str) -> WorkflowRun:
        run = WorkflowRun(
            name=name,
            workflow_type=workflow_type,
            entity_type=entity_type,
            entity_id=entity_id,
            status=WorkflowStatus.PENDING.value
        )
        self.db.add(run)
        self.db.flush()
        
        if workflow_type == "INCIDENT_RECOVERY":
            steps = self._create_incident_recovery_steps(run.id)
            for step in steps:
                self.db.add(step)
        else:
            raise ValueError(f"Unknown workflow_type: {workflow_type}")
            
        self.db.commit()
        return run

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowRun]:
        return self.db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()

    def list_workflows(self) -> List[WorkflowRun]:
        return self.db.query(WorkflowRun).order_by(WorkflowRun.created_at.desc()).all()
        
    def start_workflow(self, workflow_id: str) -> WorkflowRun:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError("Workflow not found")
        if wf.status != WorkflowStatus.PENDING.value:
            raise ValueError("Can only start PENDING workflows")
            
        wf.status = WorkflowStatus.RUNNING.value
        wf.started_at = datetime.datetime.now(datetime.UTC)
        self.db.commit()
        
        # Trigger executor (in real system, might be queued; here we can do it inline or separately)
        # We'll rely on an Executor class to actually step through
        return wf

    def cancel_workflow(self, workflow_id: str) -> WorkflowRun:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError("Workflow not found")
        if wf.status not in [WorkflowStatus.RUNNING.value, WorkflowStatus.WAITING_APPROVAL.value, WorkflowStatus.PAUSED.value]:
            raise ValueError("Cannot cancel completed or failed workflow")
            
        wf.status = WorkflowStatus.CANCELLED.value
        self.db.commit()
        return wf

    def approve_step(self, workflow_id: str, reviewer: str, comments: str = None) -> WorkflowRun:
        wf = self.get_workflow(workflow_id)
        if not wf or wf.status != WorkflowStatus.WAITING_APPROVAL.value:
            raise ValueError("Workflow not waiting for approval")
            
        # Find the waiting step
        waiting_step = next((s for s in wf.steps if s.status == WorkflowStepStatus.WAITING.value), None)
        if not waiting_step:
            raise ValueError("No waiting step found")
            
        approval = self.db.query(WorkflowApproval).filter(WorkflowApproval.workflow_step_run_id == waiting_step.id).first()
        if not approval:
            raise ValueError("Approval record not found")
            
        approval.status = WorkflowApprovalStatus.APPROVED.value
        approval.responded_at = datetime.datetime.now(datetime.UTC)
        approval.reviewer = reviewer
        approval.comments = comments
        
        waiting_step.status = WorkflowStepStatus.SUCCESS.value
        waiting_step.completed_at = datetime.datetime.now(datetime.UTC)
        
        wf.status = WorkflowStatus.RUNNING.value
        self.db.commit()
        return wf

    def reject_step(self, workflow_id: str, reviewer: str, comments: str = None) -> WorkflowRun:
        wf = self.get_workflow(workflow_id)
        if not wf or wf.status != WorkflowStatus.WAITING_APPROVAL.value:
            raise ValueError("Workflow not waiting for approval")
            
        waiting_step = next((s for s in wf.steps if s.status == WorkflowStepStatus.WAITING.value), None)
        if not waiting_step:
            raise ValueError("No waiting step found")
            
        approval = self.db.query(WorkflowApproval).filter(WorkflowApproval.workflow_step_run_id == waiting_step.id).first()
        if not approval:
            raise ValueError("Approval record not found")
            
        approval.status = WorkflowApprovalStatus.REJECTED.value
        approval.responded_at = datetime.datetime.now(datetime.UTC)
        approval.reviewer = reviewer
        approval.comments = comments
        
        waiting_step.status = WorkflowStepStatus.FAILED.value
        waiting_step.error_message = f"Rejected by {reviewer}"
        waiting_step.completed_at = datetime.datetime.now(datetime.UTC)
        
        wf.status = WorkflowStatus.FAILED.value
        self.db.commit()
        return wf
