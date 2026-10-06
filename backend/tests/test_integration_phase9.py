import pytest
from app.db.session import SessionLocal
from app.models.incident import Incident, IncidentSignal
from app.models.investigation import Investigation
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.services.incident_memory_service import IncidentMemoryService
from app.services.regression_service import RegressionService
from app.services.similarity_service import SimilarityService

# A mock database session for end-to-end integration test
# We'll use the testing DB (SQLite in memory or file based on setup)
# Because we just ran tests and they pass, we can use a new SessionLocal.

@pytest.fixture
def db():
    # Make sure we use a test db, in standard FastAPI testing we override get_db
    # But here we can just use SessionLocal and rollback at the end
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_full_incident_memory_lifecycle(db):
    # 1. Create degraded incident
    incident_1 = Incident(
        id="integration-inc-1",
        incident_key="integration-key-1",
        model_id="spam-classifier",
        model_version_id="v1",
        title="Spam classifier preprocessing mismatch",
        severity="critical",
        status="open",
        category="performance"
    )
    db.add(incident_1)
    db.commit()
    
    # 2. Add signals
    sig = IncidentSignal(
        incident_id=incident_1.id,
        source_type="feature_drift",
        signal_name="url_length",
        status="critical"
    )
    db.add(sig)
    db.commit()

    # 3. Investigate
    inv = Investigation(
        id="integration-inv-1",
        incident_id=incident_1.id,
        status="completed"
    )
    db.add(inv)
    db.commit()

    # 4. Patch
    patch = PatchProposal(
        id="integration-patch-1",
        investigation_id=inv.id,
        incident_id=incident_1.id,
        repository_id="repo-1",
        repository_snapshot_id="snap-1",
        summary="Restore preprocessing step",
        rationale="Fix drift",
        expected_behavior="Normal",
        status="approved"
    )
    db.add(patch)
    db.commit()

    # 5. Validate & ML Recovery PASS
    val = ValidationRun(
        id="integration-val-1",
        patch_proposal_id=patch.id,
        incident_id=incident_1.id,
        repository_snapshot_id="snap-1",
        status="completed",
        verdict="PASS"
    )
    db.add(val)
    
    # 6. Resolve Incident
    incident_1.status = "resolved"
    db.commit()
    
    # 7. Create Incident Memory
    mem_svc = IncidentMemoryService(db)
    eligibility = mem_svc.check_eligibility(incident_1.id)
    assert eligibility["eligible"] is True
    
    memory = mem_svc.create_memory(
        incident_1.id,
        {
            "title": "Resolved: Spam preprocessing mismatch",
            "root_cause_category": "Preprocessing",
            "affected_features": ["url_length"],
            "resolution_summary": "Restored url_length normalization."
        }
    )
    assert memory is not None
    assert memory.root_cause_category == "Preprocessing"

    # 8. Create Regression Test
    reg_svc = RegressionService(db)
    case = reg_svc.create_case_from_memory(memory.id, {
        "name": "Regression: Preprocessing drift",
        "affected_segments": ["URL-heavy messages"]
    })
    assert case is not None

    # 9. Run Regression Test
    evaluator_result = {
        "status": "passed",
        "metrics": {"patched": {"f1_score": 0.90}},
        "segments": {"patched": {"URL-heavy messages": 0.88}}
    }
    run = reg_svc.record_run_result(case.id, "simulated-val", evaluator_result)
    assert run.status == "PASS"

    # 10. Create second similar incident
    incident_2 = Incident(
        id="integration-inc-2",
        incident_key="integration-key-2",
        model_id="spam-classifier",
        model_version_id="v1",
        title="Spam classifier feature shift",
        severity="critical",
        status="open",
        category="performance"
    )
    db.add(incident_2)
    sig2 = IncidentSignal(
        incident_id=incident_2.id,
        source_type="feature_drift",
        signal_name="url_length",
        status="critical"
    )
    db.add(sig2)
    db.commit()

    # 11. Similarity engine finds previous incident
    sim_svc = SimilarityService(db)
    similar = sim_svc.find_similar_memories_for_incident(incident_2)
    
    # Should find memory 1 because of model match, severity match, feature match!
    assert len(similar) > 0
    top_match = similar[0]
    
    assert top_match["memory"].id == memory.id
    # Score should be at least: model (25) + severity (5) + feature (10) = 40
    assert top_match["similarity_score"] >= 40
    
    # Cleanup for pure deterministic state
    db.rollback()
