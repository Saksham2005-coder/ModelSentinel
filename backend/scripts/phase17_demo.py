import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.models.model import Model, ModelVersion
from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory
from app.models.resolution_memory import ResolutionMemory
import app.models.monitoring
import app.models.investigation
import app.models.patch
import app.models.validation
import app.models.deployment
from app.services.resolution_memory_service import resolution_memory_service
import json
import uuid

def run_demo():
    db = SessionLocal()
    print("--- PHASE 17 VERIFICATION DEMO SCENARIO ---")
    try:
        print("\n1. Setup Historical Incident with Resolution Memory...")
        m = Model(name="Demo Model", slug=f"demo-model-{uuid.uuid4().hex[:8]}", framework="xgboost", task_type="classification", primary_metric="accuracy")
        db.add(m)
        db.commit()
        db.refresh(m)
        
        mv = ModelVersion(model_id=m.id, version="v1.0")
        db.add(mv)
        db.commit()
        
        inc_hist = Incident(model_id=m.id, model_version_id=mv.id, incident_key=f"INC-HIST-{uuid.uuid4().hex[:8]}", title="Historical Drift", severity="high", status="resolved", category="data_drift")
        db.add(inc_hist)
        db.commit()
        db.refresh(inc_hist)
        
        mem = IncidentMemory(
            incident_id=inc_hist.id, model_id=m.id, model_version_id=mv.id,
            title="Historical Drift Memory", severity="high", resolution_status="resolved",
            resolution_summary="Fixed with feature engineering"
        )
        db.add(mem)
        db.commit()
        db.refresh(mem)
        
        rm = ResolutionMemory(
            incident_memory_id=mem.id, incident_id=inc_hist.id, model_id=m.id,
            resolution_summary="Fixed with feature engineering",
            validation_status="PASSED", ml_recovery_score=0.95, deployment_status="SUCCESS", post_deployment_status="HEALTHY",
            effectiveness_score=85
        )
        db.add(rm)
        db.commit()
        db.refresh(rm)
        print(" -> Historical Incident created:", inc_hist.id)
        print(" -> Resolution Memory created:", rm.id)
        
        print("\n2. Create a new incoming Incident...")
        inc_new = Incident(model_id=m.id, model_version_id=mv.id, incident_key=f"INC-NEW-{uuid.uuid4().hex[:8]}", title="New Drift", severity="high", status="active", category="data_drift")
        db.add(inc_new)
        db.commit()
        db.refresh(inc_new)
        print(" -> New Incident created:", inc_new.id)
        
        print("\n3. Call Similar Incidents Logic...")
        results = resolution_memory_service.get_similar_incidents(db, inc_new.id)
        
        print("\n4. Verification Results:")
        print(json.dumps(results, indent=2))
        
        if len(results) > 0:
            top = results[0]
            print(f"\nSUCCESS: Found similar incident {top['incident_key']}")
            print(f"Similarity Score: {top['similarity_score']}%")
            print(f"Reasons: {top['similarity_reasons']}")
            print(f"Effectiveness Score: {top['resolution']['effectiveness_score']}")
            
            assert top["similarity_score"] >= 80, "Score should be >= 80"
            assert "Same model" in " ".join(top["similarity_reasons"]), "Should match model"
            assert "Same incident category" in " ".join(top["similarity_reasons"]), "Should match category"
            assert top["resolution"]["effectiveness_score"] > 80, "Effectiveness should be high"
            print("ALL ASSERTIONS PASSED!")
        else:
            print("FAILED: No similar incidents found")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_demo()
