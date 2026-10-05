import logging
import traceback
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.patch import PatchProposal
from app.models.validation import ValidationRun, ValidationCheck
from app.repository.storage import RepositoryStorage
from app.validation.environment import ValidationEnvironment

logger = logging.getLogger(__name__)

class ValidationRunner:
    def __init__(self, db: Session, patch_id: str):
        self.db = db
        self.patch = self.db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()
        self.storage = RepositoryStorage()
        self.env = None
        
    def _create_run(self) -> ValidationRun:
        run = ValidationRun(
            patch_proposal_id=self.patch.id,
            incident_id=self.patch.incident_id,
            repository_snapshot_id=self.patch.repository_snapshot_id,
            status="queued"
        )
        self.db.add(run)
        self.db.commit()
        return run

    def execute(self) -> ValidationRun:
        if not self.patch:
            raise ValueError("Patch not found.")
            
        run = self._create_run()
        
        try:
            run.status = "preparing"
            run.started_at = datetime.now(timezone.utc)
            self.db.commit()
            
            self.env = ValidationEnvironment(self.patch, self.storage)
            self.env.setup()
            
            run.status = "patch_applied"
            self.db.commit()
            
            # 1. Apply patch
            self._apply_patch(run)
            
            if run.status == "failed":
                return run
                
            # 2. Static validation
            run.status = "static_validation"
            self.db.commit()
            self._run_static_validation(run)
            
            if run.status == "failed":
                return run
                
            # 3. Tests
            run.status = "testing"
            self.db.commit()
            self._run_tests(run)
            
            if run.status == "failed":
                return run
                
            # 4. ML Evaluation
            run.status = "ml_evaluation"
            self.db.commit()
            self._run_ml_evaluation(run)
            
            # 5. Segment regression
            run.status = "segment_evaluation"
            self.db.commit()
            self._run_segment_regression(run)
            
            # 6. Security scan
            run.status = "security_scan"
            self.db.commit()
            self._run_security_scan(run)
            
            # Final Verdict
            self._calculate_verdict(run)
            
            run.status = "completed"
            
        except Exception as e:
            logger.error(f"Validation run failed: {traceback.format_exc()}")
            run.status = "failed"
            run.summary = f"Internal error during validation: {str(e)}"
            self._add_check(run, "custom", "Internal Error", "failed", str(e))
        finally:
            run.completed_at = datetime.now(timezone.utc)
            run.duration_ms = int((run.completed_at - run.started_at).total_seconds() * 1000)
            self.db.commit()
            if self.env:
                self.env.teardown()
                
        return run

    def _apply_patch(self, run: ValidationRun):
        try:
            self.env.apply_patch()
            self._add_check(run, "static", "Patch Application", "passed", "Patch applied cleanly.")
        except Exception as e:
            self._add_check(run, "static", "Patch Application", "failed", f"Failed to apply patch: {str(e)}")
            run.status = "failed"

    def _add_check(self, run: ValidationRun, check_type: str, name: str, status: str, summary: str, details: dict = None):
        check = ValidationCheck(
            validation_run_id=run.id,
            check_type=check_type,
            name=name,
            status=status,
            summary=summary,
            details=details
        )
        self.db.add(check)
        self.db.commit()

    # Stubs for the subsequent checkpoints
    def _run_static_validation(self, run: ValidationRun):
        pass
        
    def _run_tests(self, run: ValidationRun):
        pass
        
    def _run_ml_evaluation(self, run: ValidationRun):
        pass
        
    def _run_segment_regression(self, run: ValidationRun):
        pass
        
    def _run_security_scan(self, run: ValidationRun):
        pass
        
    def _calculate_verdict(self, run: ValidationRun):
        run.verdict = "PASS"
        run.summary = "Validation passed"
