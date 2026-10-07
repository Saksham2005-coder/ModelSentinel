from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

def generate_uuid():
    return str(uuid.uuid4())

class ReliabilityEvent(Base):
    __tablename__ = "reliability_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_id = Column(String, ForeignKey("models.id"), nullable=False, index=True)
    model_version_id = Column(String, ForeignKey("model_versions.id"), nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    source_type = Column(String, nullable=False) # e.g. "telemetry", "incident", "patch"
    source_id = Column(String, nullable=False)
    severity = Column(String, nullable=True) # e.g. "info", "warning", "high", "critical"
    status = Column(String, nullable=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    edges_out = relationship("ReliabilityEdge", foreign_keys="[ReliabilityEdge.from_event_id]", back_populates="from_event")
    edges_in = relationship("ReliabilityEdge", foreign_keys="[ReliabilityEdge.to_event_id]", back_populates="to_event")

class ReliabilityEdge(Base):
    __tablename__ = "reliability_edges"

    id = Column(String, primary_key=True, default=generate_uuid)
    from_event_id = Column(String, ForeignKey("reliability_events.id"), nullable=False, index=True)
    to_event_id = Column(String, ForeignKey("reliability_events.id"), nullable=False, index=True)
    relationship_type = Column(String, nullable=False) # e.g. "TRIGGERED_BY", "CAUSED", "RESULTED_IN"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    from_event = relationship("ReliabilityEvent", foreign_keys=[from_event_id], back_populates="edges_out")
    to_event = relationship("ReliabilityEvent", foreign_keys=[to_event_id], back_populates="edges_in")
