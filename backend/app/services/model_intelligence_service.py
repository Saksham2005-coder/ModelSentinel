from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from app.models.model import Model, ModelVersion
from app.models.monitoring import MonitoringRun, MetricResult, DataQualityResult, FeatureMonitoringResult, PredictionMonitoringResult, SegmentAnalysisResult
from app.models.incident import Incident
from app.models.deployment import Deployment
from app.models.deployment_verification import DeploymentVerification

class ModelIntelligenceService:
    
    def _calculate_health_for_run(self, db: Session, model_id: str, run: Optional[MonitoringRun], timestamp: datetime) -> Dict[str, Any]:
        base_scores = {
            "performance": 35,
            "data_quality": 20,
            "feature_drift": 20,
            "prediction_stability": 10,
            "incident_state": 15
        }
        
        scores = base_scores.copy()
        
        if run:
            # Performance
            metrics = db.query(MetricResult).filter(MetricResult.monitoring_run_id == run.id).all()
            for m in metrics:
                if m.status == "critical":
                    scores["performance"] = max(0, scores["performance"] - 10)
                elif m.status == "warning":
                    scores["performance"] = max(0, scores["performance"] - 5)
            
            # Data Quality
            dq_results = db.query(DataQualityResult).filter(DataQualityResult.monitoring_run_id == run.id).all()
            for dq in dq_results:
                if dq.status == "critical":
                    scores["data_quality"] = max(0, scores["data_quality"] - 10)
                elif dq.status == "warning":
                    scores["data_quality"] = max(0, scores["data_quality"] - 5)
                    
            # Feature Drift
            features = db.query(FeatureMonitoringResult).filter(FeatureMonitoringResult.monitoring_run_id == run.id).all()
            for f in features:
                if f.status == "critical":
                    scores["feature_drift"] = max(0, scores["feature_drift"] - 5)
                elif f.status == "warning":
                    scores["feature_drift"] = max(0, scores["feature_drift"] - 2)
                    
            # Prediction Stability
            preds = db.query(PredictionMonitoringResult).filter(PredictionMonitoringResult.monitoring_run_id == run.id).all()
            for p in preds:
                if p.status == "critical":
                    scores["prediction_stability"] = max(0, scores["prediction_stability"] - 5)
                elif p.status == "warning":
                    scores["prediction_stability"] = max(0, scores["prediction_stability"] - 2)
                    
        # Evaluate Incident State at the given timestamp
        # Incidents created before/at timestamp, and either not resolved OR resolved after timestamp
        active_incidents = db.query(Incident).filter(
            Incident.model_id == model_id,
            Incident.created_at <= timestamp,
            (Incident.status != "resolved") | (Incident.updated_at > timestamp)
        ).all()
        
        if active_incidents:
            highest_sev = "low"
            for inc in active_incidents:
                if inc.severity == "critical":
                    highest_sev = "critical"
                    break
                elif inc.severity == "high" and highest_sev not in ["critical"]:
                    highest_sev = "high"
                elif inc.severity == "medium" and highest_sev not in ["critical", "high"]:
                    highest_sev = "medium"
                    
            if highest_sev in ["critical", "high"]:
                scores["incident_state"] = 0
            elif highest_sev == "medium":
                scores["incident_state"] = 5
            else:
                scores["incident_state"] = 10
                
        # Total
        total_score = sum(scores.values())
        
        # Determine Status
        status = "HEALTHY"
        if total_score < 50:
            status = "CRITICAL"
        elif total_score < 75:
            status = "DEGRADED"
        elif total_score < 90:
            status = "STABLE"
            
        return {
            "score": total_score,
            "status": status,
            "breakdown": scores
        }

    def calculate_model_health(self, db: Session, model_id: str) -> Dict[str, Any]:
        """
        Calculates a deterministic model health score (0-100) based on latest run.
        """
        latest_run = db.query(MonitoringRun).filter(
            MonitoringRun.model_id == model_id,
            MonitoringRun.status == "completed"
        ).order_by(desc(MonitoringRun.completed_at)).first()
        
        now = datetime.now(timezone.utc)
        return self._calculate_health_for_run(db, model_id, latest_run, now)

    def get_model_health_history(self, db: Session, model_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generates a time-series history of model health.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        runs = db.query(MonitoringRun).filter(
            MonitoringRun.model_id == model_id,
            MonitoringRun.status == "completed",
            MonitoringRun.completed_at >= cutoff_date
        ).order_by(MonitoringRun.completed_at.asc()).all()

        history = []
        for run in runs:
            if not run.completed_at:
                continue
            health = self._calculate_health_for_run(db, model_id, run, run.completed_at)
            
            # Find any incidents created near this run (within 12h)
            incidents_near = db.query(Incident).filter(
                Incident.model_id == model_id,
                Incident.created_at >= run.completed_at - timedelta(hours=12),
                Incident.created_at <= run.completed_at + timedelta(hours=12)
            ).count()

            # Find deployments near this run
            deployments_near = db.query(Deployment).join(Incident).filter(
                Incident.model_id == model_id,
                Deployment.deployed_at >= run.completed_at - timedelta(hours=12),
                Deployment.deployed_at <= run.completed_at + timedelta(hours=12)
            ).count()
            
            history.append({
                "timestamp": run.completed_at.isoformat(),
                "score": health["score"],
                "status": health["status"],
                "incidents_created": incidents_near,
                "deployments": deployments_near
            })

        return history
        
    def get_version_comparison(self, db: Session, model_id: str, version_a_id: str, version_b_id: str) -> Dict[str, Any]:
        """Compares two model versions based on their latest monitoring runs and lifecycle records."""
        def get_version_stats(version_id):
            latest_run = db.query(MonitoringRun).filter(
                MonitoringRun.model_version_id == version_id,
                MonitoringRun.status == "completed"
            ).order_by(desc(MonitoringRun.completed_at)).first()
            
            stats = {
                "metrics": {},
                "feature_drift_avg": 0.0,
                "incidents": 0,
                "post_deployment": "N/A"
            }
            
            if latest_run:
                metrics = db.query(MetricResult).filter(MetricResult.monitoring_run_id == latest_run.id).all()
                for m in metrics:
                    stats["metrics"][m.metric_name] = m.metric_value
                    
                features = db.query(FeatureMonitoringResult).filter(FeatureMonitoringResult.monitoring_run_id == latest_run.id).all()
                if features:
                    stats["feature_drift_avg"] = sum(f.drift_score for f in features) / len(features)
                    
            stats["incidents"] = db.query(Incident).filter(Incident.model_version_id == version_id).count()
            
            deployment = db.query(Deployment).join(Incident).filter(Incident.model_version_id == version_id).order_by(desc(Deployment.created_at)).first()
            if deployment:
                verif = db.query(DeploymentVerification).filter(DeploymentVerification.deployment_id == deployment.id).order_by(desc(DeploymentVerification.created_at)).first()
                if verif:
                    stats["post_deployment"] = "HEALTHY" if verif.status == "success" else "DEGRADED"
                    
            return stats

        stats_a = get_version_stats(version_a_id)
        stats_b = get_version_stats(version_b_id)
        
        comparisons = []
        
        # Compare metrics
        all_metrics = set(stats_a["metrics"].keys()).union(set(stats_b["metrics"].keys()))
        for m in all_metrics:
            val_a = stats_a["metrics"].get(m)
            val_b = stats_b["metrics"].get(m)
            diff = None
            is_regression = False
            if val_a is not None and val_b is not None:
                diff = val_b - val_a
                # Simplified regression logic: assuming higher is better for standard metrics (e.g., accuracy)
                # In reality, this depends on metric. We'll mark negative diff as regression for now
                if diff < -0.05: # > 5% drop
                    is_regression = True
                    
            comparisons.append({
                "metric": m,
                "type": "performance",
                "version_a": val_a,
                "version_b": val_b,
                "difference": diff,
                "is_regression": is_regression
            })
            
        # Compare Feature Drift
        diff_drift = stats_b["feature_drift_avg"] - stats_a["feature_drift_avg"]
        comparisons.append({
            "metric": "Average Feature Drift",
            "type": "drift",
            "version_a": stats_a["feature_drift_avg"],
            "version_b": stats_b["feature_drift_avg"],
            "difference": diff_drift,
            "is_regression": diff_drift > 0.1 # higher drift is worse
        })
        
        # Compare Incidents
        comparisons.append({
            "metric": "Incident Count",
            "type": "reliability",
            "version_a": stats_a["incidents"],
            "version_b": stats_b["incidents"],
            "difference": stats_b["incidents"] - stats_a["incidents"],
            "is_regression": stats_b["incidents"] > stats_a["incidents"]
        })
        
        # Post Deployment
        comparisons.append({
            "metric": "Post Deployment Verification",
            "type": "reliability",
            "version_a": stats_a["post_deployment"],
            "version_b": stats_b["post_deployment"],
            "difference": None,
            "is_regression": stats_a["post_deployment"] == "HEALTHY" and stats_b["post_deployment"] == "DEGRADED"
        })
        
        return {
            "version_a_id": version_a_id,
            "version_b_id": version_b_id,
            "comparisons": comparisons
        }
        
    def get_feature_health(self, db: Session, model_id: str) -> List[Dict[str, Any]]:
        """Calculates feature health using the latest monitoring run."""
        latest_run = db.query(MonitoringRun).filter(
            MonitoringRun.model_id == model_id,
            MonitoringRun.status == "completed"
        ).order_by(desc(MonitoringRun.completed_at)).first()
        
        if not latest_run:
            return []
            
        features = db.query(FeatureMonitoringResult).filter(FeatureMonitoringResult.monitoring_run_id == latest_run.id).all()
        result = []
        for f in features:
            # Check past runs to determine trend
            past_runs_query = db.query(MonitoringRun).filter(
                MonitoringRun.model_id == model_id,
                MonitoringRun.status == "completed"
            )
            if latest_run.completed_at:
                past_runs_query = past_runs_query.filter(MonitoringRun.completed_at < latest_run.completed_at)
            else:
                past_runs_query = past_runs_query.filter(MonitoringRun.created_at < latest_run.created_at)
                
            past_runs = past_runs_query.order_by(desc(MonitoringRun.created_at)).limit(3).all()
            
            trend = "stable"
            if past_runs:
                past_run_ids = [r.id for r in past_runs]
                past_feats = db.query(FeatureMonitoringResult).filter(
                    FeatureMonitoringResult.monitoring_run_id.in_(past_run_ids),
                    FeatureMonitoringResult.feature_name == f.feature_name
                ).all()
                if past_feats:
                    avg_past_drift = sum(pf.drift_score for pf in past_feats) / len(past_feats)
                    if f.drift_score > avg_past_drift + 0.05:
                        trend = "increasing"
                    elif f.drift_score < avg_past_drift - 0.05:
                        trend = "decreasing"
                        
            # Number of incidents (approximate matching by title/category or metadata)
            # We'll do a simple text match for the demo
            inc_count = db.query(Incident).filter(
                Incident.model_id == model_id,
                Incident.title.ilike(f"%{f.feature_name}%")
            ).count()
            
            result.append({
                "feature_name": f.feature_name,
                "feature_type": f.feature_type,
                "drift_score": f.drift_score,
                "status": f.status,
                "trend": trend,
                "incident_count": inc_count
            })
            
        return result

    def get_segment_health(self, db: Session, model_id: str) -> List[Dict[str, Any]]:
        """Calculates segment health using the latest monitoring run."""
        latest_run = db.query(MonitoringRun).filter(
            MonitoringRun.model_id == model_id,
            MonitoringRun.status == "completed"
        ).order_by(desc(MonitoringRun.completed_at)).first()
        
        if not latest_run:
            return []
            
        segments = db.query(SegmentAnalysisResult).filter(SegmentAnalysisResult.monitoring_run_id == latest_run.id).all()
        result = []
        for s in segments:
            result.append({
                "segment_name": s.segment_name,
                "primary_metric": s.primary_metric,
                "baseline_metric_value": s.baseline_metric_value,
                "current_metric_value": s.current_metric_value,
                "change": s.change,
                "status": s.status
            })
            
        # Sort by worst performing (e.g. status='critical' first, or largest negative change)
        result.sort(key=lambda x: (x["status"] == "critical", x["status"] == "warning", -abs(x["change"] or 0)), reverse=True)
        return result

model_intelligence_service = ModelIntelligenceService()
