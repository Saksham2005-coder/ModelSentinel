from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.model import (
    ModelCreate, ModelUpdate, ModelResponse, ModelDetailResponse, ModelListResponse,
    ModelVersionCreate, ModelVersionUpdate, ModelVersionResponse, MetricResponse
)
from app.services import model_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=ModelListResponse)
def get_models(
    search: Optional[str] = None,
    status: Optional[str] = None,
    framework: Optional[str] = None,
    task_type: Optional[str] = None,
    environment: Optional[str] = None,
    sort: Optional[str] = Query("updated_at"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return model_service.get_models(db, search, status, framework, task_type, environment, sort, page, limit)

@router.post("", response_model=ModelResponse, status_code=201)
def create_model(
    model_in: ModelCreate,
    db: Session = Depends(get_db)
):
    return model_service.create_model(db, model_in)

@router.get("/{model_id}", response_model=ModelDetailResponse)
def get_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    return model_service.get_model(db, model_id)

@router.patch("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: str,
    model_in: ModelUpdate,
    db: Session = Depends(get_db)
):
    return model_service.update_model(db, model_id, model_in)

@router.delete("/{model_id}", status_code=204)
def delete_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    model_service.delete_model(db, model_id)
    return None

# --- VERSIONS ---

@router.get("/{model_id}/versions", response_model=List[ModelVersionResponse])
def get_model_versions(
    model_id: str,
    db: Session = Depends(get_db)
):
    return model_service.get_model_versions(db, model_id)

@router.post("/{model_id}/versions", response_model=ModelVersionResponse, status_code=201)
def create_model_version(
    model_id: str,
    version_in: ModelVersionCreate,
    db: Session = Depends(get_db)
):
    return model_service.create_model_version(db, model_id, version_in)

@router.patch("/{model_id}/versions/{version_id}", response_model=ModelVersionResponse)
def update_model_version(
    model_id: str,
    version_id: str,
    version_in: ModelVersionUpdate,
    db: Session = Depends(get_db)
):
    return model_service.update_model_version(db, model_id, version_id, version_in)

@router.post("/{model_id}/versions/{version_id}/activate", response_model=ModelVersionResponse)
def activate_model_version(
    model_id: str,
    version_id: str,
    db: Session = Depends(get_db)
):
    return model_service.activate_model_version(db, model_id, version_id)

# --- METRICS ---

@router.get("/{model_id}/metrics", response_model=List[MetricResponse])
def get_model_metrics(
    model_id: str,
    db: Session = Depends(get_db)
):
    return model_service.get_model_metrics(db, model_id)
