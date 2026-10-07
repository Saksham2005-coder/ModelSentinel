import uuid
import json
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.models.pull_request import PullRequest
from app.models.patch import PatchProposal
from app.models.validation import ValidationRun
from app.models.regression import RegressionRun
from app.models.change_risk import ChangeRiskAssessment
from app.services.policy_service import PolicyEvaluationService

class DeploymentGateService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_gate(self, pull_request_id: str) -> Deployment:
        pr = self.db.query(PullRequest).filter(PullRequest.id == pull_request_id).first()
        if not pr:
            raise ValueError("Pull Request not found")

        patch = self.db.query(PatchProposal).filter(PatchProposal.id == pr.patch_proposal_id).first()
        val_run = self.db.query(ValidationRun).filter(ValidationRun.id == pr.validation_run_id).first()
        
        # Regression checks
        regression_runs = self.db.query(RegressionRun).filter(RegressionRun.validation_run_id == pr.validation_run_id).all()
        regression_passed = True
        for r in regression_runs:
            if r.status != 'PASS':
                regression_passed = False
                
        # Evaluate rules deterministically
        gate_results = {
            "patch_approved": patch.status == "approved" if patch else False,
            "validation_passed": val_run.status == "completed" and val_run.verdict == "PASS" if val_run else False,
            "regression_passed": regression_passed,
            "ci_passed": pr.status in ["PASSED", "MERGED"]
        }

        block_reason = None
        is_eligible = True
        
        if not gate_results["patch_approved"]:
            is_eligible = False
            block_reason = "Patch is not approved."
        elif not gate_results["validation_passed"]:
            is_eligible = False
            block_reason = "Validation did not pass."
        elif not gate_results["regression_passed"]:
            is_eligible = False
            block_reason = "Regression suite failed."
        elif not gate_results["ci_passed"]:
            is_eligible = False
            block_reason = "CI checks have not passed."

        # Policy Engine Evaluation
        risk = self.db.query(ChangeRiskAssessment).filter(ChangeRiskAssessment.patch_proposal_id == patch.id).first() if patch else None
        context = {
            "risk_level": risk.risk_level if risk else "UNKNOWN",
            "human_approval": "PASS" if gate_results["patch_approved"] else "FAIL",
            "validation_status": "PASS" if gate_results["validation_passed"] else "FAIL",
            "regression_status": "PASS" if gate_results["regression_passed"] else "FAIL",
            "ci_status": "PASS" if gate_results["ci_passed"] else "FAIL",
            "deployment_health": "HEALTHY"
        }

        policy_svc = PolicyEvaluationService(self.db)
        policy_res = policy_svc.evaluate_action(
            target_type="DEPLOYMENT",
            target_id=pr.id,
            context=context
        )

        gate_results["policy_result"] = policy_res

        if policy_res["result"] == "BLOCK":
            is_eligible = False
            block_reason = f"Blocked by Reliability Policy: {policy_res['matched_policy']}"
        elif policy_res["result"] == "REVIEW_REQUIRED" and is_eligible:
            # Policy allows but flags for review
            # For deployment gate, we might still allow ELIGIBLE but with warnings
            pass

        # Ensure we don't recreate deployment if it already exists and is ELIGIBLE
        existing_deployment = self.db.query(Deployment).filter(Deployment.pull_request_id == pr.id).first()
        if existing_deployment:
            existing_deployment.status = "ELIGIBLE" if is_eligible else "BLOCKED"
            existing_deployment.gate_result = json.dumps(gate_results)
            existing_deployment.block_reason = block_reason
            existing_deployment.policy_result = json.dumps(policy_res)
            self.db.commit()
            return existing_deployment

        deployment = Deployment(
            id=str(uuid.uuid4()),
            pull_request_id=pr.id,
            incident_id=pr.incident_id,
            commit_sha=pr.commit_sha,
            status="ELIGIBLE" if is_eligible else "BLOCKED",
            gate_result=json.dumps(gate_results),
            block_reason=block_reason,
            policy_result=json.dumps(policy_res)
        )
        self.db.add(deployment)
        self.db.commit()
        return deployment
