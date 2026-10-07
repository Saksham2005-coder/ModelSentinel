from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResolutionMemory(Base):
    __tablename__ = "resolution_memories"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    # Provenance Links
    incident_memory_id = Column(String, ForeignKey("incident_memories.id"), nullable=False, unique=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    patch_id = Column(String, ForeignKey("patch_proposals.id"), nullable=True)
    validation_id = Column(String, ForeignKey("validation_runs.id"), nullable=True)
    deployment_id = Column(String, ForeignKey("deployments.id"), nullable=True)
    
    # Structured data
    resolution_summary = Column(Text, nullable=True)
    affected_files = Column(JSON, nullable=True)
    
    # Effectiveness and statuses
    validation_status = Column(String, nullable=True)
    ml_recovery_score = Column(Float, nullable=True)
    regression_status = Column(String, nullable=True)
    deployment_status = Column(String, nullable=True)
    post_deployment_status = Column(String, nullable=True)
    recurrence_count = Column(Integer, default=0)
    
    effectiveness_score = Column(Integer, nullable=False, default=0)
    score_breakdown = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    incident_memory = relationship("IncidentMemory", backref="resolution")
    incident = relationship("Incident")
    model = relationship("Model")
    patch = relationship("PatchProposal")
    validation = relationship("ValidationRun")
    deployment = relationship("Deployment")
