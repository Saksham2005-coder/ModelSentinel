from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class ChangeRiskAssessment(Base):
    __tablename__ = "change_risk_assessments"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    patch_proposal_id = Column(String, ForeignKey("patch_proposals.id"), unique=True, index=True, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=False) # LOW, MODERATE, HIGH, CRITICAL
    factors = Column(JSON, nullable=False, default=list) # e.g. [{"factor": "Preprocessing code changed", "contribution": 18}]
    blast_radius = Column(JSON, nullable=False, default=dict) # e.g. {"files": [], "models": [], "regression_tests": [], "historical_incidents": []}
    recommended_regressions = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
