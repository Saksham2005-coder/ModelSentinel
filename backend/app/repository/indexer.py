import os
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.repository import Repository, RepositorySnapshot, RepositoryFile, RepositorySymbol, RepositoryDependency
from app.repository.parser import RepositoryParser
from app.repository.storage import RepositoryStorage
from app.repository.git_service import GitService

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".js": "javascript",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown"
}

class RepositoryIndexer:
    def __init__(self, db: Session):
        self.db = db
        self.storage = RepositoryStorage()

    def index_repository(self, repository_id: str):
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")

        repo_dir = self.storage.get_repo_path(repository_id)
        if not os.path.exists(repo_dir):
            repo.status = "failed"
            self.db.commit()
            raise ValueError(f"Repository directory not found: {repo_dir}")

        repo.status = "indexing"
        self.db.commit()

        git_service = GitService(repo_dir)
        commit_sha = git_service.get_current_commit()
        branch = git_service.get_default_branch()

        snapshot = RepositorySnapshot(
            repository_id=repository_id,
            commit_sha=commit_sha,
            branch=branch
        )
        self.db.add(snapshot)
        self.db.commit()

        file_count = 0
        languages = set()
        
        path_to_file_id = {}
        pending_dependencies = []

        for root, _, files in os.walk(repo_dir):
            if ".git" in root.split(os.sep):
                continue

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                
                # Check for files without extension (like Dockerfile)
                if not ext and file.lower() == "dockerfile":
                    language = "dockerfile"
                elif file.lower() == "requirements.txt":
                    language = "requirements"
                elif ext in SUPPORTED_EXTENSIONS:
                    language = SUPPORTED_EXTENSIONS[ext]
                else:
                    continue

                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, repo_dir).replace('\\', '/')
                
                try:
                    size_bytes = os.path.getsize(filepath)
                    sha256 = self.storage.compute_sha256(filepath)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_count = len(content.splitlines())
                        is_binary = False
                except UnicodeDecodeError:
                    is_binary = True
                    line_count = 0
                    content = ""
                except Exception as e:
                    logger.warning(f"Failed to read file {filepath}: {e}")
                    continue

                repo_file = RepositoryFile(
                    repository_snapshot_id=snapshot.id,
                    path=rel_path,
                    language=language,
                    size_bytes=size_bytes,
                    sha256=sha256,
                    line_count=line_count,
                    is_binary=is_binary
                )
                self.db.add(repo_file)
                self.db.commit() # commit early to get ID
                
                path_to_file_id[rel_path] = repo_file.id
                
                file_count += 1
                languages.add(language)

                if language == "python" and not is_binary:
                    symbols, dependencies = RepositoryParser.parse_python(rel_path, content)
                    for sym_info in symbols:
                        sym = RepositorySymbol(
                            repository_file_id=repo_file.id,
                            symbol_type=sym_info.symbol_type,
                            name=sym_info.name,
                            qualified_name=sym_info.qualified_name(),
                            start_line=sym_info.start_line,
                            end_line=sym_info.end_line,
                            parent_symbol=sym_info.parent,
                            signature=sym_info.signature
                        )
                        self.db.add(sym)
                    
                    for dep in dependencies:
                        pending_dependencies.append({
                            "source_id": repo_file.id,
                            "source_path": rel_path,
                            "target": dep.target,
                            "type": dep.type
                        })

        # Resolve dependencies loosely
        for dep in pending_dependencies:
            target = dep["target"]
            # Convert import path to a plausible file path
            target_path = target.replace(".", "/") + ".py"
            resolved_id = None
            if target_path in path_to_file_id:
                resolved_id = path_to_file_id[target_path]
            elif target_path.replace("/py", ".py") in path_to_file_id:
                 pass # Simple matching
                 
            self.db.add(RepositoryDependency(
                repository_snapshot_id=snapshot.id,
                source_file_id=dep["source_id"],
                target_reference=target,
                dependency_type=dep["type"],
                resolved_target_file_id=resolved_id
            ))

        snapshot.file_count = file_count
        snapshot.language_count = len(languages)
        snapshot.status = "ready"
        
        repo.current_commit = commit_sha
        repo.default_branch = branch
        repo.status = "ready"
        repo.indexed_at = datetime.now(timezone.utc)
        
        self.db.commit()
