from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
from app.models.model import Model, ModelVersion, ModelMetric
from app.schemas.model import ModelCreate, ModelUpdate, ModelVersionCreate, ModelVersionUpdate
from typing import Optional, List
import uuid

def get_models(
    db: Session, 
    search: Optional[str] = None,
    status: Optional[str] = None,
    framework: Optional[str] = None,
    task_type: Optional[str] = None,
    environment: Optional[str] = None,
    sort: Optional[str] = "updated_at",
    page: int = 1,
    limit: int = 20
):
    query = db.query(Model)
    
    if search:
        query = query.filter(Model.name.ilike(f"%{search}%"))
    if status:
        query = query.filter(Model.status == status)
    if framework:
        query = query.filter(Model.framework == framework)
    if task_type:
        query = query.filter(Model.task_type == task_type)
    if environment:
        query = query.filter(Model.environment == environment)
        
    if sort == "updated_at":
        query = query.order_by(desc(Model.updated_at))
    elif sort == "created_at":
        query = query.order_by(desc(Model.created_at))
    elif sort == "name":
        query = query.order_by(Model.name)
        
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    return {"items": items, "total": total, "page": page, "limit": limit}

def get_model(db: Session, model_id: str):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

def create_model(db: Session, model_in: ModelCreate):
    existing = db.query(Model).filter(Model.slug == model_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model slug already exists")
    
    model = Model(**model_in.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

def update_model(db: Session, model_id: str, model_in: ModelUpdate):
    model = get_model(db, model_id)
    update_data = model_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(model, field, value)
        
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

def delete_model(db: Session, model_id: str):
    model = get_model(db, model_id)
    db.delete(model)
    db.commit()
    return {"success": True}

# Versions
def get_model_versions(db: Session, model_id: str):
    return db.query(ModelVersion).filter(ModelVersion.model_id == model_id).order_by(desc(ModelVersion.created_at)).all()

def create_model_version(db: Session, model_id: str, version_in: ModelVersionCreate):
    model = get_model(db, model_id)
    existing = db.query(ModelVersion).filter(ModelVersion.model_id == model_id, ModelVersion.version == version_in.version).first()
    if existing:
        raise HTTPException(status_code=400, detail="Version already exists for this model")
        
    if version_in.is_active:
        db.query(ModelVersion).filter(ModelVersion.model_id == model_id).update({"is_active": False})
        
    version = ModelVersion(**version_in.model_dump(), model_id=model_id)
    db.add(version)
    db.commit()
    db.refresh(version)
    return version

def update_model_version(db: Session, model_id: str, version_id: str, version_in: ModelVersionUpdate):
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id, ModelVersion.model_id == model_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
        
    update_data = version_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(version, field, value)
        
    db.add(version)
    db.commit()
    db.refresh(version)
    return version

def activate_model_version(db: Session, model_id: str, version_id: str):
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id, ModelVersion.model_id == model_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
        
    # Deactivate all others
    db.query(ModelVersion).filter(ModelVersion.model_id == model_id).update({"is_active": False})
    
    # Activate this one
    version.is_active = True
    db.add(version)
    db.commit()
    db.refresh(version)
    return version

# Metrics
def get_model_metrics(db: Session, model_id: str):
    # Get all metrics for all versions of this model for charting
    # Usually you'd filter by version or return grouped, but for demo:
    return db.query(ModelMetric).join(ModelVersion).filter(ModelVersion.model_id == model_id).order_by(ModelMetric.recorded_at).all()
