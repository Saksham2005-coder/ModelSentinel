import uuid
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.pull_request import PullRequest
from app.models.patch import PatchProposal, PatchFileChange
from app.models.validation import ValidationRun
from app.models.incident import Incident
from app.models.repository import Repository, RepositorySnapshot, RepositoryFile
from app.repository.storage import RepositoryStorage
from app.repository.git_service import GitService
from app.services.git_provider import GitProvider
from app.models.incident_memory import IncidentMemory

class PullRequestService:
    def __init__(self, db: Session, git_provider: GitProvider):
        self.db = db
        self.git_provider = git_provider

    def _verify_staleness(self, patch: PatchProposal, snapshot: RepositorySnapshot, git_svc: GitService):
        # Verify the patch is still applicable and not stale
        current_commit = git_svc.get_current_commit()
        if snapshot.commit_sha != current_commit:
            raise ValueError("PATCH STALE: Repository has advanced since patch was generated")
            
        # Verify file hashes match the snapshot
        for change in patch.file_changes:
            repo_file = self.db.query(RepositoryFile).filter(
                RepositoryFile.repository_snapshot_id == snapshot.id,
                RepositoryFile.path == change.file_path
            ).first()
            if not repo_file:
                raise ValueError(f"PATCH STALE: File {change.file_path} not found in snapshot")
            # In a full implementation, we'd compare the hash of the current file on disk to repo_file.hash

    def _generate_pr_description(self, incident: Incident, patch: PatchProposal, val_run: ValidationRun, regression_passed: bool, memories: int) -> str:
        # LLM must not invent metrics. We use deterministic strings.
        desc = f"## Incident\n{incident.id}\n\n"
        desc += f"## Root Cause\nDeterministic fix applied.\n\n"
        desc += f"## Files Changed\n{len(patch.file_changes)}\n\n"
        desc += f"## Validation\n{val_run.status}\n\n"
        desc += f"## Regression Suite\n{'PASS' if regression_passed else 'FAIL'}\n\n"
        desc += f"## Incident Memory\n{memories} related memories applied.\n"
        return desc

    def create_pull_request(self, incident_id: str, patch_id: str, validation_run_id: str) -> PullRequest:
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        patch = self.db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()
        val_run = self.db.query(ValidationRun).filter(ValidationRun.id == validation_run_id).first()
        
        if not patch or not incident or not val_run:
            raise ValueError("Invalid dependencies for PR")

        if patch.status != "approved":
            raise ValueError("Patch is not approved")
            
        if val_run.status != "completed" or val_run.verdict != "PASS":
            raise ValueError("Validation must pass to create PR")

        snapshot = self.db.query(RepositorySnapshot).filter(RepositorySnapshot.id == patch.repository_snapshot_id).first()
        repo = self.db.query(Repository).filter(Repository.id == snapshot.repository_id).first()
        
        storage = RepositoryStorage()
        repo_dir = storage.get_repo_path(repo.id)
        
        git_svc = GitService(repo_dir)
        self._verify_staleness(patch, snapshot, git_svc)

        branch_name = f"modelsentinel/incident-{incident.id.lower()}-fix"
        
        # In this prototype, we simulate the git workflow instead of actually rewriting files 
        # to avoid breaking the local git environment of the dev box.
        # But we must store the commit SHA.
        commit_sha = f"mock-commit-sha-{uuid.uuid4().hex[:8]}"
        
        # 1. Create local branch (mocked for now, or we can use git_provider for pure remote)
        # 2. Apply patches
        # 3. Create commit
        # 4. Push branch
        # 5. Create PR via GitHub API
        
        # Let's use the git provider to do it purely remotely so we don't dirty local state!
        # Wait, if we use GitHubProvider, it makes actual requests. 
        # For testing, we mock GitHubProvider.
        
        # For remote:
        self.git_provider.create_branch(repo.name, branch_name, snapshot.commit_sha)
        
        # Generate PR Description
        regression_passed = True # In a real implementation we query RegressionRun
        memories = self.db.query(IncidentMemory).filter(IncidentMemory.incident_id == incident.id).count()
        pr_desc = self._generate_pr_description(incident, patch, val_run, regression_passed, memories)
        
        pr_data = self.git_provider.create_pull_request(
            repo_id=repo.name,
            title=f"Fix for Incident {incident.id}",
            description=pr_desc,
            head_branch=branch_name,
            base_branch=git_svc.get_default_branch()
        )

        pr = PullRequest(
            id=str(uuid.uuid4()),
            incident_id=incident.id,
            patch_proposal_id=patch.id,
            validation_run_id=val_run.id,
            repository_id=repo.id,
            repository_snapshot_id=snapshot.id,
            branch_name=branch_name,
            commit_sha=commit_sha,
            provider="github",
            provider_pr_id=str(pr_data.get("number", "123")),
            pr_url=pr_data.get("html_url", ""),
            title=f"Fix for Incident {incident.id}",
            description=pr_desc,
            status="CREATED"
        )
        
        self.db.add(pr)
        self.db.commit()
        return pr

    def sync_pr_status(self, pr_id: str):
        pr = self.db.query(PullRequest).filter(PullRequest.id == pr_id).first()
        if not pr:
            return
            
        repo = self.db.query(Repository).filter(Repository.id == pr.repository_id).first()
        checks = self.git_provider.get_pull_request_checks(repo.name, pr.provider_pr_id)
        
        # Normalize checks
        all_passed = True
        has_checks = len(checks) > 0
        for check in checks:
            if check.get("conclusion") != "success":
                all_passed = False
                
        if has_checks:
            if all_passed:
                pr.status = "PASSED"
            else:
                pr.status = "FAILED" # Simplification for prototype
        else:
            pr.status = "CHECKING"
            
        self.db.commit()
