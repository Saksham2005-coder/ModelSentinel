import sys
import os
import argparse
import datetime
import uuid
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.db.base_class import Base

# Import all models
from app.models.model import Model, ModelVersion
from app.models.incident import Incident
from app.models.investigation import Investigation, InvestigationEvent, InvestigationEvidence, InvestigationHypothesis
from app.models.monitoring import MonitoringRun, MetricResult, FeatureMonitoringResult
from app.models.telemetry import ProductionTelemetry
from app.models.slo import ReliabilityObjective, SLOEvaluation, Alert, AlertRule
from app.models.patch import PatchProposal, PatchFileChange
from app.models.change_risk import ChangeRiskAssessment
from app.models.validation import ValidationRun, ValidationCheck, ValidationMetric
from app.models.regression import RegressionCase, RegressionRun, RegressionResult
from app.models.pull_request import PullRequest
from app.models.deployment import Deployment
from app.models.deployment_verification import DeploymentVerification
from app.models.incident_memory import IncidentMemory
from app.models.resolution_memory import ResolutionMemory
from app.models.reliability import ReliabilityEvent, ReliabilityEdge
from app.models.policy import ReliabilityPolicy, PolicyEvaluation
from app.models.workflow import WorkflowRun, WorkflowStepRun
from app.models.repository import Repository, RepositorySnapshot, RepositoryFile, RepositorySymbol
from app.models.user import User
from app.models.integration import Integration
from app.models.audit import AuditEvent
from app.core.security import get_password_hash

DEMO_NOW = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

def dt(days=0, hours=0, minutes=0):
    return DEMO_NOW + datetime.timedelta(days=days, hours=hours, minutes=minutes)

def generate_uuid():
    return str(uuid.uuid4())

def reset_demo(db):
    print("Resetting demo environment...")
    
    # Identify demo models
    model_slugs = ["customer-churn-v2", "fraud-detection-v3", "demand-forecast-v1", "spam-classifier-v2"]
    
    models = db.query(Model).filter(Model.slug.in_(model_slugs)).all()
    if not models:
        print("No demo models found to reset, but continuing to clear other tables...")
        model_ids = []
    else:
        model_ids = [m.id for m in models]

    
    # Tables to clear
    # Note: Not all tables have model_id directly, some are via incident, patch, etc.
    db.query(AuditEvent).filter(AuditEvent.actor_id == "demo-admin").delete(synchronize_session=False)
    db.query(Integration).filter(Integration.name.like("%Demo%")).delete(synchronize_session=False)
    
    for m_id in model_ids:
        db.query(ReliabilityEvent).filter(ReliabilityEvent.model_id == m_id).delete(synchronize_session=False)
        db.query(ResolutionMemory).filter(ResolutionMemory.model_id == m_id).delete(synchronize_session=False)
        db.query(IncidentMemory).filter(IncidentMemory.model_id == m_id).delete(synchronize_session=False)
        db.query(SLOEvaluation).filter(SLOEvaluation.model_id == m_id).delete(synchronize_session=False)
        db.query(Alert).filter(Alert.model_id == m_id).delete(synchronize_session=False)
        db.query(ReliabilityObjective).filter(ReliabilityObjective.model_id == m_id).delete(synchronize_session=False)
        db.query(ProductionTelemetry).filter(ProductionTelemetry.model_id == m_id).delete(synchronize_session=False)
        db.query(MonitoringRun).filter(MonitoringRun.model_id == m_id).delete(synchronize_session=False)
        db.query(RegressionCase).filter(RegressionCase.model_id == m_id).delete(synchronize_session=False)
        db.query(ReliabilityPolicy).filter(ReliabilityPolicy.model_id == m_id).delete(synchronize_session=False)
        
        incidents = db.query(Incident).filter(Incident.model_id == m_id).all()
        for inc in incidents:
            invs = db.query(Investigation).filter(Investigation.incident_id == inc.id).all()
            for inv in invs:
                db.query(InvestigationHypothesis).filter(InvestigationHypothesis.investigation_id == inv.id).delete(synchronize_session=False)
                db.query(Investigation).filter(Investigation.id == inv.id).delete(synchronize_session=False)
            
            patches = db.query(PatchProposal).filter(PatchProposal.incident_id == inc.id).all()
            for patch in patches:
                db.query(ChangeRiskAssessment).filter(ChangeRiskAssessment.patch_proposal_id == patch.id).delete(synchronize_session=False)
                db.query(PatchProposal).filter(PatchProposal.id == patch.id).delete(synchronize_session=False)
                
            db.query(ValidationRun).filter(ValidationRun.incident_id == inc.id).delete(synchronize_session=False)
            db.query(PullRequest).filter(PullRequest.incident_id == inc.id).delete(synchronize_session=False)
            
            deps = db.query(Deployment).filter(Deployment.incident_id == inc.id).all()
            for dep in deps:
                db.query(DeploymentVerification).filter(DeploymentVerification.deployment_id == dep.id).delete(synchronize_session=False)
                db.query(Deployment).filter(Deployment.id == dep.id).delete(synchronize_session=False)
                
            db.query(Incident).filter(Incident.id == inc.id).delete(synchronize_session=False)
            
    db.query(ModelVersion).filter(ModelVersion.model_id.in_(model_ids)).delete(synchronize_session=False)
    db.query(Model).filter(Model.id.in_(model_ids)).delete(synchronize_session=False)
    
    # Remove demo repos
    repo_names = ["ml-serving-platform", "fraud-prediction-service"]
    db.query(Repository).filter(Repository.name.in_(repo_names)).delete(synchronize_session=False)
    
    # Remove demo user
    db.query(User).filter(User.email == "demo-admin@modelsentinel.com").delete(synchronize_session=False)
    
    db.commit()
    print("Demo environment reset complete.")

