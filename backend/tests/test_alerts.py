import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.slo import ReliabilityObjective, AlertRule, Alert
from app.models.model import Model
from app.main import app

client = TestClient(app)

def test_list_alerts(db: Session):
    model = Model(name="Test Model for Alert", slug="test-model-alert", framework="sklearn", task_type="classification", primary_metric="accuracy", status="active", description="test")
    db.add(model)
    db.commit()
    db.refresh(model)
    
    obj = ReliabilityObjective(
        model_id=model.id,
        name="Test Objective",
        description="test",
        objective_type="model_performance",
        metric_name="latency",
        target_value=100.0,
        comparison_operator="<",
        evaluation_window="30d",
        enabled=True
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    
    
    rule = AlertRule(
        objective_id=obj.id,
        name="Test Rule",
        enabled=True,
        severity="high",
        condition_type="SLO_BREACHED"
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    alert = Alert(
        model_id=model.id,
        objective_id=obj.id,
        rule_id=rule.id,
        status="OPEN",
        severity="high",
        triggered_at=datetime.now(timezone.utc),
        deduplication_key="test-key",
        summary="Test alert summary",
        evidence={"test": "test"}
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    response = client.get(f"/api/v1/alerts?model_id={model.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == alert.id
    
def test_acknowledge_alert(db: Session):
    model = Model(name="Test Model for Alert Ack", slug="test-model-alert-ack", framework="sklearn", task_type="classification", primary_metric="accuracy", status="active", description="test")
    db.add(model)
    db.commit()
    
    obj = ReliabilityObjective(
        model_id=model.id,
        name="Test Objective",
        description="test",
        objective_type="model_performance",
        metric_name="latency",
        target_value=100.0,
        comparison_operator="<",
        evaluation_window="30d",
        enabled=True
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    rule = AlertRule(
        objective_id=obj.id,
        name="Test Rule",
        enabled=True,
        severity="high",
        condition_type="SLO_BREACHED"
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    alert = Alert(
        model_id=model.id,
        objective_id=obj.id,
        rule_id=rule.id,
        status="OPEN",
        severity="high",
        triggered_at=datetime.now(timezone.utc),
        deduplication_key="test-key-2",
        summary="Test alert summary",
        evidence={}
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    response = client.post(f"/api/v1/alerts/{alert.id}/acknowledge")
    assert response.status_code == 200
    assert response.json()["status"] == "ACKNOWLEDGED"
