from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.model import Model, ModelVersion
from app.models.incident import Incident
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    db = SessionLocal()
    yield
    db.query(Incident).delete()
    db.query(ModelVersion).delete()
    db.query(Model).delete()
    db.commit()
    db.close()

def test_incident_flow():
    # 1. Create Model
    client.post(
        "/api/v1/models",
        json={
            "name": "Test Incident Model",
            "slug": "email-spam-classifier",
            "framework": "scikit-learn",
            "task_type": "classification",
            "primary_metric": "f1_score"
        }
    )
    
    models = client.get("/api/v1/models").json()["items"]
    model_id = models[0]["id"]
    
    # create a version
    client.post(
        f"/api/v1/models/{model_id}/versions",
        json={
            "version": "v1.0.0",
            "description": "Initial version",
            "is_active": True
        }
    )
    
    model_detail = client.get(f"/api/v1/models/{model_id}").json()
    model_version_id = model_detail["versions"][0]["id"]
    
    # 2. Run monitoring
    run_resp = client.post(
        f"/api/v1/models/{model_id}/monitoring/runs",
        json={"model_version_id": model_version_id, "run_type": "batch"}
    )
    run_id = run_resp.json()["id"]
    
    # 3. Detect incidents
    detect_resp = client.post(f"/api/v1/models/{model_id}/monitoring/runs/{run_id}/detect-incidents")
    assert detect_resp.status_code == 200
    
    # 4. Check incident list
    inc_resp = client.get("/api/v1/incidents")
    assert inc_resp.status_code == 200
    incidents = inc_resp.json()
    assert len(incidents) >= 1
    inc_id = incidents[0]["id"]
    
    # 5. Get detail
    det_resp = client.get(f"/api/v1/incidents/{inc_id}")
    assert det_resp.status_code == 200
    det = det_resp.json()
    assert len(det["signals"]) > 0
    
    # 6. Lifecycle
    ack_resp = client.post(f"/api/v1/incidents/{inc_id}/acknowledge")
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "acknowledged"
    
    inv_resp = client.post(f"/api/v1/incidents/{inc_id}/start-investigation")
    assert inv_resp.status_code == 200
    assert inv_resp.json()["status"] == "investigating"
    
    res_resp = client.post(
        f"/api/v1/incidents/{inc_id}/resolve",
        json={"resolution_note": "Fixed dataset"}
    )
    assert res_resp.status_code == 200
    assert res_resp.json()["status"] == "resolved"
