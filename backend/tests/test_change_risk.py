import pytest
from app.services.change_risk_service import ChangeRiskService
from app.services.blast_radius_service import BlastRadiusService
from app.models.patch import PatchProposal, PatchFileChange
from app.models.incident import Incident
from app.models.model import Model
from app.models.repository import RepositorySnapshot, RepositoryFile, RepositoryDependency

def test_blast_radius_calculation_empty(db):
    patch = PatchProposal(id="patch-1", summary="test", rationale="r", expected_behavior="e", investigation_id="inv-1", incident_id="inc-1", repository_id="repo-1", repository_snapshot_id="snap-1")
    db.add(patch)
    db.commit()
    
    blast = BlastRadiusService.calculate_blast_radius(db, patch)
    assert blast["files"] == []
    assert blast["models"] == []

def test_change_risk_evaluation_critical_file(db):
    patch = PatchProposal(id="patch-2", summary="test", rationale="r", expected_behavior="e", investigation_id="inv-1", incident_id="inc-1", repository_id="repo-1", repository_snapshot_id="snap-1")
    fc = PatchFileChange(patch_proposal_id="patch-2", file_path="src/model_inference.py", change_type="modify", rationale="r", diff_text="diff")
    db.add(patch)
    db.add(fc)
    db.commit()
    
    assessment = ChangeRiskService.evaluate_patch(db, patch)
    assert assessment.risk_level in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert assessment.risk_score > 0
    assert any(f["factor"] == "Critical inference/model file changed" for f in assessment.factors)

def test_change_risk_evaluation_large_patch(db):
    patch = PatchProposal(id="patch-3", summary="test", rationale="r", expected_behavior="e", investigation_id="inv-1", incident_id="inc-1", repository_id="repo-1", repository_snapshot_id="snap-1")
    db.add(patch)
    for i in range(6):
        fc = PatchFileChange(patch_proposal_id="patch-3", file_path=f"src/util_{i}.py", change_type="modify", rationale="r", diff_text="diff")
        db.add(fc)
    db.commit()
    
    assessment = ChangeRiskService.evaluate_patch(db, patch)
    assert any("Large patch" in f["factor"] for f in assessment.factors)
