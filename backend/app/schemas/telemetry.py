from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class ProductionTelemetryBase(BaseModel):
    model_id: str
    model_version_id: str
    source: str
    window_start: datetime
    window_end: datetime

class ProductionTelemetryCreate(ProductionTelemetryBase):
    pass

class ProductionTelemetryResponse(ProductionTelemetryBase):
    id: str
    received_at: datetime
    sample_count: Optional[int] = None
    status: str
    file_path: Optional[str] = None
    validation_errors: Optional[List[Any]] = None
    monitoring_run_id: Optional[str] = None
    incident_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
