import datetime
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowRun, WorkflowStepRun, WorkflowApproval
from app.schemas.workflow import WorkflowStatus, WorkflowStepStatus, WorkflowApprovalStatus

# Dummy imports representing existing services
# We assume they exist and are accessible, for demo we'll mock their interaction based on entity_id (incident_id)

class WorkflowExecutor:
    def __init__(self, db: Session):
        self.db = db

    def resume_workflow(self, workflow_id: str):
        wf = self.db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
        if not wf:
            return
            
        if wf.status != WorkflowStatus.RUNNING.value:
            return
            
        pending_steps = [s for s in wf.steps if s.status in (WorkflowStepStatus.PENDING.value, WorkflowStepStatus.RUNNING.value)]
        pending_steps.sort(key=lambda x: x.order)
        
        for step in pending_steps:
            if wf.status != WorkflowStatus.RUNNING.value:
                break
                
            self._execute_step(wf, step)

        # Check if all steps completed
        if all(s.status == WorkflowStepStatus.SUCCESS.value for s in wf.steps):
            wf.status = WorkflowStatus.COMPLETED.value
            wf.completed_at = datetime.datetime.now(datetime.UTC)
            self.db.commit()

    def _execute_step(self, wf: WorkflowRun, step: WorkflowStepRun):
        step.status = WorkflowStepStatus.RUNNING.value
        step.started_at = step.started_at or datetime.datetime.now(datetime.UTC)
        step.attempt_count += 1
        self.db.commit()
        
        if step.requires_approval:
            self._request_approval(wf, step)
            return

        try:
            # Here we would delegate to actual backend services based on step.step_type.
            # E.g., if step_type == "INVESTIGATION", call InvestigationService
            # We mock the successful deterministic return for testing unless it fails.
            
            # Simulated dummy dispatcher
            result_status = WorkflowStepStatus.SUCCESS.value
            
            if step.step_type == "VALIDATION":
                # Simulated explicit logic
                # Normally calls ValidationRunner
                pass
                
            elif step.step_type == "POLICY_EVALUATION":
                pass
                
            elif step.step_type == "CHANGE_RISK":
                pass
                
            step.status = result_status
            step.completed_at = datetime.datetime.now(datetime.UTC)
            self.db.commit()
            
        except Exception as e:
            if step.attempt_count < step.max_attempts:
                step.status = WorkflowStepStatus.PENDING.value # allow retry next time
                self.db.commit()
            else:
                step.status = WorkflowStepStatus.FAILED.value
                step.error_message = str(e)
                step.completed_at = datetime.datetime.now(datetime.UTC)
                wf.status = WorkflowStatus.FAILED.value
                self.db.commit()

    def _request_approval(self, wf: WorkflowRun, step: WorkflowStepRun):
        step.status = WorkflowStepStatus.WAITING.value
        wf.status = WorkflowStatus.WAITING_APPROVAL.value
        
        # Create approval record
        approval = WorkflowApproval(
            workflow_step_run_id=step.id,
            status=WorkflowApprovalStatus.PENDING.value
        )
        self.db.add(approval)
        self.db.commit()
