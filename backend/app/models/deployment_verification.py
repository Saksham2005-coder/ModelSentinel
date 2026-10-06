from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
import datetime
from app.db.base_class import Base
from app.models.deployment import Deployment

class DeploymentVerification(Base):
    __tablename__ = "deployment_verifications"

    id = Column(String, primary_key=True, index=True)
    deployment_id = Column(String, ForeignKey("deployments.id"), nullable=False)
    
    status = Column(String, nullable=False) # VERIFYING, HEALTHY, DEGRADED, FAILED
    
    baseline_reference = Column(JSON, nullable=True)
    post_deployment_observation = Column(JSON, nullable=True)
    
    summary = Column(String, nullable=True)
    failure_reason = Column(String, nullable=True)
    
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    deployment = relationship("Deployment")
