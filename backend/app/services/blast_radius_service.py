from sqlalchemy.orm import Session
from app.models.patch import PatchProposal, PatchFileChange
from app.models.incident import Incident
from app.models.incident_memory import IncidentMemory
from app.models.regression import RegressionCase
from app.models.repository import RepositoryDependency, RepositoryFile

class BlastRadiusService:
    @staticmethod
    def calculate_blast_radius(db: Session, patch: PatchProposal) -> dict:
        # Get files changed in this patch
        file_changes = db.query(PatchFileChange).filter(PatchFileChange.patch_proposal_id == patch.id).all()
        changed_file_paths = [fc.file_path for fc in file_changes]

        if not changed_file_paths:
            return {
                "files": [],
                "models": [],
                "features": [],
                "regression_tests": [],
                "historical_incidents": []
            }

        # 1. Historical Incidents & Models & Features & Regression Tests
        # Find other patches that modified these same files
        historical_patches = db.query(PatchFileChange).filter(
            PatchFileChange.file_path.in_(changed_file_paths),
            PatchFileChange.patch_proposal_id != patch.id
        ).all()
        
        historical_patch_ids = list(set([hp.patch_proposal_id for hp in historical_patches]))
        
        related_incidents = set()
        related_models = set()
        related_features = set()
        related_regressions = set()

        if historical_patch_ids:
            patches = db.query(PatchProposal).filter(PatchProposal.id.in_(historical_patch_ids)).all()
            incident_ids = [p.incident_id for p in patches if p.incident_id]
            
            if incident_ids:
                # Get incidents
                incidents = db.query(Incident).filter(Incident.id.in_(incident_ids)).all()
                for i in incidents:
                    related_incidents.add(i.id)
                    related_models.add(i.model_id)

                # Get incident memories to extract features
                memories = db.query(IncidentMemory).filter(IncidentMemory.incident_id.in_(incident_ids)).all()
                memory_ids = []
                for m in memories:
                    memory_ids.append(m.id)
                    if m.affected_features:
                        for f in m.affected_features:
                            related_features.add(f)
                
                # Get regression cases related to these incidents
                if memory_ids:
                    regressions = db.query(RegressionCase).filter(RegressionCase.incident_memory_id.in_(memory_ids), RegressionCase.status == 'active').all()
                    for r in regressions:
                        related_regressions.add(r.id)

        # 2. Dependency resolution using Repository Intelligence
        # Find which files depend on the changed files
        dependent_files = set()
        if patch.repository_snapshot_id:
            # Find RepositoryFile ids for the changed paths
            repo_files = db.query(RepositoryFile).filter(
                RepositoryFile.repository_snapshot_id == patch.repository_snapshot_id,
                RepositoryFile.path.in_(changed_file_paths)
            ).all()
            repo_file_ids = [rf.id for rf in repo_files]
            
            if repo_file_ids:
                deps = db.query(RepositoryDependency).filter(
                    RepositoryDependency.repository_snapshot_id == patch.repository_snapshot_id,
                    RepositoryDependency.resolved_target_file_id.in_(repo_file_ids)
                ).all()
                
                source_file_ids = [d.source_file_id for d in deps]
                if source_file_ids:
                    source_files = db.query(RepositoryFile).filter(RepositoryFile.id.in_(source_file_ids)).all()
                    for sf in source_files:
                        dependent_files.add(sf.path)

        return {
            "files": list(set(changed_file_paths) | dependent_files),
            "models": list(related_models),
            "features": list(related_features),
            "regression_tests": list(related_regressions),
            "historical_incidents": list(related_incidents)
        }
