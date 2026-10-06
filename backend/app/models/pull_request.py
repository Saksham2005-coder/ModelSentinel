from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.db.base_class import Base
from app.models.incident import Incident
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.models.repository import Repository, RepositorySnapshot

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    patch_proposal_id = Column(String, ForeignKey("patch_proposals.id"), nullable=False)
    validation_run_id = Column(String, ForeignKey("validation_runs.id"), nullable=False)
    
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    repository_snapshot_id = Column(String, ForeignKey("repository_snapshots.id"), nullable=False)

    branch_name = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)

    provider = Column(String, nullable=False)
    provider_pr_id = Column(String, nullable=True)
    pr_url = Column(String, nullable=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    status = Column(String, nullable=False) # PREPARING, READY, CREATED, CHECKING, PASSED, FAILED, MERGED, CLOSED, BLOCKED

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    incident = relationship(Incident)
    patch = relationship(PatchProposal)
    validation_run = relationship(ValidationRun)
    repository = relationship(Repository)
    repository_snapshot = relationship(RepositorySnapshot)
