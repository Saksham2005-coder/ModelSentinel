import requests
from typing import Dict, List, Any, Optional
from app.core.config import settings
from app.models.integration import ExternalCheck

class CIProvider:
    """Abstract base class for CI providers."""
    def get_run_status(self, repo_id: str, run_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def get_run_checks(self, repo_id: str, run_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_commit_checks(self, repo_id: str, commit_sha: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

class GitHubActionsProvider(CIProvider):
    def __init__(self):
        self.token = settings.MODELSENTINEL_GITHUB_TOKEN
        self.api_url = settings.MODELSENTINEL_GITHUB_API_URL or "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.api_url}{endpoint}"
        if not self.token:
            pass # In tests
        response = requests.request(method, url, headers=self.headers, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_run_status(self, repo_id: str, run_id: str) -> Dict[str, Any]:
        # GET /repos/{owner}/{repo}/actions/runs/{run_id}
        endpoint = f"/repos/{repo_id}/actions/runs/{run_id}"
        return self._request("GET", endpoint)

    def get_run_checks(self, repo_id: str, run_id: str) -> List[Dict[str, Any]]:
        # GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs
        endpoint = f"/repos/{repo_id}/actions/runs/{run_id}/jobs"
        data = self._request("GET", endpoint)
        return data.get("jobs", [])

    def get_commit_checks(self, repo_id: str, commit_sha: str) -> List[Dict[str, Any]]:
        # GET /repos/{owner}/{repo}/commits/{ref}/check-runs
        endpoint = f"/repos/{repo_id}/commits/{commit_sha}/check-runs"
        data = self._request("GET", endpoint)
        return data.get("check_runs", [])

def map_github_status_to_internal(status: str, conclusion: Optional[str]) -> tuple[str, str]:
    """Map GitHub status/conclusion to internal representation."""
    # GitHub status: queued, in_progress, completed
    # GitHub conclusion: action_required, cancelled, failure, neutral, success, skipped, stale, timed_out
    
    internal_status = status.upper() if status else "UNKNOWN"
    internal_conclusion = conclusion.upper() if conclusion else None
    
    return internal_status, internal_conclusion
