import pytest
import datetime
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.model import Model
from app.models.deployment import Deployment
from app.models.incident_memory import IncidentMemory
from app.models.regression import RegressionCase
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.models.investigation import Investigation
from app.services.reliability_analytics_service import ReliabilityAnalyticsService
import uuid

def create_incident(db: Session, status="resolved", severity="high", age_days=1, model_id=None):
    if not model_id:
        m = Model(id=str(uuid.uuid4()), name="Test Model", slug="test-model", framework="sk", task_type="cls", primary_metric="acc")
        db.add(m)
        db.commit()
        model_id = m.id

    now = datetime.datetime.now(datetime.timezone.utc)
    det_at = now - datetime.timedelta(days=age_days)
    res_at = det_at + datetime.timedelta(minutes=60) if status == "resolved" else None
    
    inc = Incident(
        id=str(uuid.uuid4()),
        incident_key=f"INC-{uuid.uuid4()}",
        title="Test Inc",
        model_id=model_id,
        model_version_id=str(uuid.uuid4()),
        severity=severity,
        status=status,
        category="data_quality",
        detected_at=det_at,
        acknowledged_at=det_at + datetime.timedelta(minutes=5),
        resolved_at=res_at,
        created_at=det_at
    )
    db.add(inc)
    db.commit()
    return inc

def cleanup(db: Session):
    db.query(Incident).delete()
    db.query(Investigation).delete()
    db.query(Deployment).delete()
    db.query(PatchProposal).delete()
    db.query(ValidationRun).delete()
    db.commit()

def test_overview_metrics_empty(db: Session):
    cleanup(db)
    res = ReliabilityAnalyticsService.get_overview_metrics(db)
    assert res["total_incidents"] == 0
    assert res["mttd_minutes"] is None
    assert res["mttr_minutes"] is None
    assert res["reliability_score"] == 100

def test_overview_metrics_populated(db: Session):
    cleanup(db)
    i1 = create_incident(db, status="resolved", severity="critical", age_days=2)
    i2 = create_incident(db, status="investigating", severity="high", age_days=1, model_id=i1.model_id)

    res = ReliabilityAnalyticsService.get_overview_metrics(db)
    assert res["total_incidents"] == 2
    assert res["resolved_incidents"] == 1
    assert res["open_incidents"] == 1
    assert res["critical_incidents"] == 1
    
    assert res["mttd_minutes"] == 5.0
    assert res["mttr_minutes"] == 60.0
    assert res["reliability_score"] <= 100

def test_model_reliability_empty(db: Session):
    res = ReliabilityAnalyticsService.get_model_reliability(db)
    assert isinstance(res, list)

def test_root_cause_trends_empty(db: Session):
    cleanup(db)
    res = ReliabilityAnalyticsService.get_root_cause_trends(db)
    assert res == []

def test_deployment_health_empty(db: Session):
    cleanup(db)
    res = ReliabilityAnalyticsService.get_deployment_health(db)
    assert res["total_deployments"] == 0

def test_fix_effectiveness_empty(db: Session):
    cleanup(db)
    res = ReliabilityAnalyticsService.get_fix_effectiveness(db)
    assert res["patch_validation_success_rate"] == 0
    assert res["full_loop_completion_rate"] == 0
