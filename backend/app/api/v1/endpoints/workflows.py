from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.schemas.workflow import WorkflowRunSchema, WorkflowActionRequest
from app.services.workflow_service import WorkflowService
from app.workflows.executor import WorkflowExecutor

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[WorkflowRunSchema])
def list_workflows(db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    return svc.list_workflows()

@router.get("/{workflow_id}", response_model=WorkflowRunSchema)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    wf = svc.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf

@router.post("/{workflow_id}/start", response_model=WorkflowRunSchema)
def start_workflow(workflow_id: str, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    try:
        wf = svc.start_workflow(workflow_id)
        # In a real app we'd dispatch to Celery/background task here. 
        # For Phase 21 local/synchronous is acceptable per instructions.
        executor = WorkflowExecutor(db)
        executor.resume_workflow(workflow_id)
        # Re-fetch after execution
        return svc.get_workflow(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/resume", response_model=WorkflowRunSchema)
def resume_workflow(workflow_id: str, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    wf = svc.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if wf.status != "RUNNING":
        raise HTTPException(status_code=400, detail="Workflow must be RUNNING to resume")
        
    executor = WorkflowExecutor(db)
    executor.resume_workflow(workflow_id)
    return svc.get_workflow(workflow_id)

@router.post("/{workflow_id}/cancel", response_model=WorkflowRunSchema)
def cancel_workflow(workflow_id: str, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    try:
        return svc.cancel_workflow(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/approve", response_model=WorkflowRunSchema)
def approve_workflow_step(workflow_id: str, req: WorkflowActionRequest, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    try:
        wf = svc.approve_step(workflow_id, reviewer="Current User", comments=req.comments)
        # Auto resume
        executor = WorkflowExecutor(db)
        executor.resume_workflow(workflow_id)
        return svc.get_workflow(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/reject", response_model=WorkflowRunSchema)
def reject_workflow_step(workflow_id: str, req: WorkflowActionRequest, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    try:
        return svc.reject_step(workflow_id, reviewer="Current User", comments=req.comments)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=WorkflowRunSchema)
def create_workflow(name: str, workflow_type: str, entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    svc = WorkflowService(db)
    try:
        return svc.create_workflow(name, workflow_type, entity_type, entity_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
