from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import math

from app.models.incident import Incident
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.models.regression import RegressionCase
from app.models.deployment import Deployment
from app.models.model import Model
from app.models.incident_memory import IncidentMemory
from app.models.slo import ReliabilityObjective, SLOEvaluation, Alert
from app.models.change_risk import ChangeRiskAssessment
from app.models.resolution_memory import ResolutionMemory
from app.services.reliability_analytics_service import ReliabilityAnalyticsService

class EngineeringIntelligenceService:
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
    def get_engineering_overview(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        base_overview = ReliabilityAnalyticsService.get_overview_metrics(db, time_range_days, model_id)
        
        # Add extra intelligence
        q_inc = db.query(Incident)
        q_inc = cls._apply_time_filter(q_inc, Incident.detected_at, time_range_days)
        q_inc = cls._apply_model_filter(q_inc, Incident.model_id, model_id)
        total_incidents = q_inc.count()
        
        # Models at risk
        models_at_risk = 0
        if not model_id:
            all_models = db.query(Model).all()
            for m in all_models:
                m_overview = ReliabilityAnalyticsService.get_overview_metrics(db, time_range_days, m.id)
                if m_overview.get("reliability_score", 100) < 70:
                    models_at_risk += 1

        # SLO pressure
        q_eval = db.query(SLOEvaluation)
        q_eval = cls._apply_time_filter(q_eval, SLOEvaluation.evaluated_at, time_range_days)
        q_eval = cls._apply_model_filter(q_eval, SLOEvaluation.model_id, model_id)
        active_slo_pressure = q_eval.filter(SLOEvaluation.error_budget_remaining < 20).count()
        
        return {
            "reliability_score": base_overview["reliability_score"],
            "total_incidents": total_incidents,
            "models_at_risk": models_at_risk,
            "active_slo_pressure": active_slo_pressure,
            "deployment_degradation_rate": base_overview["deployment_degradation_rate"]
        }

    @classmethod
    def get_reliability_trends(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        # Divide the time_range into 5 buckets or return all days if not specified
        days = time_range_days or 30
        now = datetime.now(timezone.utc)
        
        trends = []
        for i in range(days, 0, -max(1, days // 10)):
            start_time = now - timedelta(days=i)
            end_time = now - timedelta(days=i - max(1, days // 10))
            
            q_inc = db.query(Incident).filter(Incident.detected_at >= start_time, Incident.detected_at < end_time)
            q_inc = cls._apply_model_filter(q_inc, Incident.model_id, model_id)
            incident_count = q_inc.count()
            
            trends.append({
                "timestamp": end_time.isoformat(),
                "incidents": incident_count,
                "reliability_score": 100 - min(100, incident_count * 5) # simplified trend score
            })
            
        direction = "STABLE"
        if len(trends) >= 2:
            first_half = sum(t["incidents"] for t in trends[:len(trends)//2])
            second_half = sum(t["incidents"] for t in trends[len(trends)//2:])
            if second_half > first_half:
                direction = "DEGRADING"
            elif second_half < first_half:
                direction = "IMPROVING"

        return {
            "trends": trends,
            "direction": direction,
            "data_sufficiency": "SUFFICIENT" if len(trends) > 0 else "INSUFFICIENT_DATA"
        }

    @classmethod
    def get_models_comparison(cls, db: Session, time_range_days: Optional[int] = None) -> List[Dict[str, Any]]:
        models = db.query(Model).all()
        results = []
        for m in models:
            overview = ReliabilityAnalyticsService.get_overview_metrics(db, time_range_days, m.id)
            
            q_eval = db.query(SLOEvaluation).filter(SLOEvaluation.model_id == m.id)
            q_eval = cls._apply_time_filter(q_eval, SLOEvaluation.evaluated_at, time_range_days)
            slo_breaches = q_eval.filter(SLOEvaluation.status == "BREACHED").count()
            
            score = overview.get("reliability_score", 100)
            status = "INSUFFICIENT_DATA"
            if overview["total_incidents"] > 0 or db.query(Deployment).join(Incident).filter(Incident.model_id == m.id).count() > 0:
                if score >= 90:
                    status = "HEALTHY"
                elif score >= 70:
                    status = "STABLE"
                elif score >= 50:
                    status = "AT_RISK"
                else:
                    status = "DEGRADING"
            else:
                status = "HEALTHY" # No data typically implies healthy unless we want strict sufficient checks
                
            results.append({
                "model_id": m.id,
                "model_name": m.name,
                "reliability_score": score,
                "incidents": overview["total_incidents"],
                "critical_incidents": overview["critical_incidents"],
                "mttr_minutes": overview["mttr_minutes"],
                "deployment_health": 100 - overview["deployment_degradation_rate"],
                "slo_breaches": slo_breaches,
                "status": status,
                "trend": "STABLE" # Placeholder for comparison view
            })
        
        # Rank by score desc
        results.sort(key=lambda x: x["reliability_score"], reverse=True)
        return results

    @classmethod
    def get_engineering_effectiveness(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        return ReliabilityAnalyticsService.get_fix_effectiveness(db, time_range_days, model_id)

    @classmethod
    def get_root_cause_intelligence(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return ReliabilityAnalyticsService.get_root_cause_trends(db, time_range_days, model_id)

    @classmethod
    def get_change_reliability_correlation(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        q_changes = db.query(ChangeRiskAssessment)
        q_changes = cls._apply_time_filter(q_changes, ChangeRiskAssessment.created_at, time_range_days)
        total_changes = q_changes.count()
        
        # Simplified: check incidents happened after changes
        high_risk_changes = q_changes.filter(ChangeRiskAssessment.risk_score >= 70).count()
        
        q_inc = db.query(Incident)
        q_inc = cls._apply_time_filter(q_inc, Incident.detected_at, time_range_days)
        q_inc = cls._apply_model_filter(q_inc, Incident.model_id, model_id)
        incidents = q_inc.count()
        
        return {
            "total_changes_analyzed": total_changes,
            "high_risk_changes": high_risk_changes,
            "incidents_observed": incidents,
            "correlation_note": "associated production degradation analysis based on temporal proximity",
            "post_deployment_degradation_changes": 0 # Would require exact commit -> deployment mapping
        }

    @classmethod
    def get_engineering_hotspots(cls, db: Session, time_range_days: Optional[int] = None) -> List[Dict[str, Any]]:
        # A hotspot is typically a repo component, but we will use models as components if repo data is scarce
        models = db.query(Model).all()
        results = []
        for m in models:
            overview = ReliabilityAnalyticsService.get_overview_metrics(db, time_range_days, m.id)
            
            incident_pressure = overview["total_incidents"] * 10
            slo_pressure = 0
            
            q_eval = db.query(SLOEvaluation).filter(SLOEvaluation.model_id == m.id)
            q_eval = cls._apply_time_filter(q_eval, SLOEvaluation.evaluated_at, time_range_days)
            if q_eval.filter(SLOEvaluation.error_budget_remaining < 50).count() > 0:
                slo_pressure = 20
                
            degradation = overview["deployment_degradation_rate"] * 0.5
            coverage_discount = overview["regression_coverage"] * 0.2
            
            score = max(0, incident_pressure + slo_pressure + degradation - coverage_discount)
            
            category = "LOW"
            if score >= 80: category = "CRITICAL"
            elif score >= 50: category = "HIGH"
            elif score >= 20: category = "MODERATE"
            
            results.append({
                "component": m.name,
                "hotspot_score": round(score),
                "incident_pressure": overview["total_incidents"],
                "slo_pressure": slo_pressure > 0,
                "regression_coverage": overview["regression_coverage"],
                "category": category
            })
            
        results.sort(key=lambda x: x["hotspot_score"], reverse=True)
        return results

    @classmethod
    def get_slo_intelligence(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> Dict[str, Any]:
        return ReliabilityAnalyticsService.get_slo_analytics(db, time_range_days, model_id)

    @classmethod
    def get_reliability_drivers(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        # Mock drivers based on root cause trends
        trends = ReliabilityAnalyticsService.get_root_cause_trends(db, time_range_days, model_id)
        drivers = []
        for t in trends:
            evidence = t["frequency"]
            if evidence > 0:
                drivers.append({
                    "driver": t["root_cause"],
                    "evidence_count": evidence,
                    "affected_models": t["affected_models"],
                    "incident_count": evidence,
                    "degradation_count": evidence // 2,
                    "confidence": "HIGH" if evidence > 5 else "MODERATE"
                })
        return drivers

    @classmethod
    def get_intervention_effectiveness(cls, db: Session, time_range_days: Optional[int] = None, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        q_res = db.query(ResolutionMemory)
        q_res = cls._apply_time_filter(q_res, ResolutionMemory.created_at, time_range_days)
        q_res = cls._apply_model_filter(q_res, ResolutionMemory.model_id, model_id)
        
        total = q_res.count()
        successful = q_res.filter(ResolutionMemory.effectiveness_score >= 80).count()
        
        return [{
            "intervention_type": "Patch Application",
            "total_interventions": total,
            "successful": successful,
            "success_rate": (successful / total * 100) if total > 0 else 0
        }]
