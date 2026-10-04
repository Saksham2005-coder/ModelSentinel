import os
import pandas as pd
import pytest
from app.monitoring.metrics import calculate_classification_metrics
from app.monitoring.drift import calculate_feature_drift
from app.monitoring.data_quality import calculate_data_quality
from app.monitoring.predictions import calculate_prediction_drift

@pytest.fixture
def mock_dfs():
    b_df = pd.DataFrame({
        'target': [1, 0, 1, 0, 1],
        'prediction': [1, 0, 1, 0, 0],
        'probability': [0.9, 0.1, 0.8, 0.2, 0.4],
        'num_feature': [1.0, 2.0, 1.5, 2.5, 1.1],
        'cat_feature': ['A', 'B', 'A', 'B', 'A']
    })
    
    c_df = pd.DataFrame({
        'target': [1, 0, 1, 0, 1],
        'prediction': [0, 0, 1, 0, 0],
        'probability': [0.4, 0.2, 0.6, 0.3, 0.4],
        'num_feature': [5.0, 6.0, 5.5, 6.5, 5.1], # drifted
        'cat_feature': ['B', 'B', 'A', 'B', 'B'] # drifted
    })
    return b_df, c_df

def test_metrics(mock_dfs):
    _, c_df = mock_dfs
    metrics = calculate_classification_metrics(c_df, 'target', 'prediction', 'probability')
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1_score' in metrics
    assert 'roc_auc' in metrics

def test_feature_drift(mock_dfs):
    b_df, c_df = mock_dfs
    drifts = calculate_feature_drift(b_df, c_df, ['num_feature', 'cat_feature'])
    
    num_d = next(d for d in drifts if d['feature_name'] == 'num_feature')
    cat_d = next(d for d in drifts if d['feature_name'] == 'cat_feature')
    
    assert num_d['drift_method'] == 'KS'
    assert num_d['drift_score'] > 0.5 # Huge drift
    
    assert cat_d['drift_method'] == 'PSI'
    assert cat_d['drift_score'] > 0 # Some drift

def test_data_quality(mock_dfs):
    _, c_df = mock_dfs
    dq = calculate_data_quality(c_df, ['num_feature', 'cat_feature'])
    assert dq['row_count'] == 5
    assert dq['missing_value_percentage'] == 0.0
    assert dq['duplicate_percentage'] == 0.0

def test_prediction_drift(mock_dfs):
    b_df, c_df = mock_dfs
    drifts = calculate_prediction_drift(b_df, c_df, 'prediction', 'probability')
    class_drift = next(d for d in drifts if d['prediction_metric'] == 'class_drift_psi')
    prob_drift = next(d for d in drifts if d['prediction_metric'] == 'probability_drift_psi')
    assert class_drift['value'] > 0
    assert prob_drift['value'] > 0
