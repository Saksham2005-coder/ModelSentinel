import pytest
from app.models.model import Model, ModelVersion
from app.models.monitoring import MonitoringRun, MetricResult, FeatureMonitoringResult, PredictionMonitoringResult, DataQualityResult, SegmentAnalysisResult
from app.models.incident import Incident
from app.models.deployment import Deployment
from app.models.deployment_verification import DeploymentVerification
from app.services.model_intelligence_service import model_intelligence_service

@pytest.fixture
def test_model(db):
    m = Model(name="Health Test Model", slug="health-test", framework="xgboost", task_type="classification", primary_metric="accuracy")
    db.add(m)
    db.commit()
    db.refresh(m)
    
    mv = ModelVersion(model_id=m.id, version="v1.0")
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return m, mv

def test_model_no_history(db, test_model):
    m, mv = test_model
    health = model_intelligence_service.calculate_model_health(db, m.id)
    assert health["score"] == 100
    assert health["status"] == "HEALTHY"
    
def test_healthy_model_health_score(db, test_model):
    m, mv = test_model
    run = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)
    
    mr = MetricResult(monitoring_run_id=run.id, metric_name="accuracy", metric_value=0.95, metric_type="performance", status="healthy")
    db.add(mr)
    db.commit()
    
    health = model_intelligence_service.calculate_model_health(db, m.id)
    assert health["score"] == 100
    assert health["status"] == "HEALTHY"
    
def test_degraded_model_health_score(db, test_model):
    m, mv = test_model
    run = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)
    
    mr = MetricResult(monitoring_run_id=run.id, metric_name="accuracy", metric_value=0.8, metric_type="performance", status="warning")
    db.add(mr)
    
    fm = FeatureMonitoringResult(monitoring_run_id=run.id, feature_name="age", feature_type="numeric", drift_method="PSI", drift_score=0.2, status="critical")
    db.add(fm)
    db.commit()
    
    health = model_intelligence_service.calculate_model_health(db, m.id)
    # -5 for warning metric, -5 for critical drift
    # 100 - 10 = 90 (Wait, warning is -5, critical feature drift is -5)
    # Let's check status: 90 is STABLE. Let's make it DEGRADED (50-74).
    # Add an active medium incident
    inc = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-D1", title="Warn", severity="medium", status="active", category="data_drift")
    db.add(inc)
    db.commit()
    
    health = model_intelligence_service.calculate_model_health(db, m.id)
    # -5 performance, -5 drift, -10 incident state (from 15 to 5)
    # Total = 100 - 5 - 5 - 10 = 80 -> STABLE
    # We need < 75. Let's add more degraded metrics.
    
    mr2 = MetricResult(monitoring_run_id=run.id, metric_name="recall", metric_value=0.5, metric_type="performance", status="critical")
    db.add(mr2)
    db.commit()
    
    health = model_intelligence_service.calculate_model_health(db, m.id)
    # -5 perf, -10 perf, -5 drift, -10 incident => 100 - 30 = 70 => DEGRADED
    assert health["score"] == 70
    assert health["status"] == "DEGRADED"

def test_critical_model_health_score(db, test_model):
    m, mv = test_model
    run = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)
    
    mr1 = MetricResult(monitoring_run_id=run.id, metric_name="acc", metric_value=0.1, metric_type="perf", status="critical")
    mr2 = MetricResult(monitoring_run_id=run.id, metric_name="rec", metric_value=0.1, metric_type="perf", status="critical")
    mr3 = MetricResult(monitoring_run_id=run.id, metric_name="prec", metric_value=0.1, metric_type="perf", status="critical")
    mr4 = MetricResult(monitoring_run_id=run.id, metric_name="f1", metric_value=0.1, metric_type="perf", status="critical")
    db.add_all([mr1, mr2, mr3, mr4])
    
    # 4 critical perf => -40, but perf base is 35, so 0 for perf. Total -35.
    inc = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-C1", title="Crit", severity="high", status="active", category="performance")
    db.add(inc)
    
    # High active incident => incident state is 0, so -15. Total -50. Score = 50.
    # To get < 50, add critical DQ.
    dq = DataQualityResult(monitoring_run_id=run.id, metric_name="missing", value=0.5, status="critical")
    db.add(dq)
    db.commit()
    
    health = model_intelligence_service.calculate_model_health(db, m.id)
    assert health["score"] < 50
    assert health["status"] == "CRITICAL"
    
def test_version_comparison_and_regression(db, test_model):
    m, mv = test_model
    mv2 = ModelVersion(model_id=m.id, version="v2.0")
    db.add(mv2)
    db.commit()
    
    # Run 1 for v1
    run1 = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed")
    db.add(run1)
    db.commit()
    db.refresh(run1)
    mr1 = MetricResult(monitoring_run_id=run1.id, metric_name="accuracy", metric_value=0.90, metric_type="performance", status="healthy")
    db.add(mr1)
    
    # Run 2 for v2
    run2 = MonitoringRun(model_id=m.id, model_version_id=mv2.id, run_type="batch", status="completed")
    db.add(run2)
    db.commit()
    db.refresh(run2)
    mr2 = MetricResult(monitoring_run_id=run2.id, metric_name="accuracy", metric_value=0.84, metric_type="performance", status="healthy")
    db.add(mr2)
    db.commit()
    
    comp = model_intelligence_service.get_version_comparison(db, m.id, mv.id, mv2.id)
    assert len(comp["comparisons"]) > 0
    acc_comp = next(c for c in comp["comparisons"] if c["metric"] == "accuracy")
    assert acc_comp["difference"] < -0.05
    assert acc_comp["is_regression"] is True

def test_feature_and_segment_health(db, test_model):
    m, mv = test_model
    run = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)
    
    fm = FeatureMonitoringResult(monitoring_run_id=run.id, feature_name="age", feature_type="numeric", drift_method="PSI", drift_score=0.15, status="warning")
    db.add(fm)
    
    seg = SegmentAnalysisResult(monitoring_run_id=run.id, segment_name="age>50", sample_count=100, primary_metric="accuracy", current_metric_value=0.7, change=-0.1, status="warning")
    db.add(seg)
    db.commit()
    
    f_health = model_intelligence_service.get_feature_health(db, m.id)
    assert len(f_health) == 1
    assert f_health[0]["feature_name"] == "age"
    
    s_health = model_intelligence_service.get_segment_health(db, m.id)
    assert len(s_health) == 1
    assert s_health[0]["segment_name"] == "age>50"

def test_model_health_history(db, test_model):
    from datetime import datetime, timedelta, timezone
    m, mv = test_model
    now = datetime.now(timezone.utc)
    
    # Run 1: 10 days ago
    run1 = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed", completed_at=now - timedelta(days=10))
    db.add(run1)
    db.commit()
    
    # Run 2: 5 days ago
    run2 = MonitoringRun(model_id=m.id, model_version_id=mv.id, run_type="batch", status="completed", completed_at=now - timedelta(days=5))
    db.add(run2)
    db.commit()
    
    # Add an incident around run 2
    inc = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-HIST1", title="Hist", severity="high", status="active", category="data_drift", created_at=now - timedelta(days=5, hours=2))
    db.add(inc)
    db.commit()
    
    history = model_intelligence_service.get_model_health_history(db, m.id, days=30)
    assert len(history) == 2
    
    # First run history should have 0 incidents created
    assert history[0]["incidents_created"] == 0
    
    # Second run history should have 1 incident created
    assert history[1]["incidents_created"] == 1
