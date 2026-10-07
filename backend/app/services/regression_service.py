from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.models.incident_memory import IncidentMemory
from app.models.regression import RegressionCase, RegressionRun, RegressionResult
from app.models.validation import ValidationRun

class RegressionService:
    def __init__(self, db: Session):
        self.db = db

    def create_case_from_memory(self, memory_id: str, payload: Dict[str, Any]) -> RegressionCase:
        memory = self.db.query(IncidentMemory).filter(IncidentMemory.id == memory_id).first()
        if not memory:
            raise ValueError("Incident memory not found")
            
        existing = self.db.query(RegressionCase).filter(RegressionCase.incident_memory_id == memory_id).first()
        if existing:
            raise ValueError("Regression case already exists for this memory")
            
        case = RegressionCase(
            source_incident_id=memory.incident_id,
            incident_memory_id=memory.id,
            model_id=memory.model_id,
            model_version_id=memory.model_version_id,
            
            name=payload.get("name", f"Regression: {memory.title}"),
            description=payload.get("description", memory.summary),
            failure_signature=payload.get("failure_signature", memory.root_cause),
            expected_behavior=payload.get("expected_behavior", memory.resolution_summary),
            
            baseline_metrics=payload.get("baseline_metrics", {}),
            failure_metrics=payload.get("failure_metrics", {}),
            acceptance_criteria=payload.get("acceptance_criteria", {"f1_score": {"min": 0.85}}),
            
            affected_features=memory.affected_features,
            affected_segments=memory.affected_segments,
            severity=memory.severity,
            status="active"
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        
        from app.services.reliability_service import reliability_service
        reg_event = reliability_service.emit_event(
            db=self.db,
            model_id=memory.model_id,
            model_version_id=memory.model_version_id,
            event_type="REGRESSION_LEARNED",
            source_type="regression_case",
            source_id=case.id,
            title="Regression Test Learned",
            summary=f"Incident memory captured as a formal regression test: {case.name}",
            status="active"
        )
        
        inc_event = reliability_service.find_event_by_source(self.db, "incident", memory.incident_id, "INCIDENT_CREATED")
        if inc_event:
            reliability_service.link_events(self.db, inc_event.id, reg_event.id, "RESULTED_IN")
            
        return case

    def record_run_result(self, case_id: str, validation_run_id: str, evaluator_result: Dict[str, Any]) -> RegressionRun:
        """
        Record a regression test execution based on a Phase 8 ML Evaluator result (or ValidationRun).
        """
        case = self.db.query(RegressionCase).filter(RegressionCase.id == case_id).first()
        if not case:
            raise ValueError("Regression case not found")
            
        run = RegressionRun(
            regression_case_id=case.id,
            validation_run_id=validation_run_id,
            status="processing",
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        
        has_failure = False
        
        if evaluator_result.get("status") != "passed":
            run.status = "ERROR"
            run.failure_reason = evaluator_result.get("reason", "Evaluation failed before generating metrics.")
        else:
            metrics = evaluator_result.get("metrics", {})
            p_m = metrics.get("patched", {}) # Current state evaluated
            
            segments = evaluator_result.get("segments", {})
            p_s = segments.get("patched", {})
            
            criteria = case.acceptance_criteria or {}
            
            # Evaluate overall metrics
            for metric, constraints in criteria.items():
                if metric not in p_m:
                    continue
                actual = p_m[metric]
                min_val = constraints.get("min")
                max_val = constraints.get("max")
                
                status = "PASS"
                if min_val is not None and actual < min_val:
                    status = "FAIL"
                if max_val is not None and actual > max_val:
                    status = "FAIL"
                    
                if status == "FAIL":
                    has_failure = True
                    
                res = RegressionResult(
                    regression_run_id=run.id,
                    metric_name=metric,
                    expected_value=min_val if min_val is not None else max_val,
                    actual_value=actual,
                    status=status
                )
                self.db.add(res)
                
            # Evaluate segments. We ensure the segment f1_score doesn't drop below the acceptance_criteria
            # For simplicity, apply same min_val to segment if it exists
            for seg, actual in p_s.items():
                # Is it an affected segment?
                if case.affected_segments and seg in case.affected_segments:
                    min_val = criteria.get("f1_score", {}).get("min")
                    status = "PASS"
                    if min_val is not None and actual < min_val:
                        status = "FAIL"
                        has_failure = True
                        
                    res = RegressionResult(
                        regression_run_id=run.id,
                        metric_name="f1_score",
                        segment_name=seg,
                        expected_value=min_val,
                        actual_value=actual,
                        status=status
                    )
                    self.db.add(res)
                    
            if has_failure:
                run.status = "FAIL"
                run.failure_reason = "Acceptance criteria not met for one or more metrics."
            else:
                run.status = "PASS"
                
        run.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(run)
        return run

    def list_regression_cases(self) -> List[RegressionCase]:
        return self.db.query(RegressionCase).order_by(RegressionCase.created_at.desc()).all()
