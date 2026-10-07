import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.reliability import ReliabilityEvent, ReliabilityEdge
from app.models.model import ModelVersion

logger = logging.getLogger(__name__)

class ReliabilityService:
    def emit_event(
        self,
        db: Session,
        model_id: str,
        event_type: str,
        source_type: str,
        source_id: str,
        title: str,
        model_version_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        summary: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
        occurred_at: Optional[datetime] = None
    ) -> ReliabilityEvent:
        
        if not occurred_at:
            occurred_at = datetime.now(timezone.utc)
            
        event = ReliabilityEvent(
            model_id=model_id,
            model_version_id=model_version_id,
            event_type=event_type,
            source_type=source_type,
            source_id=source_id,
            title=title,
            severity=severity,
            status=status,
            summary=summary,
            metadata_json=metadata_json or {},
            occurred_at=occurred_at
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def link_events(
        self,
        db: Session,
        from_event_id: str,
        to_event_id: str,
        relationship_type: str
    ) -> ReliabilityEdge:
        
        # Check if exists
        existing = db.query(ReliabilityEdge).filter(
            ReliabilityEdge.from_event_id == from_event_id,
            ReliabilityEdge.to_event_id == to_event_id,
            ReliabilityEdge.relationship_type == relationship_type
        ).first()
        
        if existing:
            return existing
            
        edge = ReliabilityEdge(
            from_event_id=from_event_id,
            to_event_id=to_event_id,
            relationship_type=relationship_type
        )
        db.add(edge)
        db.commit()
        db.refresh(edge)
        return edge

    def find_event_by_source(
        self,
        db: Session,
        source_type: str,
        source_id: str,
        event_type: Optional[str] = None
    ) -> Optional[ReliabilityEvent]:
        
        query = db.query(ReliabilityEvent).filter(
            ReliabilityEvent.source_type == source_type,
            ReliabilityEvent.source_id == source_id
        )
        if event_type:
            query = query.filter(ReliabilityEvent.event_type == event_type)
            
        return query.first()

    def get_timeline(
        self,
        db: Session,
        model_id: str,
        model_version_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ReliabilityEvent]:
        
        query = db.query(ReliabilityEvent).filter(ReliabilityEvent.model_id == model_id)
        
        if model_version_id:
            query = query.filter(ReliabilityEvent.model_version_id == model_version_id)
        if start_time:
            query = query.filter(ReliabilityEvent.occurred_at >= start_time)
        if end_time:
            query = query.filter(ReliabilityEvent.occurred_at <= end_time)
            
        return query.order_by(
            desc(ReliabilityEvent.occurred_at), 
            desc(ReliabilityEvent.created_at)
        ).limit(limit).all()

    def get_incident_graph(
        self,
        db: Session,
        incident_event_id: str
    ) -> Dict[str, Any]:
        """
        Returns a simplified causal graph of events connected to an incident event.
        We traverse forward and backward from the incident event.
        """
        nodes = {}
        edges = []
        
        visited = set()
        queue = [incident_event_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            event = db.query(ReliabilityEvent).filter(ReliabilityEvent.id == current_id).first()
            if not event:
                continue
                
            nodes[current_id] = event
            
            # Outgoing edges
            out_edges = db.query(ReliabilityEdge).filter(ReliabilityEdge.from_event_id == current_id).all()
            for e in out_edges:
                edges.append({
                    "id": e.id,
                    "from_id": e.from_event_id,
                    "to_id": e.to_event_id,
                    "type": e.relationship_type
                })
                if e.to_event_id not in visited:
                    queue.append(e.to_event_id)
                    
            # Incoming edges
            in_edges = db.query(ReliabilityEdge).filter(ReliabilityEdge.to_event_id == current_id).all()
            for e in in_edges:
                # To prevent duplicates in edges list
                edge_dict = {
                    "id": e.id,
                    "from_id": e.from_event_id,
                    "to_id": e.to_event_id,
                    "type": e.relationship_type
                }
                if edge_dict not in edges:
                    edges.append(edge_dict)
                    
                if e.from_event_id not in visited:
                    queue.append(e.from_event_id)
                    
        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }

reliability_service = ReliabilityService()
