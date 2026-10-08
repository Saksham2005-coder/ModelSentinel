from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_engineering_overview():
    response = client.get("/api/v1/analytics/engineering-overview")
    assert response.status_code == 200
    data = response.json()
    assert "reliability_score" in data
    assert "models_at_risk" in data

def test_reliability_trends():
    response = client.get("/api/v1/analytics/reliability-trends")
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert "direction" in data
    assert "data_sufficiency" in data

def test_models_comparison():
    response = client.get("/api/v1/analytics/models/comparison")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_engineering_effectiveness():
    response = client.get("/api/v1/analytics/engineering-effectiveness")
    assert response.status_code == 200
    data = response.json()
    assert "patch_validation_success_rate" in data

def test_root_causes_intelligence():
    response = client.get("/api/v1/analytics/root-causes/intelligence")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_change_reliability():
    response = client.get("/api/v1/analytics/change-reliability")
    assert response.status_code == 200
    data = response.json()
    assert "total_changes_analyzed" in data

def test_hotspots():
    response = client.get("/api/v1/analytics/hotspots")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_slo_intelligence():
    response = client.get("/api/v1/analytics/slo-intelligence")
    assert response.status_code == 200
    data = response.json()
    assert "total_objectives" in data

def test_reliability_drivers():
    response = client.get("/api/v1/analytics/reliability-drivers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_interventions():
    response = client.get("/api/v1/analytics/interventions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
