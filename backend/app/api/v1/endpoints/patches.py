from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.patch.service import PatchService
from app.schemas.patch import (
    PatchProposalResponse, 
    PatchPlanOutput, 
    PatchReviewCreate, 
    PatchReviewResponse
)
from app.repository.relevance import RelevanceEngine
from app.models.investigation import Investigation

router = APIRouter()

@router.post("/investigations/{investigation_id}/patches/plan", response_model=PatchPlanOutput)
def plan_patch(
    investigation_id: str,
    db: Session = Depends(get_db)
) -> Any:
    service = PatchService(db)
    
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    incident = investigation.incident
    from app.models.model import ModelVersion
    model_version = db.query(ModelVersion).filter(ModelVersion.id == incident.model_version_id).first()
    if not model_version or not model_version.repository_snapshot_id:
        raise HTTPException(status_code=400, detail="No repository snapshot available for incident model version")
        
    # Get relevant files
    relevance_engine = RelevanceEngine(db, model_version.repository_snapshot_id)
    keywords = [s.signal_name for s in incident.signals]
    relevant_files = relevance_engine.find_relevant_files(keywords, set())
    if not relevant_files:
        # Fallback to some random files from snapshot if none are found
        from app.models.repository import RepositoryFile
        fallback = db.query(RepositoryFile).filter(RepositoryFile.repository_snapshot_id == model_version.repository_snapshot_id).limit(5).all()
        relevant_files = [{"file_path": f.path, "relevance": "Fallback"} for f in fallback]
    
    # Filter to top 5 files to avoid token limits
    top_files = relevant_files[:5]
    
    try:
        plan = service.plan_patch(investigation_id, top_files)
        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/investigations/{investigation_id}/patches", response_model=PatchProposalResponse)
def generate_patch(
    investigation_id: str,
    plan: PatchPlanOutput,
    parent_patch_id: str = None,
    feedback: str = None,
    db: Session = Depends(get_db)
) -> Any:
    service = PatchService(db)
    
    investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
        
    incident = investigation.incident
    from app.models.model import ModelVersion
    model_version = db.query(ModelVersion).filter(ModelVersion.id == incident.model_version_id).first()
    if not model_version or not model_version.repository_snapshot_id:
        raise HTTPException(status_code=400, detail="No repository snapshot available for incident model version")
    
    # allowlist extraction from plan
    allowlist = [f.file_path for f in plan.affected_files]
    
    try:
        proposal = service.generate_patch(
            investigation_id=investigation_id,
            snapshot_id=model_version.repository_snapshot_id,
            plan=plan,
            allowlist=allowlist,
            parent_patch_id=parent_patch_id,
            feedback=feedback
        )
        return proposal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/investigations/{investigation_id}/patches", response_model=List[PatchProposalResponse])
def list_patches(
    investigation_id: str,
    db: Session = Depends(get_db)
) -> Any:
    from app.models.patch import PatchProposal
    proposals = db.query(PatchProposal).filter(PatchProposal.investigation_id == investigation_id).order_by(PatchProposal.created_at.desc()).all()
    return proposals

@router.get("/patches/{patch_id}", response_model=PatchProposalResponse)
def get_patch(
    patch_id: str,
    db: Session = Depends(get_db)
) -> Any:
    service = PatchService(db)
    proposal = service.get_patch_proposal(patch_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Patch not found")
    return proposal

@router.post("/patches/{patch_id}/review", response_model=PatchProposalResponse)
def review_patch(
    patch_id: str,
    review_in: PatchReviewCreate,
    db: Session = Depends(get_db)
) -> Any:
    service = PatchService(db)
    try:
        proposal = service.review_patch(patch_id, review_in.reviewer_type, review_in.decision, review_in.comment)
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/patches/{patch_id}/change-intelligence")
def get_patch_change_intelligence(
    patch_id: str,
    db: Session = Depends(get_db)
) -> Any:
    from app.repository.change_intelligence import ChangeIntelligenceService
    service = ChangeIntelligenceService(db)
    result = service.analyze_patch(patch_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
