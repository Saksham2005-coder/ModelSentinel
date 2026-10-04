import pytest
from datetime import datetime, timezone
from app.incidents.severity import calculate_incident_severity
from app.incidents.deduplication import determine_primary_category, generate_incident_fingerprint

def test_severity_calculation():
    # Critical performance
    signals = [{'status': 'critical', 'source_type': 'metric'}]
    assert calculate_incident_severity(signals) == 'critical'
    
    # Critical data quality
    signals = [{'status': 'critical', 'source_type': 'data_quality'}]
    assert calculate_incident_severity(signals) == 'critical'
    
    # Single critical non-performance/DQ
    signals = [{'status': 'critical', 'source_type': 'feature_drift'}]
    assert calculate_incident_severity(signals) == 'high'
    
    # Multiple warnings in same category -> medium
    signals = [
        {'status': 'warning', 'source_type': 'feature_drift'},
        {'status': 'warning', 'source_type': 'feature_drift'}
    ]
    assert calculate_incident_severity(signals) == 'medium'
    
    # Multiple warnings in different categories -> high
    signals = [
        {'status': 'warning', 'source_type': 'feature_drift'},
        {'status': 'warning', 'source_type': 'metric'}
    ]
    assert calculate_incident_severity(signals) == 'high'

def test_category_determination():
    signals = [
        {'status': 'warning', 'source_type': 'feature_drift'},
        {'status': 'warning', 'source_type': 'metric'}
    ]
    assert determine_primary_category(signals) == 'performance'

def test_fingerprint():
    fp = generate_incident_fingerprint("model_1", "v_1", "performance")
    assert fp == "model_1_v_1_performance"
