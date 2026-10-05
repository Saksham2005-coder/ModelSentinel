import os
import hashlib
from typing import List, Optional
from pydantic import BaseModel
import re

from app.models.repository import RepositoryFile, RepositorySymbol
from app.schemas.patch import PatchGenerationOutput, PatchFileOutput
from app.patch.risk import PROTECTED_PATHS

class ValidationError(Exception):
    pass

class PatchValidator:
    def __init__(self, db_session, repository_snapshot_id: str, repo_base_path: str):
        self.db = db_session
        self.snapshot_id = repository_snapshot_id
        self.repo_base_path = repo_base_path

    def _get_repo_file(self, file_path: str) -> Optional[RepositoryFile]:
        return self.db.query(RepositoryFile).filter(
            RepositoryFile.repository_snapshot_id == self.snapshot_id,
            RepositoryFile.path == file_path
        ).first()

    def _get_symbol(self, file_id: str, symbol_name: str) -> Optional[RepositorySymbol]:
        return self.db.query(RepositorySymbol).filter(
            RepositorySymbol.repository_file_id == file_id,
            RepositorySymbol.name == symbol_name
        ).first()

    def _is_safe_path(self, path: str) -> bool:
        resolved_path = os.path.abspath(os.path.join(self.repo_base_path, path))
        return resolved_path.startswith(os.path.abspath(self.repo_base_path))

    def _is_protected(self, path: str) -> bool:
        return any(p in path for p in PROTECTED_PATHS)

    def validate(self, patch: PatchGenerationOutput, allowlist_files: List[str]):
        if not patch.files:
            raise ValidationError("Patch contains no file changes.")

        for file_change in patch.files:
            # 5. file is allowlisted
            if file_change.file_path not in allowlist_files:
                raise ValidationError(f"File {file_change.file_path} is not in the allowlist.")

            # 3. path is inside repository root
            if not self._is_safe_path(file_change.file_path):
                raise ValidationError(f"Path traversal detected: {file_change.file_path}")

            # 4. path is not protected
            if self._is_protected(file_change.file_path):
                raise ValidationError(f"Cannot modify protected file: {file_change.file_path}")

            repo_file = self._get_repo_file(file_change.file_path)

            if file_change.change_type in ['modify', 'delete']:
                # 1. file exists for modify/delete
                if not repo_file:
                    raise ValidationError(f"File {file_change.file_path} does not exist in repository snapshot.")
                
                # 6. symbol exists where required
                if file_change.target_symbol:
                    symbol = self._get_symbol(repo_file.id, file_change.target_symbol)
                    if not symbol:
                        raise ValidationError(f"Symbol {file_change.target_symbol} does not exist in {file_change.file_path}")

            elif file_change.change_type == 'add':
                # 2. add target does not already exist
                if repo_file:
                    raise ValidationError(f"File {file_change.file_path} already exists. Cannot add.")

            # 8. diff syntax is valid (basic check)
            for hunk in file_change.patch_hunks:
                if not hunk.added_lines and not hunk.deleted_lines:
                    raise ValidationError(f"Hunk in {file_change.file_path} has no additions or deletions.")

            # 12. only permitted file types are modified (preventing binaries)
            ext = os.path.splitext(file_change.file_path)[1].lower()
            if ext in ['.pyc', '.so', '.dll', '.exe', '.bin', '.pdf', '.png', '.jpg', '.jpeg']:
                raise ValidationError(f"Cannot modify binary file type: {ext}")

        return True
