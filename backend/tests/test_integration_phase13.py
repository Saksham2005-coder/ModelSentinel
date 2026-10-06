import pytest
from app.services.change_risk_service import ChangeRiskService
from app.models.patch import PatchProposal, PatchFileChange
from app.models.incident import Incident
from app.models.model import Model, ModelVersion
from app.models.incident_memory import IncidentMemory
from app.models.regression import RegressionCase

def test_phase13_integration(db):
    # Setup base entities
    m = Model(id="mod-risk", name="Risk Model", slug="risk-model", framework="custom", task_type="classification", problem_type="binary", primary_metric="f1", owner="test", status="draft", environment="development")
    mv = ModelVersion(id="mod-risk-v1", model_id="mod-risk", version="v1")
    db.add_all([m, mv])
    db.commit()
    
    # 1. Historical Incident
    i = Incident(id="inc-hist", incident_key="KEY-1", model_id="mod-risk", model_version_id="mod-risk-v1", title="test", category="test", severity="high", status="resolved")
    db.add(i)
    db.commit()
    
    mem = IncidentMemory(
        id="mem-1",
        incident_id="inc-hist",
        model_id="mod-risk",
        model_version_id="mod-risk-v1",
        title="Hist mem",
        severity="high",
        affected_features=["feature_a"]
    )
    db.add(mem)
    db.commit()
    
    reg = RegressionCase(
        id="reg-1",
        source_incident_id="inc-hist",
        incident_memory_id="mem-1",
        model_id="mod-risk",
        model_version_id="mod-risk-v1",
        name="Reg 1",
        severity="high"
    )
    db.add(reg)
    db.commit()
    
    # 2. Historical Patch for that incident
    hist_patch = PatchProposal(id="patch-hist", incident_id="inc-hist", status="applied", summary="test", rationale="r", expected_behavior="e", investigation_id="inv-1", repository_id="repo-1", repository_snapshot_id="snap-1")
    fc_hist = PatchFileChange(patch_proposal_id="patch-hist", file_path="src/preprocess.py", change_type="modify", rationale="r", diff_text="diff")
    db.add_all([hist_patch, fc_hist])
    db.commit()
    
    # 3. New patch touching the same file
    new_patch = PatchProposal(id="patch-new", status="proposed", summary="test", rationale="r", expected_behavior="e", investigation_id="inv-2", incident_id="inc-2", repository_id="repo-1", repository_snapshot_id="snap-1")
    fc_new = PatchFileChange(patch_proposal_id="patch-new", file_path="src/preprocess.py", change_type="modify", rationale="r", diff_text="diff")
    db.add_all([new_patch, fc_new])
    db.commit()
    
    # 4. Evaluate Risk
    assessment = ChangeRiskService.evaluate_patch(db, new_patch)
    
    # Assert blast radius
    assert "src/preprocess.py" in assessment.blast_radius["files"]
    assert "inc-hist" in assessment.blast_radius["historical_incidents"]
    assert "mod-risk" in assessment.blast_radius["models"]
    assert "reg-1" in assessment.blast_radius["regression_tests"]
    assert "feature_a" in assessment.blast_radius["features"]
    
    # Assert risk
    assert assessment.risk_score > 0
    factors = [f["factor"] for f in assessment.factors]
    assert any("historical incident" in f for f in factors)
    assert any("Preprocessing" in f for f in factors)
    assert any("Regression coverage" in f for f in factors)
