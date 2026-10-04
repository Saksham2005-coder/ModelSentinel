from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import os

from app.db.session import SessionLocal
from app.schemas.monitoring import (
    MonitoringRunResponse, MonitoringRunDetailResponse,
    MetricResultResponse, FeatureMonitoringResultResponse,
    DataQualityResultResponse, PredictionMonitoringResultResponse,
    SegmentAnalysisResultResponse, MonitoringRunCreate
)
from app.models.model import Model
from app.models.monitoring import (
    MonitoringRun, MetricResult, FeatureMonitoringResult,
    DataQualityResult, PredictionMonitoringResult, SegmentAnalysisResult
)
from app.monitoring.runner import run_monitoring_job

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _get_model(db: Session, model_id: str):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.get("/runs", response_model=List[MonitoringRunResponse])
def get_monitoring_runs(
    model_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    _get_model(db, model_id)
    return db.query(MonitoringRun)\
             .filter(MonitoringRun.model_id == model_id)\
             .order_by(desc(MonitoringRun.created_at))\
             .limit(limit).all()

@router.post("/runs", response_model=MonitoringRunResponse, status_code=201)
def create_monitoring_run(
    model_id: str,
    run_in: MonitoringRunCreate,
    db: Session = Depends(get_db)
):
    _get_model(db, model_id)
    
    # In a real system, you'd fetch the dataset paths from config or blob storage based on timestamps.
    # For this phase's deterministic testing, we use local dummy files based on the model slug.
    model = db.query(Model).filter(Model.id == model_id).first()
    
    # Path relative to backend root where seed data will be saved
    baseline_path = os.path.join(os.getcwd(), 'data', f'{model.slug}_baseline.csv')
    current_path = os.path.join(os.getcwd(), 'data', f'{model.slug}_current.csv')
    
    # We define standard segments and columns for the demo
    target_col = 'target'
    pred_col = 'prediction'
    prob_col = 'probability'
    segments = [
        {'name': 'url_heavy', 'condition': 'url_count > 2'},
        {'name': 'normal', 'condition': 'url_count <= 2'}
    ]
    
    run = run_monitoring_job(
        db=db,
        model_id=model_id,
        model_version_id=run_in.model_version_id,
        baseline_path=baseline_path,
        current_path=current_path,
        target_col=target_col,
        pred_col=pred_col,
        prob_col=prob_col,
        segments=segments
    )
    
    return run

@router.get("/runs/{run_id}", response_model=MonitoringRunDetailResponse)
def get_monitoring_run(
    model_id: str,
    run_id: str,
    db: Session = Depends(get_db)
):
    _get_model(db, model_id)
    run = db.query(MonitoringRun).filter(MonitoringRun.id == run_id, MonitoringRun.model_id == model_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Monitoring run not found")
    return run

@router.get("/metrics", response_model=List[MetricResultResponse])
def get_metrics(
    model_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(MetricResult)\
             .join(MonitoringRun)\
             .filter(MonitoringRun.model_id == model_id)\
             .order_by(desc(MetricResult.created_at))\
             .limit(limit).all()

@router.get("/drift", response_model=List[FeatureMonitoringResultResponse])
def get_drift(
    model_id: str,
    run_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(FeatureMonitoringResult).join(MonitoringRun).filter(MonitoringRun.model_id == model_id)
    if run_id:
        query = query.filter(FeatureMonitoringResult.monitoring_run_id == run_id)
    return query.order_by(desc(FeatureMonitoringResult.created_at)).limit(limit).all()

@router.get("/data-quality", response_model=List[DataQualityResultResponse])
def get_data_quality(
    model_id: str,
    run_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(DataQualityResult).join(MonitoringRun).filter(MonitoringRun.model_id == model_id)
    if run_id:
        query = query.filter(DataQualityResult.monitoring_run_id == run_id)
    return query.order_by(desc(DataQualityResult.created_at)).limit(limit).all()

@router.get("/segments", response_model=List[SegmentAnalysisResultResponse])
def get_segments(
    model_id: str,
    run_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(SegmentAnalysisResult).join(MonitoringRun).filter(MonitoringRun.model_id == model_id)
    if run_id:
        query = query.filter(SegmentAnalysisResult.monitoring_run_id == run_id)
    return query.order_by(desc(SegmentAnalysisResult.created_at)).limit(limit).all()

@router.post("/runs/{run_id}/detect-incidents")
def detect_incidents_from_run(
    model_id: str,
    run_id: str,
    db: Session = Depends(get_db)
):
    from app.models.incident import Incident
    from app.schemas.incident import IncidentResponse
    from app.incidents.detector import process_monitoring_run
    
    run = db.query(MonitoringRun).filter(MonitoringRun.id == run_id, MonitoringRun.model_id == model_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Monitoring run not found")
        
    incident = process_monitoring_run(db, run)
    
    if incident:
        # Return as IncidentResponse dict or just the object
        # Since we just want to know if it was triggered, we can return the incident info
        return {"message": "Incident detected and processed", "incident_id": incident.id}
    return {"message": "No incidents detected from this monitoring run."}
