import pandas as pd
from app.monitoring.drift import calculate_psi

def calculate_prediction_drift(baseline_df: pd.DataFrame, current_df: pd.DataFrame, pred_col: str, prob_col: str = None) -> list:
    """Compare prediction distributions between baseline and current."""
    results = []
    
    if pred_col in baseline_df.columns and pred_col in current_df.columns:
        # Class distribution drift via PSI
        b_pred = baseline_df[pred_col].dropna()
        c_pred = current_df[pred_col].dropna()
        
        if len(b_pred) > 0 and len(c_pred) > 0:
            psi_score = calculate_psi(b_pred.values, c_pred.values)
            results.append({
                'prediction_metric': 'class_drift_psi',
                'value': float(psi_score),
                'baseline_value': 0.0 # PSI baseline is effectively 0
            })
            
    if prob_col and prob_col in baseline_df.columns and prob_col in current_df.columns:
        b_prob = baseline_df[prob_col].dropna()
        c_prob = current_df[prob_col].dropna()
        
        if len(b_prob) > 0 and len(c_prob) > 0:
            psi_score = calculate_psi(b_prob.values, c_prob.values)
            results.append({
                'prediction_metric': 'probability_drift_psi',
                'value': float(psi_score),
                'baseline_value': 0.0
            })
            
    return results
