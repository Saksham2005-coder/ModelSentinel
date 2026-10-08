from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReliabilityObjectiveBase(BaseModel):
    model_id: str
    name: str
    description: Optional[str] = None
    objective_type: str = Field(..., description="model_performance, data_quality, feature_drift, prediction_drift")
    metric_name: str
    comparison_operator: str = Field(..., description=">=, <=, >, <")
    target_value: float
    evaluation_window: str = Field(..., description="1h, 6h, 24h, 7d, 30d")
    enabled: bool = True
    severity: str = "medium"

class ReliabilityObjectiveCreate(ReliabilityObjectiveBase):
    pass

class ReliabilityObjectiveUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objective_type: Optional[str] = None
    metric_name: Optional[str] = None
    comparison_operator: Optional[str] = None
    target_value: Optional[float] = None
    evaluation_window: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[str] = None

class ReliabilityObjectiveInDBBase(ReliabilityObjectiveBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReliabilityObjective(ReliabilityObjectiveInDBBase):
    pass

class SLOEvaluationBase(BaseModel):
    objective_id: str
    model_id: str
    model_version_id: Optional[str] = None
    evaluation_start: datetime
    evaluation_end: datetime
    measured_value: Optional[float] = None
    target_value: float
    comparison_operator: str
    status: str
    compliance_ratio: Optional[float] = None
    error_budget_total: Optional[float] = None
    error_budget_consumed: Optional[float] = None
    error_budget_remaining: Optional[float] = None
    burn_rate: Optional[float] = None
    sample_count: Optional[int] = None

class SLOEvaluation(SLOEvaluationBase):
    id: str
    evaluated_at: datetime

    class Config:
        from_attributes = True

class AlertRuleBase(BaseModel):
    objective_id: str
    name: str
    enabled: bool = True
    severity: str
    condition_type: str = Field(..., description="BURN_RATE_ABOVE, ERROR_BUDGET_BELOW, SLO_BREACHED")
    threshold: Optional[float] = None
    short_window: Optional[str] = None
    long_window: Optional[str] = None
    cooldown_seconds: int = 3600
    auto_create_incident: bool = True

class AlertRuleCreate(AlertRuleBase):
    pass

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[str] = None
    condition_type: Optional[str] = None
    threshold: Optional[float] = None
    short_window: Optional[str] = None
    long_window: Optional[str] = None
    cooldown_seconds: Optional[int] = None
    auto_create_incident: Optional[bool] = None

class AlertRule(AlertRuleBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    rule_id: str
    objective_id: str
    model_id: str
    severity: str
    status: str
    deduplication_key: str
    summary: str
    evidence: Optional[Dict[str, Any]] = None

class Alert(AlertBase):
    id: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    incident_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
