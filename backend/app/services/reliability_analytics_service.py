from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import uuid

from app.models.incident import Incident
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.models.regression import RegressionRun, RegressionCase
from app.models.deployment import Deployment
from app.models.deployment_verification import DeploymentVerification
from app.models.model import Model
from app.models.model import Model
from app.models.incident_memory import IncidentMemory
from app.models.policy import PolicyEvaluation

class ReliabilityAnalyticsService:

    @staticmethod
    def _apply_time_filter(query, time_field, time_range_days: Optional[int]):
        if time_range_days:
            cutoff = datetime.now(timezone.utc) - timedelta(days=time_range_days)
            return query.filter(time_field >= cutoff)
        return query

    @staticmethod
    def _apply_model_filter(query, model_field, model_id: Optional[str]):
        if model_id:
            return query.filter(model_field == model_id)
        return query

    @classmethod
    def get_overview_metrics(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        # Incidents
        q_inc = db.query(Incident)
        q_inc = cls._apply_time_filter(q_inc, Incident.detected_at, time_range_days)
        q_inc = cls._apply_model_filter(q_inc, Incident.model_id, model_id)
        total_incidents = q_inc.count()
        critical_incidents = q_inc.filter(Incident.severity == "critical").count()
        resolved_incidents = q_inc.filter(Incident.status == "resolved").count()
        open_incidents = total_incidents - resolved_incidents - q_inc.filter(Incident.status == "suppressed").count()

        # MTTD, MTTR
        resolved_inc = q_inc.filter(Incident.resolved_at.isnot(None), Incident.detected_at.isnot(None)).all()
        mttd_list = [(i.acknowledged_at - i.detected_at).total_seconds() for i in resolved_inc if i.acknowledged_at]
        mttd = (sum(mttd_list) / len(mttd_list) / 60.0) if mttd_list else None # in minutes
        mttr_list = [(i.resolved_at - i.detected_at).total_seconds() for i in resolved_inc]
        mttr = (sum(mttr_list) / len(mttr_list) / 60.0) if mttr_list else None

        # Deployment Health
        q_dep = db.query(Deployment)
        q_dep = cls._apply_time_filter(q_dep, Deployment.created_at, time_range_days)
        if model_id:
            q_dep = q_dep.join(Incident).filter(Incident.model_id == model_id)
        total_deployments = q_dep.count()
        healthy_deployments = q_dep.filter(Deployment.status == "HEALTHY").count()
        degraded_deployments = q_dep.filter(Deployment.status.in_(["DEGRADED", "FAILED"])).count()
        post_deployment_degradation_rate = (degraded_deployments / total_deployments) * 100 if total_deployments > 0 else 0

        # Regression Coverage
        q_mem = db.query(IncidentMemory)
        q_mem = cls._apply_time_filter(q_mem, IncidentMemory.created_at, time_range_days)
        q_mem = cls._apply_model_filter(q_mem, IncidentMemory.model_id, model_id)
        total_memories = q_mem.count()
        q_reg = db.query(RegressionCase)
        q_reg = cls._apply_time_filter(q_reg, RegressionCase.created_at, time_range_days)
        q_reg = cls._apply_model_filter(q_reg, RegressionCase.model_id, model_id)
        total_regression_cases = q_reg.count()
        regression_coverage = (total_regression_cases / total_memories) * 100 if total_memories > 0 else 100

        # Score calculation
        score = 100
        incident_freq_penalty = min(total_incidents * 2, 20)
        critical_penalty = min(critical_incidents * 4, 30)
        degradation_penalty = min(degraded_deployments * 5, 25)
        mttr_penalty = min((mttr or 0) / 60.0, 15) # 1 point per hour, max 15
        coverage_bonus = (regression_coverage / 100.0) * 10
        score = max(0, min(100, score - incident_freq_penalty - critical_penalty - degradation_penalty - mttr_penalty + coverage_bonus))

        return {
            "reliability_score": round(score),
            "score_contributors": {
                "Incident Frequency": -round(incident_freq_penalty),
                "Critical Incidents": -round(critical_penalty),
                "Deployment Stability": -round(degradation_penalty),
                "MTTR": -round(mttr_penalty),
                "Regression Stability": round(coverage_bonus)
            },
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "resolved_incidents": resolved_incidents,
            "critical_incidents": critical_incidents,
            "mttd_minutes": mttd,
            "mttr_minutes": mttr,
            "deployment_degradation_rate": post_deployment_degradation_rate,
            "regression_coverage": regression_coverage
        }

    @classmethod
    def get_incident_analytics(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        q_inc = db.query(Incident)
        q_inc = cls._apply_time_filter(q_inc, Incident.detected_at, time_range_days)
        q_inc = cls._apply_model_filter(q_inc, Incident.model_id, model_id)
        
        total = q_inc.count()
        critical = q_inc.filter(Incident.severity == "critical").count()
        warning = q_inc.filter(Incident.severity.in_(["high", "medium", "low"])).count()
        resolved = q_inc.filter(Incident.status == "resolved").count()
        
        severity_dist = db.query(Incident.severity, func.count(Incident.id)).group_by(Incident.severity).all()
        status_dist = db.query(Incident.status, func.count(Incident.id)).group_by(Incident.status).all()
        category_dist = db.query(Incident.category, func.count(Incident.id)).group_by(Incident.category).all()
        
        return {
            "total_incidents": total,
            "critical_incidents": critical,
            "warning_incidents": warning,
            "resolved_incidents": resolved,
            "recurring_incidents": 0, # Placeholder without deep memory cross-reference
            "severity_distribution": [{"name": s[0], "value": s[1]} for s in severity_dist],
            "status_distribution": [{"name": s[0], "value": s[1]} for s in status_dist],
            "category_distribution": [{"name": s[0], "value": s[1]} for s in category_dist]
        }

    @classmethod
    def get_model_reliability(cls, db: Session, time_range_days: Optional[int] = None) -> List[Dict[str, Any]]:
        models = db.query(Model).all()
        results = []
        for m in models:
            overview = cls.get_overview_metrics(db, time_range_days=time_range_days, model_id=m.id)
            
            # Validation success
            q_val = db.query(ValidationRun).join(Incident).filter(Incident.model_id == m.id)
            q_val = cls._apply_time_filter(q_val, ValidationRun.created_at, time_range_days)
            total_val = q_val.count()
            passed_val = q_val.filter(ValidationRun.verdict == "PASS").count()
            val_success = (passed_val / total_val) * 100 if total_val > 0 else None
            
            results.append({
                "model_id": m.id,
                "model_name": m.name,
                "incidents": overview["total_incidents"],
                "critical_incidents": overview["critical_incidents"],
                "validation_success": val_success,
                "regression_coverage": overview["regression_coverage"],
                "degradation_rate": overview["deployment_degradation_rate"],
                "mttr_minutes": overview["mttr_minutes"],
                "reliability_score": overview["reliability_score"]
            })
        return results

    @classmethod
    def get_root_cause_trends(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        q_mem = db.query(
            IncidentMemory.root_cause_category, 
            func.count(IncidentMemory.id).label("freq"),
            func.count(func.distinct(IncidentMemory.model_id)).label("models")
        )
        q_mem = cls._apply_time_filter(q_mem, IncidentMemory.created_at, time_range_days)
        q_mem = cls._apply_model_filter(q_mem, IncidentMemory.model_id, model_id)
        q_mem = q_mem.filter(IncidentMemory.root_cause_category.isnot(None))
        q_mem = q_mem.group_by(IncidentMemory.root_cause_category)
        
        results = []
        for row in q_mem.all():
            cat = row[0]
            freq = row[1]
            models_affected = row[2]
            
            # Find related deployments for this category
            mems = db.query(IncidentMemory).filter(IncidentMemory.root_cause_category == cat).all()
            inc_ids = [m.incident_id for m in mems]
            deps = db.query(Deployment).filter(Deployment.incident_id.in_(inc_ids)).all()
            
            total_deps = len(deps)
            healthy_deps = len([d for d in deps if d.status == "HEALTHY"])
            success_rate = (healthy_deps / total_deps * 100) if total_deps > 0 else 100
            
            results.append({
                "root_cause": cat,
                "frequency": freq,
                "affected_models": models_affected,
                "successful_fix_rate": success_rate,
                "severity": "high" if success_rate < 80 else "medium"
            })
        return results

    @classmethod
    def get_deployment_health(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        q_dep = db.query(Deployment)
        q_dep = cls._apply_time_filter(q_dep, Deployment.created_at, time_range_days)
        if model_id:
            q_dep = q_dep.join(Incident).filter(Incident.model_id == model_id)
        
        total = q_dep.count()
        healthy = q_dep.filter(Deployment.status == "HEALTHY").count()
        degraded = q_dep.filter(Deployment.status == "DEGRADED").count()
        failed = q_dep.filter(Deployment.status == "FAILED").count()
        pending = q_dep.filter(Deployment.status.in_(["DEPLOYED", "VERIFYING"])).count()
        
        completed = healthy + degraded + failed
        degradation_rate = ((degraded + failed) / completed * 100) if completed > 0 else 0
        
        return {
            "total_deployments": total,
            "healthy": healthy,
            "degraded": degraded,
            "failed": failed,
            "verification_pending": pending,
            "post_deployment_degradation_rate": degradation_rate
        }

    @classmethod
    def get_fix_effectiveness(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        q_inc = db.query(Incident)
        q_inc = cls._apply_time_filter(q_inc, Incident.created_at, time_range_days)
        q_inc = cls._apply_model_filter(q_inc, Incident.model_id, model_id)
        total_detected = q_inc.count()
        
        # Loop steps
        q_inv = db.query(Incident).filter(Incident.status.in_(["investigating", "fix_generated", "validation", "resolved"]))
        q_inv = cls._apply_time_filter(q_inv, Incident.created_at, time_range_days)
        q_inv = cls._apply_model_filter(q_inv, Incident.model_id, model_id)
        investigated = q_inv.count()
        
        # Validated
        q_val = db.query(ValidationRun).filter(ValidationRun.verdict == "PASS")
        q_val = cls._apply_time_filter(q_val, ValidationRun.created_at, time_range_days)
        if model_id:
            q_val = q_val.join(Incident).filter(Incident.model_id == model_id)
        validated = q_val.count()
        
        # Learned (Memories)
        q_mem = db.query(IncidentMemory)
        q_mem = cls._apply_time_filter(q_mem, IncidentMemory.created_at, time_range_days)
        q_mem = cls._apply_model_filter(q_mem, IncidentMemory.model_id, model_id)
        learned = q_mem.count()
        
        # Deployed
        q_dep = db.query(Deployment).filter(Deployment.status.in_(["DEPLOYED", "VERIFYING", "HEALTHY", "DEGRADED", "FAILED"]))
        q_dep = cls._apply_time_filter(q_dep, Deployment.created_at, time_range_days)
        if model_id:
            q_dep = q_dep.join(Incident).filter(Incident.model_id == model_id)
        deployed = q_dep.count()
        
        # Verified healthy
        q_health = db.query(Deployment).filter(Deployment.status == "HEALTHY")
        q_health = cls._apply_time_filter(q_health, Deployment.created_at, time_range_days)
        if model_id:
            q_health = q_health.join(Incident).filter(Incident.model_id == model_id)
        verified_healthy = q_health.count()
        
        full_loop_completion = (verified_healthy / total_detected * 100) if total_detected > 0 else 0
        
        return {
            "patch_validation_success_rate": (validated / investigated * 100) if investigated > 0 else 0,
            "deployment_health_success_rate": (verified_healthy / deployed * 100) if deployed > 0 else 0,
            "full_loop_completion_rate": full_loop_completion,
            "funnel": {
                "detected": total_detected,
                "investigated": investigated,
                "validated": validated,
                "learned": learned,
                "deployed": deployed,
                "verified_healthy": verified_healthy
            }
        }

    @classmethod
    def get_policy_metrics(cls, db: Session, time_range_days: Optional[int] = None) -> Dict[str, Any]:
        q_eval = db.query(PolicyEvaluation)
        q_eval = cls._apply_time_filter(q_eval, PolicyEvaluation.evaluated_at, time_range_days)
        
        total = q_eval.count()
        allowed = q_eval.filter(PolicyEvaluation.result == "ALLOW").count()
        blocked = q_eval.filter(PolicyEvaluation.result == "BLOCK").count()
        review_required = q_eval.filter(PolicyEvaluation.result == "REVIEW_REQUIRED").count()
        
        # Breakdown by target type
        target_dist = db.query(PolicyEvaluation.target_type, func.count(PolicyEvaluation.id)).group_by(PolicyEvaluation.target_type).all()
        
        return {
            "total_evaluations": total,
            "allowed": allowed,
            "blocked": blocked,
            "review_required": review_required,
            "target_distribution": [{"name": s[0], "value": s[1]} for s in target_dist]
        }

    @classmethod
    def get_slo_analytics(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        from app.models.slo import ReliabilityObjective, SLOEvaluation, Alert
        
        # Objectives
        q_obj = db.query(ReliabilityObjective).filter(ReliabilityObjective.enabled == True)
        if model_id:
            q_obj = q_obj.filter(ReliabilityObjective.model_id == model_id)
        total_objectives = q_obj.count()
        
        # Evaluations (latest per objective)
        # For simplicity, we just aggregate all recent evaluations
        q_eval = db.query(SLOEvaluation)
        q_eval = cls._apply_time_filter(q_eval, SLOEvaluation.evaluated_at, time_range_days)
        if model_id:
            q_eval = q_eval.filter(SLOEvaluation.model_id == model_id)
            
        total_evals = q_eval.count()
        breached_evals = q_eval.filter(SLOEvaluation.status == "BREACHED").count()
        slo_compliance_rate = ((total_evals - breached_evals) / total_evals * 100) if total_evals > 0 else 100.0
        
        avg_budget_remaining = db.query(func.avg(SLOEvaluation.error_budget_remaining)).filter(
            SLOEvaluation.error_budget_remaining.isnot(None)
        )
        if model_id:
            avg_budget_remaining = avg_budget_remaining.filter(SLOEvaluation.model_id == model_id)
        avg_budget_remaining = avg_budget_remaining.scalar() or 0.0
        
        exhausted_budgets = q_eval.filter(SLOEvaluation.error_budget_remaining <= 0).count()
        
        # Alerts
        q_alert = db.query(Alert)
        q_alert = cls._apply_time_filter(q_alert, Alert.triggered_at, time_range_days)
        if model_id:
            q_alert = q_alert.filter(Alert.model_id == model_id)
            
        total_alerts = q_alert.count()
        active_alerts = q_alert.filter(Alert.status == "OPEN").count()
        
        alerts_with_incident = q_alert.filter(Alert.incident_id.isnot(None)).count()
        alert_to_incident_conversion = (alerts_with_incident / total_alerts * 100) if total_alerts > 0 else 0.0
        
        resolved_alerts = q_alert.filter(Alert.resolved_at.isnot(None), Alert.triggered_at.isnot(None)).all()
        mttr_list = [(a.resolved_at - a.triggered_at).total_seconds() for a in resolved_alerts]
        alert_mttr_minutes = (sum(mttr_list) / len(mttr_list) / 60.0) if mttr_list else None
        
        ack_alerts = q_alert.filter(Alert.acknowledged_at.isnot(None), Alert.triggered_at.isnot(None)).all()
        mtta_list = [(a.acknowledged_at - a.triggered_at).total_seconds() for a in ack_alerts]
        alert_mtta_minutes = (sum(mtta_list) / len(mtta_list) / 60.0) if mtta_list else None
        
        return {
            "total_objectives": total_objectives,
            "slo_compliance_rate": slo_compliance_rate,
            "exhausted_budgets": exhausted_budgets,
            "average_remaining_budget": avg_budget_remaining,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "alert_to_incident_conversion_rate": alert_to_incident_conversion,
            "alert_mtta_minutes": alert_mtta_minutes,
            "alert_mttr_minutes": alert_mttr_minutes
        }
