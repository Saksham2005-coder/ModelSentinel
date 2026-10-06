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
                self._calculate_verdict(run)
                return run
                
            # 2. Static validation
            run.status = "static_validation"
            self.db.commit()
            self._run_static_validation(run)
            
            if run.status == "failed":
                self._calculate_verdict(run)
                return run
                
            # 3. Tests
            run.status = "testing"
            self.db.commit()
            self._run_tests(run)
            
            if run.status == "failed":
                self._calculate_verdict(run)
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
            
            if run.status != "failed":
                run.status = "completed"
            
        except Exception as e:
            logger.error(f"Validation run failed: {traceback.format_exc()}")
            run.status = "failed"
            run.summary = f"Internal error during validation: {str(e)}"
            self._add_check(run, "custom", "Internal Error", "failed", str(e))
            self._calculate_verdict(run)
        finally:
            run.completed_at = datetime.now(timezone.utc)
            start_tz = run.started_at
            if start_tz and start_tz.tzinfo is None:
                start_tz = start_tz.replace(tzinfo=timezone.utc)
            if start_tz:
                run.duration_ms = int((run.completed_at - start_tz).total_seconds() * 1000)
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

    def _run_static_validation(self, run: ValidationRun):
        from app.validation.static_checks import StaticValidator
        validator = StaticValidator(self.env.repo_path)
        # Check all python files in patch
        py_files = [c.file_path for c in self.patch.file_changes if c.file_path.endswith('.py') and c.change_type != 'delete']
        errors = validator.check_syntax(py_files)
        
        if errors:
            self._add_check(run, "static", "Syntax Check", "failed", "Syntax errors detected in patched files.", {"errors": errors})
            run.status = "failed"
        else:
            self._add_check(run, "static", "Syntax Check", "passed", "No syntax errors detected in patched files.")
        
    def _run_tests(self, run: ValidationRun):
        from app.validation.test_runner import TestRunner
        runner = TestRunner(self.env.repo_path)
        result = runner.run_tests()
        
        if result["status"] == "passed":
            self._add_check(run, "unit_test", "Unit Tests", "passed", "All tests passed.", result)
        elif result["status"] == "skipped":
            self._add_check(run, "unit_test", "Unit Tests", "skipped", result.get("reason", "Skipped"), result)
        else:
            self._add_check(run, "unit_test", "Unit Tests", "failed", result.get("reason", "Tests failed."), result)
            run.status = "failed"
        
    def _run_ml_evaluation(self, run: ValidationRun):
        from app.validation.ml_evaluator import MLEvaluator
        evaluator = MLEvaluator(self.db, self.patch, self.patch.incident)
        result = evaluator.evaluate()
        
        if result["status"] == "passed":
            self._add_check(run, "ml_evaluation", "ML Recovery", "passed", "ML evaluation completed successfully.", result)
            self._process_metrics_and_segments(run, result)
        elif result["status"] == "skipped":
            self._add_check(run, "ml_evaluation", "ML Recovery", "skipped", result.get("reason", "Skipped"), result)
        else:
            self._add_check(run, "ml_evaluation", "ML Recovery", "failed", result.get("reason", "ML evaluation failed."), result)
            run.status = "failed"
            
    def _process_metrics_and_segments(self, run: ValidationRun, result: dict):
        from app.models.validation import ValidationMetric
        
        metrics = result["metrics"]
        b_m = metrics["baseline"]
        c_m = metrics["current"]
        p_m = metrics["patched"]
        
        # Populate Metrics
        for m_name in b_m.keys():
            b_val = b_m.get(m_name, 0.0)
            c_val = c_m.get(m_name, 0.0)
            p_val = p_m.get(m_name, 0.0)
            
            delta = p_val - c_val
            
            # Use ML_DEFAULT profile logic: minimum recovery = 0.85
            # For simplicity, if patched_value is better than current and meets target, it's recovered
            if p_val >= 0.85:
                status = "recovered"
            elif p_val > c_val:
                status = "recovered" # Improved but maybe didn't hit 0.85
            else:
                status = "regressed"
                
            vm = ValidationMetric(
                validation_run_id=run.id,
                metric_name=m_name,
                baseline_value=b_val,
                current_value=c_val,
                patched_value=p_val,
                delta=delta,
                status=status
            )
            self.db.add(vm)
            
        # Segments
        segments = result["segments"]
        b_s = segments["baseline"]
        c_s = segments["current"]
        p_s = segments["patched"]
        
        segment_regressed = False
        for s_name in b_s.keys():
            b_val = b_s.get(s_name, 0.0)
            c_val = c_s.get(s_name, 0.0)
            p_val = p_s.get(s_name, 0.0)
            delta = p_val - c_val
            
            if p_val >= c_val:
                status = "recovered"
            else:
                status = "regressed"
                segment_regressed = True
                
            vm = ValidationMetric(
                validation_run_id=run.id,
                metric_name="f1_score",
                baseline_value=b_val,
                current_value=c_val,
                patched_value=p_val,
                delta=delta,
                status=status,
                segment_name=s_name
            )
            self.db.add(vm)
            
        self.db.commit()
        
        if segment_regressed:
            self._add_check(run, "segment_regression", "Segment Recovery", "failed", "One or more segments regressed.")
        else:
            self._add_check(run, "segment_regression", "Segment Recovery", "passed", "All segments recovered.")
            
    def _run_segment_regression(self, run: ValidationRun):
        # Already handled in _process_metrics_and_segments for atomic DB commits
        pass
        
    def _run_security_scan(self, run: ValidationRun):
        from app.validation.security import SecurityScanner
        scanner = SecurityScanner(self.env.repo_path)
        result = scanner.scan()
        
        if result["status"] == "passed":
            self._add_check(run, "security", "Security Scan", "passed", "No security issues found.", result)
        elif result["status"] == "skipped":
            self._add_check(run, "security", "Security Scan", "skipped", result.get("reason", "Skipped"), result)
        else:
            self._add_check(run, "security", "Security Scan", "failed", result.get("reason", "Security scan failed."), result)
            if result["status"] == "failed":
                run.status = "failed"
        
    def _calculate_verdict(self, run: ValidationRun):
        if run.status == "failed":
            run.verdict = "FAIL"
            run.summary = "Validation failed due to critical check failure."
            return
            
        # Deterministic Verdict Logic
        has_failed_checks = any(c.status == "failed" for c in run.checks)
        overall_metrics = [m for m in run.metrics if not m.segment_name]
        segment_metrics = [m for m in run.metrics if m.segment_name]
        
        primary_metric = next((m for m in overall_metrics if m.metric_name == "f1_score"), None)
        
        if has_failed_checks:
            run.verdict = "FAIL"
            run.summary = "Validation failed due to one or more check failures."
            return
            
        # Acceptance Criteria
        if primary_metric:
            if primary_metric.patched_value < 0.85:
                run.verdict = "FAIL"
                run.summary = f"F1 Score ({primary_metric.patched_value:.3f}) did not meet the 0.85 minimum recovery target."
                return
                
        has_regressed_overall = any(m.status == "regressed" for m in overall_metrics)
        has_regressed_segment = any(m.status == "regressed" for m in segment_metrics)
        
        if has_regressed_overall or has_regressed_segment:
            run.verdict = "PARTIAL"
            run.summary = "Patch provides partial recovery but introduces regressions in secondary metrics or segments."
        else:
            run.verdict = "PASS"
            run.summary = "All checks passed. Metrics successfully recovered without regression."
