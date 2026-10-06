from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List
from pydantic import BaseModel

from app.db.session import SessionLocal
from app.models.change_risk import ChangeRiskAssessment
from app.models.patch import PatchProposal
from app.services.change_risk_service import ChangeRiskService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FactorModel(BaseModel):
    factor: str
    contribution: int

class BlastRadiusModel(BaseModel):
    files: List[str]
    models: List[str]
    features: List[str]
    regression_tests: List[str]
    historical_incidents: List[str]

class ChangeRiskResponse(BaseModel):
    id: str
    patch_proposal_id: str
    risk_score: int
    risk_level: str
    factors: List[FactorModel]
    blast_radius: BlastRadiusModel
    recommended_regressions: List[str]
    created_at: Any

    class Config:
        from_attributes = True

@router.get("", response_model=List[ChangeRiskResponse])
def list_assessments(db: Session = Depends(get_db)):
    """List all recent change risk assessments."""
    assessments = db.query(ChangeRiskAssessment).order_by(ChangeRiskAssessment.created_at.desc()).limit(50).all()
    return assessments

@router.get("/{patch_id}", response_model=ChangeRiskResponse)
def get_or_evaluate_risk(patch_id: str, db: Session = Depends(get_db)):
    """Get the risk assessment for a patch. Evaluate if it doesn't exist."""
    patch = db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
        
    assessment = ChangeRiskService.evaluate_patch(db, patch)
    return assessment
