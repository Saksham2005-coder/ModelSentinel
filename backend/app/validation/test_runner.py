import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        
    def run_tests(self) -> Dict[str, Any]:
        """
        Discovers and runs tests in the isolated environment.
        Currently supports pytest.
        """
        # Look for pytest tests
        # Checking if pytest is configured or tests directory exists
        has_pytest = False
        if os.path.exists(os.path.join(self.repo_path, "pytest.ini")) or \
           os.path.exists(os.path.join(self.repo_path, "tests")) or \
           os.path.exists(os.path.join(self.repo_path, "test")):
            has_pytest = True
            
        if not has_pytest:
            return {
                "status": "skipped",
                "reason": "No test suite discovered."
            }
            
        try:
            # We enforce a timeout and run pytest in a subprocess
            # Note: since this is an isolated repo, we assume python env has pytest
            # In a real system we would use a Docker container, but here we just run a subprocess
            cmd = ["pytest"]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60 # 60 seconds timeout
            )
            
            status = "passed" if result.returncode == 0 else "failed"
            return {
                "status": status,
                "exit_code": result.returncode,
                "stdout": result.stdout[:2000], # Summarize to avoid huge logs
                "stderr": result.stderr[:2000]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "reason": "Test execution timed out."
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e)
            }
