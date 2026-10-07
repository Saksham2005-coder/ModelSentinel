from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class ProductionTelemetry(Base):
    __tablename__ = "production_telemetries"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    source = Column(String, nullable=False)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    sample_count = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="RECEIVED") # RECEIVED, VALIDATING, VALID, INVALID, PROCESSED, FAILED
    file_path = Column(String, nullable=True)
    validation_errors = Column(JSON, nullable=True)
    
    # Relationships to existing pipeline
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    monitoring_run = relationship("MonitoringRun")
    incident = relationship("Incident")
