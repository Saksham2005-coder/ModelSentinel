from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class RegressionCase(Base):
    __tablename__ = "regression_cases"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    source_incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    incident_memory_id = Column(String, ForeignKey("incident_memories.id"), nullable=False)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    failure_signature = Column(Text, nullable=True) # Textual/JSON signature of failure
    expected_behavior = Column(Text, nullable=True)

    baseline_metrics = Column(JSON, nullable=True) # Snapshot of what healthy looks like
    failure_metrics = Column(JSON, nullable=True)  # Snapshot of what broken looked like
    acceptance_criteria = Column(JSON, nullable=True) # Constraints that must be passed

    affected_features = Column(JSON, nullable=True)
    affected_segments = Column(JSON, nullable=True)
    severity = Column(String, nullable=False)

    status = Column(String, nullable=False, default="active") # active, retired, etc
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    source_incident = relationship("Incident")
    incident_memory = relationship("IncidentMemory")
    model = relationship("Model", foreign_keys=[model_id])
    model_version = relationship("ModelVersion", foreign_keys=[model_version_id])
    runs = relationship("RegressionRun", back_populates="regression_case", cascade="all, delete-orphan")


class RegressionRun(Base):
    __tablename__ = "regression_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    regression_case_id = Column(String, ForeignKey("regression_cases.id"), nullable=False)
    validation_run_id = Column(String, ForeignKey("validation_runs.id"), nullable=True)
    
    status = Column(String, nullable=False) # PASS, FAIL, PARTIAL, ERROR
    failure_reason = Column(Text, nullable=True)

    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    regression_case = relationship("RegressionCase", back_populates="runs")
    validation_run = relationship("ValidationRun")
    results = relationship("RegressionResult", back_populates="run", cascade="all, delete-orphan")


class RegressionResult(Base):
    __tablename__ = "regression_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    regression_run_id = Column(String, ForeignKey("regression_runs.id"), nullable=False)
    
    metric_name = Column(String, nullable=False)
    segment_name = Column(String, nullable=True)
    
    expected_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    delta = Column(Float, nullable=True)
    
    status = Column(String, nullable=False) # PASS, FAIL

    # Relationship
    run = relationship("RegressionRun", back_populates="results")
