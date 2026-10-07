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
from app.services.policy_service import PolicyEvaluationService

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
        
        from app.services.reliability_service import reliability_service
        dep_event = reliability_service.emit_event(
            db=db,
            model_id=deployment.incident.model_id,
            model_version_id=deployment.incident.model_version_id,
            event_type="DEPLOYMENT_COMPLETED",
            source_type="deployment",
            source_id=deployment.id,
            title="Deployment Completed",
            summary=f"Fix deployed to {environment}.",
            status="success"
        )
        pr_event = reliability_service.find_event_by_source(db, "pull_request", deployment.pull_request_id, "PULL_REQUEST_CREATED")
        if pr_event:
            reliability_service.link_events(db, pr_event.id, dep_event.id, "RESULTED_IN")
            
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

        # Evaluate Post-Deployment Policies
        policy_context = {
            "post_deployment_verification": "PASS" if health_status == "HEALTHY" else "FAIL",
            "deployment_health": health_status
        }
        policy_svc = PolicyEvaluationService(db)
        policy_res = policy_svc.evaluate_action(
            target_type="DEPLOYMENT",
            target_id=deployment_id,
            context=policy_context
        )
        
        if policy_res["result"] == "BLOCK":
            health_status = "FAILED"
            failure_reason = f"Blocked by Post-Deployment Policy: {policy_res['matched_policy']}"

        verification.post_deployment_observation = observations
        verification.status = health_status
        verification.completed_at = datetime.datetime.utcnow()
        verification.failure_reason = failure_reason
        verification.summary = f"Deployment health evaluated: {health_status}"
        
        deployment.status = health_status

        db.commit()
        db.refresh(verification)
        db.refresh(deployment)
        
        from app.services.reliability_service import reliability_service
        ver_event = reliability_service.emit_event(
            db=db,
            model_id=deployment.incident.model_id,
            model_version_id=deployment.incident.model_version_id,
            event_type="VERIFICATION_COMPLETED",
            source_type="deployment_verification",
            source_id=verification.id,
            title=f"Deployment Verification {health_status}",
            summary=verification.summary,
            status="success" if health_status == "HEALTHY" else "error"
        )
        dep_event = reliability_service.find_event_by_source(db, "deployment", deployment.id, "DEPLOYMENT_COMPLETED")
        if dep_event:
            reliability_service.link_events(db, dep_event.id, ver_event.id, "VALIDATED_BY")
            
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
            db.flush()

            deg_event = reliability_service.emit_event(
                db=db,
                model_id=incident.model_id,
                model_version_id=incident.model_version_id,
                event_type="POST_DEPLOYMENT_DEGRADATION",
                source_type="deployment_verification",
                source_id=verification.id,
                title="Post-Deployment Degradation",
                summary=f"Verification resulted in {health_status}.",
                severity="high" if health_status == "FAILED" else "warning",
                status="failed"
            )

            inc_event = reliability_service.emit_event(
                db=db,
                model_id=incident.model_id,
                model_version_id=incident.model_version_id,
                event_type="INCIDENT_CREATED",
                source_type="incident",
                source_id=new_incident.id,
                title=new_incident.title,
                summary=new_incident.summary,
                severity=new_incident.severity,
                status="active"
            )
            
            reliability_service.link_events(db, ver_event.id, deg_event.id, "RESULTED_IN")
            reliability_service.link_events(db, deg_event.id, inc_event.id, "CAUSED")
            db.commit()

        return verification
