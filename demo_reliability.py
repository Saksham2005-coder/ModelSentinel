import os
import sys
import json
import uuid
import datetime
import importlib

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
os.environ["DATABASE_URL"] = "sqlite:///./demo_reliability.db"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base

# Import all models to ensure they are registered with Base
import app.models.change_risk
import app.models.deployment
import app.models.deployment_verification
import app.models.incident
import app.models.incident_memory
import app.models.investigation
import app.models.model
import app.models.monitoring
import app.models.patch
import app.models.policy
import app.models.pull_request
import app.models.regression
import app.models.reliability
import app.models.repository
import app.models.telemetry
import app.models.validation

from app.services.reliability_service import reliability_service

engine = create_engine("sqlite:///./demo_reliability.db")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    db = SessionLocal()
    
    print("1. Setup: Create Model, Version")
    model = app.models.model.Model(name="Fraud Detection v4", slug="fraud-v4", framework="xgboost", task_type="classification", primary_metric="roc_auc", status="active")
    db.add(model)
    db.commit()
    db.refresh(model)

    version = app.models.model.ModelVersion(model_id=model.id, version="v4.0.0", is_active=True)
    db.add(version)
    db.commit()
    db.refresh(version)
    
    print("2. Initial State: Send healthy telemetry windows")
    tel_event_1 = reliability_service.emit_event(db, model.id, version.id, "TELEMETRY_RECEIVED", "telemetry", str(uuid.uuid4()), "Production Telemetry Received", summary="Healthy baseline.")
    mon_event_1 = reliability_service.emit_event(db, model.id, version.id, "MONITORING_COMPLETED", "monitoring_run", str(uuid.uuid4()), "Monitoring Run Completed", summary="No drift.")
    reliability_service.link_events(db, tel_event_1.id, mon_event_1.id, "TRIGGERED_BY")
    
    print("3. Degradation: Send anomalous telemetry window")
    tel_event_deg = reliability_service.emit_event(db, model.id, version.id, "TELEMETRY_RECEIVED", "telemetry", str(uuid.uuid4()), "Production Telemetry Received", summary="Anomalous predictions detected.")
    
    print("4. Monitoring Run & Incident")
    mon_event_deg = reliability_service.emit_event(db, model.id, version.id, "MONITORING_COMPLETED", "monitoring_run", str(uuid.uuid4()), "Monitoring Run Completed", summary="Drift detected.")
    deg_event = reliability_service.emit_event(db, model.id, version.id, "DEGRADATION_DETECTED", "monitoring_run", mon_event_deg.source_id, "Model Degradation Detected", summary="Critical drift in amount feature.")
    
    incident = app.models.incident.Incident(incident_key="INC-DEMO-1", model_id=model.id, model_version_id=version.id, title="Fraud Prob Drift", status="active", severity="high", category="data_drift")
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    inc_event = reliability_service.emit_event(db, model.id, version.id, "INCIDENT_CREATED", "incident", incident.id, "Incident Created", summary="High severity data drift incident.")
    
    reliability_service.link_events(db, tel_event_deg.id, mon_event_deg.id, "TRIGGERED_BY")
    reliability_service.link_events(db, mon_event_deg.id, deg_event.id, "CAUSED")
    reliability_service.link_events(db, deg_event.id, inc_event.id, "ESCALATED_TO")
    
    print("5. Investigation & Root Cause")
    inv_event = reliability_service.emit_event(db, model.id, version.id, "INVESTIGATION_STARTED", "investigation", str(uuid.uuid4()), "AI Investigation Started", summary="Running drift analysis.")
    rc_event = reliability_service.emit_event(db, model.id, version.id, "ROOT_CAUSE_IDENTIFIED", "investigation", inv_event.source_id, "Root Cause Identified", summary="Feature shift in 'amount'.")
    
    reliability_service.link_events(db, inc_event.id, inv_event.id, "TRIGGERED_BY")
    reliability_service.link_events(db, inv_event.id, rc_event.id, "RESULTED_IN")
    
    print("6. Patch & Validation")
    patch_event = reliability_service.emit_event(db, model.id, version.id, "PATCH_PROPOSED", "patch_proposal", str(uuid.uuid4()), "Patch Proposed", summary="Retrain with recent data.")
    val_event = reliability_service.emit_event(db, model.id, version.id, "VALIDATION_COMPLETED", "validation_run", str(uuid.uuid4()), "Validation Completed", summary="Metrics recovered to 0.92 ROC-AUC.")
    pr_event = reliability_service.emit_event(db, model.id, version.id, "PULL_REQUEST_CREATED", "pull_request", str(uuid.uuid4()), "Pull Request Created", summary="Fix Fraud Model.")
    
    reliability_service.link_events(db, rc_event.id, patch_event.id, "RESOLVED_BY")
    reliability_service.link_events(db, patch_event.id, val_event.id, "VERIFIED_BY")
    reliability_service.link_events(db, val_event.id, pr_event.id, "LED_TO")
    
    print("7. Deployment")
    dep_event = reliability_service.emit_event(db, model.id, version.id, "DEPLOYMENT_COMPLETED", "deployment", str(uuid.uuid4()), "Deployment Completed", summary="Deployed via gate approval.")
    reliability_service.link_events(db, pr_event.id, dep_event.id, "LED_TO")
    
    print("8. Post-Deploy Failure & Verification")
    tel_event_post = reliability_service.emit_event(db, model.id, version.id, "TELEMETRY_RECEIVED", "telemetry", str(uuid.uuid4()), "Production Telemetry Received", summary="Anomalous post-deploy.")
    mon_event_post = reliability_service.emit_event(db, model.id, version.id, "MONITORING_COMPLETED", "monitoring_run", str(uuid.uuid4()), "Monitoring Run Completed", summary="Failed check.")
    
    verif_event = reliability_service.emit_event(db, model.id, version.id, "VERIFICATION_COMPLETED", "verification_run", str(uuid.uuid4()), "Deployment Verification Failed", summary="Critical degradation immediately after deploy.")
    post_deg_event = reliability_service.emit_event(db, model.id, version.id, "POST_DEPLOYMENT_DEGRADATION", "verification_run", verif_event.source_id, "Post-Deployment Degradation", summary="Linked to recent deployment.")
    
    incident_post = app.models.incident.Incident(incident_key="INC-DEMO-2", model_id=model.id, model_version_id=version.id, title="Post Deploy Crash", status="active", severity="critical", category="performance")
    db.add(incident_post)
    db.commit()
    db.refresh(incident_post)
    
    inc_event_post = reliability_service.emit_event(db, model.id, version.id, "INCIDENT_CREATED", "incident", incident_post.id, "Incident Created", summary="Critical post-deployment failure.")
    
    reliability_service.link_events(db, dep_event.id, tel_event_post.id, "MONITORED_BY")
    reliability_service.link_events(db, tel_event_post.id, mon_event_post.id, "TRIGGERED_BY")
    reliability_service.link_events(db, mon_event_post.id, verif_event.id, "EVALUATED_BY")
    reliability_service.link_events(db, verif_event.id, post_deg_event.id, "RESULTED_IN")
    reliability_service.link_events(db, post_deg_event.id, inc_event_post.id, "ESCALATED_TO")
    reliability_service.link_events(db, dep_event.id, post_deg_event.id, "CAUSED")
    
    print("10. Final State: Request the full causal graph")
    graph = reliability_service.get_incident_graph(db, inc_event.id)
    with open("reliability_demo_graph.json", "w") as f:
        json.dump(graph, f, indent=2, default=str)
    print("Success: reliability_demo_graph.json written.")
        
    db.close()

if __name__ == "__main__":
    main()
