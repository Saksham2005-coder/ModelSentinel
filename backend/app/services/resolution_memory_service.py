import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory
from app.models.resolution_memory import ResolutionMemory
from app.models.model import Model

class ResolutionMemoryService:
    def evaluate_effectiveness(self, db: Session, incident_memory: IncidentMemory) -> Dict[str, Any]:
        """Calculates a deterministic effectiveness score for a given IncidentMemory."""
        score = 0
        breakdown = []
        
        # We will populate these dynamically based on related records
        
        # Validation Success
        if incident_memory.successful_validation_id:
            # We assume it passed if it's marked as successful_validation_id
            score += 25
            breakdown.append("+25 Validation passed")
            
        # Patch Exists
        if incident_memory.successful_patch_id:
            score += 15
            breakdown.append("+15 Patch proposed")
            
        return {
            "score": min(score, 100),
            "breakdown": breakdown
        }

    def evaluate_effectiveness_from_rm(self, db: Session, rm: ResolutionMemory) -> Dict[str, Any]:
        """Calculates a deterministic effectiveness score from a ResolutionMemory."""
        score = 0
        breakdown = []
        
        # 1. Validation Success
        if rm.validation_status == "PASSED":
            score += 25
            breakdown.append("+25 Validation passed")
        elif rm.validation_status == "FAILED":
            score -= 20
            breakdown.append("-20 Validation failed")
            
        # 2. ML Recovery Score
        if rm.ml_recovery_score is not None:
            if rm.ml_recovery_score > 0.90:
                score += 20
                breakdown.append(f"+20 ML recovery {int(rm.ml_recovery_score * 100)}%")
            elif rm.ml_recovery_score > 0.80:
                score += 10
                breakdown.append(f"+10 ML recovery {int(rm.ml_recovery_score * 100)}%")
                
        # 3. Regression test
        if rm.regression_status == "CREATED" or rm.regression_status == "PASSED":
            score += 15
            breakdown.append("+15 Regression test exists")
        elif rm.regression_status == "FAILED":
            score -= 15
            breakdown.append("-15 Regression detected")
            
        # 4. Deployment
        if rm.deployment_status == "SUCCESS":
            score += 15
            breakdown.append("+15 Deployment healthy")
        elif rm.deployment_status == "FAILED":
            score -= 25
            breakdown.append("-25 Deployment failed")
            
        # 5. Post Deployment
        if rm.post_deployment_status == "HEALTHY":
            score += 10
            breakdown.append("+10 Post-deployment verification healthy")
        elif rm.post_deployment_status == "DEGRADED":
            score -= 30
            breakdown.append("-30 Post-deployment degradation")
            
        # 6. Recurrence
        if rm.recurrence_count and rm.recurrence_count > 0:
            penalty = min(rm.recurrence_count * 10, 30)
            score -= penalty
            breakdown.append(f"-{penalty} Historical recurrence")
            
        return {
            "score": max(min(score, 100), 0),
            "breakdown": breakdown
        }

    def generate_resolution_memory(self, db: Session, incident_memory_id: str) -> Optional[ResolutionMemory]:
        """Creates or updates a ResolutionMemory for a given IncidentMemory."""
        memory = db.query(IncidentMemory).filter(IncidentMemory.id == incident_memory_id).first()
        if not memory:
            return None
            
        # Try to fetch existing
        rm = db.query(ResolutionMemory).filter(ResolutionMemory.incident_memory_id == memory.id).first()
        if not rm:
            rm = ResolutionMemory(
                incident_memory_id=memory.id,
                incident_id=memory.incident_id,
                model_id=memory.model_id,
                patch_id=memory.successful_patch_id,
                validation_id=memory.successful_validation_id
            )
            db.add(rm)
            
        # Populate fields from IncidentMemory BEFORE scoring
        if memory.successful_validation_id and not rm.validation_status:
            rm.validation_status = "PASSED"
        
        rm.resolution_summary = memory.resolution_summary
        
        # Evaluate effectiveness with populated fields
        eval_result = self.evaluate_effectiveness_from_rm(db, rm)
        if eval_result["score"] == 0 and not eval_result["breakdown"]:
            # fallback to basic evaluation from IncidentMemory links
            eval_result = self.evaluate_effectiveness(db, memory)
            
        rm.effectiveness_score = eval_result["score"]
        rm.score_breakdown = eval_result["breakdown"]
        
        db.commit()
        db.refresh(rm)
        return rm

    def calculate_similarity(self, target_incident: Incident, candidate: IncidentMemory) -> Dict[str, Any]:
        """Calculate a 0-100 similarity score between an active incident and a historical incident memory."""
        score = 0
        reasons = []
        
        # 1. Model match (Highest weight)
        if target_incident.model_id == candidate.model_id:
            score += 40
            reasons.append(f"+40 Same model ({candidate.model.name if candidate.model else candidate.model_id})")
            
            # Version match if model matches
            if target_incident.model_version_id == candidate.model_version_id:
                score += 10
                reasons.append("+10 Same model version")
        else:
            # Different model, maybe same framework or task type
            target_model = target_incident.model
            cand_model = candidate.model
            if target_model and cand_model:
                if target_model.task_type == cand_model.task_type:
                    score += 10
                    reasons.append(f"+10 Same task type ({target_model.task_type})")
        
        # 2. Incident Category
        if target_incident.category == candidate.incident.category:
            score += 20
            reasons.append(f"+20 Same incident category ({target_incident.category})")
            
        # 3. Severity
        if target_incident.severity == candidate.severity:
            score += 10
            reasons.append(f"+10 Same severity level ({target_incident.severity})")
            
        # 4. Root Cause Category (if known for target, usually known for candidate)
        # Assuming we might know root cause category early from investigation
        
        # Normalize max 100
        final_score = min(score, 100)
        
        return {
            "score": final_score,
            "reasons": reasons
        }

    def get_similar_incidents(self, db: Session, incident_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Finds historically similar incidents for a given incident."""
        target = db.query(Incident).filter(Incident.id == incident_id).first()
        if not target:
            return []
            
        # Get candidates (resolved incidents with memory)
        # Basic indexed filtering: only same model or same category to reduce O(N^2)
        candidates = db.query(IncidentMemory).filter(
            (IncidentMemory.model_id == target.model_id) | 
            (IncidentMemory.incident.has(category=target.category))
        ).filter(IncidentMemory.incident_id != target.id).all()
        
        results = []
        for cand in candidates:
            sim = self.calculate_similarity(target, cand)
            if sim["score"] > 0:
                # Get resolution memory if exists
                rm = db.query(ResolutionMemory).filter(ResolutionMemory.incident_memory_id == cand.id).first()
                if not rm:
                    # Generate on the fly if missing (for older memories)
                    rm = self.generate_resolution_memory(db, cand.id)
                
                results.append({
                    "incident_id": cand.incident_id,
                    "incident_memory_id": cand.id,
                    "incident_key": cand.incident.incident_key,
                    "title": cand.title,
                    "root_cause": cand.root_cause,
                    "root_cause_category": cand.root_cause_category,
                    "similarity_score": sim["score"],
                    "similarity_reasons": sim["reasons"],
                    "resolution": {
                        "id": rm.id if rm else None,
                        "summary": rm.resolution_summary if rm else None,
                        "effectiveness_score": rm.effectiveness_score if rm else 0,
                        "validation_status": rm.validation_status if rm else None,
                        "ml_recovery_score": rm.ml_recovery_score if rm else None,
                        "deployment_status": rm.deployment_status if rm else None,
                        "post_deployment_status": rm.post_deployment_status if rm else None
                    }
                })
                
        # Sort descending by score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

resolution_memory_service = ResolutionMemoryService()
