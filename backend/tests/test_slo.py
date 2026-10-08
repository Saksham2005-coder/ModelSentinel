import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.slo import ReliabilityObjective, AlertRule, Alert
from app.models.model import Model
from app.main import app

client = TestClient(app)

def test_create_objective(db: Session):
    model = Model(name="Test Model for SLO", slug="test-model-slo", framework="sklearn", task_type="classification", primary_metric="accuracy", status="active", description="test")
    db.add(model)
    db.commit()
    db.refresh(model)

    response = client.post(
        "/api/v1/slo/objectives",
        json={
            "model_id": model.id,
            "name": "Test SLO",
            "description": "Ensure latency < 100ms",
            "objective_type": "model_performance",
            "metric_name": "latency",
            "target_value": 100.0,
            "comparison_operator": "<",
            "evaluation_window": "30d",
            "enabled": True,
            "severity": "high"
        }
    )
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test SLO"
    assert data["model_id"] == model.id
    
def test_list_objectives(db: Session):
    response = client.get("/api/v1/slo/objectives")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_evaluate_objective_not_found(db: Session):
    response = client.post("/api/v1/slo/objectives/invalid-id/evaluate")
    assert response.status_code == 422 # mapped SLOError
