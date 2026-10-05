import os
import logging
from typing import Dict, Any

from sqlalchemy.orm import Session
from app.models.patch import PatchProposal
from app.models.incident import Incident
from app.monitoring.runner import run_monitoring_job
from app.models.model import ModelVersion

logger = logging.getLogger(__name__)

class MLEvaluator:
    def __init__(self, db: Session, patch: PatchProposal, incident: Incident):
        self.db = db
        self.patch = patch
        self.incident = incident
        
    def evaluate(self) -> Dict[str, Any]:
        """
        Executes ML Evaluation on the patched repository.
        In a real production environment, this would trigger a training/inference pipeline
        inside the isolated environment and evaluate the resulting predictions.
        Here we simulate it by running the deterministic monitoring job on a pre-generated patched dataset.
        """
        try:
            model = self.incident.model
            version = self.db.query(ModelVersion).filter(ModelVersion.id == self.incident.model_version_id).first()
            
            # Paths
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            baseline_path = os.path.join(data_dir, f"{model.slug}_baseline.csv")
            patched_path = os.path.join(data_dir, f"{model.slug}_patched.csv")
            
            if not os.path.exists(baseline_path) or not os.path.exists(patched_path):
                return {
                    "status": "skipped",
                    "reason": "Baseline or patched dataset not found. ML evaluation requires predictions.",
                    "run_id": None
                }
                
            # Run deterministic evaluation
            run = run_monitoring_job(
                db=self.db,
                model_id=model.id,
                model_version_id=version.id,
                baseline_path=baseline_path,
                current_path=patched_path,
                target_col="target",
                pred_col="prediction",
                prob_col="probability"
            )
            
            return {
                "status": "passed",
                "reason": "ML evaluation completed.",
                "run_id": run.id
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e),
                "run_id": None
            }
