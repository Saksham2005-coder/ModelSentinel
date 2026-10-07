from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.db.base_class import Base
from app.models.pull_request import PullRequest
from app.models.incident import Incident

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(String, primary_key=True, index=True)
    pull_request_id = Column(String, ForeignKey("pull_requests.id"), nullable=False)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    commit_sha = Column(String, nullable=False)

    status = Column(String, nullable=False) # ELIGIBLE, BLOCKED, APPROVED, DEPLOYED, VERIFYING, HEALTHY, DEGRADED, FAILED
    gate_result = Column(String, nullable=False) # JSON dump of gate evaluations
    block_reason = Column(String, nullable=True)
    policy_result = Column(String, nullable=True) # JSON dump of policy evaluation
    policy_evaluation_id = Column(String, ForeignKey("policy_evaluations.id"), nullable=True)

    deployed_at = Column(DateTime, nullable=True)
    environment = Column(String, nullable=True)
    deployment_source = Column(String, nullable=True)
    deployed_by = Column(String, nullable=True)

    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    pull_request = relationship(PullRequest)
    incident = relationship(Incident)
