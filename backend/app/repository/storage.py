import os
import zipfile
import hashlib
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

MAX_ZIP_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
MAX_EXTRACT_SIZE_BYTES = 100 * 1024 * 1024 # 100MB
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024 # 5MB

class RepositoryStorage:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.getenv("STORAGE_DIR", "./data/repositories")
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def get_repo_path(self, repo_id: str) -> str:
        return os.path.join(self.base_dir, repo_id)

    def compute_sha256(self, filepath: str) -> str:
        sha = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()

    def _is_safe_path(self, base: str, path: str) -> bool:
        resolved_path = os.path.abspath(os.path.join(base, path))
        return resolved_path.startswith(base)

    def extract_zip(self, repo_id: str, zip_path: str) -> bool:
        if os.path.getsize(zip_path) > MAX_ZIP_SIZE_BYTES:
            raise ValueError(f"ZIP file exceeds maximum allowed size of {MAX_ZIP_SIZE_BYTES} bytes.")

        repo_dir = self.get_repo_path(repo_id)
        os.makedirs(repo_dir, exist_ok=True)

        extracted_size = 0
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for info in zf.infolist():
                    if info.file_size > MAX_FILE_SIZE_BYTES:
                        logger.warning(f"Skipping {info.filename}: file too large ({info.file_size} bytes).")
                        continue
                        
                    extracted_size += info.file_size
                    if extracted_size > MAX_EXTRACT_SIZE_BYTES:
                        raise ValueError(f"Total extracted size exceeds limit of {MAX_EXTRACT_SIZE_BYTES} bytes.")

                    # Prevent path traversal
                    if not self._is_safe_path(repo_dir, info.filename):
                        logger.warning(f"Skipping unsafe path: {info.filename}")
                        continue

                    # Extract file
                    zf.extract(info, repo_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to extract zip: {e}")
            # Clean up
            shutil.rmtree(repo_dir, ignore_errors=True)
            raise e

    def delete_repo(self, repo_id: str):
        repo_dir = self.get_repo_path(repo_id)
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, ignore_errors=True)
