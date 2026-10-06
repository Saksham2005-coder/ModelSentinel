import pytest
from app.services.incident_memory_service import IncidentMemoryService
from app.models.incident import Incident
from app.models.patch import PatchProposal
from app.models.investigation import Investigation
from app.models.validation import ValidationRun
from app.models.incident_memory import IncidentMemory
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_session():
    return MagicMock()

def test_eligibility_not_resolved(mock_db_session):
    incident = Incident(id="inc-1", status="open")
    mock_db_session.query.return_value.filter.return_value.first.return_value = incident
    
    svc = IncidentMemoryService(mock_db_session)
    res = svc.check_eligibility("inc-1")
    assert not res["eligible"]
    assert "not resolved" in res["reason"]

def test_eligibility_no_patch(mock_db_session):
    incident = Incident(id="inc-1", status="resolved")
    inv = Investigation(id="inv-1", status="completed")
    incident.investigations = [inv]
    
    def query_side_effect(model):
        m = MagicMock()
        if model == Incident:
            m.filter.return_value.first.return_value = incident
        elif model == PatchProposal:
            m.filter.return_value.first.return_value = None
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = IncidentMemoryService(mock_db_session)
    res = svc.check_eligibility("inc-1")
    assert not res["eligible"]
    assert "No approved patch found" in res["reason"]

def test_eligibility_validation_failed(mock_db_session):
    incident = Incident(id="inc-1", status="resolved")
    patch = PatchProposal(id="patch-1", status="approved")
    inv = Investigation(id="inv-1", status="completed")
    incident.investigations = [inv]
    
    val = ValidationRun(id="val-1", status="completed", verdict="FAIL")
    
    # Query logic mock
    def query_side_effect(model):
        m = MagicMock()
        if model == Incident:
            m.filter.return_value.first.return_value = incident
        elif model == PatchProposal:
            m.filter.return_value.first.return_value = patch
        elif model == ValidationRun:
            m.filter.return_value.order_by.return_value.first.return_value = val
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = IncidentMemoryService(mock_db_session)
    res = svc.check_eligibility("inc-1")
    assert not res["eligible"]
    assert "Validation verdict is FAIL" in res["reason"]

def test_eligibility_success(mock_db_session):
    incident = Incident(id="inc-1", status="resolved")
    patch = PatchProposal(id="patch-1", status="approved")
    inv = Investigation(id="inv-1", status="completed")
    incident.investigations = [inv]
    
    val = ValidationRun(id="val-1", status="completed", verdict="PASS")
    
    def query_side_effect(model):
        m = MagicMock()
        if model == Incident:
            m.filter.return_value.first.return_value = incident
        elif model == PatchProposal:
            m.filter.return_value.first.return_value = patch
        elif model == ValidationRun:
            m.filter.return_value.order_by.return_value.first.return_value = val
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = IncidentMemoryService(mock_db_session)
    res = svc.check_eligibility("inc-1")
    assert res["eligible"]

def test_create_memory_duplicate(mock_db_session):
    incident = Incident(id="inc-1", status="resolved")
    patch = PatchProposal(id="patch-1", status="approved")
    inv = Investigation(id="inv-1", status="completed")
    incident.investigations = [inv]
    val = ValidationRun(id="val-1", status="completed", verdict="PASS")
    
    def query_side_effect(model):
        m = MagicMock()
        if model == Incident:
            m.filter.return_value.first.return_value = incident
        elif model == PatchProposal:
            m.filter.return_value.first.return_value = patch
        elif model == ValidationRun:
            m.filter.return_value.order_by.return_value.first.return_value = val
        elif model == IncidentMemory:
            m.filter.return_value.first.return_value = IncidentMemory(id="mem-1")
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = IncidentMemoryService(mock_db_session)
    with pytest.raises(ValueError, match="already exists"):
        svc.create_memory("inc-1", {})
