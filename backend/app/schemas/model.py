from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# -------- METRICS --------
class MetricResponse(BaseModel):
    id: str
    model_version_id: str
    metric_name: str
    metric_value: float
    dataset_name: Optional[str] = None
    evaluation_type: Optional[str] = None
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

# -------- MODEL VERSIONS --------
class ModelVersionBase(BaseModel):
    version: str
    description: Optional[str] = None
    artifact_uri: Optional[str] = None
    git_commit: Optional[str] = None
    framework_version: Optional[str] = None
    python_version: Optional[str] = None
    is_active: bool = False

class ModelVersionCreate(ModelVersionBase):
    pass

class ModelVersionUpdate(BaseModel):
    description: Optional[str] = None
    artifact_uri: Optional[str] = None
    git_commit: Optional[str] = None
    framework_version: Optional[str] = None
    python_version: Optional[str] = None

class ModelVersionResponse(ModelVersionBase):
    id: str
    model_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

# -------- MODELS --------
class ModelBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    framework: str
    task_type: str
    problem_type: Optional[str] = None
    primary_metric: str
    owner: Optional[str] = None
    status: str = "draft"
    environment: str = "development"
    repository_id: Optional[str] = None

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    task_type: Optional[str] = None
    problem_type: Optional[str] = None
    primary_metric: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    environment: Optional[str] = None
    repository_id: Optional[str] = None

class ModelResponse(ModelBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class ModelDetailResponse(ModelResponse):
    versions: List[ModelVersionResponse] = []

class ModelListResponse(BaseModel):
    items: List[ModelResponse]
    total: int
    page: int
    limit: int
