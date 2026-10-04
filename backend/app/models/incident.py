from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_key = Column(String, unique=True, index=True, nullable=False) # fingerprint
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    severity = Column(String, nullable=False) # critical, high, medium, low
    status = Column(String, nullable=False, default="detected") # detected, acknowledged, investigating, fix_generated, validation, resolved, suppressed
    category = Column(String, nullable=False) # performance, data_drift, prediction_drift, data_quality, segment_degradation, multiple
    
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    signals = relationship("IncidentSignal", back_populates="incident", cascade="all, delete-orphan")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan")
    evidence = relationship("IncidentEvidence", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    
    model = relationship("Model")

class IncidentSignal(Base):
    __tablename__ = "incident_signals"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    
    source_type = Column(String, nullable=False) # metric, feature_drift, prediction_drift, data_quality, segment
    source_id = Column(String, nullable=True) # refers to the specific result id (MetricResult.id, etc.) if tracking is desired
    signal_name = Column(String, nullable=False) # e.g. "url_length", "f1_score"
    
    observed_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    comparison = Column(String, nullable=True) # >, <, !=
    status = Column(String, nullable=False) # warning, critical
    explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="signals")

class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    
    event_type = Column(String, nullable=False) # incident_detected, signal_added, severity_changed, status_changed, etc.
    message = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="events")

class IncidentEvidence(Base):
    __tablename__ = "incident_evidence"

    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=False)
    snapshot = Column(JSON, nullable=False) # stores a copy of the metrics/drift data that triggered it
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="evidence")
    monitoring_run = relationship("MonitoringRun")
