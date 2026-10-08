from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.slo import ReliabilityObjective, SLOEvaluation, AlertRule, Alert
from app.models.monitoring import (
    MonitoringRun,
    MetricResult,
    FeatureMonitoringResult,
    DataQualityResult,
    PredictionMonitoringResult
)
from app.schemas.slo import (
    ReliabilityObjectiveCreate, ReliabilityObjectiveUpdate,
    AlertRuleCreate, AlertRuleUpdate
)
from app.services.audit_service import record_event as audit_record_event
from app.services.reliability_service import reliability_service
from app.incidents.service import IncidentService
from app.schemas.incident import IncidentCreate

class SLOError(Exception):
    pass

def parse_window(window: str) -> timedelta:
    if window.endswith('h'):
        return timedelta(hours=int(window[:-1]))
    elif window.endswith('d'):
        return timedelta(days=int(window[:-1]))
    elif window.endswith('m'):
        return timedelta(minutes=int(window[:-1]))
    raise SLOError(f"Invalid evaluation window: {window}")

class SLOService:
    
    def create_objective(self, db: Session, obj_in: ReliabilityObjectiveCreate, current_user: Any = None) -> ReliabilityObjective:
        # Validate metric
        valid_types = ['model_performance', 'data_quality', 'feature_drift', 'prediction_drift']
        if obj_in.objective_type not in valid_types:
            raise SLOError(f"Invalid objective_type. Must be one of {valid_types}")
            
        if obj_in.comparison_operator not in ['>=', '<=', '>', '<']:
            raise SLOError(f"Invalid comparison operator {obj_in.comparison_operator}")
            
        # Ensure window is valid
        parse_window(obj_in.evaluation_window)
        
        db_obj = ReliabilityObjective(
            model_id=obj_in.model_id,
            name=obj_in.name,
            description=obj_in.description,
            objective_type=obj_in.objective_type,
            metric_name=obj_in.metric_name,
            comparison_operator=obj_in.comparison_operator,
            target_value=obj_in.target_value,
            evaluation_window=obj_in.evaluation_window,
            enabled=obj_in.enabled,
            severity=obj_in.severity,
            created_by=current_user.id if current_user else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        if current_user:
            audit_record_event(
                db=db,
                action="SLO_CREATED",
                actor_type="USER",
                actor_id=current_user.id,
                resource_type="RELIABILITY_OBJECTIVE",
                resource_id=db_obj.id,
                result="SUCCESS",
                metadata={"name": db_obj.name, "model_id": db_obj.model_id}
            )
            
        return db_obj

    def evaluate_objective(self, db: Session, objective_id: str, custom_time: Optional[datetime] = None) -> SLOEvaluation:
        objective = db.query(ReliabilityObjective).filter(ReliabilityObjective.id == objective_id).first()
        if not objective:
            raise SLOError("Objective not found")
            
        end_time = custom_time or datetime.now(timezone.utc)
        try:
            window_delta = parse_window(objective.evaluation_window)
        except Exception:
            window_delta = timedelta(hours=1)
            
        start_time = end_time - window_delta
        
        # Query monitoring runs in window
        runs = db.query(MonitoringRun).filter(
            MonitoringRun.model_id == objective.model_id,
            MonitoringRun.status == "completed",
            MonitoringRun.created_at >= start_time,
            MonitoringRun.created_at <= end_time
        ).order_by(desc(MonitoringRun.created_at)).all()
        
        run_ids = [run.id for run in runs]
        
        values = []
        if not run_ids:
            pass # no runs
        elif objective.objective_type == 'model_performance':
            results = db.query(MetricResult).filter(
                MetricResult.monitoring_run_id.in_(run_ids),
                MetricResult.metric_name == objective.metric_name
            ).all()
            values = [r.metric_value for r in results]
        elif objective.objective_type == 'data_quality':
            results = db.query(DataQualityResult).filter(
                DataQualityResult.monitoring_run_id.in_(run_ids),
                DataQualityResult.metric_name == objective.metric_name
            ).all()
            values = [r.value for r in results]
        elif objective.objective_type == 'feature_drift':
            results = db.query(FeatureMonitoringResult).filter(
                FeatureMonitoringResult.monitoring_run_id.in_(run_ids),
                FeatureMonitoringResult.feature_name == objective.metric_name
            ).all()
            values = [r.drift_score for r in results]
        elif objective.objective_type == 'prediction_drift':
            results = db.query(PredictionMonitoringResult).filter(
                PredictionMonitoringResult.monitoring_run_id.in_(run_ids),
                PredictionMonitoringResult.prediction_metric == objective.metric_name
            ).all()
            values = [r.value for r in results]
            
        # Calculation logic
        # Methodology:
        # Error Budget: 
        # For HIGHER_IS_BETTER (>=, >):
        # Target = e.g., 0.95. Total Budget = 1.0 - target = 0.05
        # Consumed = 1.0 - measured
        # For LOWER_IS_BETTER (<=, <):
        # Target = e.g., 0.20. Total Budget = target = 0.20
        # Consumed = measured
        
        if not values:
            eval_record = SLOEvaluation(
                objective_id=objective.id,
                model_id=objective.model_id,
                evaluation_start=start_time,
                evaluation_end=end_time,
                target_value=objective.target_value,
                comparison_operator=objective.comparison_operator,
                status="NO_DATA",
                sample_count=0
            )
        else:
            measured_value = sum(values) / len(values)
            target = objective.target_value
            operator = objective.comparison_operator
            
            # evaluate condition
            breached = False
            if operator == '>=': breached = not (measured_value >= target)
            elif operator == '>': breached = not (measured_value > target)
            elif operator == '<=': breached = not (measured_value <= target)
            elif operator == '<': breached = not (measured_value < target)
            
            # Compliance ratio
            if operator in ['>=', '>']:
                compliance = measured_value / target if target != 0 else 1.0
                eb_total = 1.0 - target
                eb_consumed = 1.0 - measured_value
            else:
                compliance = target / measured_value if measured_value != 0 else 1.0
                eb_total = target
                eb_consumed = measured_value
                
            eb_remaining = eb_total - eb_consumed
            
            if eb_total > 0:
                burn_rate = eb_consumed / eb_total
            else:
                burn_rate = 0.0 if not breached else 999.0
                
            status = "HEALTHY"
            if breached:
                status = "BREACHED"
            elif burn_rate >= 0.8:
                status = "AT_RISK"
                
            eval_record = SLOEvaluation(
                objective_id=objective.id,
                model_id=objective.model_id,
                evaluation_start=start_time,
                evaluation_end=end_time,
                measured_value=measured_value,
                target_value=target,
                comparison_operator=operator,
                status=status,
                compliance_ratio=compliance,
                error_budget_total=eb_total,
                error_budget_consumed=eb_consumed,
                error_budget_remaining=eb_remaining,
                burn_rate=burn_rate,
                sample_count=len(values)
            )
            
        db.add(eval_record)
        db.commit()
        db.refresh(eval_record)
        
        # Reliability Timeline Event
        if eval_record.status == "BREACHED":
            reliability_service.create_event(
                db=db,
                model_id=objective.model_id,
                event_type="SLO_BREACHED",
                title=f"SLO Breached: {objective.name}",
                description=f"Measured {eval_record.measured_value:.4f} vs target {eval_record.comparison_operator} {eval_record.target_value:.4f}",
                severity="critical",
                source="slo_evaluator"
            )
            
        return eval_record

    def evaluate_alert_rules(self, db: Session, objective_id: str, evaluation: SLOEvaluation) -> List[Alert]:
        rules = db.query(AlertRule).filter(AlertRule.objective_id == objective_id, AlertRule.enabled == True).all()
        alerts_generated = []
        
        now = datetime.now(timezone.utc)
        
        for rule in rules:
            triggered = False
            # We use the current evaluation for short_window if it matches, but for simplicity, 
            # we evaluate the condition directly on the latest evaluation for now.
            if rule.condition_type == 'SLO_BREACHED':
                triggered = (evaluation.status == 'BREACHED')
            elif rule.condition_type == 'BURN_RATE_ABOVE':
                triggered = (evaluation.burn_rate is not None and evaluation.burn_rate > (rule.threshold or 1.0))
            elif rule.condition_type == 'ERROR_BUDGET_BELOW':
                # e.g., error budget < 0 (exhausted)
                triggered = (evaluation.error_budget_remaining is not None and evaluation.error_budget_remaining < (rule.threshold or 0.0))
                
            dedup_key = f"{objective_id}:{rule.id}:{rule.condition_type}"
            
            # Check existing alerts
            existing_alert = db.query(Alert).filter(
                Alert.deduplication_key == dedup_key,
                Alert.status.in_(['OPEN', 'ACKNOWLEDGED'])
            ).first()
            
            if triggered:
                if existing_alert:
                    # ongoing condition, do not create duplicate
                    # Just update updated_at
                    existing_alert.updated_at = now
                    db.commit()
                else:
                    # check cooldown
                    last_resolved = db.query(Alert).filter(
                        Alert.deduplication_key == dedup_key,
                        Alert.status == 'RESOLVED'
                    ).order_by(desc(Alert.resolved_at)).first()
                    
                    in_cooldown = False
                    if last_resolved and last_resolved.resolved_at:
                        if (now - last_resolved.resolved_at).total_seconds() < rule.cooldown_seconds:
                            in_cooldown = True
                            
                    if not in_cooldown:
                        # CREATE ALERT
                        alert = Alert(
                            rule_id=rule.id,
                            objective_id=objective_id,
                            model_id=evaluation.model_id,
                            severity=rule.severity,
                            status="OPEN",
                            deduplication_key=dedup_key,
                            summary=f"Alert triggered: {rule.name} for {evaluation.objective.name}",
                            evidence={
                                "measured_value": evaluation.measured_value,
                                "target_value": evaluation.target_value,
                                "burn_rate": evaluation.burn_rate,
                                "error_budget_remaining": evaluation.error_budget_remaining
                            }
                        )
                        db.add(alert)
                        db.commit()
                        db.refresh(alert)
                        alerts_generated.append(alert)
                        
                        audit_record_event(db, "SYSTEM", "SYSTEM", "ALERT_TRIGGERED", "ALERT", alert.id, "SUCCESS", {"rule_name": rule.name})
                        
                        reliability_service.emit_event(
                            db, evaluation.model_id, "ALERT_TRIGGERED", "alert", alert.id, f"Alert: {rule.name}", 
                            summary=f"Rule {rule.condition_type} triggered.", severity=rule.severity
                        )
                        
                        if rule.auto_create_incident:
                            self._create_incident_from_alert(db, alert, evaluation)
            else:
                # Recover existing alert if it was triggered
                if existing_alert and existing_alert.status != 'RESOLVED':
                    existing_alert.status = 'RESOLVED'
                    existing_alert.resolved_at = now
                    existing_alert.resolved_by = "SYSTEM"
                    db.commit()
                    audit_record_event(db, "SYSTEM", "SYSTEM", "ALERT_RESOLVED", "ALERT", existing_alert.id, "SUCCESS")
                    reliability_service.emit_event(
                        db, evaluation.model_id, "SLO_RECOVERED", "alert", existing_alert.id, f"SLO Recovered: {evaluation.objective.name}", 
                        summary="Alert condition resolved automatically.", severity="info"
                    )
                    
        return alerts_generated
        
    def _create_incident_from_alert(self, db: Session, alert: Alert, evaluation: SLOEvaluation):
        # We reuse the existing incident system and deduplication logic (which uses incident_key)
        incident_key = f"slo_breach_{alert.model_id}_{alert.objective_id}"
        
        # Check if active incident already exists via incident_service
        # (IncidentService handles deduplication natively if we create)
        incident_create = IncidentCreate(
            incident_key=incident_key,
            model_id=alert.model_id,
            model_version_id="latest", # Or from evaluation
            title=alert.summary,
            summary=f"Automated incident from SLO Alert: {alert.summary}. Target: {evaluation.target_value}, Measured: {evaluation.measured_value}",
            severity=alert.severity,
            category=evaluation.objective.objective_type
        )
        
        try:
            # We don't have access to the exact model version ID in objective, we can get it from models if needed
            from app.models.model import ModelVersion
            mv = db.query(ModelVersion).filter(ModelVersion.model_id == alert.model_id).order_by(desc(ModelVersion.created_at)).first()
            if mv:
                incident_create.model_version_id = mv.id
                
            inc = IncidentService.create_incident(db, incident_create)
            
            # Associate alert with incident
            alert.incident_id = inc.id
            db.commit()
            
            reliability_service.emit_event(
                db, alert.model_id, "INCIDENT_CREATED", "incident", inc.id, f"Incident {inc.id} created from alert", 
                summary="", severity=alert.severity
            )
            
        except Exception as e:
            # If incident already exists and is active, incident_service raises 400 (deduplication)
            pass

slo_service = SLOService()
