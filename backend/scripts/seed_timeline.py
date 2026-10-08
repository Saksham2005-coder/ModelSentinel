import sys
import os
import uuid
import random
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.append("c:/Users/Saksham Gupta/Desktop/ModelSentinel/backend")
from app.db.session import SessionLocal
from app.models.model import Model
from app.services.reliability_service import reliability_service

def seed():
    db = SessionLocal()
    
    # Get any model
    model = db.query(Model).first()
    if not model:
        print("No models found!")
        return

    model_id = model.id
    print(f"Seeding events for model {model.name} ({model_id})")
    
    # Clean up existing events for this model to avoid duplicates
    from app.models.reliability import ReliabilityEvent, ReliabilityEdge
    events = db.query(ReliabilityEvent).filter(ReliabilityEvent.model_id == model_id).all()
    event_ids = [e.id for e in events]
    if event_ids:
        db.query(ReliabilityEdge).filter(ReliabilityEdge.from_event_id.in_(event_ids)).delete(synchronize_session=False)
        db.query(ReliabilityEdge).filter(ReliabilityEdge.to_event_id.in_(event_ids)).delete(synchronize_session=False)
        db.query(ReliabilityEvent).filter(ReliabilityEvent.id.in_(event_ids)).delete(synchronize_session=False)
        db.commit()

    base_time = datetime.now(timezone.utc) - timedelta(hours=2)

    # 1. Telemetry Received
    tel_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="TELEMETRY_RECEIVED", source_type="telemetry", source_id="tel-123", 
        title="Production Telemetry Received", status="success", summary="Received 50,000 samples from production.", occurred_at=base_time
    )

    # 2. Monitoring Completed
    mon_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="MONITORING_COMPLETED", source_type="monitoring_run", source_id="mon-123", 
        title="Monitoring Run Completed", status="success", summary="Deterministic monitoring completed on telemetry window.", occurred_at=base_time + timedelta(minutes=2)
    )
    reliability_service.link_events(db, tel_event.id, mon_event.id, "TRIGGERED_BY")

    # 3. Degradation Detected
    deg_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="DEGRADATION_DETECTED", source_type="monitoring_run", source_id="mon-123", 
        title="Performance Degradation Detected", severity="critical", summary="Detected 3 signals indicating F1 score drop to 0.72.", occurred_at=base_time + timedelta(minutes=3)
    )
    reliability_service.link_events(db, mon_event.id, deg_event.id, "TRIGGERED_BY")

    # 4. Incident Created
    inc_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="INCIDENT_CREATED", source_type="incident", source_id="inc-123", 
        title="Critical Performance Drop", severity="critical", summary="Incident INC-842 created.", occurred_at=base_time + timedelta(minutes=4)
    )
    reliability_service.link_events(db, deg_event.id, inc_event.id, "RESULTED_IN")

    # 5. Investigation Started
    inv_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="INVESTIGATION_STARTED", source_type="investigation", source_id="inv-123", 
        title="AI Investigation Started", status="running", summary="AI investigation engine launched to find root cause.", occurred_at=base_time + timedelta(minutes=6)
    )
    reliability_service.link_events(db, inc_event.id, inv_event.id, "RESULTED_IN")

    # 6. Root Cause Identified
    rc_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="ROOT_CAUSE_IDENTIFIED", source_type="investigation", source_id="inv-123", 
        title="Root Cause Identified", status="success", summary="Feature drift in user_age caused model performance degradation.", occurred_at=base_time + timedelta(minutes=15)
    )
    reliability_service.link_events(db, inv_event.id, rc_event.id, "RESULTED_IN")

    # 7. Patch Proposed
    patch_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="PATCH_PROPOSED", source_type="patch", source_id="pat-123", 
        title="Patch Proposed", status="review", summary="AI proposed fixing data pipeline imputation logic.", occurred_at=base_time + timedelta(minutes=20)
    )
    reliability_service.link_events(db, rc_event.id, patch_event.id, "FIXED_BY")

    # 8. Validation Completed
    val_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="VALIDATION_COMPLETED", source_type="validation", source_id="val-123", 
        title="Validation PASS", status="success", summary="All checks passed. Metrics successfully recovered without regression.", occurred_at=base_time + timedelta(minutes=35)
    )
    reliability_service.link_events(db, patch_event.id, val_event.id, "VALIDATED_BY")

    # 9. Pull Request Created
    pr_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="PULL_REQUEST_CREATED", source_type="pull_request", source_id="pr-123", 
        title="Pull Request Created", status="active", summary="Automated PR #42 created for incident INC-842", occurred_at=base_time + timedelta(minutes=40)
    )
    reliability_service.link_events(db, val_event.id, pr_event.id, "TRIGGERED_BY")

    # 10. Deployment Completed
    dep_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="DEPLOYMENT_COMPLETED", source_type="deployment", source_id="dep-123", 
        title="Deployment Completed", status="success", summary="Fix deployed to production.", occurred_at=base_time + timedelta(minutes=90)
    )
    reliability_service.link_events(db, pr_event.id, dep_event.id, "RESULTED_IN")

    # 11. Verification Completed
    ver_event = reliability_service.emit_event(
        db=db, model_id=model_id, event_type="VERIFICATION_COMPLETED", source_type="deployment_verification", source_id="ver-123", 
        title="Deployment Verification HEALTHY", status="success", summary="Deployment health evaluated: HEALTHY", occurred_at=base_time + timedelta(minutes=95)
    )
    reliability_service.link_events(db, dep_event.id, ver_event.id, "VALIDATED_BY")

    print("Successfully seeded Reliability Graph!")
    db.close()

if __name__ == "__main__":
    seed()
