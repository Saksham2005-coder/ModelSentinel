from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import SessionLocal
from app.schemas.telemetry import ProductionTelemetryResponse
from app.services.telemetry_service import telemetry_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProductionTelemetryResponse, status_code=201)
def upload_telemetry(
    model_id: str = Form(...),
    model_version_id: str = Form(...),
    source: str = Form(...),
    window_start: datetime = Form(...),
    window_end: datetime = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Ingest a new telemetry CSV window for a model.
    """
    return telemetry_service.process_telemetry(
        db=db,
        model_id=model_id,
        model_version_id=model_version_id,
        source=source,
        window_start=window_start,
        window_end=window_end,
        file=file
    )

@router.get("/", response_model=List[ProductionTelemetryResponse])
def get_telemetry_list(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return telemetry_service.get_telemetry_list(db=db, limit=limit)

@router.get("/{telemetry_id}", response_model=ProductionTelemetryResponse)
def get_telemetry(
    telemetry_id: str,
    db: Session = Depends(get_db)
):
    return telemetry_service.get_telemetry(db=db, telemetry_id=telemetry_id)
