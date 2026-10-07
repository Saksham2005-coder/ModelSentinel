from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.repository import Repository, RepositorySnapshot, RepositoryFile, RepositorySymbol, RepositoryDependency
from app.models.incident import Incident, IncidentEvidence
from app.models.patch import PatchProposal, PatchFileChange
from app.models.validation import ValidationRun
from app.models.deployment_verification import DeploymentVerification
from app.repository.impact import classify_ml_component

class ChangeIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def get_file_symbols_and_imports(self, file_id: str):
        symbols = self.db.query(RepositorySymbol).filter(RepositorySymbol.repository_file_id == file_id).all()
        imports = self.db.query(RepositoryDependency).filter(
            RepositoryDependency.source_file_id == file_id,
            RepositoryDependency.dependency_type.in_(["import", "import_from"])
        ).all()
        return symbols, imports

    def analyze_changes(self, repository_id: str, snapshot_id: str, changed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        changed_files: [{"path": "...", "symbols": ["..."]}]
        """
        results = {
            "changed_files": [],
            "affected_dependencies": [],
            "ml_impact": [],
            "historical_evidence": [],
            "affected_models": [],
            "blast_radius": "LOW",
            "risk_score": 0,
            "risk_factors": []
        }

        if not changed_files:
            return results

        processed_file_ids = set()
        direct_changed_symbols = set()
        
        # 1. Analyze Changed Files & ML Impact
        for change in changed_files:
            rfile = self.db.query(RepositoryFile).filter(
                RepositoryFile.repository_snapshot_id == snapshot_id,
                RepositoryFile.path == change["path"]
            ).first()
            
            if not rfile:
                results["changed_files"].append({"path": change["path"], "status": "not_found_in_index"})
                continue
                
            processed_file_ids.add(rfile.id)
            symbols, imports = self.get_file_symbols_and_imports(rfile.id)
            
            sym_names = [s.name for s in symbols]
            imp_names = [i.target_reference for i in imports]
            
            ml_impact = classify_ml_component(rfile.path, sym_names, imp_names)
            
            results["changed_files"].append({
                "path": rfile.path,
                "symbols_changed": change.get("symbols", []),
                "ml_category": ml_impact["category"],
                "confidence": ml_impact["confidence"]
            })
            
            # Aggregate ML impact
            results["ml_impact"].append({
                "component": ml_impact["category"],
                "impact": ml_impact["confidence"],
                "reason": ml_impact["reason"]
            })
            
            for sym in change.get("symbols", []):
                direct_changed_symbols.add(sym)

        # 2. Dependency Traversal (Find what depends on changed files/symbols)
        # Bounded BFS traversal to prevent N+1 explosion
        dependent_symbols = set()
        visited_deps = set()
        queue = list(processed_file_ids)
        depth = 0
        MAX_DEPTH = 3
        MAX_DEPS = 100
        
        while queue and depth < MAX_DEPTH and len(dependent_symbols) < MAX_DEPS:
            current_batch = queue[:]
            queue = []
            
            deps = self.db.query(RepositoryDependency).filter(
                RepositoryDependency.repository_snapshot_id == snapshot_id,
                RepositoryDependency.resolved_target_file_id.in_(current_batch)
            ).all()
            
            for dep in deps:
                if dep.id in visited_deps:
                    continue
                visited_deps.add(dep.id)
                
                # If we know specific symbols changed, filter by target_symbol_name if available
                # If target_symbol_name is null, assume it's a file-level import
                if direct_changed_symbols and dep.target_symbol_name and dep.target_symbol_name not in direct_changed_symbols:
                    # Depending on a symbol that didn't change (heuristic)
                    pass
                else:
                    dependent_symbols.add(dep.source_symbol_name or dep.source_file.path)
                    queue.append(dep.source_file_id)
            
            depth += 1
            
        for d in dependent_symbols:
            results["affected_dependencies"].append(d)

        # 3. Historical Correlation
        # Look for past incidents involving these files
        paths = [c["path"] for c in changed_files]
        if paths:
            # We check patch file changes for past issues
            past_changes = self.db.query(PatchFileChange).filter(
                PatchFileChange.file_path.in_(paths)
            ).all()
            
            patch_ids = [p.patch_proposal_id for p in past_changes]
            
            if patch_ids:
                patches = self.db.query(PatchProposal).filter(PatchProposal.id.in_(patch_ids)).all()
                for p in patches:
                    if p.status in ("rejected", "changes_requested"):
                        results["historical_evidence"].append({
                            "type": "failed_patch",
                            "evidence": "DIRECT EVIDENCE",
                            "description": f"File was part of a rejected patch ({p.id[:8]})"
                        })
                
                incident_ids = [p.incident_id for p in patches if p.incident_id]
                if incident_ids:
                    incidents = self.db.query(Incident).filter(Incident.id.in_(incident_ids)).all()
                    for inc in incidents:
                        results["historical_evidence"].append({
                            "type": "incident",
                            "evidence": "HISTORICAL CORRELATION",
                            "description": f"File was previously patched for incident: {inc.category} ({inc.severity})"
                        })
                        results["affected_models"].append({
                            "model_id": inc.model_id,
                            "version_id": inc.model_version_id
                        })
        
        # Deduplicate models
        unique_models = []
        seen = set()
        for m in results["affected_models"]:
            key = f'{m["model_id"]}_{m["version_id"]}'
            if key not in seen:
                seen.add(key)
                unique_models.append(m)
        results["affected_models"] = unique_models

        # 4. Risk & Blast Radius
        risk_score = 0
        risk_factors = []
        
        # Base risk from ML components
        categories = set(m["component"] for m in results["ml_impact"])
        if "inference" in categories or "model_definition" in categories:
            risk_score += 40
            risk_factors.append("+40 Critical ML component (inference/model)")
            results["blast_radius"] = "HIGH"
        elif "feature_engineering" in categories or "preprocessing" in categories:
            risk_score += 30
            risk_factors.append("+30 Core data pipeline component")
            if results["blast_radius"] != "HIGH":
                results["blast_radius"] = "MEDIUM"
        elif "tests" in categories and len(categories) == 1:
            risk_score += 5
            risk_factors.append("+5 Test-only changes")
            
        # Dependencies factor
        dep_count = len(dependent_symbols)
        if dep_count > 20:
            risk_score += 20
            risk_factors.append(f"+20 Widespread dependency impact (>20 affected symbols)")
            results["blast_radius"] = "HIGH"
        elif dep_count > 5:
            risk_score += 10
            risk_factors.append(f"+10 Moderate dependency impact ({dep_count} affected symbols)")

        # Historical factor
        incidents = [e for e in results["historical_evidence"] if e["type"] == "incident"]
        if incidents:
            risk_score += min(len(incidents) * 10, 30)
            risk_factors.append(f"+{min(len(incidents) * 10, 30)} Historical incidents correlated with changed files")
            
        results["risk_score"] = min(risk_score, 100)
        results["risk_factors"] = risk_factors
        
        return results

    def analyze_patch(self, patch_id: str) -> Dict[str, Any]:
        patch = self.db.query(PatchProposal).filter(PatchProposal.id == patch_id).first()
        if not patch:
            return {"error": "Patch not found"}
            
        changes = []
        for fc in patch.file_changes:
            syms = []
            if fc.target_symbol:
                syms.append(fc.target_symbol)
            changes.append({
                "path": fc.file_path,
                "symbols": syms
            })
            
        return self.analyze_changes(patch.repository_id, patch.repository_snapshot_id, changes)
