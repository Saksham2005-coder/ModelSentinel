from typing import List, Dict, Any

def generate_incident_fingerprint(model_id: str, model_version_id: str, category: str) -> str:
    """
    Generate a deterministic fingerprint.
    For this phase, a continuing problem on the same model/version in the same category
    (e.g., performance) counts as the same active incident.
    """
    return f"{model_id}_{model_version_id}_{category}"

def determine_primary_category(signals: List[Dict[str, Any]]) -> str:
    """
    If multiple signals exist, determine the primary category.
    Precedence: performance > data_quality > prediction_drift > feature_drift > segment
    """
    types = [s['source_type'] for s in signals]
    
    if 'metric' in types:
        return 'performance'
    if 'data_quality' in types:
        return 'data_quality'
    if 'prediction_drift' in types:
        return 'prediction_drift'
    if 'feature_drift' in types:
        return 'data_drift'
    if 'segment' in types:
        return 'segment_degradation'
    
    return 'other'
    
def generate_incident_title(category: str, severity: str) -> str:
    """Generate a deterministic, factual title."""
    mapping = {
        'performance': 'Performance degradation detected',
        'data_quality': 'Data quality degradation detected',
        'prediction_drift': 'Prediction distribution shift detected',
        'data_drift': 'Feature drift detected',
        'segment_degradation': 'Segment performance degradation detected',
        'other': 'Anomaly detected'
    }
    base = mapping.get(category, 'Anomaly detected')
    if severity == 'critical':
        base = base.replace('detected', 'detected (Critical)')
    return base
