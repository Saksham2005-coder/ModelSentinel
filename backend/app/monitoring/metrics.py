import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def calculate_classification_metrics(df: pd.DataFrame, target_col: str, pred_col: str, prob_col: str = None) -> dict:
    """Calculate deterministic performance metrics for a classification model."""
    if df.empty or target_col not in df.columns or pred_col not in df.columns:
        return {}
        
    y_true = df[target_col]
    y_pred = df[pred_col]

    metrics = {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
        'f1_score': float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
    }

    if prob_col and prob_col in df.columns:
        y_prob = df[prob_col]
        try:
            # Handle binary vs multiclass implicitly by attempting roc_auc
            if len(y_true.unique()) == 2:
                metrics['roc_auc'] = float(roc_auc_score(y_true, y_prob))
        except Exception:
            pass # Invalid roc_auc is silently ignored

    return metrics
