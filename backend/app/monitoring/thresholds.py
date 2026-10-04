def evaluate_metric_status(metric_name: str, value: float) -> str:
    """Evaluate performance metrics."""
    if metric_name in ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']:
        if value < 0.70:
            return 'critical'
        elif value < 0.85:
            return 'warning'
        return 'healthy'
    return 'healthy'

def evaluate_drift_status(method: str, score: float) -> str:
    """Evaluate drift score."""
    if method == 'PSI':
        if score > 0.25:
            return 'critical'
        elif score > 0.10:
            return 'warning'
        return 'healthy'
    elif method == 'KS':
        # p-value logic inverted if score is D-statistic
        if score > 0.3:
            return 'critical'
        elif score > 0.15:
            return 'warning'
        return 'healthy'
    return 'healthy'

def evaluate_data_quality_status(metric: str, value: float) -> str:
    if metric == 'missing_value_percentage':
        if value > 10.0:
            return 'critical'
        elif value > 5.0:
            return 'warning'
        return 'healthy'
    if metric == 'duplicate_percentage':
        if value > 5.0:
            return 'critical'
        elif value > 1.0:
            return 'warning'
        return 'healthy'
    return 'healthy'

def evaluate_segment_status(change: float) -> str:
    if change is None:
        return 'healthy'
    if change < -20.0:
        return 'critical'
    if change < -5.0:
        return 'warning'
    return 'healthy'

def get_overall_health(statuses: list) -> str:
    if 'critical' in statuses:
        return 'critical'
    if 'warning' in statuses:
        return 'warning'
    return 'healthy'
