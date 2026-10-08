import os
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from datetime import datetime, timezone
import shutil
import uuid

from app.models.telemetry import ProductionTelemetry
from app.models.model import Model
from app.monitoring.runner import run_monitoring_job
from app.incidents.detector import process_monitoring_run

class TelemetryService:
    def __init__(self):
        self.data_dir = os.path.join(os.getcwd(), 'data', 'telemetry')
        os.makedirs(self.data_dir, exist_ok=True)

    def process_telemetry(
        self,
        db: Session,
        model_id: str,
        model_version_id: str,
        source: str,
        window_start: datetime,
        window_end: datetime,
        file: UploadFile
    ) -> ProductionTelemetry:
        
        # Validate model
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Idempotency check
        existing = db.query(ProductionTelemetry).filter(
            ProductionTelemetry.model_version_id == model_version_id,
            ProductionTelemetry.source == source,
            ProductionTelemetry.window_start == window_start,
            ProductionTelemetry.window_end == window_end
        ).first()

        if existing:
            return existing

        # Create record
        telemetry = ProductionTelemetry(
            model_id=model_id,
            model_version_id=model_version_id,
            source=source,
            window_start=window_start,
            window_end=window_end,
            status="VALIDATING"
        )
        db.add(telemetry)
        db.commit()
        db.refresh(telemetry)

        # Save file safely
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != '.csv':
            telemetry.status = "INVALID"
            telemetry.validation_errors = ["Only CSV files are supported"]
            db.commit()
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
            
        MAX_FILE_SIZE = 50 * 1024 * 1024 # 50 MB
        if getattr(file, 'size', 0) and file.size > MAX_FILE_SIZE:
            telemetry.status = "INVALID"
            telemetry.validation_errors = ["File exceeds 50MB limit"]
            db.commit()
            raise HTTPException(status_code=413, detail="File too large")

        file_path = os.path.join(self.data_dir, f"{telemetry.id}.csv")
        try:
            bytes_written = 0
            with open(file_path, "wb") as buffer:
                while chunk := file.file.read(8192):
                    bytes_written += len(chunk)
                    if bytes_written > MAX_FILE_SIZE:
                        raise ValueError("File exceeds maximum allowed size.")
                    buffer.write(chunk)
        except Exception as e:
            telemetry.status = "FAILED"
            telemetry.validation_errors = [f"File save failed: {str(e)}"]
            db.commit()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=413 if "maximum allowed size" in str(e) else 500, detail=str(e) if "maximum allowed size" in str(e) else "Could not save file")

        telemetry.file_path = file_path

        # Validate CSV content
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("Dataset is empty")
            if 'prediction' not in df.columns:
                raise ValueError("Missing 'prediction' column")
            
            telemetry.sample_count = len(df)
            telemetry.status = "VALID"
            db.commit()
        except Exception as e:
            telemetry.status = "INVALID"
            telemetry.validation_errors = [str(e)]
            db.commit()
            return telemetry

        # Run existing monitoring engine
        baseline_path = os.path.join(os.getcwd(), 'data', f'{model.slug}_baseline.csv')
        if not os.path.exists(baseline_path):
            telemetry.status = "FAILED"
            telemetry.validation_errors = ["Baseline data not found for model"]
            db.commit()
            return telemetry

        try:
            run = run_monitoring_job(
                db=db,
                model_id=model_id,
                model_version_id=model_version_id,
                baseline_path=baseline_path,
                current_path=file_path,
                target_col='target',
                pred_col='prediction',
                prob_col='probability' if 'probability' in df.columns else None,
                segments=[
                    {'name': 'url_heavy', 'condition': 'url_count > 2'},
                    {'name': 'normal', 'condition': 'url_count <= 2'}
                ] if 'url_count' in df.columns else None
            )
            
            telemetry.monitoring_run_id = run.id
            telemetry.status = "PROCESSED"
            
            # Detect incidents
            incident = process_monitoring_run(db, run)
            if incident:
                telemetry.incident_id = incident.id
            
            db.commit()
            db.refresh(telemetry)
            
            from app.services.reliability_service import reliability_service
            tel_event = reliability_service.emit_event(
                db=db,
                model_id=model_id,
                model_version_id=model_version_id,
                event_type="TELEMETRY_RECEIVED",
                source_type="telemetry",
                source_id=telemetry.id,
                title="Production Telemetry Received",
                summary=f"Received {telemetry.sample_count} samples from {source}.",
                status="success"
            )
            
            mon_event = reliability_service.emit_event(
                db=db,
                model_id=model_id,
                model_version_id=model_version_id,
                event_type="MONITORING_COMPLETED",
                source_type="monitoring_run",
                source_id=run.id,
                title="Monitoring Run Completed",
                summary="Deterministic monitoring completed on telemetry window.",
                status="success"
            )
            reliability_service.link_events(db, tel_event.id, mon_event.id, "TRIGGERED_BY")
            
        except Exception as e:
            telemetry.status = "FAILED"
            telemetry.validation_errors = [f"Monitoring failed: {str(e)}"]
            db.commit()

        return telemetry

    def get_telemetry_list(self, db: Session, limit: int = 50):
        return db.query(ProductionTelemetry).order_by(ProductionTelemetry.created_at.desc()).limit(limit).all()

    def get_telemetry(self, db: Session, telemetry_id: str):
        telemetry = db.query(ProductionTelemetry).filter(ProductionTelemetry.id == telemetry_id).first()
        if not telemetry:
            raise HTTPException(status_code=404, detail="Telemetry not found")
        return telemetry

telemetry_service = TelemetryService()
