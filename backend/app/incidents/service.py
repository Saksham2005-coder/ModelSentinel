from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.incident import Incident, IncidentEvent

class IncidentService:
    @staticmethod
    def _add_event(db: Session, incident: Incident, event_type: str, message: str):
        event = IncidentEvent(
            incident_id=incident.id,
            event_type=event_type,
            message=message
        )
        db.add(event)
        
    @staticmethod
    def acknowledge(db: Session, incident: Incident):
        if incident.status == 'detected':
            incident.status = 'acknowledged'
            incident.acknowledged_at = datetime.now(timezone.utc)
            IncidentService._add_event(db, incident, 'status_changed', "Incident acknowledged by engineer.")
            db.commit()
            db.refresh(incident)
        return incident
        
    @staticmethod
    def start_investigation(db: Session, incident: Incident):
        if incident.status in ['detected', 'acknowledged']:
            incident.status = 'investigating'
            IncidentService._add_event(db, incident, 'status_changed', "Investigation started.")
            db.commit()
            db.refresh(incident)
        return incident
        
    @staticmethod
    def resolve(db: Session, incident: Incident, resolution_note: str = None):
        if incident.status not in ['resolved', 'suppressed']:
            incident.status = 'resolved'
            incident.resolved_at = datetime.now(timezone.utc)
            msg = "Incident resolved."
            if resolution_note:
                msg += f" Note: {resolution_note}"
            IncidentService._add_event(db, incident, 'incident_resolved', msg)
            db.commit()
            db.refresh(incident)
        return incident
        
    @staticmethod
    def suppress(db: Session, incident: Incident):
        if incident.status not in ['resolved', 'suppressed']:
            incident.status = 'suppressed'
            incident.resolved_at = datetime.now(timezone.utc)
            IncidentService._add_event(db, incident, 'status_changed', "Incident suppressed.")
            db.commit()
            db.refresh(incident)
        return incident
