import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from modelsentinel.main import app
from modelsentinel.errors import APIError, NotFoundError, CLIError

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ModelSentinel Engineering CLI" in result.stdout

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_models_list_json(mock_request):
    mock_request.return_value = [{"id": "m1", "name": "Test Model", "status": "active"}]
    from modelsentinel.output import set_json_output
    set_json_output(True)
    try:
        result = runner.invoke(app, ["models", "list"])
        assert result.exit_code == 0
        assert '"id": "m1"' in result.stdout
    finally:
        set_json_output(False)

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_models_list_human(mock_request):
    mock_request.return_value = [{"id": "m1", "name": "Test Model", "task_type": "cls", "status": "active"}]
    result = runner.invoke(app, ["models", "list"])
    assert result.exit_code == 0
    assert "m1" in result.stdout
    assert "Test Model" in result.stdout

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_not_found(mock_request):
    mock_request.side_effect = NotFoundError("Incident not found")
    result = runner.invoke(app, ["incidents", "show", "missing"])
    assert isinstance(result.exception, NotFoundError)
    assert result.exception.exit_code == 4

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_change_intelligence(mock_request):
    mock_request.return_value = {
        "risk_score": 85,
        "blast_radius": "HIGH",
        "changed_files": [],
        "affected_dependencies": ["A", "B"],
        "ml_impact": [{"component": "Inference", "impact": "HIGH"}],
        "historical_evidence": [],
        "affected_models": [],
        "risk_factors": ["+10 history"]
    }
    result = runner.invoke(app, ["change-intelligence", "patch1"])
    assert result.exit_code == 0
    assert "85" in result.stdout
    assert "HIGH" in result.stdout

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_validation_failure(mock_request):
    mock_request.return_value = {
        "id": "v1",
        "status": "failed",
        "environment": "test",
        "results": []
    }
    result = runner.invoke(app, ["validation", "show", "v1"])
    # Typer CliRunner catches sys.exit(6) as SystemExit with code 6
    assert result.exit_code == 6

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_api_error(mock_request):
    mock_request.side_effect = APIError("Backend error (500)")
    result = runner.invoke(app, ["models", "list"])
    assert isinstance(result.exception, APIError)
    assert result.exception.exit_code == 3
