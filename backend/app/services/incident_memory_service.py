from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory
from app.models.validation import ValidationRun
from typing import Dict, Any, Optional

class IncidentMemoryService:
    def __init__(self, db: Session):
        self.db = db
        
    def check_eligibility(self, incident_id: str) -> Dict[str, Any]:
        """
        Check if an incident is eligible to become an Incident Memory.
        Eligibility rules:
        - Incident must be resolved
        - Must have a patch proposed
        - Must have a completed validation run
        - Validation verdict MUST be PASS. (FAILED cannot, PARTIAL needs human confirmation which we'll handle outside if needed, but for now deterministic PASS)
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return {"eligible": False, "reason": "Incident not found"}
            
        if incident.status != "resolved":
            return {"eligible": False, "reason": f"Incident is {incident.status}, not resolved"}
            
        # Check investigations and patches
        active_inv = next((inv for inv in incident.investigations if inv.status in ("completed", "in_progress")), None)
        if not active_inv:
            return {"eligible": False, "reason": "No active investigation found"}
            
        from app.models.patch import PatchProposal
        approved_patch = self.db.query(PatchProposal).filter(
            PatchProposal.investigation_id == active_inv.id,
            PatchProposal.status == "approved"
        ).first()
        if not approved_patch:
            return {"eligible": False, "reason": "No approved patch found"}
            
        # Find latest validation run
        latest_val = self.db.query(ValidationRun).filter(
            ValidationRun.patch_proposal_id == approved_patch.id
        ).order_by(ValidationRun.started_at.desc()).first()
        
        if not latest_val or latest_val.status != "completed":
            return {"eligible": False, "reason": "No completed validation run found"}
            
        if latest_val.verdict == "FAIL":
            return {"eligible": False, "reason": "Validation verdict is FAIL"}
        elif latest_val.verdict == "PARTIAL":
            return {"eligible": False, "reason": "Validation verdict is PARTIAL, explicit confirmation required"}
            
        return {
            "eligible": True,
            "incident": incident,
            "investigation": active_inv,
            "patch": approved_patch,
            "validation": latest_val
        }

    def create_memory(self, incident_id: str, payload: Dict[str, Any]) -> IncidentMemory:
        """
        Create an Incident Memory from the provided payload if eligible.
        """
        eligibility = self.check_eligibility(incident_id)
        if not eligibility["eligible"]:
            raise ValueError(f"Incident is not eligible for memory: {eligibility['reason']}")
            
        existing = self.db.query(IncidentMemory).filter(IncidentMemory.incident_id == incident_id).first()
        if existing:
            raise ValueError("Incident memory already exists for this incident")
            
        incident = eligibility["incident"]
        investigation = eligibility["investigation"]
        patch = eligibility["patch"]
        validation = eligibility["validation"]
        
        memory = IncidentMemory(
            incident_id=incident.id,
            model_id=incident.model_id,
            model_version_id=incident.model_version_id,
            investigation_id=investigation.id,
            successful_patch_id=patch.id,
            successful_validation_id=validation.id,
            
            title=payload.get("title", f"Resolved: {incident.title}"),
            summary=payload.get("summary", ""),
            root_cause=payload.get("root_cause", ""),
            root_cause_category=payload.get("root_cause_category", "Unknown"),
            
            affected_metrics=payload.get("affected_metrics", []),
            affected_features=payload.get("affected_features", []),
            affected_segments=payload.get("affected_segments", []),
            signal_families=payload.get("signal_families", []),
            
            severity=incident.severity,
            resolution_status="resolved",
            resolution_summary=payload.get("resolution_summary", "")
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_memory_by_incident(self, incident_id: str) -> Optional[IncidentMemory]:
        return self.db.query(IncidentMemory).filter(IncidentMemory.incident_id == incident_id).first()
