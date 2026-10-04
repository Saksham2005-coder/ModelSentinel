import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

def calculate_psi(expected, actual, buckettype='bins', buckets=10, axis=0):
    """Calculate the PSI (population stability index) across all variables."""
    def psi(expected_array, actual_array, buckets):
        def scale_range (input, min, max):
            input += -(np.min(input))
            input /= np.max(input) / (max - min)
            input += min
            return input

        breakpoints = np.arange(0, buckets + 1) / (buckets) * 100
        breakpoints = scale_range(breakpoints, np.min(expected_array), np.max(expected_array))
        
        expected_percents = np.histogram(expected_array, breakpoints)[0] / len(expected_array)
        actual_percents = np.histogram(actual_array, breakpoints)[0] / len(actual_array)

        def sub_psi(e_perc, a_perc):
            if a_perc == 0:
                a_perc = 0.0001
            if e_perc == 0:
                e_perc = 0.0001
            value = (e_perc - a_perc) * np.log(e_perc / a_perc)
            return value

        return np.sum(sub_psi(expected_percents[i], actual_percents[i]) for i in range(0, len(expected_percents)))

    # Fallback to a simpler, more robust histogram approach for our usecase
    # To handle zero division cleanly:
    def simple_psi(expected_array, actual_array, bins=10):
        if len(expected_array) == 0 or len(actual_array) == 0:
            return 0.0
            
        # For numerical
        if pd.api.types.is_numeric_dtype(expected_array) and pd.api.types.is_numeric_dtype(actual_array):
            min_val = min(np.min(expected_array), np.min(actual_array))
            max_val = max(np.max(expected_array), np.max(actual_array))
            if min_val == max_val: # constant feature
                return 0.0
            
            bins_edges = np.linspace(min_val, max_val, bins + 1)
            e_counts, _ = np.histogram(expected_array, bins=bins_edges)
            a_counts, _ = np.histogram(actual_array, bins=bins_edges)
        else:
            # For categorical
            unique_cats = set(expected_array).union(set(actual_array))
            if not unique_cats:
                return 0.0
                
            e_counts = np.array([np.sum(expected_array == c) for c in unique_cats])
            a_counts = np.array([np.sum(actual_array == c) for c in unique_cats])
            
        e_freqs = e_counts / len(expected_array)
        a_freqs = a_counts / len(actual_array)
        
        # avoid zero
        e_freqs = np.where(e_freqs == 0, 0.0001, e_freqs)
        a_freqs = np.where(a_freqs == 0, 0.0001, a_freqs)
        
        psi_val = np.sum((a_freqs - e_freqs) * np.log(a_freqs / e_freqs))
        return float(psi_val)
        
    return simple_psi(expected, actual)


def calculate_feature_drift(baseline_df: pd.DataFrame, current_df: pd.DataFrame, feature_cols: list) -> list:
    """Calculate deterministic feature drift using KS stat and PSI."""
    results = []
    
    for col in feature_cols:
        if col not in baseline_df.columns or col not in current_df.columns:
            continue
            
        baseline_col = baseline_df[col].dropna()
        current_col = current_df[col].dropna()
        
        if len(baseline_col) == 0 or len(current_col) == 0:
            continue
            
        feature_type = 'numeric' if pd.api.types.is_numeric_dtype(baseline_col) else 'categorical'
        
        if feature_type == 'numeric':
            # KS test
            stat, _ = ks_2samp(baseline_col, current_col)
            drift_score = float(stat)
            drift_method = 'KS'
            
            b_summary = {'mean': float(baseline_col.mean()), 'std': float(baseline_col.std()) if len(baseline_col) > 1 else 0}
            c_summary = {'mean': float(current_col.mean()), 'std': float(current_col.std()) if len(current_col) > 1 else 0}
        else:
            # PSI for categorical
            drift_score = calculate_psi(baseline_col.values, current_col.values)
            drift_method = 'PSI'
            
            b_summary = baseline_col.value_counts(normalize=True).to_dict()
            c_summary = current_col.value_counts(normalize=True).to_dict()
            
        results.append({
            'feature_name': col,
            'feature_type': feature_type,
            'drift_method': drift_method,
            'drift_score': drift_score,
            'baseline_summary': b_summary,
            'current_summary': c_summary
        })
        
    return results
