from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class IncidentMemory(Base):
    __tablename__ = "incident_memories"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Relationships to existing entities
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False, unique=True) # One memory per incident
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=False)
    investigation_id = Column(String, ForeignKey("investigations.id"), nullable=True)
    successful_patch_id = Column(String, ForeignKey("patch_proposals.id"), nullable=True)
    successful_validation_id = Column(String, ForeignKey("validation_runs.id"), nullable=True)

    # Core structured info
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    root_cause_category = Column(String, nullable=True)
    
    # JSON arrays/objects for flexibility
    affected_metrics = Column(JSON, nullable=True)  # e.g., ["f1_score", "precision"]
    affected_features = Column(JSON, nullable=True) # e.g., ["url_length"]
    affected_segments = Column(JSON, nullable=True) # e.g., ["URL-heavy messages"]
    signal_families = Column(JSON, nullable=True)   # e.g., ["data_drift", "performance"]

    severity = Column(String, nullable=False)
    resolution_status = Column(String, nullable=False, default="resolved")
    resolution_summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ORM Relationships
    incident = relationship("Incident", backref="memory")
    model = relationship("Model", foreign_keys=[model_id])
    model_version = relationship("ModelVersion", foreign_keys=[model_version_id])
    investigation = relationship("Investigation")
    successful_patch = relationship("PatchProposal")
    successful_validation = relationship("ValidationRun")
