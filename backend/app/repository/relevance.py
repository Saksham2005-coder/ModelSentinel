import os
import re
from typing import List, Dict, Set
from sqlalchemy.orm import Session
from app.models.repository import RepositoryFile, RepositorySymbol, RepositoryDependency, RepositorySnapshot

class RelevanceEngine:
    def __init__(self, db: Session, snapshot_id: str):
        self.db = db
        self.snapshot_id = snapshot_id

    def normalize_feature(self, name: str) -> str:
        # e.g. url_length -> urllength, URL_Length -> urllength
        return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

    def find_relevant_files(self, keywords: List[str], changed_files: Set[str]) -> List[Dict]:
        results = {}
        
        normalized_keywords = [self.normalize_feature(k) for k in keywords if k]
        if not normalized_keywords:
            return []

        # Find matching symbols
        symbols = self.db.query(RepositorySymbol).join(RepositoryFile).filter(
            RepositoryFile.repository_snapshot_id == self.snapshot_id
        ).all()

        for sym in symbols:
            norm_sym_name = self.normalize_feature(sym.name)
            for nk in normalized_keywords:
                if nk in norm_sym_name or norm_sym_name in nk:
                    # Match!
                    if sym.repository_file_id not in results:
                        results[sym.repository_file_id] = {
                            "file": sym.file,
                            "score": 0,
                            "reasons": set()
                        }
                    
                    if sym.name == nk or norm_sym_name == nk:
                        results[sym.repository_file_id]["score"] += 10
                        results[sym.repository_file_id]["reasons"].add(f"Exact feature/symbol match: {sym.name}")
                    else:
                        results[sym.repository_file_id]["score"] += 3
                        results[sym.repository_file_id]["reasons"].add(f"Partial feature/symbol match: {sym.name}")

        # Add score for recent changes
        for file_id, data in results.items():
            if data["file"].path in changed_files:
                data["score"] += 5
                data["reasons"].add("File changed recently before incident.")

        # Boost by dependency (if a file is relevant, things importing it or imported by it might be relevant)
        # Simplified: we just return what we have sorted
        
        output = []
        for file_id, data in results.items():
            # Determine relevance level
            level = "Low"
            if data["score"] >= 10:
                level = "High"
            elif data["score"] >= 5:
                level = "Medium"
                
            output.append({
                "file_path": data["file"].path,
                "relevance": level,
                "reasons": list(data["reasons"]),
                "score": data["score"]
            })

        output.sort(key=lambda x: x["score"], reverse=True)
        return output
