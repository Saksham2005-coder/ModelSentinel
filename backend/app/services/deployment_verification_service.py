import datetime
import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.deployment import Deployment
from app.models.deployment_verification import DeploymentVerification
from app.models.pull_request import PullRequest
from app.models.validation import ValidationRun, ValidationMetric
from app.models.monitoring import MonitoringRun, MetricResult, FeatureMonitoringResult, PredictionMonitoringResult
from app.models.incident import Incident, IncidentEvent

class DeploymentVerificationService:

    @staticmethod
    def record_deployment(db: Session, deployment_id: str, environment: str, deployment_source: str, deployed_by: Optional[str] = None) -> Deployment:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        if deployment.status not in ["ELIGIBLE", "APPROVED"]:
            raise ValueError(f"Deployment must be ELIGIBLE to record deployment, currently {deployment.status}")

        deployment.status = "DEPLOYED"
        deployment.deployed_at = datetime.datetime.utcnow()
        deployment.environment = environment
        deployment.deployment_source = deployment_source
        deployment.deployed_by = deployed_by

        db.commit()
        db.refresh(deployment)
        return deployment

    @staticmethod
    def start_verification(db: Session, deployment_id: str) -> DeploymentVerification:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise ValueError("Deployment not found")
            
        if deployment.status != "DEPLOYED":
            raise ValueError(f"Deployment must be DEPLOYED to start verification, currently {deployment.status}")

        deployment.status = "VERIFYING"
        
        pr = db.query(PullRequest).filter(PullRequest.id == deployment.pull_request_id).first()
        baseline_data = {}
        if pr and pr.validation_run_id:
            val_run = db.query(ValidationRun).filter(ValidationRun.id == pr.validation_run_id).first()
            if val_run:
                for vm in val_run.metrics:
                    baseline_data[vm.metric_name] = {
                        "baseline_value": vm.baseline_value,
                        "patched_value": vm.patched_value,
                        "threshold": vm.threshold
                    }

        verification = DeploymentVerification(
            id=str(uuid.uuid4()),
            deployment_id=deployment.id,
            status="VERIFYING",
            baseline_reference=baseline_data,
            post_deployment_observation={},
            summary="Verification started",
            started_at=datetime.datetime.utcnow()
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
        db.refresh(deployment)
        return verification

    @staticmethod
    def evaluate_health(db: Session, deployment_id: str) -> DeploymentVerification:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        verification = db.query(DeploymentVerification).filter(
            DeploymentVerification.deployment_id == deployment_id
        ).order_by(DeploymentVerification.started_at.desc()).first()
        
        if not verification:
            raise ValueError("No verification found for deployment")
            
        # Get the latest monitoring run for this model (simulating post-deployment monitoring)
        monitoring_run = db.query(MonitoringRun).filter(
            MonitoringRun.model_id == deployment.incident.model_id
        ).order_by(MonitoringRun.created_at.desc()).first()

        observations = {}
        health_status = "HEALTHY"
        critical_count = 0
        warning_count = 0
        failure_reason = ""

        baseline = verification.baseline_reference or {}

        if monitoring_run:
            for mr in monitoring_run.metrics:
                obs = {
                    "current": mr.metric_value,
                    "status": mr.status,
                    "baseline": baseline.get(mr.metric_name, {}).get("baseline_value")
                }
                observations[mr.metric_name] = obs
                if mr.status == "critical":
                    critical_count += 1
                elif mr.status == "warning":
                    warning_count += 1
                    
            for fr in monitoring_run.feature_results:
                obs = {
                    "current": fr.drift_score,
                    "status": fr.status,
                    "baseline": baseline.get(fr.feature_name, {}).get("baseline_value")
                }
                observations[f"feature_{fr.feature_name}"] = obs
                if fr.status == "critical":
                    critical_count += 1
                elif fr.status == "warning":
                    warning_count += 1

        if critical_count > 0:
            health_status = "FAILED"
            failure_reason = f"{critical_count} critical metrics detected post-deployment"
        elif warning_count > 0:
            health_status = "DEGRADED"
            failure_reason = f"{warning_count} warning metrics detected post-deployment"
        else:
            health_status = "HEALTHY"

        verification.post_deployment_observation = observations
        verification.status = health_status
        verification.completed_at = datetime.datetime.utcnow()
        verification.failure_reason = failure_reason
        verification.summary = f"Deployment health evaluated: {health_status}"
        
        deployment.status = health_status

        # Closed-loop Incident Creation if failed or degraded
        if health_status in ["DEGRADED", "FAILED"]:
            incident = deployment.incident
            
            # Create a POST_DEPLOYMENT_DEGRADATION event on original incident
            event = IncidentEvent(
                incident_id=incident.id,
                event_type="post_deployment_degradation",
                message=f"Post-deployment verification resulted in {health_status}. Reason: {failure_reason}",
                metadata_json={"deployment_id": deployment.id}
            )
            db.add(event)
            
            # Create a new incident linked to the deployment failure
            new_incident = Incident(
                incident_key=f"POST-DEPLOY-{deployment.id[:8]}",
                model_id=incident.model_id,
                model_version_id=incident.model_version_id,
                title=f"Post-Deployment Degradation for {incident.title}",
                summary=f"Deployment {deployment.id} resulted in {health_status} state. {failure_reason}",
                severity="high" if health_status == "FAILED" else "medium",
                status="detected",
                category="performance"
            )
            db.add(new_incident)

        db.commit()
        db.refresh(verification)
        db.refresh(deployment)
        return verification
