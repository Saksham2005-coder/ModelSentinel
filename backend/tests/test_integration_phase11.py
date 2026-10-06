import pytest
import datetime
import uuid
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.model import Model, ModelVersion
from app.models.deployment import Deployment
from app.models.pull_request import PullRequest
from app.models.monitoring import MonitoringRun, MetricResult
from app.services.deployment_verification_service import DeploymentVerificationService

def test_deployment_verification_success_path(db: Session):
    # Setup
    m = Model(name="Test Model", slug="test-model", framework="scikit-learn", task_type="classification", primary_metric="f1_score")
    db.add(m)
    db.commit()
    mv = ModelVersion(model_id=m.id, version="v1", artifact_uri="s3://...")
    db.add(mv)
    db.commit()

    inc = Incident(
        incident_key="INC-TEST-11-1",
        title="Test Incident",
        model_id=m.id,
        model_version_id=mv.id,
        severity="high",
        category="performance"
    )
    db.add(inc)
    db.commit()

    pr = PullRequest(
        id=str(uuid.uuid4()),
        incident_id=inc.id,
        patch_proposal_id="test-patch-id-1",
        validation_run_id="test-val-id-1",
        repository_id="test-repo",
        repository_snapshot_id="test-snap",
        commit_sha="test-commit",
        provider="github",
        title="test pr",
        description="test desc",
        branch_name="fix-branch",
        status="MERGED"
    )
    db.add(pr)
    db.commit()

    dep = Deployment(
        id=str(uuid.uuid4()),
        pull_request_id=pr.id,
        incident_id=inc.id,
        commit_sha="a84f91c",
        status="ELIGIBLE",
        gate_result="{}"
    )
    db.add(dep)
    db.commit()
    db.refresh(dep)

    # 1. Record Deployment
    updated_dep = DeploymentVerificationService.record_deployment(
        db, dep.id, "production", "Manual Deployment", "admin"
    )
    assert updated_dep.status == "DEPLOYED"
    assert updated_dep.deployed_at is not None

    # 2. Start Verification
    verif = DeploymentVerificationService.start_verification(db, dep.id)
    assert verif.status == "VERIFYING"
    assert updated_dep.status == "VERIFYING"

    # 3. Simulate post-deployment monitoring run with HEALTHY metrics
    mr = MonitoringRun(
        model_id=m.id,
        model_version_id=mv.id,
        run_type="post-deployment",
        status="completed"
    )
    db.add(mr)
    db.commit()

    metric = MetricResult(
        monitoring_run_id=mr.id,
        metric_name="f1_score",
        metric_value=0.95,
        metric_type="performance",
        status="healthy"
    )
    db.add(metric)
    db.commit()

    # 4. Evaluate Health
    final_verif = DeploymentVerificationService.evaluate_health(db, dep.id)
    assert final_verif.status == "HEALTHY"
    assert updated_dep.status == "HEALTHY"
    assert final_verif.completed_at is not None

def test_deployment_verification_failure_path(db: Session):
    # Setup
    m = Model(name="Test Model 2", slug="test-model-2", framework="scikit-learn", task_type="classification", primary_metric="f1_score")
    db.add(m)
    db.commit()
    mv = ModelVersion(model_id=m.id, version="v1", artifact_uri="s3://...")
    db.add(mv)
    db.commit()

    inc = Incident(
        incident_key="INC-TEST-11-2",
        title="Test Incident 2",
        model_id=m.id,
        model_version_id=mv.id,
        severity="medium",
        category="performance"
    )
    db.add(inc)
    db.commit()

    pr = PullRequest(
        id=str(uuid.uuid4()),
        incident_id=inc.id,
        patch_proposal_id="test-patch-id-2",
        validation_run_id="test-val-id-2",
        repository_id="test-repo",
        repository_snapshot_id="test-snap",
        commit_sha="test-commit",
        provider="github",
        title="test pr",
        description="test desc",
        branch_name="fix-branch-2",
        status="MERGED"
    )
    db.add(pr)
    db.commit()

    dep = Deployment(
        id=str(uuid.uuid4()),
        pull_request_id=pr.id,
        incident_id=inc.id,
        commit_sha="b84f91c",
        status="ELIGIBLE",
        gate_result="{}"
    )
    db.add(dep)
    db.commit()

    DeploymentVerificationService.record_deployment(db, dep.id, "production", "Manual")
    DeploymentVerificationService.start_verification(db, dep.id)

    # Post-deployment degradation
    mr = MonitoringRun(
        model_id=m.id,
        model_version_id=mv.id,
        run_type="post-deployment",
        status="completed"
    )
    db.add(mr)
    db.commit()

    metric = MetricResult(
        monitoring_run_id=mr.id,
        metric_name="f1_score",
        metric_value=0.50,
        metric_type="performance",
        status="critical"
    )
    db.add(metric)
    db.commit()

    verif = DeploymentVerificationService.evaluate_health(db, dep.id)
    assert verif.status == "FAILED"
    db.refresh(dep)
    assert dep.status == "FAILED"

    # Check that a new incident was created
    new_incident = db.query(Incident).filter(Incident.incident_key.like(f"POST-DEPLOY-{dep.id[:8]}%")).first()
    assert new_incident is not None
    assert new_incident.severity == "high"

def test_invalid_deployment_state(db: Session):
    m = Model(name="Test Model 3", slug="test-model-3", framework="scikit-learn", task_type="classification", primary_metric="f1_score")
    db.add(m)
    db.commit()
    mv = ModelVersion(model_id=m.id, version="v1", artifact_uri="s3://...")
    db.add(mv)
    db.commit()
    
    inc = Incident(
        incident_key="INC-TEST-11-3",
        title="Test Incident 3",
        model_id=m.id,
        model_version_id=mv.id,
        severity="low",
        category="performance"
    )
    db.add(inc)
    db.commit()
    pr = PullRequest(
        id=str(uuid.uuid4()),
        incident_id=inc.id,
        patch_proposal_id="test-patch-id-3",
        validation_run_id="test-val-id-3",
        repository_id="test-repo",
        repository_snapshot_id="test-snap",
        commit_sha="test-commit",
        provider="github",
        title="test pr",
        description="test desc",
        branch_name="b",
        status="CREATED"
    )
    db.add(pr)
    db.commit()

    dep = Deployment(
        id=str(uuid.uuid4()),
        pull_request_id=pr.id,
        incident_id=inc.id,
        commit_sha="c84f91c",
        status="BLOCKED", # Not eligible
        gate_result="{}"
    )
    db.add(dep)
    db.commit()

    with pytest.raises(ValueError):
        DeploymentVerificationService.record_deployment(db, dep.id, "production", "Manual")
        
    dep.status = "ELIGIBLE"
    db.commit()
    
    with pytest.raises(ValueError):
        # Can't start verification before recording deployment
        DeploymentVerificationService.start_verification(db, dep.id)
