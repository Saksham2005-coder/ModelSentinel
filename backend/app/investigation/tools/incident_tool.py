from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentSignal
from app.investigation.tool_registry import registry

@registry.register(
    name="get_incident_context",
    description="Get the base context of an incident, including its severity, status, category, and triggering signals.",
    parameters_schema={
        "type": "object",
        "properties": {
            "incident_id": {"type": "string", "description": "The ID of the incident"}
        },
        "required": ["incident_id"]
    }
)
def get_incident_context(incident_id: str, db: Session) -> dict:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": f"Incident {incident_id} not found."}
    
    signals = db.query(IncidentSignal).filter(IncidentSignal.incident_id == incident_id).all()
    
    return {
        "id": incident.id,
        "model_id": incident.model_id,
        "model_version_id": incident.model_version_id,
        "status": incident.status,
        "severity": incident.severity,
        "category": incident.category,
        "title": incident.title,
        "description": incident.description,
        "signals": [
            {
                "signal_type": s.signal_type,
                "feature_name": s.feature_name,
                "metric_name": s.metric_name,
                "value": s.value,
                "threshold": s.threshold
            } for s in signals
        ]
    }
