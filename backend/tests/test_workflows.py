import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowRun, WorkflowStepRun, WorkflowApproval
from app.main import app

client = TestClient(app)

def test_create_workflow(db: Session):
    response = client.post("/api/v1/workflows/?name=Test&workflow_type=INCIDENT_RECOVERY&entity_type=incident&entity_id=123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PENDING"
    assert data["workflow_type"] == "INCIDENT_RECOVERY"
    assert len(data["steps"]) == 12

def test_start_and_execute_workflow(db: Session):
    response = client.post("/api/v1/workflows/?name=TestStart&workflow_type=INCIDENT_RECOVERY&entity_type=incident&entity_id=123")
    wf_id = response.json()["id"]

    response = client.post(f"/api/v1/workflows/{wf_id}/start")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "WAITING_APPROVAL"
    
    # 6 automatic steps should be SUCCESS
    for step in data["steps"][:6]:
        assert step["status"] == "SUCCESS"
        
    # The 7th is HUMAN_APPROVAL, should be WAITING
    assert data["steps"][6]["status"] == "WAITING"
    assert data["steps"][6]["requires_approval"] is True
    
def test_approve_workflow(db: Session):
    response = client.post("/api/v1/workflows/?name=TestApprove&workflow_type=INCIDENT_RECOVERY&entity_type=incident&entity_id=123")
    wf_id = response.json()["id"]
    client.post(f"/api/v1/workflows/{wf_id}/start")

    response = client.post(f"/api/v1/workflows/{wf_id}/approve", json={"comments": "looks good"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    
    # Check that human approval step succeeded
    assert data["steps"][6]["status"] == "SUCCESS"
    
    # Check that remaining steps succeeded
    for step in data["steps"][7:]:
        assert step["status"] == "SUCCESS"

def test_reject_workflow(db: Session):
    response = client.post("/api/v1/workflows/?name=TestReject&workflow_type=INCIDENT_RECOVERY&entity_type=incident&entity_id=123")
    wf_id = response.json()["id"]
    client.post(f"/api/v1/workflows/{wf_id}/start")

    response = client.post(f"/api/v1/workflows/{wf_id}/reject", json={"comments": "nope"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    
    # Approval step is FAILED
    assert data["steps"][6]["status"] == "FAILED"
    
    # Downstream steps remain PENDING
    assert data["steps"][7]["status"] == "PENDING"
