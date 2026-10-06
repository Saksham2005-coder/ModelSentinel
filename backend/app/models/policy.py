from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class ReliabilityPolicy(Base):
    __tablename__ = "reliability_policies"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    scope = Column(String, nullable=False) # GLOBAL, MODEL, ENVIRONMENT, REPOSITORY
    environment = Column(String, nullable=True)
    model_id = Column(String, ForeignKey("models.id"), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    rules = Column(JSON, nullable=False, default=list) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PolicyEvaluation(Base):
    __tablename__ = "policy_evaluations"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    policy_id = Column(String, ForeignKey("reliability_policies.id"), nullable=False)
    target_type = Column(String, nullable=False) # e.g. PATCH, DEPLOYMENT, POST_DEPLOYMENT
    target_id = Column(String, nullable=False) 
    result = Column(String, nullable=False) # ALLOW, BLOCK, REVIEW_REQUIRED, POLICY_VIOLATION
    rule_results = Column(JSON, nullable=False, default=list)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
