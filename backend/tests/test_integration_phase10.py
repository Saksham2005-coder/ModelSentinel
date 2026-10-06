import pytest
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.patch import PatchProposal, PatchFileChange
from app.models.validation import ValidationRun
from app.models.repository import Repository, RepositorySnapshot, RepositoryFile
from app.models.model import Model, ModelVersion
from app.services.pull_request_service import PullRequestService
from app.services.deployment_gate_service import DeploymentGateService
from app.services.git_provider import GitProvider
import uuid

class MockGitProvider(GitProvider):
    def __init__(self):
        self.branches = []
        self.prs = []

    def create_branch(self, repo_id: str, branch_name: str, commit_sha: str) -> bool:
        self.branches.append(branch_name)
        return True

    def create_commit(self, repo_id: str, message: str, tree_sha: str, parent_sha: str) -> str:
        return "mock-commit-sha"

    def create_pull_request(self, repo_id: str, title: str, description: str, head_branch: str, base_branch: str) -> dict:
        pr = {"id": "1", "number": 1, "html_url": "http://github.com/test/1"}
        self.prs.append(pr)
        return pr

    def get_pull_request_checks(self, repo_id: str, pr_id: str) -> list:
        return [{"conclusion": "success"}]

def test_phase10_lifecycle(db: Session):
    repo = Repository(id="repo-1", name="test-repo", source_type="public_git")
    snap = RepositorySnapshot(id="snap-1", repository_id="repo-1", commit_sha="abc1234")
    f1 = RepositoryFile(id="f1", repository_snapshot_id="snap-1", path="test.py", sha256="hash1", size_bytes=10, language="python")
    db.add_all([repo, snap, f1])
    
    model = Model(id="mod-1", name="test-model", slug="test-model-1", framework="pytorch", task_type="classification", primary_metric="accuracy")
    mv = ModelVersion(id="mv-1", model_id="mod-1", version="1", artifact_uri="http")
    db.add_all([model, mv])

    inc = Incident(id="inc-1", incident_key="test-1", title="Test Incident", model_id="mod-1", model_version_id="mv-1", status="resolved", severity="high", category="performance")
    db.add(inc)

    inv = Investigation(id="inv-1", incident_id="inc-1", status="completed", summary="test")
    db.add(inv)
    
    patch = PatchProposal(id="patch-1", investigation_id="inv-1", incident_id="inc-1", repository_id="repo-1", repository_snapshot_id="snap-1", status="approved", summary="test", rationale="test", expected_behavior="test")
    pc = PatchFileChange(id="pc-1", patch_proposal_id="patch-1", file_path="test.py", change_type="modify", rationale="test", diff_text="diff")
    db.add(patch)
    db.add(pc)
    
    val_run = ValidationRun(id="val-1", incident_id="inc-1", patch_proposal_id="patch-1", repository_snapshot_id="snap-1", status="completed", verdict="PASS")
    db.add(val_run)
    db.commit()

    # Mock the git service since we don't have a real repo at /tmp/test
    import app.services.pull_request_service as pr_mod
    class MockGitService:
        def __init__(self, path): pass
        def get_current_commit(self): return "abc1234"
        def get_default_branch(self): return "main"
    
    original_svc = pr_mod.GitService
    pr_mod.GitService = MockGitService
    
    try:
        git_provider = MockGitProvider()
        pr_svc = PullRequestService(db, git_provider)
        
        pr = pr_svc.create_pull_request("inc-1", "patch-1", "val-1")
        assert pr.status == "CREATED"
        
        pr_svc.sync_pr_status(pr.id)
        assert pr.status == "PASSED"
        
        dep_svc = DeploymentGateService(db)
        dep = dep_svc.evaluate_gate(pr.id)
        assert dep.status == "ELIGIBLE"
    finally:
        pr_mod.GitService = original_svc
