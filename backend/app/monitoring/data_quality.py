import pandas as pd

def calculate_data_quality(df: pd.DataFrame, feature_cols: list) -> dict:
    """Calculate basic data quality metrics for the current window."""
    if df.empty:
        return {}
        
    row_count = len(df)
    
    # Calculate missing values % across feature columns
    if not feature_cols:
        missing_pct = 0.0
    else:
        available_cols = [c for c in feature_cols if c in df.columns]
        if available_cols:
            missing_pct = df[available_cols].isnull().sum().sum() / (row_count * len(available_cols))
        else:
            missing_pct = 0.0
            
    # Calculate duplicates %
    duplicate_pct = df.duplicated().sum() / row_count
    
    return {
        'row_count': float(row_count),
        'missing_value_percentage': float(missing_pct * 100),
        'duplicate_percentage': float(duplicate_pct * 100)
    }
