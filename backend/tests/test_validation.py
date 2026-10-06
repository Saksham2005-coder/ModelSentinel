import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.models.validation import ValidationRun, ValidationCheck, ValidationMetric
from app.validation.runner import ValidationRunner
from app.models.patch import PatchProposal
from app.models.incident import Incident

@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    
    # Mock query behavior
    mock_query = MagicMock()
    mock_patch = MagicMock(spec=PatchProposal)
    mock_patch.id = "patch-1"
    mock_patch.status = "approved"
    mock_patch.incident_id = "inc-1"
    mock_patch.repository_snapshot_id = "snap-1"
    mock_patch.file_changes = []
    
    mock_incident = MagicMock(spec=Incident)
    mock_patch.incident = mock_incident
    
    mock_query.filter.return_value.first.return_value = mock_patch
    mock_session.query.return_value = mock_query
    return mock_session

@patch('app.validation.environment.ValidationEnvironment.setup')
@patch('app.validation.environment.ValidationEnvironment.apply_patch')
@patch('app.validation.environment.ValidationEnvironment.teardown')
@patch('app.validation.runner.ValidationRunner._run_static_validation')
@patch('app.validation.runner.ValidationRunner._run_tests')
@patch('app.validation.ml_evaluator.MLEvaluator.evaluate')
@patch('app.validation.runner.ValidationRunner._run_security_scan')
def test_validation_runner_success(
    mock_security, mock_ml_eval, mock_tests, mock_static, mock_teardown, mock_apply, mock_setup, mock_db_session
):
    # Setup mocks
    mock_ml_eval.return_value = {
        "status": "passed",
        "metrics": {
            "baseline": {"f1_score": 0.90},
            "current": {"f1_score": 0.60},
            "patched": {"f1_score": 0.88}
        },
        "segments": {
            "baseline": {"segment1": 0.90},
            "current": {"segment1": 0.60},
            "patched": {"segment1": 0.88}
        }
    }
    
    mock_security.return_value = None
    mock_tests.return_value = None
    mock_static.return_value = None
    
    runner = ValidationRunner(mock_db_session, "patch-1")
    
    # Mock checks and metrics that are added during the run
    run = ValidationRun(id="run-1", checks=[], metrics=[])
    runner._create_run = MagicMock(return_value=run)
    mock_db_session.add.side_effect = lambda obj: run.checks.append(obj) if isinstance(obj, ValidationCheck) else run.metrics.append(obj) if isinstance(obj, ValidationMetric) else None
    
    result = runner.execute()
    
    assert result.status == "completed"
    assert result.verdict == "PASS"
    assert mock_setup.called
    assert mock_apply.called
    assert mock_teardown.called

@patch('app.validation.environment.ValidationEnvironment.setup')
@patch('app.validation.environment.ValidationEnvironment.apply_patch')
@patch('app.validation.environment.ValidationEnvironment.teardown')
@patch('app.validation.runner.ValidationRunner._run_static_validation')
@patch('app.validation.runner.ValidationRunner._run_tests')
@patch('app.validation.ml_evaluator.MLEvaluator.evaluate')
@patch('app.validation.runner.ValidationRunner._run_security_scan')
def test_validation_runner_failure_metric_regression(
    mock_security, mock_ml_eval, mock_tests, mock_static, mock_teardown, mock_apply, mock_setup, mock_db_session
):
    # Setup mocks to simulate poor ML recovery (F1 < 0.85)
    mock_ml_eval.return_value = {
        "status": "passed",
        "metrics": {
            "baseline": {"f1_score": 0.90},
            "current": {"f1_score": 0.60},
            "patched": {"f1_score": 0.70}  # < 0.85 means FAIL
        },
        "segments": {
            "baseline": {"segment1": 0.90},
            "current": {"segment1": 0.60},
            "patched": {"segment1": 0.70}
        }
    }
    
    runner = ValidationRunner(mock_db_session, "patch-1")
    
    # Mock checks and metrics that are added during the run
    def side_effect_add(obj):
        if isinstance(obj, ValidationRun):
            obj.id = "run-1"
            obj.checks = []
            obj.metrics = []
        elif isinstance(obj, ValidationCheck):
            runner.run.checks.append(obj)
        elif isinstance(obj, ValidationMetric):
            runner.run.metrics.append(obj)
            
    run = ValidationRun(id="run-1", checks=[], metrics=[])
    runner._create_run = MagicMock(return_value=run)
    # mock_db_session.add needs to put elements in run.metrics so they can be processed
    mock_db_session.add.side_effect = lambda obj: run.checks.append(obj) if isinstance(obj, ValidationCheck) else run.metrics.append(obj) if isinstance(obj, ValidationMetric) else None
    
    result = runner.execute()
    
    assert result.status == "completed"
    assert result.verdict == "FAIL"
    assert "did not meet the 0.85" in result.summary

@patch('app.validation.environment.ValidationEnvironment.setup')
@patch('app.validation.environment.ValidationEnvironment.apply_patch')
@patch('app.validation.environment.ValidationEnvironment.teardown')
def test_validation_patch_apply_failure(mock_teardown, mock_apply, mock_setup, mock_db_session):
    mock_apply.side_effect = Exception("Merge conflict")
    
    runner = ValidationRunner(mock_db_session, "patch-1")
    run = ValidationRun(id="run-1", checks=[], metrics=[])
    runner._create_run = MagicMock(return_value=run)
    
    result = runner.execute()
    
    # Run fails completely
    assert result.status == "failed"
    assert result.verdict == "FAIL"
