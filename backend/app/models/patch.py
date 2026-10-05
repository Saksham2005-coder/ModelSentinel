import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_now() -> datetime:
    return datetime.now(timezone.utc)

class PatchProposal(Base):
    __tablename__ = "patch_proposals"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    investigation_id = Column(String, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    repository_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    repository_snapshot_id = Column(String, ForeignKey("repository_snapshots.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    parent_patch_id = Column(String, ForeignKey("patch_proposals.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, nullable=False, default="draft") # draft, review, changes_requested, approved, rejected, stale, superseded
    summary = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    risk_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_now, onupdate=get_now, nullable=False)

    investigation = relationship("Investigation")
    incident = relationship("Incident")
    repository = relationship("Repository")
    snapshot = relationship("RepositorySnapshot")
    parent_patch = relationship("PatchProposal", remote_side=[id], backref="child_patches")
    file_changes = relationship("PatchFileChange", back_populates="patch_proposal", cascade="all, delete-orphan")
    reviews = relationship("PatchReview", back_populates="patch_proposal", cascade="all, delete-orphan", order_by="PatchReview.created_at")


class PatchFileChange(Base):
    __tablename__ = "patch_file_changes"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    patch_proposal_id = Column(String, ForeignKey("patch_proposals.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    change_type = Column(String, nullable=False) # modify, add, delete
    target_symbol = Column(String, nullable=True)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    rationale = Column(Text, nullable=False)
    original_hash = Column(String, nullable=True)
    proposed_hash = Column(String, nullable=True)
    additions = Column(Integer, nullable=False, default=0)
    deletions = Column(Integer, nullable=False, default=0)
    diff_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    patch_proposal = relationship("PatchProposal", back_populates="file_changes")


class PatchReview(Base):
    __tablename__ = "patch_reviews"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    patch_proposal_id = Column(String, ForeignKey("patch_proposals.id", ondelete="CASCADE"), nullable=False)
    reviewer_type = Column(String, nullable=False) # human, system
    decision = Column(String, nullable=False) # approve, reject, request_changes
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_now, nullable=False)

    patch_proposal = relationship("PatchProposal", back_populates="reviews")
