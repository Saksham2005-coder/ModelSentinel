from sqlalchemy.orm import Session
from app.models.monitoring import (
    MonitoringRun, MetricResult, FeatureMonitoringResult,
    DataQualityResult, PredictionMonitoringResult, SegmentAnalysisResult
)
from app.investigation.tool_registry import registry

@registry.register(
    name="get_monitoring_run",
    description="Get basic details of a monitoring run.",
    parameters_schema={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"}
        },
        "required": ["run_id"]
    }
)
def get_monitoring_run(run_id: str, db: Session) -> dict:
    run = db.query(MonitoringRun).filter(MonitoringRun.id == run_id).first()
    if not run:
        return {"error": f"Monitoring run {run_id} not found."}
    return {
        "id": run.id,
        "model_id": run.model_id,
        "model_version_id": run.model_version_id,
        "status": run.status,
        "health_summary": run.health_summary,
        "started_at": run.started_at.isoformat() if run.started_at else None
    }

@registry.register(
    name="get_performance_metrics",
    description="Get model performance metrics (like F1 score, accuracy) for a monitoring run.",
    parameters_schema={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"}
        },
        "required": ["run_id"]
    }
)
def get_performance_metrics(run_id: str, db: Session) -> dict:
    metrics = db.query(MetricResult).filter(MetricResult.monitoring_run_id == run_id).all()
    return {
        "metrics": [
            {
                "name": m.metric_name,
                "value": m.metric_value,
                "status": m.status
            } for m in metrics
        ]
    }

@registry.register(
    name="get_feature_drift",
    description="Get feature drift analysis for a monitoring run.",
    parameters_schema={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"}
        },
        "required": ["run_id"]
    }
)
def get_feature_drift(run_id: str, db: Session) -> dict:
    drift = db.query(FeatureMonitoringResult).filter(FeatureMonitoringResult.monitoring_run_id == run_id).all()
    return {
        "feature_drift": [
            {
                "feature": d.feature_name,
                "method": d.drift_method,
                "score": d.drift_score,
                "status": d.status
            } for d in drift
        ]
    }

@registry.register(
    name="get_prediction_drift",
    description="Get prediction drift analysis for a monitoring run.",
    parameters_schema={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"}
        },
        "required": ["run_id"]
    }
)
def get_prediction_drift(run_id: str, db: Session) -> dict:
    drift = db.query(PredictionMonitoringResult).filter(PredictionMonitoringResult.monitoring_run_id == run_id).all()
    return {
        "prediction_drift": [
            {
                "metric": d.prediction_metric,
                "value": d.value,
                "status": d.status
            } for d in drift
        ]
    }

@registry.register(
    name="get_data_quality",
    description="Get data quality metrics (like missing values) for a monitoring run.",
    parameters_schema={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"}
        },
        "required": ["run_id"]
    }
)
def get_data_quality(run_id: str, db: Session) -> dict:
    quality = db.query(DataQualityResult).filter(DataQualityResult.monitoring_run_id == run_id).all()
    return {
        "data_quality": [
            {
                "metric": q.metric_name,
                "value": q.value,
                "status": q.status
            } for q in quality
        ]
    }

@registry.register(
    name="get_segment_analysis",
    description="Get performance change analysis across data segments.",
    parameters_schema={
        "type": "object",
        "properties": {
            "run_id": {"type": "string"}
        },
        "required": ["run_id"]
    }
)
def get_segment_analysis(run_id: str, db: Session) -> dict:
    segments = db.query(SegmentAnalysisResult).filter(SegmentAnalysisResult.monitoring_run_id == run_id).all()
    return {
        "segments": [
            {
                "segment": s.segment_name,
                "change": s.change,
                "status": s.status
            } for s in segments
        ]
    }
