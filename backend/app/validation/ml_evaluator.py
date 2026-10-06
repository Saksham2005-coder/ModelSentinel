import os
import logging
import pandas as pd
from typing import Dict, Any

from sqlalchemy.orm import Session
from app.models.patch import PatchProposal
from app.models.incident import Incident
from app.models.model import ModelVersion
from app.monitoring.metrics import calculate_classification_metrics
from app.monitoring.segmentation import analyze_segments

logger = logging.getLogger(__name__)

class MLEvaluator:
    def __init__(self, db: Session, patch: PatchProposal, incident: Incident):
        self.db = db
        self.patch = patch
        self.incident = incident
        
    def evaluate(self) -> Dict[str, Any]:
        """
        Executes ML Evaluation on the patched repository.
        Performs a three-way comparison: Healthy (Baseline) vs Current (Incident) vs Patched.
        """
        try:
            model = self.incident.model
            
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            baseline_path = os.path.join(data_dir, f"{model.slug}_baseline.csv")
            current_path = os.path.join(data_dir, f"{model.slug}_current.csv")
            patched_path = os.path.join(data_dir, f"{model.slug}_patched.csv")
            
            if not os.path.exists(baseline_path) or not os.path.exists(current_path) or not os.path.exists(patched_path):
                return {
                    "status": "skipped",
                    "reason": "Required datasets (baseline, current, patched) not found."
                }
                
            b_df = pd.read_csv(baseline_path)
            c_df = pd.read_csv(current_path)
            p_df = pd.read_csv(patched_path)
            
            b_metrics = calculate_classification_metrics(b_df, "target", "prediction", "probability")
            c_metrics = calculate_classification_metrics(c_df, "target", "prediction", "probability")
            p_metrics = calculate_classification_metrics(p_df, "target", "prediction", "probability")
            
            segments = [
                {"name": "URL-heavy emails", "condition": "url_count > 2"},
                {"name": "Normal emails", "condition": "url_count <= 2"}
            ]
            
            b_seg = analyze_segments(b_df, b_df, "target", "prediction", segments)
            c_seg = analyze_segments(b_df, c_df, "target", "prediction", segments)
            p_seg = analyze_segments(b_df, p_df, "target", "prediction", segments)

            return {
                "status": "passed",
                "metrics": {
                    "baseline": b_metrics,
                    "current": c_metrics,
                    "patched": p_metrics
                },
                "segments": {
                    "baseline": {s["segment_name"]: s["current_metric_value"] for s in b_seg},
                    "current": {s["segment_name"]: s["current_metric_value"] for s in c_seg},
                    "patched": {s["segment_name"]: s["current_metric_value"] for s in p_seg}
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e)
            }
