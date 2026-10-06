import pytest
from app.services.regression_service import RegressionService
from app.models.incident_memory import IncidentMemory
from app.models.regression import RegressionCase, RegressionRun, RegressionResult
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_session():
    return MagicMock()

def test_create_case_from_memory(mock_db_session):
    memory = IncidentMemory(
        id="mem-1", incident_id="inc-1", model_id="mod-1", model_version_id="mv-1",
        title="Test Mem", summary="Sum", root_cause="cause", resolution_summary="resolved",
        affected_features=["feat1"], affected_segments=["seg1"], severity="high"
    )
    
    def query_side_effect(model):
        m = MagicMock()
        if model == IncidentMemory:
            m.filter.return_value.first.return_value = memory
        elif model == RegressionCase:
            m.filter.return_value.first.return_value = None
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = RegressionService(mock_db_session)
    case = svc.create_case_from_memory("mem-1", {"name": "Test Case"})
    
    assert case.name == "Test Case"
    assert case.source_incident_id == "inc-1"
    assert case.affected_segments == ["seg1"]
    assert mock_db_session.add.called
    assert mock_db_session.commit.called

def test_create_case_duplicate(mock_db_session):
    memory = IncidentMemory(id="mem-1", incident_id="inc-1")
    existing_case = RegressionCase(id="case-1")
    
    def query_side_effect(model):
        m = MagicMock()
        if model == IncidentMemory:
            m.filter.return_value.first.return_value = memory
        elif model == RegressionCase:
            m.filter.return_value.first.return_value = existing_case
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = RegressionService(mock_db_session)
    with pytest.raises(ValueError, match="already exists"):
        svc.create_case_from_memory("mem-1", {})

def test_record_run_result_pass(mock_db_session):
    case = RegressionCase(id="case-1", acceptance_criteria={"f1_score": {"min": 0.85}}, affected_segments=["seg1"])
    
    def query_side_effect(model):
        m = MagicMock()
        m.filter.return_value.first.return_value = case
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    eval_result = {
        "status": "passed",
        "metrics": {"patched": {"f1_score": 0.90}},
        "segments": {"patched": {"seg1": 0.88}}
    }
    
    run = RegressionRun(id="run-1")
    def side_effect_add(obj):
        pass # allow mock to add normally
        
    mock_db_session.add.side_effect = side_effect_add
    
    svc = RegressionService(mock_db_session)
    result_run = svc.record_run_result("case-1", "val-1", eval_result)
    
    assert result_run.status == "PASS"

def test_record_run_result_fail(mock_db_session):
    case = RegressionCase(id="case-1", acceptance_criteria={"f1_score": {"min": 0.85}}, affected_segments=["seg1"])
    mock_db_session.query.return_value.filter.return_value.first.return_value = case
    
    eval_result = {
        "status": "passed",
        "metrics": {"patched": {"f1_score": 0.80}}, # Below min
        "segments": {"patched": {"seg1": 0.88}}
    }
    
    svc = RegressionService(mock_db_session)
    result_run = svc.record_run_result("case-1", "val-1", eval_result)
    
    assert result_run.status == "FAIL"
