import os
import shutil
import tempfile
import logging
from typing import Dict, Any, List

from app.models.patch import PatchProposal
from app.repository.storage import RepositoryStorage

logger = logging.getLogger(__name__)

class ValidationEnvironment:
    """
    Provides an isolated execution environment for a patch.
    This copies the original repository snapshot to a temporary directory
    and applies the patch there.
    """
    def __init__(self, patch: PatchProposal, storage: RepositoryStorage):
        self.patch = patch
        self.storage = storage
        self.temp_dir = tempfile.mkdtemp(prefix=f"val_{patch.id}_")
        self.repo_path = os.path.join(self.temp_dir, "repo")
        
    def setup(self):
        """Copies the original snapshot into the isolated directory."""
        original_repo_path = self.storage.get_repo_path(self.patch.repository_id)
        if not os.path.exists(original_repo_path):
            raise FileNotFoundError(f"Original repository path not found: {original_repo_path}")
            
        logger.info(f"Setting up isolated environment at {self.repo_path}")
        shutil.copytree(original_repo_path, self.repo_path)
        
    def apply_patch(self):
        """Applies the file changes defined in the patch to the isolated repository."""
        logger.info(f"Applying patch {self.patch.id} in isolated environment")
        
        for change in self.patch.file_changes:
            target_path = os.path.join(self.repo_path, change.file_path)
            
            # Prevent path traversal
            resolved_path = os.path.abspath(target_path)
            if not resolved_path.startswith(os.path.abspath(self.repo_path)):
                raise ValueError(f"Unsafe path detected in patch: {change.file_path}")
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            
            if change.change_type == "delete":
                if os.path.exists(resolved_path):
                    os.remove(resolved_path)
            else:
                # Apply diff_text. Simple context replacement.
                # Better patch applier
                if os.path.exists(resolved_path):
                    with open(resolved_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                else:
                    file_content = ""

                diff_lines = change.diff_text.splitlines()
                
                hunks = []
                current_hunk = None
                for line in diff_lines:
                    if line.startswith("---") or line.startswith("+++"):
                        continue
                    if line == "@@":
                        if current_hunk:
                            hunks.append(current_hunk)
                        current_hunk = {"before": [], "deleted": [], "added": [], "after": []}
                        # We don't have explicit sections, we just infer from + and - 
                    elif current_hunk is not None:
                        if line.startswith("-"):
                            current_hunk["deleted"].append(line[1:])
                        elif line.startswith("+"):
                            current_hunk["added"].append(line[1:])
                        else:
                            # It's context. If we haven't seen deleted/added, it's before.
                            if not current_hunk["deleted"] and not current_hunk["added"]:
                                current_hunk["before"].append(line)
                            else:
                                current_hunk["after"].append(line)
                if current_hunk:
                    hunks.append(current_hunk)
                    
                for hunk in hunks:
                    search_str = "\n".join(hunk["before"] + hunk["deleted"] + hunk["after"])
                    replace_str = "\n".join(hunk["before"] + hunk["added"] + hunk["after"])
                    if search_str:
                        file_content = file_content.replace(search_str, replace_str)
                    
                with open(resolved_path, "w", encoding="utf-8") as f:
                    f.write(file_content)

                    
    def teardown(self):
        """Cleans up the isolated environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

