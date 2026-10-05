import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SecurityScanner:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        
    def scan(self) -> Dict[str, Any]:
        """
        Scans the repository for security issues.
        Currently uses Bandit if installed in the environment.
        """
        has_bandit = False
        try:
            subprocess.run(["bandit", "--version"], capture_output=True, check=True)
            has_bandit = True
        except FileNotFoundError:
            pass
            
        if not has_bandit:
            return {
                "status": "skipped",
                "reason": "Bandit is not installed."
            }
            
        try:
            cmd = ["bandit", "-r", self.repo_path, "-f", "json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Bandit returns 0 if no issues, 1 if issues found
            status = "passed" if result.returncode == 0 else "failed"
            
            return {
                "status": status,
                "exit_code": result.returncode,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:2000]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "reason": "Security scan timed out."
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e)
            }
