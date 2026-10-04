from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.model import Model, ModelVersion
import uuid
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    db = SessionLocal()
    yield
    db.query(ModelVersion).delete()
    db.query(Model).delete()
    db.commit()
    db.close()

def test_create_model():
    response = client.post(
        "/api/v1/models",
        json={
            "name": "Test Model",
            "slug": "test-model-1",
            "framework": "scikit-learn",
            "task_type": "classification",
            "primary_metric": "f1_score"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Model"
    assert "id" in data

def test_get_models():
    # First create one
    client.post(
        "/api/v1/models",
        json={
            "name": "Test Model 2",
            "slug": "test-model-2",
            "framework": "scikit-learn",
            "task_type": "classification",
            "primary_metric": "f1_score"
        }
    )
    
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["name"] == "Test Model 2"
