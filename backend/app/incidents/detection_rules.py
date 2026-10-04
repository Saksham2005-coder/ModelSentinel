from app.models.monitoring import MonitoringRun
from typing import List, Dict, Any

def evaluate_performance_signals(run: MonitoringRun) -> List[Dict[str, Any]]:
    signals = []
    for m in run.metrics:
        if m.status in ['critical', 'warning']:
            signals.append({
                'source_type': 'metric',
                'source_id': m.id,
                'signal_name': m.metric_name,
                'observed_value': m.metric_value,
                'threshold': m.threshold,
                'comparison': '<',
                'status': m.status,
                'explanation': f"{m.metric_name} is {m.status} ({m.metric_value})"
            })
    return signals

def evaluate_drift_signals(run: MonitoringRun) -> List[Dict[str, Any]]:
    signals = []
    for f in run.feature_results:
        if f.status in ['critical', 'warning']:
            signals.append({
                'source_type': 'feature_drift',
                'source_id': f.id,
                'signal_name': f.feature_name,
                'observed_value': f.drift_score,
                'threshold': f.threshold,
                'comparison': '>',
                'status': f.status,
                'explanation': f"{f.feature_name} exhibits {f.status} drift ({f.drift_method}: {f.drift_score})"
            })
    return signals

def evaluate_prediction_drift_signals(run: MonitoringRun) -> List[Dict[str, Any]]:
    signals = []
    for p in run.prediction_results:
        if p.status in ['critical', 'warning']:
            signals.append({
                'source_type': 'prediction_drift',
                'source_id': p.id,
                'signal_name': p.prediction_metric,
                'observed_value': p.value,
                'threshold': p.threshold,
                'comparison': '>',
                'status': p.status,
                'explanation': f"{p.prediction_metric} shows {p.status} shift ({p.value})"
            })
    return signals

def evaluate_data_quality_signals(run: MonitoringRun) -> List[Dict[str, Any]]:
    signals = []
    for dq in run.data_quality_results:
        if dq.status in ['critical', 'warning']:
            signals.append({
                'source_type': 'data_quality',
                'source_id': dq.id,
                'signal_name': dq.metric_name,
                'observed_value': dq.value,
                'threshold': dq.threshold,
                'comparison': '>',
                'status': dq.status,
                'explanation': f"{dq.metric_name} is {dq.status} ({dq.value})"
            })
    return signals

def evaluate_segment_signals(run: MonitoringRun) -> List[Dict[str, Any]]:
    signals = []
    for s in run.segment_results:
        if s.status in ['critical', 'warning']:
            signals.append({
                'source_type': 'segment',
                'source_id': s.id,
                'signal_name': s.segment_name,
                'observed_value': s.change,
                'threshold': None,
                'comparison': '<',
                'status': s.status,
                'explanation': f"Segment {s.segment_name} degraded by {s.change}%"
            })
    return signals

def apply_detection_rules(run: MonitoringRun) -> List[Dict[str, Any]]:
    """Evaluates all rules on a MonitoringRun and returns candidate signals."""
    signals = []
    signals.extend(evaluate_performance_signals(run))
    signals.extend(evaluate_drift_signals(run))
    signals.extend(evaluate_prediction_drift_signals(run))
    signals.extend(evaluate_data_quality_signals(run))
    signals.extend(evaluate_segment_signals(run))
    return signals
