import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_now() -> datetime:
    return datetime.now(timezone.utc)

class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    patch_proposal_id = Column(String, ForeignKey("patch_proposals.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    repository_snapshot_id = Column(String, ForeignKey("repository_snapshots.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String, nullable=False, default="queued") # queued, preparing, patch_applied, static_validation, testing, ml_evaluation, segment_evaluation, security_scan, completed, failed, cancelled, timed_out
    verdict = Column(String, nullable=True) # PASS, PARTIAL, FAIL, INCONCLUSIVE
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_now, onupdate=get_now, nullable=False)

    patch_proposal = relationship("PatchProposal")
    incident = relationship("Incident")
    snapshot = relationship("RepositorySnapshot")
    
    checks = relationship("ValidationCheck", back_populates="validation_run", cascade="all, delete-orphan", order_by="ValidationCheck.created_at")
    metrics = relationship("ValidationMetric", back_populates="validation_run", cascade="all, delete-orphan", order_by="ValidationMetric.created_at")
    artifacts = relationship("ValidationArtifact", back_populates="validation_run", cascade="all, delete-orphan", order_by="ValidationArtifact.created_at")


class ValidationCheck(Base):
    __tablename__ = "validation_checks"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    validation_run_id = Column(String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False)
    check_type = Column(String, nullable=False) # syntax, static, unit_test, integration_test, ml_evaluation, segment_regression, security, dependency, custom
    name = Column(String, nullable=False)
    status = Column(String, nullable=False) # passed, failed, warning, skipped, error
    
    exit_code = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    summary = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    validation_run = relationship("ValidationRun", back_populates="checks")


class ValidationMetric(Base):
    __tablename__ = "validation_metrics"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    validation_run_id = Column(String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String, nullable=False)
    
    baseline_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    patched_value = Column(Float, nullable=False)
    delta = Column(Float, nullable=False)
    
    threshold = Column(Float, nullable=True)
    status = Column(String, nullable=False) # recovered, regressed, unchanged
    segment_name = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    validation_run = relationship("ValidationRun", back_populates="metrics")


class ValidationArtifact(Base):
    __tablename__ = "validation_artifacts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    validation_run_id = Column(String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False)
    artifact_type = Column(String, nullable=False) # log, report, diff, metrics_json
    path = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    validation_run = relationship("ValidationRun", back_populates="artifacts")
