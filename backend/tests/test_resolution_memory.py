import pytest
from app.models.incident import Incident
from app.models.model import Model, ModelVersion
from app.models.incident_memory import IncidentMemory
from app.models.resolution_memory import ResolutionMemory
from app.services.resolution_memory_service import resolution_memory_service

@pytest.fixture
def test_model(db):
    m = Model(name="Test Model", slug="test-model", framework="xgboost", task_type="classification", primary_metric="accuracy")
    db.add(m)
    db.commit()
    db.refresh(m)
    
    mv = ModelVersion(model_id=m.id, version="v1.0")
    db.add(mv)
    db.commit()
    return m, mv

@pytest.fixture
def other_model(db):
    m = Model(name="Other Model", slug="other-model", framework="sklearn", task_type="regression", primary_metric="mse")
    db.add(m)
    db.commit()
    db.refresh(m)
    mv = ModelVersion(model_id=m.id, version="v1.0")
    db.add(mv)
    db.commit()
    return m, mv

def test_no_historical_incidents(db, test_model):
    m, mv = test_model
    inc = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-001", title="Drift", severity="high", status="active", category="data_drift")
    db.add(inc)
    db.commit()
    
    results = resolution_memory_service.get_similar_incidents(db, inc.id)
    assert len(results) == 0

def test_one_similar_incident(db, test_model):
    m, mv = test_model
    inc_hist = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-HIST", title="Historical Drift", severity="high", status="resolved", category="data_drift")
    db.add(inc_hist)
    db.commit()
    db.refresh(inc_hist)
    
    mem = IncidentMemory(
        incident_id=inc_hist.id, model_id=m.id, model_version_id=mv.id,
        title="Historical Drift Memory", severity="high", resolution_status="resolved",
        resolution_summary="Fixed with feature engineering"
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    
    rm = ResolutionMemory(
        incident_memory_id=mem.id, incident_id=inc_hist.id, model_id=m.id,
        resolution_summary="Fixed with feature engineering",
        validation_status="PASSED", ml_recovery_score=0.95, deployment_status="SUCCESS", post_deployment_status="HEALTHY",
        effectiveness_score=85
    )
    db.add(rm)
    db.commit()
    
    inc_new = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-NEW", title="New Drift", severity="high", status="active", category="data_drift")
    db.add(inc_new)
    db.commit()
    db.refresh(inc_new)
    
    results = resolution_memory_service.get_similar_incidents(db, inc_new.id)
    assert len(results) == 1
    assert results[0]["incident_id"] == inc_hist.id
    assert results[0]["similarity_score"] > 0
    assert "similarity_reasons" in results[0]
    assert results[0]["resolution"]["effectiveness_score"] > 0
    assert results[0]["resolution"]["validation_status"] == "PASSED"

def test_unrelated_incidents_excluded_and_different_model_filtering(db, test_model, other_model):
    m, mv = test_model
    om, omv = other_model
    inc_hist = Incident(model_id=om.id, model_version_id=omv.id, incident_key="INC-OTHER", title="Other Drift", severity="high", status="resolved", category="performance")
    db.add(inc_hist)
    db.commit()
    
    mem = IncidentMemory(
        incident_id=inc_hist.id, model_id=om.id, model_version_id=omv.id,
        title="Other Drift", severity="high", resolution_status="resolved"
    )
    db.add(mem)
    db.commit()
    
    inc_new = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-NEW-2", title="New Drift", severity="high", status="active", category="data_drift")
    db.add(inc_new)
    db.commit()
    
    results = resolution_memory_service.get_similar_incidents(db, inc_new.id)
    # Should exclude because different model and different category
    assert len(results) == 0

def test_effectiveness_calculation_negative_signals(db, test_model):
    m, mv = test_model
    inc_hist = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-FAIL", title="Failed Fix", severity="high", status="resolved", category="data_drift")
    db.add(inc_hist)
    db.commit()
    db.refresh(inc_hist)
    
    mem = IncidentMemory(
        incident_id=inc_hist.id, model_id=m.id, model_version_id=mv.id,
        title="Failed Memory", severity="high", resolution_status="resolved"
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    
    # Negative resolution memory
    rm = ResolutionMemory(
        incident_memory_id=mem.id, incident_id=inc_hist.id, model_id=m.id,
        validation_status="FAILED", deployment_status="FAILED", post_deployment_status="DEGRADED",
        recurrence_count=2
    )
    db.add(rm)
    db.commit()
    db.refresh(rm)
    
    eval_result = resolution_memory_service.evaluate_effectiveness_from_rm(db, rm)
    assert eval_result["score"] == 0 # Score floor is 0
    assert any("Validation failed" in b for b in eval_result["breakdown"])
    assert any("Deployment failed" in b for b in eval_result["breakdown"])
    assert any("Post-deployment degradation" in b for b in eval_result["breakdown"])
    assert any("Historical recurrence" in b for b in eval_result["breakdown"])

def test_effectiveness_calculation_positive_signals(db, test_model):
    m, mv = test_model
    inc_hist = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-SUCC", title="Success Fix", severity="high", status="resolved", category="data_drift")
    db.add(inc_hist)
    db.commit()
    db.refresh(inc_hist)
    
    mem = IncidentMemory(
        incident_id=inc_hist.id, model_id=m.id, model_version_id=mv.id,
        title="Success Memory", severity="high", resolution_status="resolved"
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    
    # Positive resolution memory
    rm = ResolutionMemory(
        incident_memory_id=mem.id, incident_id=inc_hist.id, model_id=m.id,
        validation_status="PASSED", deployment_status="SUCCESS", post_deployment_status="HEALTHY",
        ml_recovery_score=0.96, regression_status="PASSED"
    )
    db.add(rm)
    db.commit()
    db.refresh(rm)
    
    eval_result = resolution_memory_service.evaluate_effectiveness_from_rm(db, rm)
    assert eval_result["score"] > 80
    assert any("Validation passed" in b for b in eval_result["breakdown"])
    assert any("Deployment healthy" in b for b in eval_result["breakdown"])
    assert any("ML recovery" in b for b in eval_result["breakdown"])
    assert any("Regression test" in b for b in eval_result["breakdown"])

def test_top_k_ordering(db, test_model):
    m, mv = test_model
    
    # 1. Very similar (same model, same category, same severity)
    inc1 = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-SIM1", title="Sim 1", severity="high", status="resolved", category="data_drift")
    db.add(inc1)
    db.commit()
    mem1 = IncidentMemory(incident_id=inc1.id, model_id=m.id, model_version_id=mv.id, title="Sim 1", severity="high", resolution_status="resolved")
    db.add(mem1)
    db.commit()
    
    # 2. Less similar (same model, different category)
    inc2 = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-SIM2", title="Sim 2", severity="high", status="resolved", category="performance")
    db.add(inc2)
    db.commit()
    mem2 = IncidentMemory(incident_id=inc2.id, model_id=m.id, model_version_id=mv.id, title="Sim 2", severity="high", resolution_status="resolved")
    db.add(mem2)
    db.commit()
    
    inc_new = Incident(model_id=m.id, model_version_id=mv.id, incident_key="INC-TARGET", title="Target", severity="high", status="active", category="data_drift")
    db.add(inc_new)
    db.commit()
    
    results = resolution_memory_service.get_similar_incidents(db, inc_new.id, top_k=5)
    assert len(results) == 2
    # inc1 should be first because it matches category too
    assert results[0]["incident_id"] == inc1.id
    assert results[1]["incident_id"] == inc2.id
    assert results[0]["similarity_score"] > results[1]["similarity_score"]
