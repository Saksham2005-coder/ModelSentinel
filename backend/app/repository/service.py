import os
import shutil
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.repository import Repository, RepositorySnapshot, RepositoryFile, RepositorySymbol
from app.models.incident import Incident
from app.repository.storage import RepositoryStorage
from app.repository.indexer import RepositoryIndexer
from app.repository.git_service import GitService
from app.repository.relevance import RelevanceEngine

logger = logging.getLogger(__name__)

class RepositoryService:
    def __init__(self, db: Session):
        self.db = db
        self.storage = RepositoryStorage()
        self.indexer = RepositoryIndexer(db)

    def ingest_zip(self, name: str, zip_path: str, original_filename: str) -> Repository:
        repo = Repository(
            name=name,
            source_type="zip",
            source_reference=original_filename,
            status="pending"
        )
        self.db.add(repo)
        self.db.commit()

        try:
            self.storage.extract_zip(repo.id, zip_path)
            self.indexer.index_repository(repo.id)
        except Exception as e:
            repo.status = "failed"
            self.db.commit()
            raise e

        return repo

    def ingest_public_git(self, name: str, url: str) -> Repository:
        repo = Repository(
            name=name,
            source_type="public_git",
            source_reference=url,
            status="pending"
        )
        self.db.add(repo)
        self.db.commit()

        try:
            repo.status = "cloning"
            self.db.commit()
            
            repo_path = self.storage.get_repo_path(repo.id)
            GitService.clone_public_repo(url, repo_path)
            
            self.indexer.index_repository(repo.id)
        except Exception as e:
            repo.status = "failed"
            self.db.commit()
            raise e

        return repo

    def search_code(self, repository_id: str, query: str) -> List[Dict]:
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo or not repo.current_commit:
            return []
            
        snapshot = self.db.query(RepositorySnapshot).filter(
            RepositorySnapshot.repository_id == repository_id,
            RepositorySnapshot.commit_sha == repo.current_commit
        ).first()
        
        if not snapshot:
            return []

        # Search symbols
        symbols = self.db.query(RepositorySymbol).join(RepositoryFile).filter(
            RepositoryFile.repository_snapshot_id == snapshot.id,
            or_(
                RepositorySymbol.name.ilike(f"%{query}%"),
                RepositoryFile.path.ilike(f"%{query}%")
            )
        ).limit(50).all()

        results = []
        for sym in symbols:
            results.append({
                "file_path": sym.file.path,
                "symbol_name": sym.name,
                "symbol_type": sym.symbol_type,
                "start_line": sym.start_line,
                "end_line": sym.end_line
            })
        return results

    def get_snippet(self, repository_id: str, file_path: str, start_line: int, end_line: int) -> Optional[str]:
        repo_dir = self.storage.get_repo_path(repository_id)
        full_path = os.path.abspath(os.path.join(repo_dir, file_path))
        
        if not full_path.startswith(repo_dir):
            return None # Traversal attempt
            
        if not os.path.exists(full_path):
            return None
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 1-indexed
            s = max(0, start_line - 1)
            e = min(len(lines), end_line)
            return "".join(lines[s:e])
        except Exception:
            return None

    def get_context_for_incident(self, incident: Incident) -> Dict:
        from app.models.model import ModelVersion
        from app.models.monitoring import MonitoringRun
        
        mv = self.db.query(ModelVersion).filter(ModelVersion.id == incident.model_version_id).first()
        if not mv or not mv.repository_snapshot_id:
            return {"error": "Repository version not linked."}
            
        snapshot = self.db.query(RepositorySnapshot).filter(RepositorySnapshot.id == mv.repository_snapshot_id).first()
        if not snapshot:
            return {"error": "Repository snapshot not found."}
            
        repo = self.db.query(Repository).filter(Repository.id == snapshot.repository_id).first()
        
        # Get recent commits before incident
        repo_dir = self.storage.get_repo_path(repo.id)
        git_svc = GitService(repo_dir)
        
        # We need changed files up to X hours before incident
        # Since we use depth=1 for git clone initially, history might be shallow.
        # But if history exists:
        recent_commits = git_svc.get_recent_commits(10)
        
        changed_files = set()
        for c in recent_commits:
            try:
                ctime = datetime.fromisoformat(c["timestamp"].replace("Z", "+00:00"))
                # If commit is before incident but within 7 days
                if ctime <= incident.created_at and (incident.created_at - ctime).days <= 7:
                    c_files = git_svc.get_changed_files(c["sha"])
                    changed_files.update(c_files)
            except Exception:
                pass
                
        # Extract features mentioned in incident
        keywords = []
        if incident.title:
            keywords.extend(incident.title.split())
        
        # We can look into incident monitoring run details if we want
        # For simplicity, just use relevance engine on keywords
        engine = RelevanceEngine(self.db, snapshot.id)
        relevant = engine.find_relevant_files(keywords, changed_files)
        
        return {
            "repository": {
                "id": repo.id,
                "name": repo.name,
                "commit": snapshot.commit_sha
            },
            "relevant_files": relevant[:10], # Top 10
            "recent_commits": recent_commits[:5]
        }
