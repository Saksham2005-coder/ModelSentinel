from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class ReliabilityObjective(Base):
    __tablename__ = "reliability_objectives"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    objective_type = Column(String, nullable=False) # e.g., 'model_performance', 'data_quality', 'feature_drift', 'prediction_drift'
    metric_name = Column(String, nullable=False)
    comparison_operator = Column(String, nullable=False) # '>=', '<=', '>', '<'
    target_value = Column(Float, nullable=False)
    evaluation_window = Column(String, nullable=False) # e.g., '1h', '6h', '24h', '7d', '30d'
    enabled = Column(Boolean, default=True)
    severity = Column(String, nullable=False, default="medium")
    
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    evaluations = relationship("SLOEvaluation", back_populates="objective", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="objective", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="objective", cascade="all, delete-orphan")


class SLOEvaluation(Base):
    __tablename__ = "slo_evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    objective_id = Column(String, ForeignKey("reliability_objectives.id"), nullable=False)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=True)
    
    evaluation_start = Column(DateTime(timezone=True), nullable=False)
    evaluation_end = Column(DateTime(timezone=True), nullable=False)
    
    measured_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=False)
    comparison_operator = Column(String, nullable=False)
    
    status = Column(String, nullable=False) # HEALTHY, AT_RISK, BREACHED, NO_DATA
    compliance_ratio = Column(Float, nullable=True)
    
    error_budget_total = Column(Float, nullable=True)
    error_budget_consumed = Column(Float, nullable=True)
    error_budget_remaining = Column(Float, nullable=True)
    burn_rate = Column(Float, nullable=True)
    
    sample_count = Column(Integer, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    objective = relationship("ReliabilityObjective", back_populates="evaluations")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String, primary_key=True, default=generate_uuid)
    objective_id = Column(String, ForeignKey("reliability_objectives.id"), nullable=False)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    severity = Column(String, nullable=False)
    
    condition_type = Column(String, nullable=False) # BURN_RATE_ABOVE, ERROR_BUDGET_BELOW, SLO_BREACHED
    threshold = Column(Float, nullable=True)
    
    short_window = Column(String, nullable=True)
    long_window = Column(String, nullable=True)
    
    cooldown_seconds = Column(Integer, nullable=False, default=3600)
    auto_create_incident = Column(Boolean, default=True)
    
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    objective = relationship("ReliabilityObjective", back_populates="alert_rules")
    alerts = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    rule_id = Column(String, ForeignKey("alert_rules.id"), nullable=False)
    objective_id = Column(String, ForeignKey("reliability_objectives.id"), nullable=False)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False) # OPEN, ACKNOWLEDGED, RESOLVED, SUPPRESSED
    
    triggered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    acknowledged_by = Column(String, nullable=True)
    resolved_by = Column(String, nullable=True)
    
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)
    deduplication_key = Column(String, nullable=False, index=True)
    
    summary = Column(String, nullable=False)
    evidence = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    rule = relationship("AlertRule", back_populates="alerts")
    objective = relationship("ReliabilityObjective", back_populates="alerts")
    incident = relationship("Incident")
