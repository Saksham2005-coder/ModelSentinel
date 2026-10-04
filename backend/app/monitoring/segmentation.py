import pandas as pd
from app.monitoring.metrics import calculate_classification_metrics

def analyze_segments(baseline_df: pd.DataFrame, current_df: pd.DataFrame, target_col: str, pred_col: str, segments: list) -> list:
    """
    segments is a list of dicts: {'name': 'url_heavy', 'condition': "url_count > 5"}
    For this phase, condition will be evaluated dynamically on pandas df using eval.
    """
    results = []
    
    if target_col not in current_df.columns or pred_col not in current_df.columns:
        return results

    for segment in segments:
        name = segment['name']
        condition = segment['condition']
        
        try:
            c_seg = current_df.query(condition)
            b_seg = baseline_df.query(condition) if not baseline_df.empty else pd.DataFrame()
            
            # primary metric we focus on is f1_score for simplicity in segmentation
            c_metrics = calculate_classification_metrics(c_seg, target_col, pred_col)
            b_metrics = calculate_classification_metrics(b_seg, target_col, pred_col) if not b_seg.empty else {}
            
            primary_metric_name = 'f1_score' if 'f1_score' in c_metrics else 'accuracy'
            c_val = c_metrics.get(primary_metric_name, 0.0)
            b_val = b_metrics.get(primary_metric_name, None)
            
            change = None
            if b_val is not None and b_val > 0:
                change = ((c_val - b_val) / b_val) * 100
                
            results.append({
                'segment_name': name,
                'sample_count': float(len(c_seg)),
                'primary_metric': primary_metric_name,
                'baseline_metric_value': float(b_val) if b_val is not None else None,
                'current_metric_value': float(c_val),
                'change': float(change) if change is not None else None
            })
        except Exception:
            # Segment condition invalid or eval failed
            pass
            
    return results
