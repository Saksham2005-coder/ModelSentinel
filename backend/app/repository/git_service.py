import subprocess
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.timeout = 10

    def _run_git(self, args: List[str]) -> str:
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {cmd}")
            raise Exception("Git command timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise Exception(f"Git error: {e.stderr.strip()}")

    def get_current_commit(self) -> Optional[str]:
        try:
            return self._run_git(["rev-parse", "HEAD"])
        except Exception:
            return None

    def get_default_branch(self) -> Optional[str]:
        try:
            return self._run_git(["branch", "--show-current"])
        except Exception:
            return None

    def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        try:
            out = self._run_git(["log", f"-n{limit}", "--format=%H|%an|%aI|%s"])
            commits = []
            for line in out.splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "sha": parts[0],
                        "author": parts[1],
                        "timestamp": parts[2],
                        "message": parts[3]
                    })
            return commits
        except Exception:
            return []

    def get_commit_metadata(self, commit_sha: str) -> Optional[Dict]:
        try:
            out = self._run_git(["show", "-s", "--format=%H|%an|%aI|%s", commit_sha])
            if out:
                parts = out.split("|", 3)
                if len(parts) == 4:
                    return {
                        "sha": parts[0],
                        "author": parts[1],
                        "timestamp": parts[2],
                        "message": parts[3]
                    }
            return None
        except Exception:
            return None

    def get_changed_files(self, commit_sha: str) -> List[str]:
        try:
            out = self._run_git(["diff-tree", "--no-commit-id", "--name-only", "-r", commit_sha])
            return [line.strip() for line in out.splitlines() if line.strip()]
        except Exception:
            return []

    def get_file_history(self, filepath: str, limit: int = 5) -> List[Dict]:
        try:
            # Note: We must ensure filepath does not contain dangerous characters
            # Subprocess without shell=True is generally safe, but good to be careful
            out = self._run_git(["log", f"-n{limit}", "--format=%H|%aI|%s", "--", filepath])
            commits = []
            for line in out.splitlines():
                parts = line.split("|", 2)
                if len(parts) == 3:
                    commits.append({
                        "sha": parts[0],
                        "timestamp": parts[1],
                        "message": parts[2]
                    })
            return commits
        except Exception:
            return []

    @staticmethod
    def clone_public_repo(url: str, dest_path: str):
        # Validate URL starts with https://
        if not url.startswith("https://"):
            raise ValueError("Only HTTPS public Git URLs are allowed")
            
        cmd = ["git", "clone", "--depth", "1", url, dest_path]
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
        except subprocess.TimeoutExpired:
            logger.error("Git clone timed out")
            raise Exception("Git clone timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed: {e.stderr}")
            raise Exception(f"Git clone error: {e.stderr.strip()}")
