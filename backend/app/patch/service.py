import os
import hashlib
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from app.models.patch import PatchProposal, PatchFileChange, PatchReview
from app.models.investigation import Investigation, InvestigationEvidence
from app.models.incident import Incident
from app.models.repository import Repository, RepositorySnapshot
from app.repository.storage import RepositoryStorage
from app.schemas.patch import PatchPlanOutput, PatchGenerationOutput, PatchFileOutput, AffectedFile
from app.patch.validator import PatchValidator, ValidationError
from app.patch.risk import RiskAnalyzer
from app.ai.service import get_llm_provider

class PatchService:
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_llm_provider()
        self.storage = RepositoryStorage()

    def get_patch_proposal(self, patch_id: str) -> Optional[PatchProposal]:
        return self.db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()

    def _build_context(self, investigation: Investigation) -> str:
        incident = investigation.incident
        evidence = self.db.query(InvestigationEvidence).filter(InvestigationEvidence.investigation_id == investigation.id).all()
        
        context = f"Incident: {incident.title}\n"
        context += f"Category: {incident.category}\n\n"
        context += f"Investigation Summary:\n{investigation.summary}\n\n"
        context += "Evidence:\n"
        for ev in evidence:
            context += f"- {ev.evidence_type}: {ev.title} (Content: {ev.value_json})\nExplanation: {ev.explanation}\n"
        return context

    def plan_patch(self, investigation_id: str, relevant_files: List[Dict[str, Any]]) -> PatchPlanOutput:
        investigation = self.db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not investigation or investigation.status != "completed":
            raise ValueError("Patch generation requires a completed investigation.")

        context = self._build_context(investigation)
        
        prompt = "Create a detailed PatchPlan to resolve the incident based on the investigation evidence.\n\n"
        prompt += f"{context}\n\n"
        prompt += "Relevant files available in the repository snapshot:\n"
        for f in relevant_files:
            prompt += f"- {f['file_path']} (Relevance: {f['relevance']})\n"
        
        system_prompt = (
            "You are an expert AI software engineer tasked with fixing a machine learning or data pipeline incident. "
            "Formulate a precise plan. You must strictly limit your changes to the provided relevant files. "
            "Do NOT add files outside the context. Explain the rationale for each change. "
            "CRITICAL: The file paths in your 'affected_files' list MUST exactly match the paths provided in 'Relevant files available in the repository snapshot'. If no files are relevant, select the closest one."
        )

        plan = self.provider.generate_structured(prompt, system_prompt, PatchPlanOutput)
        return plan

    def generate_patch(
        self, 
        investigation_id: str, 
        snapshot_id: str, 
        plan: PatchPlanOutput, 
        allowlist: List[str], 
        parent_patch_id: Optional[str] = None,
        feedback: Optional[str] = None
    ) -> PatchProposal:
        investigation = self.db.query(Investigation).filter(Investigation.id == investigation_id).first()
        snapshot = self.db.query(RepositorySnapshot).filter(RepositorySnapshot.id == snapshot_id).first()
        repo = snapshot.repository
        
        # Build prompt
        context = self._build_context(investigation)
        prompt = "Generate the actual code changes for the patch.\n\n"
        prompt += f"Context:\n{context}\n\n"
        prompt += f"Plan Summary:\n{plan.summary if hasattr(plan, 'summary') else plan.problem_statement}\n\n"
        if feedback:
            prompt += f"Human Review Feedback (Address this!):\n{feedback}\n\n"

        # Load file contents for allowlisted files
        repo_path = self.storage.get_repo_path(repo.id)
        for fpath in allowlist:
            full_path = os.path.join(repo_path, fpath)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                prompt += f"--- FILE: {fpath} ---\n{content}\n----------------\n\n"

        system_prompt = (
            "You are generating a multi-file patch proposal. You will output the proposed changes as structured data. "
            "For each file, specify the target symbol (if applicable), the change type, and the patch hunks. "
            "A hunk consists of context lines before, deleted lines, added lines, and context lines after. "
            "Limit changes strictly to the necessary logic.\n"
            f"CRITICAL: You MUST ONLY modify the following files: {', '.join(allowlist)}. "
            "Any other file modifications will be rejected."
        )

        patch_output = self.provider.generate_structured(prompt, system_prompt, PatchGenerationOutput)

        # Validate statically
        validator = PatchValidator(self.db, snapshot_id, repo_path)
        validator.validate(patch_output, allowlist)

        # Create database record
        version = 1
        if parent_patch_id:
            parent = self.get_patch_proposal(parent_patch_id)
            if parent:
                version = parent.version + 1
                parent.status = "superseded"

        proposal = PatchProposal(
            investigation_id=investigation_id,
            incident_id=investigation.incident_id,
            repository_id=repo.id,
            repository_snapshot_id=snapshot_id,
            version=version,
            parent_patch_id=parent_patch_id,
            status="review",
            summary=patch_output.summary,
            rationale=patch_output.rationale,
            expected_behavior=patch_output.expected_behavior,
        )
        self.db.add(proposal)
        self.db.flush()

        for f_out in patch_output.files:
            # Construct diff_text from hunks
            diff_text = f"--- a/{f_out.file_path}\n+++ b/{f_out.file_path}\n"
            additions = 0
            deletions = 0
            for hunk in f_out.patch_hunks:
                diff_text += "@@\n"
                if hunk.context_lines_before:
                    diff_text += f"{hunk.context_lines_before}\n"
                if hunk.deleted_lines:
                    for line in hunk.deleted_lines.split('\n'):
                        diff_text += f"-{line}\n"
                        if line.strip(): deletions += 1
                if hunk.added_lines:
                    for line in hunk.added_lines.split('\n'):
                        diff_text += f"+{line}\n"
                        if line.strip(): additions += 1
                if hunk.context_lines_after:
                    diff_text += f"{hunk.context_lines_after}\n"

            # Compute original hash
            full_path = os.path.join(repo_path, f_out.file_path)
            orig_hash = None
            if os.path.exists(full_path):
                orig_hash = self.storage.compute_sha256(full_path)

            file_change = PatchFileChange(
                patch_proposal_id=proposal.id,
                file_path=f_out.file_path,
                change_type=f_out.change_type,
                target_symbol=f_out.target_symbol,
                rationale=f_out.rationale,
                original_hash=orig_hash,
                additions=additions,
                deletions=deletions,
                diff_text=diff_text
            )
            self.db.add(file_change)
        
        self.db.flush()

        # Compute risk
        risk_data = RiskAnalyzer.analyze(proposal.file_changes, patch_output.test_changes)
        proposal.risk_summary = risk_data

        self.db.commit()
        self.db.refresh(proposal)
        
        from app.services.reliability_service import reliability_service
        patch_event = reliability_service.emit_event(
            db=self.db,
            model_id=investigation.incident.model_id,
            model_version_id=investigation.incident.model_version_id,
            event_type="PATCH_PROPOSED",
            source_type="patch",
            source_id=proposal.id,
            title="Patch Proposed",
            summary=proposal.summary,
            status="review"
        )
        
        # Link to root cause or investigation
        rc_event = reliability_service.find_event_by_source(self.db, "investigation", investigation.id, "ROOT_CAUSE_IDENTIFIED")
        if rc_event:
            reliability_service.link_events(self.db, rc_event.id, patch_event.id, "FIXED_BY")
        
        return proposal

    def review_patch(self, patch_id: str, reviewer_type: str, decision: str, comment: Optional[str] = None) -> PatchProposal:
        proposal = self.get_patch_proposal(patch_id)
        if not proposal:
            raise ValueError("Patch not found.")
        
        if proposal.status not in ["review"]:
            raise ValueError(f"Cannot review patch in {proposal.status} state.")

        if decision == "approve":
            proposal.status = "approved"
        elif decision == "reject":
            proposal.status = "rejected"
        elif decision == "request_changes":
            proposal.status = "changes_requested"
        else:
            raise ValueError(f"Invalid decision: {decision}")

        review = PatchReview(
            patch_proposal_id=proposal.id,
            reviewer_type=reviewer_type,
            decision=decision,
            comment=comment
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal
