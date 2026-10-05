from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    framework = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    problem_type = Column(String, nullable=True)
    primary_metric = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")  # active, degraded, archived, draft
    environment = Column(String, nullable=False, default="development")  # development, staging, production
    repository_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")

class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (
        UniqueConstraint('model_id', 'version', name='uq_model_version'),
    )

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    version = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    artifact_uri = Column(String, nullable=True)
    git_commit = Column(String, nullable=True)
    repository_snapshot_id = Column(String, nullable=True)
    framework_version = Column(String, nullable=True)
    python_version = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=False)

    model = relationship("Model", back_populates="versions")
    metrics = relationship("ModelMetric", back_populates="model_version", cascade="all, delete-orphan")

class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    dataset_name = Column(String, nullable=True)
    evaluation_type = Column(String, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    model_version = relationship("ModelVersion", back_populates="metrics")
