import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.main import app
from app.models.reliability import ReliabilityEvent, ReliabilityEdge
from app.models.incident import Incident
from app.models.model import Model, ModelVersion
from app.services.reliability_service import reliability_service

client = TestClient(app)

def test_timeline_empty(db: Session):
    model = Model(name="Test Model", slug="test-model", framework="sklearn", task_type="classification", primary_metric="accuracy", status="active")
    db.add(model)
    db.commit()
    db.refresh(model)
    
    response = client.get(f"/api/v1/models/{model.id}/reliability/timeline")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_telemetry_creates_event(db: Session):
    model = Model(name="Test Model 2", slug="test-model-2", framework="sklearn", task_type="classification", primary_metric="accuracy", status="active")
    db.add(model)
    db.commit()
    db.refresh(model)
    
    # Just testing the service manually or via an API that invokes telemetry
    event = reliability_service.emit_event(
        db, model.id, "TELEMETRY_RECEIVED", "telemetry", "src-1", "Telemetry Received",
        status="success", occurred_at=datetime.now(timezone.utc)
    )
    
    response = client.get(f"/api/v1/models/{model.id}/reliability/timeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["event_type"] == "TELEMETRY_RECEIVED"

def test_incident_graph(db: Session):
    model = Model(name="Test Model 3", slug="test-model-3", framework="sklearn", task_type="classification", primary_metric="accuracy", status="active")
    db.add(model)
    db.commit()
    db.refresh(model)
    
    version_obj = ModelVersion(model_id=model.id, version="v1.0.0", is_active=True)
    db.add(version_obj)
    db.commit()
    db.refresh(version_obj)
    
    incident = Incident(incident_key="INC-1", model_id=model.id, model_version_id=version_obj.id, title="Test Inc", status="active", severity="high", category="performance")
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    inc_event = reliability_service.emit_event(
        db, model.id, "INCIDENT_CREATED", "incident", incident.id, "Incident Created",
        status="active", occurred_at=datetime.now(timezone.utc)
    )
    
    inv_event = reliability_service.emit_event(
        db, model.id, "INVESTIGATION_STARTED", "investigation", "inv-1", "Investigation Started",
        status="running", occurred_at=datetime.now(timezone.utc)
    )
    
    reliability_service.link_events(db, inc_event.id, inv_event.id, "RESULTED_IN")
    
    response = client.get(f"/api/v1/models/{model.id}/reliability/incidents/{incident.id}/graph")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    
    # Timeline should also return these
    timeline_res = client.get(f"/api/v1/models/{model.id}/reliability/timeline")
    assert timeline_res.status_code == 200
    assert len(timeline_res.json()) == 2
