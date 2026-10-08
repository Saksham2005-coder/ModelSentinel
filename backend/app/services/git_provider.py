import os
import requests
import urllib.parse
from typing import Dict, List, Optional, Any
from app.core.config import settings

class GitProvider:
    """Abstract base class for Git providers."""
    
    def create_branch(self, repo_id: str, branch_name: str, commit_sha: str) -> bool:
        raise NotImplementedError

    def create_commit(self, repo_id: str, message: str, tree_sha: str, parent_sha: str) -> str:
        raise NotImplementedError

    def create_pull_request(self, repo_id: str, title: str, description: str, head_branch: str, base_branch: str) -> Dict[str, Any]:
        raise NotImplementedError

    def get_pull_request_checks(self, repo_id: str, pr_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

class GitHubProvider(GitProvider):
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
            # We are in testing or mocked mode
            pass
        response = requests.request(method, url, headers=self.headers, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()

    def create_branch(self, repo_id: str, branch_name: str, commit_sha: str) -> bool:
        # For simplicity, repo_id could be owner/repo format.
        endpoint = f"/repos/{repo_id}/git/refs"
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": commit_sha
        }
        self._request("POST", endpoint, json=payload)
        return True

    def create_commit(self, repo_id: str, message: str, tree_sha: str, parent_sha: str) -> str:
        endpoint = f"/repos/{repo_id}/git/commits"
        payload = {
            "message": message,
            "tree": tree_sha,
            "parents": [parent_sha]
        }
        res = self._request("POST", endpoint, json=payload)
        return res["sha"]

    def create_pull_request(self, repo_id: str, title: str, description: str, head_branch: str, base_branch: str) -> Dict[str, Any]:
        endpoint = f"/repos/{repo_id}/pulls"
        payload = {
            "title": title,
            "body": description,
            "head": head_branch,
            "base": base_branch
        }
        res = self._request("POST", endpoint, json=payload)
        return res

    def get_pull_request_checks(self, repo_id: str, pr_id: str) -> List[Dict[str, Any]]:
        # In GitHub API, we usually query check runs by commit SHA, but we can query by PR commit
        # For this mock implementation, we assume pr_id is the pull request number
        # GET /repos/{owner}/{repo}/pulls/{pull_number} -> get head sha -> GET /repos/{owner}/{repo}/commits/{ref}/check-runs
        pr_data = self._request("GET", f"/repos/{repo_id}/pulls/{pr_id}")
        head_sha = pr_data["head"]["sha"]
        
        checks_data = self._request("GET", f"/repos/{repo_id}/commits/{head_sha}/check-runs")
        return checks_data.get("check_runs", [])
