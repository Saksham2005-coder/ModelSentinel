from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory

class SimilarityService:
    def __init__(self, db: Session):
        self.db = db
        
        self.weights = {
            "model_match": 25,
            "incident_category": 15, # we can use Incident.title or a category field if added
            "signal_family": 15,
            "root_cause_category": 15,
            "affected_features": 10,
            "affected_segments": 10,
            "metric_overlap": 5,
            "severity": 5
        }

    def find_similar_memories_for_incident(self, incident: Incident) -> List[Dict[str, Any]]:
        """
        Find similar IncidentMemories for a given active or historical Incident.
        Since Incident might not have full root_cause_category yet (if still investigating),
        we do the best we can with what it has (e.g. from IncidentSignal).
        Wait, usually similarity is run from an Investigation context or an Incident context.
        Let's extract features from the incident and its signals.
        """
        # Extract source features
        source_model_id = incident.model_id
        source_severity = incident.severity
        
        source_signal_families = set()
        source_metrics = set()
        source_features = set()
        
        for sig in incident.signals:
            source_signal_families.add(sig.source_type)
            if sig.source_type == "metric":
                source_metrics.add(sig.signal_name)
            elif sig.source_type == "feature_drift":
                source_features.add(sig.signal_name)
                
        # To get the best match, we compare against all incident memories
        # Optimization: In a real system we might filter by model_id first, but let's score all for now
        memories = self.db.query(IncidentMemory).filter(IncidentMemory.incident_id != incident.id).all()
        
        results = []
        for mem in memories:
            score = 0
            reasons = []
            
            if mem.model_id == source_model_id:
                score += self.weights["model_match"]
                reasons.append("Same model")
                
            if mem.severity == source_severity:
                score += self.weights["severity"]
                reasons.append(f"Same severity ({source_severity})")
                
            # signal family overlap
            mem_signals = set(mem.signal_families or [])
            if mem_signals and source_signal_families.intersection(mem_signals):
                score += self.weights["signal_family"]
                reasons.append("Similar signal families")
                
            # feature overlap
            mem_features = set(mem.affected_features or [])
            if mem_features and source_features.intersection(mem_features):
                score += self.weights["affected_features"]
                reasons.append("Similar affected features")
                
            # metric overlap
            mem_metrics = set(mem.affected_metrics or [])
            if mem_metrics and source_metrics.intersection(mem_metrics):
                score += self.weights["metric_overlap"]
                reasons.append("Similar affected metrics")
                
            if score > 0:
                results.append({
                    "memory": mem,
                    "similarity_score": score,
                    "reasons": reasons
                })
                
        # Sort by highest score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results

    def find_similar_memories_for_memory(self, memory: IncidentMemory) -> List[Dict[str, Any]]:
        """
        Compare a memory to other memories.
        """
        source_model_id = memory.model_id
        source_severity = memory.severity
        source_signal_families = set(memory.signal_families or [])
        source_features = set(memory.affected_features or [])
        source_segments = set(memory.affected_segments or [])
        source_metrics = set(memory.affected_metrics or [])
        source_root_cause = memory.root_cause_category
        
        memories = self.db.query(IncidentMemory).filter(IncidentMemory.id != memory.id).all()
        
        results = []
        for mem in memories:
            score = 0
            reasons = []
            
            if mem.model_id == source_model_id:
                score += self.weights["model_match"]
                reasons.append("Same model")
                
            if mem.severity == source_severity:
                score += self.weights["severity"]
                reasons.append(f"Same severity ({source_severity})")
                
            mem_signals = set(mem.signal_families or [])
            if mem_signals and source_signal_families.intersection(mem_signals):
                score += self.weights["signal_family"]
                reasons.append("Similar signal families")
                
            mem_features = set(mem.affected_features or [])
            if mem_features and source_features.intersection(mem_features):
                score += self.weights["affected_features"]
                reasons.append("Similar affected features")
                
            mem_segments = set(mem.affected_segments or [])
            if mem_segments and source_segments.intersection(mem_segments):
                score += self.weights["affected_segments"]
                reasons.append("Similar affected segments")
                
            mem_metrics = set(mem.affected_metrics or [])
            if mem_metrics and source_metrics.intersection(mem_metrics):
                score += self.weights["metric_overlap"]
                reasons.append("Similar affected metrics")
                
            if source_root_cause and mem.root_cause_category == source_root_cause:
                score += self.weights["root_cause_category"]
                reasons.append(f"Same root cause category ({source_root_cause})")
                
            if score > 0:
                results.append({
                    "memory": mem,
                    "similarity_score": score,
                    "reasons": reasons
                })
                
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results
