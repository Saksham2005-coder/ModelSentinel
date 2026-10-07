from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
import uuid

from app.db.session import get_db
from app.services.model_intelligence_service import model_intelligence_service
from app.models.model import Model

router = APIRouter()

@router.get("/{model_id}/health")
def get_model_health(
    model_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get the current health score and status for a model."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    return model_intelligence_service.calculate_model_health(db, model_id)

@router.get("/{model_id}/versions/compare")
def compare_model_versions(
    model_id: str,
    v1: str = Query(..., description="First ModelVersion ID"),
    v2: str = Query(..., description="Second ModelVersion ID"),
    db: Session = Depends(get_db)
) -> Any:
    """Compare two model versions across various intelligence dimensions."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    return model_intelligence_service.get_version_comparison(db, model_id, v1, v2)

@router.get("/{model_id}/intelligence/features")
def get_feature_health(
    model_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get feature health intelligence for a model."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    return model_intelligence_service.get_feature_health(db, model_id)

@router.get("/{model_id}/intelligence/segments")
def get_segment_health(
    model_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get segment health intelligence for a model."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    return model_intelligence_service.get_segment_health(db, model_id)

@router.get("/{model_id}/intelligence")
def get_model_intelligence(
    model_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get comprehensive model intelligence including health, features, and segments."""
    health = model_intelligence_service.calculate_model_health(db, model_id)
    features = model_intelligence_service.get_feature_health(db, model_id)
    segments = model_intelligence_service.get_segment_health(db, model_id)
    
    return {
        "health": health,
        "features": features,
        "segments": segments
    }
