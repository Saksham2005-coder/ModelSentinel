import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship as orm_relationship

from app.db.base_class import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_now() -> datetime:
    return datetime.now(timezone.utc)

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="queued") # queued, running, completed, failed, cancelled
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    current_step = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    primary_hypothesis_id = Column(String, ForeignKey("investigation_hypotheses.id", use_alter=True, ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_now, onupdate=get_now, nullable=False)

    incident = orm_relationship("Incident", backref="investigations")
    events = orm_relationship("InvestigationEvent", back_populates="investigation", cascade="all, delete-orphan", order_by="InvestigationEvent.created_at")
    hypotheses = orm_relationship("InvestigationHypothesis", back_populates="investigation", cascade="all, delete-orphan", foreign_keys="[InvestigationHypothesis.investigation_id]")
    evidence = orm_relationship("InvestigationEvidence", back_populates="investigation", cascade="all, delete-orphan")

class InvestigationEvent(Base):
    __tablename__ = "investigation_events"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    investigation_id = Column(String, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    tool_name = Column(String, nullable=True)
    status = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    investigation = orm_relationship("Investigation", back_populates="events")

class InvestigationHypothesis(Base):
    __tablename__ = "investigation_hypotheses"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    investigation_id = Column(String, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False) # supported, plausible, weak, rejected, insufficient_evidence
    rank = Column(Integer, nullable=True)
    evidence_strength = Column(String, nullable=False) # high, moderate, low, insufficient
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_now, onupdate=get_now, nullable=False)

    investigation = orm_relationship("Investigation", back_populates="hypotheses", foreign_keys=[investigation_id])
    evidence_items = orm_relationship("InvestigationEvidence", back_populates="hypothesis")

class InvestigationEvidence(Base):
    __tablename__ = "investigation_evidence"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    investigation_id = Column(String, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    hypothesis_id = Column(String, ForeignKey("investigation_hypotheses.id", ondelete="CASCADE"), nullable=True)
    evidence_type = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    value_json = Column(JSON, nullable=True)
    relationship_type = Column(String, nullable=False) # supports, contradicts, neutral, context
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    investigation = orm_relationship("Investigation", back_populates="evidence")
    hypothesis = orm_relationship("InvestigationHypothesis", back_populates="evidence_items")
