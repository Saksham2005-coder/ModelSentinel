import pytest
from app.services.similarity_service import SimilarityService
from app.models.incident import Incident, IncidentSignal
from app.models.incident_memory import IncidentMemory
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_session():
    return MagicMock()

def test_find_similar_memories_for_incident(mock_db_session):
    incident = Incident(id="inc-1", model_id="mod-1", severity="high")
    sig1 = IncidentSignal(id="sig-1", source_type="feature_drift", signal_name="url_length")
    incident.signals = [sig1]
    
    mem1 = IncidentMemory(
        id="mem-1", incident_id="inc-2", model_id="mod-1", severity="high",
        signal_families=["drift"], affected_features=["url_length"], affected_metrics=["f1"]
    )
    
    mem2 = IncidentMemory(
        id="mem-2", incident_id="inc-3", model_id="mod-2", severity="low",
        signal_families=["performance"], affected_features=["other"], affected_metrics=["acc"]
    )
    
    def query_side_effect(model):
        m = MagicMock()
        m.filter.return_value.all.return_value = [mem1, mem2]
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = SimilarityService(mock_db_session)
    results = svc.find_similar_memories_for_incident(incident)
    
    assert len(results) > 0
    top_result = results[0]
    assert top_result["memory"].id == "mem-1"
    assert top_result["similarity_score"] == 40
    
    # Check mem2 is not in results or has very low score
    assert len(results) == 1

def test_find_similar_memories_for_memory(mock_db_session):
    source_mem = IncidentMemory(
        id="mem-1", model_id="mod-1", severity="high",
        root_cause_category="Data Drift",
        signal_families=["drift"], affected_segments=["seg1"]
    )
    
    mem2 = IncidentMemory(
        id="mem-2", model_id="mod-1", severity="high",
        root_cause_category="Data Drift",
        signal_families=["drift"], affected_segments=["seg1"]
    )
    
    def query_side_effect(model):
        m = MagicMock()
        m.filter.return_value.all.return_value = [mem2]
        return m
        
    mock_db_session.query.side_effect = query_side_effect
    
    svc = SimilarityService(mock_db_session)
    results = svc.find_similar_memories_for_memory(source_mem)
    
    assert len(results) == 1
    assert results[0]["memory"].id == "mem-2"
    assert results[0]["similarity_score"] == 25 + 5 + 15 + 15 + 10 # 70
