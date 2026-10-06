from sqlalchemy.orm import Session
from app.models.patch import PatchProposal, PatchFileChange
from app.models.change_risk import ChangeRiskAssessment
from app.models.validation import ValidationRun
from app.models.deployment import Deployment
from app.services.blast_radius_service import BlastRadiusService

class ChangeRiskService:
    @staticmethod
    def evaluate_patch(db: Session, patch: PatchProposal) -> ChangeRiskAssessment:
        # Check if already evaluated
        existing = db.query(ChangeRiskAssessment).filter(ChangeRiskAssessment.patch_proposal_id == patch.id).first()
        if existing:
            return existing

        blast_radius = BlastRadiusService.calculate_blast_radius(db, patch)
        
        score = 0
        factors = []

        # 1. File size & criticality
        file_changes = db.query(PatchFileChange).filter(PatchFileChange.patch_proposal_id == patch.id).all()
        if len(file_changes) >= 5:
            score += 8
            factors.append({"factor": "Large patch (>= 5 files)", "contribution": 8})
        
        has_critical = False
        has_preprocessing = False
        for fc in file_changes:
            path = fc.file_path.lower()
            if any(term in path for term in ["model", "inference", "predict", "train", "pipeline"]):
                has_critical = True
            if "preprocess" in path or "feature" in path:
                has_preprocessing = True
        
        if has_critical:
            score += 15
            factors.append({"factor": "Critical inference/model file changed", "contribution": 15})
        if has_preprocessing:
            score += 18
            factors.append({"factor": "Preprocessing/feature engineering code changed", "contribution": 18})

        # 2. Historical incidents
        incidents = blast_radius.get("historical_incidents", [])
        if incidents:
            incident_score = min(len(incidents) * 4, 20)
            score += incident_score
            factors.append({"factor": f"{len(incidents)} historical incidents", "contribution": incident_score})

        # 3. Post-deployment degradation
        if incidents:
            # We check if patches for those incidents led to bad deployments
            # Actually, just looking up bad deployments for the affected models is simpler
            bad_deployments = db.query(Deployment).filter(
                Deployment.incident_id.in_(incidents),
                Deployment.status.in_(['DEGRADED', 'FAILED'])
            ).count() if incidents else 0
            
            if bad_deployments > 0:
                deg_score = min(bad_deployments * 5, 15)
                score += deg_score
                factors.append({"factor": f"Post-deployment failure history ({bad_deployments} failures)", "contribution": deg_score})

        # 4. Failed validations
        if incidents:
            # Check validations for patches from these incidents?
            # Rough approximation: look for validation failures on models
            models = blast_radius.get("models", [])
            failed_validations = db.query(ValidationRun).filter(
                ValidationRun.incident_id.in_(incidents),
                ValidationRun.status == 'FAIL'
            ).count() if incidents else 0
            
            if failed_validations > 0:
                val_score = min(failed_validations * 2, 10)
                score += val_score
                factors.append({"factor": f"Historical failed validations ({failed_validations})", "contribution": val_score})

        # 5. Regression coverage
        regressions = blast_radius.get("regression_tests", [])
        if regressions:
            cov_score = -5
            score += cov_score
            factors.append({"factor": "Regression coverage present", "contribution": cov_score})

        # Normalize score
        score = max(0, min(100, score))

        # Determine level
        if score < 25:
            level = "LOW"
        elif score < 50:
            level = "MODERATE"
        elif score < 75:
            level = "HIGH"
        else:
            level = "CRITICAL"

        # Save assessment
        assessment = ChangeRiskAssessment(
            patch_proposal_id=patch.id,
            risk_score=score,
            risk_level=level,
            factors=factors,
            blast_radius=blast_radius,
            recommended_regressions=regressions
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        return assessment
