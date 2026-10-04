from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from app.models.monitoring import MonitoringRun
from app.models.incident import Incident, IncidentSignal, IncidentEvent, IncidentEvidence
from app.incidents.detection_rules import apply_detection_rules
from app.incidents.severity import calculate_incident_severity
from app.incidents.deduplication import generate_incident_fingerprint, determine_primary_category, generate_incident_title

def create_evidence_snapshot(run: MonitoringRun) -> dict:
    return {
        'run_id': run.id,
        'health_summary': run.health_summary,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'metrics': [{'name': m.metric_name, 'value': m.metric_value, 'status': m.status} for m in run.metrics],
        'data_quality': [{'name': dq.metric_name, 'value': dq.value, 'status': dq.status} for dq in run.data_quality_results],
        'feature_drift': [{'feature': f.feature_name, 'score': f.drift_score, 'status': f.status} for f in run.feature_results],
        'prediction_drift': [{'metric': p.prediction_metric, 'value': p.value, 'status': p.status} for p in run.prediction_results],
        'segments': [{'name': s.segment_name, 'change': s.change, 'status': s.status} for s in run.segment_results]
    }

def process_monitoring_run(db: Session, run: MonitoringRun):
    """
    Consume a completed MonitoringRun and potentially trigger incidents.
    """
    signals = apply_detection_rules(run)
    
    if not signals:
        return None # No incidents detected
        
    severity = calculate_incident_severity(signals)
    category = determine_primary_category(signals)
    fingerprint = generate_incident_fingerprint(run.model_id, run.model_version_id, category)
    
    # Check if active incident with this fingerprint exists
    existing_incident = db.query(Incident).filter(
        Incident.incident_key == fingerprint,
        Incident.status.notin_(['resolved', 'suppressed'])
    ).first()
    
    if existing_incident:
        # Update existing incident
        existing_incident.last_seen_at = datetime.now(timezone.utc)
        
        # If severity escalated
        if existing_incident.severity != severity:
            old_sev = existing_incident.severity
            # Only escalate, don't auto-de-escalate severity easily, or just update it
            existing_incident.severity = severity
            
            db.add(IncidentEvent(
                incident_id=existing_incident.id,
                event_type='severity_changed',
                message=f"Severity changed from {old_sev} to {severity} based on new monitoring run.",
                metadata_json={'run_id': run.id}
            ))
            
        # We don't necessarily want to duplicate all signals again, but we can log that it occurred again
        db.add(IncidentEvent(
            incident_id=existing_incident.id,
            event_type='signal_added',
            message=f"Incident signals detected again in run {run.id}.",
            metadata_json={'run_id': run.id}
        ))
        
        db.commit()
        db.refresh(existing_incident)
        return existing_incident
        
    else:
        # Create new incident
        title = generate_incident_title(category, severity)
        
        incident = Incident(
            incident_key=fingerprint,
            model_id=run.model_id,
            model_version_id=run.model_version_id,
            title=title,
            summary=f"Incident detected by automated monitoring. Primary category: {category}. Rule evaluation identified {len(signals)} signals.",
            severity=severity,
            status='detected',
            category=category
        )
        db.add(incident)
        db.flush() # get ID
        
        # Add signals
        for s in signals:
            db.add(IncidentSignal(
                incident_id=incident.id,
                source_type=s['source_type'],
                source_id=s['source_id'],
                signal_name=s['signal_name'],
                observed_value=s['observed_value'],
                threshold=s['threshold'],
                comparison=s['comparison'],
                status=s['status'],
                explanation=s['explanation']
            ))
            
        # Add event
        db.add(IncidentEvent(
            incident_id=incident.id,
            event_type='incident_detected',
            message="Incident created from deterministic monitoring rules.",
            metadata_json={'run_id': run.id, 'signal_count': len(signals)}
        ))
        
        # Add evidence
        snapshot = create_evidence_snapshot(run)
        db.add(IncidentEvidence(
            incident_id=incident.id,
            monitoring_run_id=run.id,
            snapshot=snapshot
        ))
        
        db.commit()
        db.refresh(incident)
        return incident