def seed_demo(db):
    print("Seeding demo environment...")
    
    # 0. Create Demo User
    user_id = generate_uuid()
    user = User(
        id=user_id,
        email="demo-admin@modelsentinel.com",
        hashed_password=get_password_hash("password123"),
        full_name="Demo Admin",
        role="ADMIN",
        is_active=True,
        email_verified=True,
        email_verified_at=dt(-30)
    )
    db.add(user)
    
    # 1. Integrations
    github_int = Integration(provider="github", type="repository", name="Demo GitHub", status="CONNECTED", config={}, created_by=user_id, created_at=dt(-25))
    pagerduty_int = Integration(provider="pagerduty", type="alerting", name="Demo PagerDuty", status="CONNECTED", config={}, created_by=user_id, created_at=dt(-25))
    db.add_all([github_int, pagerduty_int])

    # 2. Create Repositories & Files
    repo_ml = Repository(name="ml-serving-platform", source_type="github", source_reference="modelsentinel/ml-serving-platform", default_branch="main", status="ACTIVE", indexed_at=dt(-10))
    repo_fraud = Repository(name="fraud-prediction-service", source_type="github", source_reference="modelsentinel/fraud-prediction-service", default_branch="main", status="ACTIVE", indexed_at=dt(-10))
    db.add_all([repo_ml, repo_fraud])
    db.flush()
    
    snap_ml = RepositorySnapshot(repository_id=repo_ml.id, commit_sha="a1b2c3d4", branch="main", status="COMPLETED", file_count=42, language_count=3, created_at=dt(-10))
    snap_fraud = RepositorySnapshot(repository_id=repo_fraud.id, commit_sha="f5e6d7c8", branch="main", status="COMPLETED", file_count=15, language_count=1, created_at=dt(-10))
    db.add_all([snap_ml, snap_fraud])
    db.flush()

    files = [
        RepositoryFile(repository_snapshot_id=snap_ml.id, path="src/models/spam_classifier.py", language="python", size_bytes=2048, line_count=120),
        RepositoryFile(repository_snapshot_id=snap_ml.id, path="src/features/text_features.py", language="python", size_bytes=4096, line_count=210),
        RepositoryFile(repository_snapshot_id=snap_ml.id, path="src/inference/predict.py", language="python", size_bytes=1024, line_count=50),
        RepositoryFile(repository_snapshot_id=snap_fraud.id, path="app/main.py", language="python", size_bytes=2000, line_count=90),
    ]
    db.add_all(files)
    
    # 3. Create Models & Versions
    m1 = Model(name="Customer Churn V2", slug="customer-churn-v2", framework="xgboost", task_type="classification", primary_metric="accuracy", status="HEALTHY", environment="production")
    m2 = Model(name="Fraud Detection V3", slug="fraud-detection-v3", framework="lightgbm", task_type="classification", primary_metric="roc_auc", status="HEALTHY", environment="production", repository_id=repo_fraud.id)
    m3 = Model(name="Demand Forecast V1", slug="demand-forecast-v1", framework="pytorch", task_type="regression", primary_metric="rmse", status="AT_RISK", environment="production")
    m4 = Model(name="Spam Classifier V2", slug="spam-classifier-v2", framework="huggingface", task_type="classification", primary_metric="f1_score", status="UNHEALTHY", environment="production", repository_id=repo_ml.id)
    
    db.add_all([m1, m2, m3, m4])
    db.flush()
    
    mv1 = ModelVersion(model_id=m1.id, version="v2.1", is_active=True, created_at=dt(-20))
    mv2 = ModelVersion(model_id=m2.id, version="v3.0", is_active=True, created_at=dt(-40))
    mv3_1 = ModelVersion(model_id=m3.id, version="v1.1", is_active=False, created_at=dt(-25))
    mv3_2 = ModelVersion(model_id=m3.id, version="v1.2", is_active=True, created_at=dt(-15))
    mv4_1 = ModelVersion(model_id=m4.id, version="v2.0", is_active=False, created_at=dt(-60))
    mv4_2 = ModelVersion(model_id=m4.id, version="v2.1", is_active=True, created_at=dt(-2), repository_snapshot_id=snap_ml.id)
    db.add_all([mv1, mv2, mv3_1, mv3_2, mv4_1, mv4_2])
    db.flush()

    # 4. Telemetry and Monitoring (Generate ~15 records)
    for i in range(15):
        t_start = dt(-15 + i, 0)
        tel = ProductionTelemetry(model_id=m1.id, model_version_id=mv1.id, source="api", window_start=t_start, window_end=t_start+datetime.timedelta(hours=1), sample_count=5000, status="PROCESSED", created_at=t_start)
        db.add(tel)
        db.flush()
        
        mon = MonitoringRun(model_id=m1.id, model_version_id=mv1.id, run_type="performance", status="COMPLETED", started_at=t_start, completed_at=t_start+datetime.timedelta(minutes=5), health_summary="Healthy")
        db.add(mon)
        db.flush()
        db.add(MetricResult(monitoring_run_id=mon.id, metric_name="accuracy", metric_value=0.88 + (0.01 * (i%3)), metric_type="performance", threshold=0.85, status="PASS"))

    for i in range(5):
        t_start = dt(-5 + i, 0)
        tel = ProductionTelemetry(model_id=m4.id, model_version_id=mv4_2.id, source="api", window_start=t_start, window_end=t_start+datetime.timedelta(hours=1), sample_count=10000, status="PROCESSED", created_at=t_start)
        db.add(tel)

    # 5. SLOs and Alerts
    slo1 = ReliabilityObjective(model_id=m1.id, name="Churn Accuracy SLO", objective_type="performance", metric_name="accuracy", comparison_operator=">=", target_value=0.85, evaluation_window="7d", enabled=True, severity="high", created_at=dt(-20))
    slo2 = ReliabilityObjective(model_id=m2.id, name="Fraud ROC AUC", objective_type="performance", metric_name="roc_auc", comparison_operator=">=", target_value=0.90, evaluation_window="24h", enabled=True, severity="critical", created_at=dt(-40))
    slo3 = ReliabilityObjective(model_id=m3.id, name="Forecast RMSE", objective_type="performance", metric_name="rmse", comparison_operator="<=", target_value=15.0, evaluation_window="24h", enabled=True, severity="critical", created_at=dt(-15))
    slo4 = ReliabilityObjective(model_id=m4.id, name="Spam F1 Score", objective_type="performance", metric_name="f1_score", comparison_operator=">=", target_value=0.85, evaluation_window="1h", enabled=True, severity="critical", created_at=dt(-60))
    db.add_all([slo1, slo2, slo3, slo4])
    db.flush()

    ar1 = AlertRule(objective_id=slo1.id, name="Churn accuracy drop", enabled=True, severity="high", condition_type="SLO_BREACHED")
    ar2 = AlertRule(objective_id=slo3.id, name="Forecast RMSE high", enabled=True, severity="critical", condition_type="SLO_BREACHED")
    ar3 = AlertRule(objective_id=slo4.id, name="Spam F1 drop", enabled=True, severity="critical", condition_type="SLO_BREACHED")
    db.add_all([ar1, ar2, ar3])
    db.flush()

    alert1 = Alert(rule_id=ar1.id, deduplication_key="dedup-1", objective_id=slo1.id, model_id=m1.id, severity="high", status="resolved", triggered_at=dt(-15), resolved_at=dt(-14), summary="Transient accuracy dip", created_at=dt(-15))
    alert2 = Alert(rule_id=ar2.id, deduplication_key="dedup-2", objective_id=slo3.id, model_id=m3.id, severity="critical", status="active", triggered_at=dt(-1, -2), summary="RMSE exceeded threshold 15.0", created_at=dt(-1, -2))
    db.add_all([alert1, alert2])

    # 6. Model 2: Fraud Detection V3 (Historical Incident)
    inc2 = Incident(model_id=m2.id, model_version_id=mv2.id, incident_key=f"INC-{uuid.uuid4().hex[:8]}", title="Concept Drift in EMEA Region", severity="medium", status="resolved", category="data_drift", created_at=dt(-25), detected_at=dt(-25))
    db.add(inc2)
    db.flush()
    
    inv2 = Investigation(incident_id=inc2.id, status="completed", started_at=dt(-25), completed_at=dt(-24), summary="Recent holiday shopping changed patterns.", created_at=dt(-25))
    db.add(inv2)
    db.flush()
    db.add(InvestigationHypothesis(investigation_id=inv2.id, title="Shopping behavior drift", description="Holiday shopping caused drift", status="confirmed", rank=1, evidence_strength=0.9))
    
    patch2 = PatchProposal(investigation_id=inv2.id, incident_id=inc2.id, repository_id=repo_fraud.id, repository_snapshot_id=snap_fraud.id, version="v1", status="merged", summary="Retrain with recent data", rationale="Data drift requires new data.", expected_behavior="Model recovers performance.", created_at=dt(-24))
    db.add(patch2)
    db.flush()
    db.add(ChangeRiskAssessment(patch_proposal_id=patch2.id, risk_score=20, risk_level="LOW"))
    
    val2 = ValidationRun(patch_proposal_id=patch2.id, incident_id=inc2.id, repository_snapshot_id=snap_fraud.id, status="completed", verdict="PASSED", started_at=dt(-24), completed_at=dt(-23))
    db.add(val2)
    db.flush()
    
    pr2 = PullRequest(id=generate_uuid(), incident_id=inc2.id, patch_proposal_id=patch2.id, validation_run_id=val2.id, repository_id=repo_fraud.id, repository_snapshot_id=snap_fraud.id, branch_name="fix/drift", commit_sha="aaa", provider="github", provider_pr_id="10", title="Fix concept drift in EMEA", description="Retrains the model to fix drift.", status="MERGED", created_at=dt(-23))
    db.add(pr2)
    db.flush()
    
    dep2 = Deployment(id=generate_uuid(), incident_id=inc2.id, pull_request_id=pr2.id, environment="production", status="DEPLOYED", commit_sha="aaa", gate_result="{}", deployed_at=dt(-22))
    db.add(dep2)
    db.flush()
    
    mem2 = IncidentMemory(incident_id=inc2.id, model_id=m2.id, model_version_id=mv2.id, title="EMEA Concept Drift", severity="medium", resolution_status="resolved", resolution_summary="Retrained with last 3 months data", created_at=dt(-20))
    db.add(mem2)
    db.flush()
    db.add(ResolutionMemory(incident_memory_id=mem2.id, incident_id=inc2.id, model_id=m2.id, patch_id=patch2.id, validation_id=val2.id, deployment_id=dep2.id, resolution_summary="Retrained data", validation_status="PASSED", ml_recovery_score=0.92, deployment_status="SUCCESS", post_deployment_status="HEALTHY", effectiveness_score=90, created_at=dt(-20)))

    # 7. Model 3: Demand Forecast V1 (Data quality problem)
    inc3 = Incident(model_id=m3.id, model_version_id=mv3_2.id, incident_key=f"INC-{uuid.uuid4().hex[:8]}", title="Spike in RMSE due to holiday season mismatch", severity="high", status="active", category="performance_degradation", created_at=dt(-1, -1), detected_at=dt(-1, -1))
    db.add(inc3)
    db.flush()
    inv3 = Investigation(incident_id=inc3.id, status="in_progress", started_at=dt(-1, 0), summary="Investigating weather data feed issues.", created_at=dt(-1, 0))
    db.add(inv3)
    db.flush()
    db.add(InvestigationHypothesis(investigation_id=inv3.id, title="Weather API timeout caused nulls", description="Third party API was down", status="testing", rank=1, evidence_strength=0.6))
    
    # 8. Model 4: Spam Classifier V2 (Hero Model - End-to-End Story)
    inc4 = Incident(model_id=m4.id, model_version_id=mv4_2.id, incident_key=f"INC-{uuid.uuid4().hex[:8]}", title="Sudden F1 drop in Spam Classifier", severity="critical", status="investigating", category="performance_degradation", detected_at=dt(-2, -3), created_at=dt(-2, -3))
    db.add(inc4)
    db.flush()
    
    alert4 = Alert(rule_id=ar3.id, deduplication_key="dedup-3", objective_id=slo4.id, model_id=m4.id, incident_id=inc4.id, severity="critical", status="acknowledged", triggered_at=dt(-2, -3), acknowledged_at=dt(-2, -2), summary="F1 Score dropped to 0.72")
    db.add(alert4)
    
    inv4 = Investigation(incident_id=inc4.id, status="completed", started_at=dt(-2, -2), completed_at=dt(-1, -10), summary="Identified edge case with text parsing for new emoji encodings.", created_at=dt(-2, -2))
    db.add(inv4)
    db.flush()
    
    hyp4 = InvestigationHypothesis(investigation_id=inv4.id, title="Text parsing failure on new emoji set", description="Fails on Unicode 15", status="confirmed", rank=1, evidence_strength=0.9)
    db.add(hyp4)
    db.flush()
    inv4.primary_hypothesis_id = hyp4.id
    
    patch4 = PatchProposal(investigation_id=inv4.id, incident_id=inc4.id, repository_id=repo_ml.id, repository_snapshot_id=snap_ml.id, version="v1", status="merged", summary="Fix emoji parsing logic in text_features.py", rationale="The new emoji set causes parsing exceptions.", expected_behavior="Emojis are correctly ignored or parsed.", created_at=dt(-1, -8))
    db.add(patch4)
    db.flush()
    db.add(PatchFileChange(patch_proposal_id=patch4.id, file_path="src/features/text_features.py", change_type="MODIFY", additions=15, deletions=2, diff_text="@@ -10,3 +10,18 @@\n-def parse(text):\n+def parse(text):\n+    import emoji", rationale="Use python emoji package instead of custom regex"))
    db.add(ChangeRiskAssessment(patch_proposal_id=patch4.id, risk_score=85, risk_level="HIGH", factors=[{"factor": "Core feature logic change", "contribution": 60}]))
    
    val4 = ValidationRun(patch_proposal_id=patch4.id, incident_id=inc4.id, repository_snapshot_id=snap_ml.id, status="completed", verdict="PASSED", started_at=dt(-1, -7), completed_at=dt(-1, -6))
    db.add(val4)
    db.flush()
    db.add(ValidationCheck(validation_run_id=val4.id, check_type="unit_test", name="pytest src/features/", status="PASSED", summary="All tests passed."))
    db.add(ValidationMetric(validation_run_id=val4.id, metric_name="f1_score", baseline_value=0.72, current_value=0.88, patched_value=0.88, delta=0.16, threshold=0.85, status="PASSED"))
    
    mem4 = IncidentMemory(incident_id=inc4.id, model_id=m4.id, model_version_id=mv4_2.id, title="Sudden F1 drop in Spam Classifier", severity="critical", resolution_status="resolved", resolution_summary="Updated emoji parsing to support Unicode 15", created_at=dt(0))
    db.add(mem4)
    db.flush()
    db.add(ResolutionMemory(incident_memory_id=mem4.id, incident_id=inc4.id, model_id=m4.id, patch_id=patch4.id, validation_id=val4.id, resolution_summary="Updated emoji parsing to support Unicode 15", validation_status="PASSED", ml_recovery_score=0.98, deployment_status="SUCCESS", post_deployment_status="HEALTHY", effectiveness_score=98, created_at=dt(0)))
    
    rc_suite1 = RegressionCase(model_id=m4.id, model_version_id=mv4_2.id, source_incident_id=inc4.id, incident_memory_id=mem4.id, name="Emoji parsing regression suite", description="Testing emojis.", expected_behavior="Emojis should not degrade text features", severity="high", status="active", created_at=dt(-20))
    rc_suite2 = RegressionCase(model_id=m4.id, model_version_id=mv4_2.id, source_incident_id=inc4.id, incident_memory_id=mem4.id, name="Length constraint suite", description="Testing length.", expected_behavior="Max length truncated correctly", severity="medium", status="active", created_at=dt(-20))
    rc_suite3 = RegressionCase(model_id=m2.id, model_version_id=mv2.id, source_incident_id=inc2.id, incident_memory_id=mem2.id, name="Null handling suite", description="Testing nulls.", expected_behavior="Nulls gracefully dropped", severity="high", status="active", created_at=dt(-20))
    db.add_all([rc_suite1, rc_suite2, rc_suite3])
    db.flush()
    
    db.add(RegressionRun(regression_case_id=rc_suite1.id, validation_run_id=val4.id, status="passed", started_at=dt(-1, -6), completed_at=dt(-1, -5)))
    db.add(RegressionRun(regression_case_id=rc_suite2.id, validation_run_id=val4.id, status="passed", started_at=dt(-1, -6), completed_at=dt(-1, -5)))
    db.add(RegressionRun(regression_case_id=rc_suite3.id, status="passed", started_at=dt(-10), completed_at=dt(-10)))
    
    pr4 = PullRequest(id=generate_uuid(), incident_id=inc4.id, patch_proposal_id=patch4.id, validation_run_id=val4.id, repository_id=repo_ml.id, repository_snapshot_id=snap_ml.id, branch_name="fix/spam-emoji", commit_sha="abc1234", provider="github", provider_pr_id="101", pr_url="https://github.com/modelsentinel/ml-serving-platform/pull/101", title="Fix emoji parsing", description="Fixes emoji parsing bug on Unicode 15.", status="MERGED", created_at=dt(-1, -4))
    db.add(pr4)
    db.flush()
    
    dep4 = Deployment(id=generate_uuid(), incident_id=inc4.id, pull_request_id=pr4.id, environment="production", status="HEALTHY", commit_sha="abc1234", gate_result="{}", deployed_at=dt(-1, -1))
    db.add(dep4)
    db.flush()
    
    ver4 = DeploymentVerification(id=generate_uuid(), deployment_id=dep4.id, status="HEALTHY", summary="Everything is running fine.", started_at=dt(-1, -1), completed_at=dt(0))
    db.add(ver4)
    
    db.add(ReliabilityEvent(model_id=m4.id, model_version_id=mv4_2.id, event_type="incident_created", occurred_at=dt(-2, -3), source_type="incident", source_id=inc4.id, severity="critical", title="Incident Created: Sudden F1 drop in Spam Classifier"))
    db.add(ReliabilityEvent(model_id=m4.id, model_version_id=mv4_2.id, event_type="investigation_started", occurred_at=dt(-2, -2), source_type="investigation", source_id=inv4.id, title="Investigation Started"))
    db.add(ReliabilityEvent(model_id=m4.id, model_version_id=mv4_2.id, event_type="patch_proposed", occurred_at=dt(-1, -8), source_type="patch_proposal", source_id=patch4.id, title="Patch Proposed"))
    db.add(ReliabilityEvent(model_id=m4.id, model_version_id=mv4_2.id, event_type="deployment_completed", occurred_at=dt(-1, -1), source_type="deployment", source_id=dep4.id, title="Deployment Completed"))
    
    # 9. Additional Incidents for volume (Total 5 requested: 1, 2, 3 created above + 2 more)
    inc5 = Incident(model_id=m1.id, model_version_id=mv1.id, incident_key=f"INC-{uuid.uuid4().hex[:8]}", title="Minor latency spike", severity="low", status="resolved", category="service_health", created_at=dt(-15), detected_at=dt(-15))
    inc6 = Incident(model_id=m4.id, model_version_id=mv4_1.id, incident_key=f"INC-{uuid.uuid4().hex[:8]}", title="Old version memory leak", severity="medium", status="resolved", category="service_health", created_at=dt(-50), detected_at=dt(-50))
    db.add_all([inc5, inc6])
    db.flush()
    mem5 = IncidentMemory(incident_id=inc5.id, model_id=m1.id, model_version_id=mv1.id, title="Minor latency spike", severity="low", resolution_status="resolved", resolution_summary="Auto-scaled instances", created_at=dt(-14))
    db.add(mem5)
    db.flush()
    db.add(ResolutionMemory(incident_memory_id=mem5.id, incident_id=inc5.id, model_id=m1.id, resolution_summary="Auto-scaled instances", validation_status="PASSED", ml_recovery_score=1.0, deployment_status="SUCCESS", post_deployment_status="HEALTHY", effectiveness_score=100, created_at=dt(-14)))

    # 10. Policies and Workflows
    pol1 = ReliabilityPolicy(name="Require High Validation F1", description="Validations must have F1 >= 0.85", scope="validation", environment="production", model_id=m4.id, enabled=True, priority=1, rules=[{"type": "metric", "operator": ">=", "metric_name": "f1_score", "required": 0.85}])
    pol2 = ReliabilityPolicy(name="Block untested deployments", description="Deployments without regressions passed are blocked", scope="deployment", environment="production", enabled=True, priority=2, rules=[{"type": "check", "operator": "==", "required": "passed"}])
    pol3 = ReliabilityPolicy(name="Review Required for Risk", description="High risk patches require manual review", scope="patch_proposal", environment="production", enabled=True, priority=3, rules=[{"type": "risk_level", "operator": "in", "required": ["HIGH", "CRITICAL"]}])
    db.add_all([pol1, pol2, pol3])
    
    wf1 = WorkflowRun(name="Patch Review Flow", workflow_type="patch_review", description="Standard review", status="COMPLETED", entity_type="patch_proposal", entity_id=patch4.id, started_at=dt(-1, -8), completed_at=dt(-1, -7))
    wf2 = WorkflowRun(name="Deployment Gate", workflow_type="deployment_gate", description="Gate for PR", status="COMPLETED", entity_type="pull_request", entity_id=pr2.id, started_at=dt(-23), completed_at=dt(-22))
    wf3 = WorkflowRun(name="Incident Triage", workflow_type="incident_triage", description="Initial triage", status="RUNNING", entity_type="incident", entity_id=inc3.id, started_at=dt(-1, -1))
    db.add_all([wf1, wf2, wf3])
    
    # 11. Audit Events (10+)
    for i in range(12):
        db.add(AuditEvent(timestamp=dt(-10 + i), actor_id=user_id, actor_type="USER", action="login" if i%3==0 else "view_model", resource_type="auth" if i%3==0 else "model", resource_id="system" if i%3==0 else m4.id, result="SUCCESS", source="web"))
        
    db.commit()
    print("Demo environment seeding complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ModelSentinel Demo Seeder")
    parser.add_argument("--reset", action="store_true", help="Reset the demo environment")
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        if args.reset:
            reset_demo(db)
        else:
            seed_demo(db)
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()
