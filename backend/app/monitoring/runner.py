import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os

from app.models.model import ModelVersion
from app.models.monitoring import (
    MonitoringRun, MetricResult, FeatureMonitoringResult,
    DataQualityResult, PredictionMonitoringResult, SegmentAnalysisResult
)
from app.monitoring.metrics import calculate_classification_metrics
from app.monitoring.drift import calculate_feature_drift
from app.monitoring.data_quality import calculate_data_quality
from app.monitoring.predictions import calculate_prediction_drift
from app.monitoring.segmentation import analyze_segments
from app.monitoring.thresholds import (
    evaluate_metric_status, evaluate_drift_status,
    evaluate_data_quality_status, evaluate_segment_status, get_overall_health
)

def run_monitoring_job(
    db: Session,
    model_id: str,
    model_version_id: str,
    baseline_path: str,
    current_path: str,
    target_col: str,
    pred_col: str,
    prob_col: str = None,
    feature_cols: list = None,
    segments: list = None
) -> MonitoringRun:
    """Execute a full monitoring run synchronously and persist to DB."""
    run = MonitoringRun(
        model_id=model_id,
        model_version_id=model_version_id,
        run_type='batch',
        status='running',
        started_at=datetime.now(timezone.utc)
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # 1. Load Data
        if not os.path.exists(baseline_path) or not os.path.exists(current_path):
            raise FileNotFoundError("Dataset path not found.")
            
        b_df = pd.read_csv(baseline_path)
        c_df = pd.read_csv(current_path)

        if feature_cols is None:
            # Auto-infer features (excluding targets)
            exclude = {target_col, pred_col, prob_col}
            feature_cols = [c for c in c_df.columns if c not in exclude]

        all_statuses = []

        # 2. Performance Metrics
        metrics = calculate_classification_metrics(c_df, target_col, pred_col, prob_col)
        for m_name, m_val in metrics.items():
            status = evaluate_metric_status(m_name, m_val)
            all_statuses.append(status)
            db.add(MetricResult(
                monitoring_run_id=run.id,
                metric_name=m_name,
                metric_value=m_val,
                metric_type='performance',
                status=status
            ))

        # 3. Data Quality
        dq = calculate_data_quality(c_df, feature_cols)
        for dq_name, dq_val in dq.items():
            if dq_name == 'row_count':
                status = 'healthy' # Just informational
            else:
                status = evaluate_data_quality_status(dq_name, dq_val)
                all_statuses.append(status)
                
            db.add(DataQualityResult(
                monitoring_run_id=run.id,
                metric_name=dq_name,
                value=dq_val,
                status=status
            ))

        # 4. Feature Drift
        f_drift = calculate_feature_drift(b_df, c_df, feature_cols)
        for f in f_drift:
            status = evaluate_drift_status(f['drift_method'], f['drift_score'])
            all_statuses.append(status)
            db.add(FeatureMonitoringResult(
                monitoring_run_id=run.id,
                feature_name=f['feature_name'],
                feature_type=f['feature_type'],
                drift_method=f['drift_method'],
                drift_score=f['drift_score'],
                baseline_summary=f['baseline_summary'],
                current_summary=f['current_summary'],
                status=status
            ))

        # 5. Prediction Drift
        p_drift = calculate_prediction_drift(b_df, c_df, pred_col, prob_col)
        for p in p_drift:
            status = evaluate_drift_status('PSI', p['value'])
            all_statuses.append(status)
            db.add(PredictionMonitoringResult(
                monitoring_run_id=run.id,
                prediction_metric=p['prediction_metric'],
                value=p['value'],
                baseline_value=p['baseline_value'],
                status=status
            ))

        # 6. Segment Analysis
        if segments:
            s_res = analyze_segments(b_df, c_df, target_col, pred_col, segments)
            for s in s_res:
                status = evaluate_segment_status(s['change'])
                all_statuses.append(status)
                db.add(SegmentAnalysisResult(
                    monitoring_run_id=run.id,
                    segment_name=s['segment_name'],
                    sample_count=s['sample_count'],
                    primary_metric=s['primary_metric'],
                    baseline_metric_value=s['baseline_metric_value'],
                    current_metric_value=s['current_metric_value'],
                    change=s['change'],
                    status=status
                ))

        run.status = 'completed'
        run.health_summary = get_overall_health(all_statuses)

    except Exception as e:
        run.status = 'failed'
        run.health_summary = 'critical'
        # Would log `e` here in a real app

    run.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run
