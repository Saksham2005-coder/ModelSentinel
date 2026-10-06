import pytest
import datetime
import uuid
from sqlalchemy.orm import Session
from app.models.model import Model, ModelVersion
from app.models.incident import Incident
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.models.incident_memory import IncidentMemory
from app.models.regression import RegressionCase
from app.models.pull_request import PullRequest
from app.models.deployment import Deployment
from app.services.reliability_analytics_service import ReliabilityAnalyticsService

def test_phase12_integration(db: Session):
    m = Model(id=str(uuid.uuid4()), name="Analytics Model", slug="analytics-model", framework="scikit-learn", task_type="classification", primary_metric="accuracy")
    db.add(m)
    db.commit()
    
    mv = ModelVersion(id=str(uuid.uuid4()), model_id=m.id, version="v1", artifact_uri="s3://...")
    db.add(mv)
    db.commit()

    # Incident A -> Healthy
    incA = Incident(id=str(uuid.uuid4()), incident_key="INC-12-A", title="Inc A", model_id=m.id, model_version_id=mv.id, severity="critical", category="performance", status="resolved")
    db.add(incA)
    db.commit()
    ppA = PatchProposal(id=str(uuid.uuid4()), investigation_id=str(uuid.uuid4()), incident_id=incA.id, repository_id=str(uuid.uuid4()), repository_snapshot_id=str(uuid.uuid4()), summary="fix", rationale="fix", expected_behavior="fix")
    db.add(ppA)
    db.commit()
    vrA = ValidationRun(id=str(uuid.uuid4()), patch_proposal_id=ppA.id, incident_id=incA.id, repository_snapshot_id=ppA.repository_snapshot_id, verdict="PASS")
    db.add(vrA)
    db.commit()
    memA = IncidentMemory(id=str(uuid.uuid4()), incident_id=incA.id, model_id=m.id, model_version_id=mv.id, title="Mem A", severity="critical", root_cause_category="preprocessing")
    db.add(memA)
    db.commit()
    regA = RegressionCase(id=str(uuid.uuid4()), source_incident_id=incA.id, incident_memory_id=memA.id, model_id=m.id, model_version_id=mv.id, name="Reg A", severity="critical")
    db.add(regA)
    db.commit()
    prA = PullRequest(id=str(uuid.uuid4()), incident_id=incA.id, patch_proposal_id=ppA.id, validation_run_id=vrA.id, repository_id=ppA.repository_id, repository_snapshot_id=ppA.repository_snapshot_id, branch_name="fix-a", commit_sha="aaa", provider="github", title="pr a", description="pr a", status="MERGED")
    db.add(prA)
    db.commit()
    depA = Deployment(id=str(uuid.uuid4()), pull_request_id=prA.id, incident_id=incA.id, commit_sha="aaa", status="HEALTHY", gate_result="{}")
    db.add(depA)
    db.commit()

    # Incident B -> Degraded
    incB = Incident(id=str(uuid.uuid4()), incident_key="INC-12-B", title="Inc B", model_id=m.id, model_version_id=mv.id, severity="high", category="data_drift", status="resolved")
    db.add(incB)
    db.commit()
    ppB = PatchProposal(id=str(uuid.uuid4()), investigation_id=str(uuid.uuid4()), incident_id=incB.id, repository_id=str(uuid.uuid4()), repository_snapshot_id=str(uuid.uuid4()), summary="fix", rationale="fix", expected_behavior="fix")
    db.add(ppB)
    db.commit()
    vrB = ValidationRun(id=str(uuid.uuid4()), patch_proposal_id=ppB.id, incident_id=incB.id, repository_snapshot_id=ppB.repository_snapshot_id, verdict="PASS")
    db.add(vrB)
    db.commit()
    prB = PullRequest(id=str(uuid.uuid4()), incident_id=incB.id, patch_proposal_id=ppB.id, validation_run_id=vrB.id, repository_id=ppB.repository_id, repository_snapshot_id=ppB.repository_snapshot_id, branch_name="fix-b", commit_sha="bbb", provider="github", title="pr b", description="pr b", status="MERGED")
    db.add(prB)
    db.commit()
    depB = Deployment(id=str(uuid.uuid4()), pull_request_id=prB.id, incident_id=incB.id, commit_sha="bbb", status="DEGRADED", gate_result="{}")
    db.add(depB)
    db.commit()
    
    # Incident C -> Unresolved, memory
    incC = Incident(id=str(uuid.uuid4()), incident_key="INC-12-C", title="Inc C", model_id=m.id, model_version_id=mv.id, severity="low", category="performance", status="investigating")
    db.add(incC)
    db.commit()

    # Fetch Analytics
    overview = ReliabilityAnalyticsService.get_overview_metrics(db, model_id=m.id)
    assert overview["total_incidents"] == 3
    assert overview["resolved_incidents"] == 2
    assert overview["open_incidents"] == 1
    assert overview["deployment_degradation_rate"] == 50.0 # 1 out of 2 deployments
    assert overview["regression_coverage"] == 100.0 # 1 case for 1 memory

    fixes = ReliabilityAnalyticsService.get_fix_effectiveness(db, model_id=m.id)
    assert round(fixes["patch_validation_success_rate"], 2) == 66.67 # 2 validated / 3 investigated
    assert fixes["deployment_health_success_rate"] == 50.0 # 1 healthy out of 2

    roots = ReliabilityAnalyticsService.get_root_cause_trends(db, model_id=m.id)
    assert len(roots) == 1
    assert roots[0]["root_cause"] == "preprocessing"
    assert roots[0]["frequency"] == 1
    
    models_res = ReliabilityAnalyticsService.get_model_reliability(db)
    model_data = [m_res for m_res in models_res if m_res["model_id"] == m.id][0]
    assert model_data["incidents"] == 3
    assert model_data["critical_incidents"] == 1
    assert model_data["degradation_rate"] == 50.0
