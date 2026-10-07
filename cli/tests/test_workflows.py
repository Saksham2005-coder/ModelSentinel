import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from modelsentinel.main import app

runner = CliRunner()

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_workflow_list(mock_request):
    mock_request.return_value = [
        {"id": "wf-1", "name": "Test", "workflow_type": "INCIDENT_RECOVERY", "status": "PENDING"}
    ]
    result = runner.invoke(app, ["workflows", "list"])
    assert result.exit_code == 0
    assert "wf-1" in result.stdout

@patch("modelsentinel.client.ModelSentinelClient._request")
def test_workflow_start(mock_request):
    # start command makes two calls: create then start
    mock_request.side_effect = [
        {"id": "wf-2", "status": "PENDING"},
        {"id": "wf-2", "status": "WAITING_APPROVAL", "steps": [{"step_type": "HUMAN_APPROVAL", "status": "WAITING"}]}
    ]
    result = runner.invoke(app, ["workflows", "start", "INCIDENT_RECOVERY", "123"])
    assert result.exit_code == 0
    assert "wf-2" in result.stdout
    assert "WAITING_APPROVAL" in result.stdout
    assert "HUMAN_APPROVAL" in result.stdout
