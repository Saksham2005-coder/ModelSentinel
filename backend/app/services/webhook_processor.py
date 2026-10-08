from sqlalchemy.orm import Session
from app.models.integration import WebhookEvent, ExternalCheck
from app.models.pull_request import PullRequest
from app.models.workflow import WorkflowRun, WorkflowStepRun
from app.services.workflow_service import WorkflowService
import datetime
import uuid

def process_webhook_event(db: Session, event: WebhookEvent):
    """Process a verified webhook event."""
    if event.event_type == "pull_request":
        process_pull_request_event(db, event)
    elif event.event_type == "check_run":
        process_check_run_event(db, event)
    elif event.event_type == "workflow_run":
        process_workflow_run_event(db, event)
    elif event.event_type == "push":
        # Handle push event if necessary, or just ignore
        pass
    else:
        # Ignore unsupported events
        pass

def process_pull_request_event(db: Session, event: WebhookEvent):
    payload = event.payload
    action = payload.get("action")
    pr_data = payload.get("pull_request", {})
    pr_number = pr_data.get("number")
    repo_data = payload.get("repository", {})
    repo_name = repo_data.get("full_name")
    
    # Try to find an internal PR matching this
    pr = db.query(PullRequest).filter(
        PullRequest.provider == "github",
        PullRequest.provider_pr_id == str(pr_number)
    ).first()
    
    if not pr:
        # If we can't find it by provider_pr_id, maybe we created it recently but haven't updated the ID?
        # Typically the PR service links it immediately.
        # It's also possible this PR wasn't created by ModelSentinel.
        return
        
    event.pull_request_id = pr.id
    
    if action == "closed":
        if pr_data.get("merged"):
            pr.status = "MERGED"
            # Workflow integration for merge?
            # E.g., moving from PR stage to DEPLOYMENT stage
        else:
            pr.status = "CLOSED"
    elif action == "reopened":
        pr.status = "OPEN"
    elif action == "opened":
        pr.status = "OPEN"
        
    db.commit()

def process_check_run_event(db: Session, event: WebhookEvent):
    payload = event.payload
    action = payload.get("action")
    check_run = payload.get("check_run", {})
    
    if action not in ["created", "completed", "rerequested"]:
        return
        
    external_id = str(check_run.get("id"))
    name = check_run.get("name")
    status = check_run.get("status").upper() if check_run.get("status") else "UNKNOWN"
    conclusion = check_run.get("conclusion").upper() if check_run.get("conclusion") else None
    head_sha = check_run.get("head_sha")
    url = check_run.get("html_url")
    
    check = db.query(ExternalCheck).filter(
        ExternalCheck.provider == "github",
        ExternalCheck.external_id == external_id
    ).first()
    
    if not check:
        # We might not know which PR this belongs to right away, unless we check the check_run's pull_requests array
        # or match by commit_sha
        pr = db.query(PullRequest).filter(PullRequest.commit_sha == head_sha).first()
        pr_id = pr.id if pr else None
        
        check = ExternalCheck(
            id=str(uuid.uuid4()),
            provider="github",
            external_id=external_id,
            name=name,
            status=status,
            conclusion=conclusion,
            commit_sha=head_sha,
            url=url,
            pull_request_id=pr_id,
            started_at=datetime.datetime.utcnow()
        )
        db.add(check)
        if pr_id:
            event.pull_request_id = pr_id
    else:
        check.status = status
        check.conclusion = conclusion
        if status == "COMPLETED" and not check.completed_at:
            check.completed_at = datetime.datetime.utcnow()
            
    db.commit()
    
    # Workflow integration
    if check.pull_request_id:
        update_workflow_on_ci_status(db, check.pull_request_id)

def process_workflow_run_event(db: Session, event: WebhookEvent):
    # workflow_run events are similar to check_run but for the whole workflow.
    # For now, we can rely on check_run for granular status, or update external checks based on workflow_run.
    pass

def update_workflow_on_ci_status(db: Session, pr_id: str):
    pr = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
    if not pr:
        return
        
    # Find all checks for this PR
    checks = db.query(ExternalCheck).filter(ExternalCheck.pull_request_id == pr_id).all()
    
    if not checks:
        return
        
    all_completed = all(c.status == "COMPLETED" for c in checks)
    any_failed = any(c.conclusion in ["FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"] for c in checks)
    
    # Find active workflow run that's waiting on CI
    # In Phase 21, we implemented workflow runs. A patch proposal/validation run usually has a workflow run.
    workflow_run = db.query(WorkflowRun).filter(
        WorkflowRun.incident_id == pr.incident_id,
        WorkflowRun.status.in_(["RUNNING", "WAITING"])
    ).first()
    
    if not workflow_run:
        return
        
    # Find the current active step that might be waiting for CI
    # This might be 'CI_VALIDATION' or 'EXTERNAL_CI'
    step = db.query(WorkflowStepRun).filter(
        WorkflowStepRun.workflow_run_id == workflow_run.id,
        WorkflowStepRun.status == "RUNNING"
    ).first()
    
    if not step:
        return
        
    # Example logic:
    if step.step_type == "CI_VALIDATION" or step.step_type == "PULL_REQUEST":
        if any_failed:
            WorkflowService.update_step_status(db, step.id, "FAILED", {"reason": "CI check failed"})
        elif all_completed and not any_failed:
            # Maybe CI succeeded, but we don't automatically deploy/complete if other gates exist.
            # But we can mark the CI step as COMPLETED.
            if step.step_type == "CI_VALIDATION":
                WorkflowService.update_step_status(db, step.id, "COMPLETED", {"reason": "CI checks passed"})
