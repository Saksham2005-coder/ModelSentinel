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
            path_parts = root.split(os.sep)
            if ".git" in path_parts or "node_modules" in path_parts or "venv" in path_parts or ".venv" in path_parts or "__pycache__" in path_parts:
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
                self.db.flush() # flush early to get ID instead of commit to save disk I/O latency
                
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
                            "type": dep.type,
                            "source_symbol": getattr(dep, 'source_symbol', None)
                        })

        # Cache symbols in memory to avoid N+1 queries during resolution
        # file_id -> {symbol_name -> symbol_id}
        local_symbols_cache = {}
        source_ids = list(set(d["source_id"] for d in pending_dependencies))
        
        batch_size = 500
        for i in range(0, len(source_ids), batch_size):
            batch = source_ids[i:i+batch_size]
            for sym in self.db.query(RepositorySymbol.repository_file_id, RepositorySymbol.name, RepositorySymbol.id).filter(
                RepositorySymbol.repository_file_id.in_(batch)
            ).all():
                file_id, name, sym_id = sym
                if file_id not in local_symbols_cache:
                    local_symbols_cache[file_id] = {}
                local_symbols_cache[file_id][name] = sym_id

        # Resolve dependencies loosely
        for dep in pending_dependencies:
            target = dep["target"]
            # Convert import path to a plausible file path
            target_path = target.replace(".", "/") + ".py"
            resolved_file_id = None
            resolved_symbol_id = None
            target_symbol_name = target
            
            if dep["type"] in ("call", "method_call"):
                # For calls, the target is usually a function/method in the same file or imported.
                # Try to resolve to a symbol in the same file first.
                source_id = dep["source_id"]
                if source_id in local_symbols_cache and target in local_symbols_cache[source_id]:
                    resolved_file_id = source_id
                    resolved_symbol_id = local_symbols_cache[source_id][target]
            else:
                # Import
                if target_path in path_to_file_id:
                    resolved_file_id = path_to_file_id[target_path]
                elif target_path.replace("/py", ".py") in path_to_file_id:
                    pass # Simple matching
                 
            self.db.add(RepositoryDependency(
                repository_snapshot_id=snapshot.id,
                source_file_id=dep["source_id"],
                source_symbol_name=dep["source_symbol"],
                target_reference=target,
                target_symbol_name=target_symbol_name,
                dependency_type=dep["type"],
                resolved_target_file_id=resolved_file_id,
                resolved_target_symbol_id=resolved_symbol_id
            ))

        snapshot.file_count = file_count
        snapshot.language_count = len(languages)
        snapshot.status = "ready"
        
        repo.current_commit = commit_sha
        repo.default_branch = branch
        repo.status = "ready"
        repo.indexed_at = datetime.now(timezone.utc)
        
        self.db.commit()
