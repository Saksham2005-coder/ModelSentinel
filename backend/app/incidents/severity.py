from typing import List, Dict, Any

def calculate_incident_severity(signals: List[Dict[str, Any]]) -> str:
    """
    CRITICAL:
    - at least one critical performance signal
    OR
    - multiple independent critical signals
    OR
    - critical data quality failure

    HIGH:
    - major performance degradation (not covered above)
    OR
    - multiple warning signals across categories
    OR
    - severe segment degradation

    MEDIUM:
    - meaningful single warning signal

    LOW:
    - weak warning / informational condition
    """
    critical_signals = [s for s in signals if s['status'] == 'critical']
    warning_signals = [s for s in signals if s['status'] == 'warning']

    critical_performance = any(s for s in critical_signals if s['source_type'] == 'metric')
    critical_data_quality = any(s for s in critical_signals if s['source_type'] == 'data_quality')
    
    if critical_performance or critical_data_quality or len(critical_signals) > 1:
        return 'critical'
        
    if len(critical_signals) == 1:
        # One critical signal that is not performance or DQ (e.g. feature drift)
        return 'high'
        
    # No critical signals, check warnings
    categories_with_warnings = set(s['source_type'] for s in warning_signals)
    
    if len(categories_with_warnings) > 1:
        return 'high'
        
    severe_segment = any(s for s in warning_signals if s['source_type'] == 'segment')
    if severe_segment:
        return 'high'
        
    if len(warning_signals) > 0:
        return 'medium'
        
    return 'low'
