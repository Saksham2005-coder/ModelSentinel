from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class MonitoringRunBase(BaseModel):
    model_id: str
    model_version_id: str
    run_type: str
    baseline_start: Optional[datetime] = None
    baseline_end: Optional[datetime] = None
    current_start: Optional[datetime] = None
    current_end: Optional[datetime] = None
    status: str = "pending"
    health_summary: Optional[str] = None

class MonitoringRunCreate(BaseModel):
    model_version_id: str
    run_type: str = "batch"
    baseline_start: Optional[datetime] = None
    baseline_end: Optional[datetime] = None
    current_start: Optional[datetime] = None
    current_end: Optional[datetime] = None

class MonitoringRunResponse(MonitoringRunBase):
    id: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class MetricResultResponse(BaseModel):
    id: str
    monitoring_run_id: str
    metric_name: str
    metric_value: float
    metric_type: str
    dataset_name: Optional[str]
    segment_name: Optional[str]
    threshold: Optional[float]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class FeatureMonitoringResultResponse(BaseModel):
    id: str
    monitoring_run_id: str
    feature_name: str
    feature_type: str
    drift_method: str
    drift_score: float
    threshold: Optional[float]
    status: str
    baseline_summary: Optional[Dict[str, Any]]
    current_summary: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class DataQualityResultResponse(BaseModel):
    id: str
    monitoring_run_id: str
    metric_name: str
    value: float
    threshold: Optional[float]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class PredictionMonitoringResultResponse(BaseModel):
    id: str
    monitoring_run_id: str
    prediction_metric: str
    value: float
    baseline_value: Optional[float]
    threshold: Optional[float]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class SegmentAnalysisResultResponse(BaseModel):
    id: str
    monitoring_run_id: str
    segment_name: str
    sample_count: float
    primary_metric: str
    baseline_metric_value: Optional[float]
    current_metric_value: float
    change: Optional[float]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class MonitoringRunDetailResponse(MonitoringRunResponse):
    metrics: List[MetricResultResponse] = []
    feature_results: List[FeatureMonitoringResultResponse] = []
    data_quality_results: List[DataQualityResultResponse] = []
    prediction_results: List[PredictionMonitoringResultResponse] = []
    segment_results: List[SegmentAnalysisResultResponse] = []
