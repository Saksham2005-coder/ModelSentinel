from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    run_type = Column(String, nullable=False) # e.g., 'batch', 'scheduled'
    baseline_start = Column(DateTime(timezone=True), nullable=True)
    baseline_end = Column(DateTime(timezone=True), nullable=True)
    current_start = Column(DateTime(timezone=True), nullable=True)
    current_end = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="pending") # pending, running, completed, failed
    health_summary = Column(String, nullable=True) # healthy, warning, critical
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    metrics = relationship("MetricResult", back_populates="run", cascade="all, delete-orphan")
    feature_results = relationship("FeatureMonitoringResult", back_populates="run", cascade="all, delete-orphan")
    data_quality_results = relationship("DataQualityResult", back_populates="run", cascade="all, delete-orphan")
    prediction_results = relationship("PredictionMonitoringResult", back_populates="run", cascade="all, delete-orphan")
    segment_results = relationship("SegmentAnalysisResult", back_populates="run", cascade="all, delete-orphan")

class MetricResult(Base):
    __tablename__ = "metric_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String, nullable=False) # e.g., 'performance'
    dataset_name = Column(String, nullable=True)
    segment_name = Column(String, nullable=True)
    threshold = Column(Float, nullable=True)
    status = Column(String, nullable=False) # healthy, warning, critical
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("MonitoringRun", back_populates="metrics")

class FeatureMonitoringResult(Base):
    __tablename__ = "feature_monitoring_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=False)
    feature_name = Column(String, nullable=False)
    feature_type = Column(String, nullable=False) # numeric, categorical
    drift_method = Column(String, nullable=False) # PSI, KS
    drift_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=True)
    status = Column(String, nullable=False) # healthy, warning, critical
    baseline_summary = Column(JSON, nullable=True) # e.g., mean, std, or distribution map
    current_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("MonitoringRun", back_populates="feature_results")

class DataQualityResult(Base):
    __tablename__ = "data_quality_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=False)
    metric_name = Column(String, nullable=False) # row_count, missing_value_percentage
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("MonitoringRun", back_populates="data_quality_results")

class PredictionMonitoringResult(Base):
    __tablename__ = "prediction_monitoring_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=False)
    prediction_metric = Column(String, nullable=False) # e.g., probability_drift, class_drift
    value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("MonitoringRun", back_populates="prediction_results")

class SegmentAnalysisResult(Base):
    __tablename__ = "segment_analysis_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    monitoring_run_id = Column(String, ForeignKey("monitoring_runs.id"), nullable=False)
    segment_name = Column(String, nullable=False)
    sample_count = Column(Float, nullable=False) # store as float for uniform schema, or Int
    primary_metric = Column(String, nullable=False)
    baseline_metric_value = Column(Float, nullable=True)
    current_metric_value = Column(Float, nullable=False)
    change = Column(Float, nullable=True) # percentage change
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("MonitoringRun", back_populates="segment_results")
