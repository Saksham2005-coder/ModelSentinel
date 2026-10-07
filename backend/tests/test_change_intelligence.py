import pytest
from sqlalchemy.orm import Session
from app.models.repository import Repository, RepositorySnapshot, RepositoryFile, RepositorySymbol, RepositoryDependency
from app.models.patch import PatchProposal, PatchFileChange
from app.models.incident import Incident
from app.models.model import Model
from app.repository.impact import classify_ml_component
from app.repository.change_intelligence import ChangeIntelligenceService

def test_ml_component_classification():
    # Test inference classification
    res = classify_ml_component("src/predict.py", ["predict_batch"], ["torch", "numpy"])
    assert res["category"] == "inference"
    assert res["confidence"] == "HIGH"

    # Test preprocessing
    res = classify_ml_component("src/data/feature_transform.py", ["scale_features"], ["pandas"])
    assert res["category"] == "feature_engineering"
    assert res["confidence"] == "HIGH"

    # Test unknown
    res = classify_ml_component("src/utils/helpers.py", ["setup_logger"], ["logging"])
    assert res["category"] == "unknown"

def test_change_intelligence_empty_patch(db: Session):
    svc = ChangeIntelligenceService(db)
    res = svc.analyze_changes("repo1", "snap1", [])
    assert res["blast_radius"] == "LOW"
    assert res["risk_score"] == 0

def test_change_intelligence_with_data(db: Session):
    # Setup repo, snapshot, file, symbol, dep
    repo = Repository(id="r1", name="test")
    snap = RepositorySnapshot(id="s1", repository_id="r1")
    rfile = RepositoryFile(id="f1", repository_snapshot_id="s1", path="predict.py", language="python")
    db.add_all([repo, snap, rfile])
    db.commit()

    sym = RepositorySymbol(id="sym1", repository_file_id="f1", name="predict", symbol_type="function")
    dep = RepositoryDependency(id="d1", repository_snapshot_id="s1", source_file_id="f1", target_reference="torch")
    db.add_all([sym, dep])
    db.commit()
    
    # Also add another file that depends on f1
    rfile2 = RepositoryFile(id="f2", repository_snapshot_id="s1", path="api.py", language="python")
    db.add(rfile2)
    db.commit()
    
    dep2 = RepositoryDependency(id="d2", repository_snapshot_id="s1", source_file_id="f2", source_symbol_name="handle_req", target_reference="predict", target_symbol_name="predict", resolved_target_file_id="f1", resolved_target_symbol_id="sym1")
    db.add(dep2)
    db.commit()

    # Now analyze
    svc = ChangeIntelligenceService(db)
    res = svc.analyze_changes("r1", "s1", [{"path": "predict.py", "symbols": ["predict"]}])
    
    assert len(res["changed_files"]) == 1
    assert res["changed_files"][0]["ml_category"] == "inference"
    assert len(res["ml_impact"]) == 1
    
    assert res["risk_score"] >= 40
    assert res["blast_radius"] in ("HIGH", "MEDIUM")
    
    # Check dependencies
    assert "handle_req" in res["affected_dependencies"]

def test_change_intelligence_historical_incident(db: Session):
    repo = Repository(id="r2", name="test2")
    snap = RepositorySnapshot(id="s2", repository_id="r2")
    rfile = RepositoryFile(id="f3", repository_snapshot_id="s2", path="data.py", language="python")
    db.add_all([repo, snap, rfile])
    db.commit()
    
    # create incident, patch, patchfile
    model = Model(id="m1", name="m1", slug="m1-slug", description="desc", task_type="classification", framework="sklearn", primary_metric="accuracy")
    db.add(model)
    db.commit()
    
    # create incident
    incident = Incident(id="inc1", incident_key="inc1", model_id="m1", model_version_id="mv1", title="test", severity="high", category="performance")
    db.add(incident)
    db.commit()
    
    patch = PatchProposal(id="p1", investigation_id="inv1", incident_id="inc1", repository_id="r2", repository_snapshot_id="s2", summary="sum", rationale="rat", expected_behavior="exp")
    db.add(patch)
    db.commit()
    
    pfc = PatchFileChange(id="pfc1", patch_proposal_id="p1", file_path="data.py", change_type="modify", rationale="rat", diff_text="")
    db.add(pfc)
    db.commit()

    svc = ChangeIntelligenceService(db)
    res = svc.analyze_changes("r2", "s2", [{"path": "data.py", "symbols": []}])
    
    assert len(res["historical_evidence"]) > 0
    assert res["historical_evidence"][0]["type"] == "incident"
    
    # incident factor bumps risk score
    assert res["risk_score"] > 0
