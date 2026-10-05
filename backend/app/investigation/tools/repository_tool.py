from typing import Dict, Any, List
from app.investigation.tool_registry import registry
from app.repository.service import RepositoryService
from app.repository.git_service import GitService

@registry.register(
    name="get_repository_context",
    description="Gets the repository context associated with the incident's model.",
    parameters={}
)
def get_repository_context(**kwargs) -> Dict[str, Any]:
    db = kwargs.get("_context", {}).get("db")
    incident_id = kwargs.get("_context", {}).get("incident_id")
    if not db or not incident_id:
        return {"error": "Missing context"}

    from app.models.incident import Incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}

    svc = RepositoryService(db)
    return svc.get_context_for_incident(incident)


@registry.register(
    name="search_repository",
    description="Searches the code repository for a given query (feature name, function, file path).",
    parameters={
        "query": {
            "type": "string",
            "description": "The search term (e.g. url_length)"
        }
    }
)
def search_repository(query: str, **kwargs) -> Dict[str, Any]:
    db = kwargs.get("_context", {}).get("db")
    incident_id = kwargs.get("_context", {}).get("incident_id")
    if not db or not incident_id:
        return {"error": "Missing context"}

    from app.models.incident import Incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    svc = RepositoryService(db)
    context = svc.get_context_for_incident(incident)
    
    repo_id = context.get("repository", {}).get("id")
    if not repo_id:
        return {"error": "No repository linked"}
        
    return {"results": svc.search_code(repo_id, query)}


@registry.register(
    name="get_file_snippet",
    description="Retrieves a specific snippet of code from a file in the repository.",
    parameters={
        "file_path": {
            "type": "string",
            "description": "The path to the file."
        },
        "start_line": {
            "type": "integer",
            "description": "The starting line number (1-indexed)."
        },
        "end_line": {
            "type": "integer",
            "description": "The ending line number."
        }
    }
)
def get_file_snippet(file_path: str, start_line: int, end_line: int, **kwargs) -> Dict[str, Any]:
    db = kwargs.get("_context", {}).get("db")
    incident_id = kwargs.get("_context", {}).get("incident_id")
    if not db or not incident_id:
        return {"error": "Missing context"}

    from app.models.incident import Incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    svc = RepositoryService(db)
    context = svc.get_context_for_incident(incident)
    
    repo_id = context.get("repository", {}).get("id")
    if not repo_id:
        return {"error": "No repository linked"}
        
    snippet = svc.get_snippet(repo_id, file_path, start_line, end_line)
    if snippet is None:
        return {"error": "Snippet not found or traversal attempt."}
    return {"snippet": snippet}


@registry.register(
    name="get_recent_repository_changes",
    description="Gets the recent git commits made to the repository.",
    parameters={
        "limit": {
            "type": "integer",
            "description": "Maximum number of commits to retrieve."
        }
    }
)
def get_recent_repository_changes(limit: int = 10, **kwargs) -> Dict[str, Any]:
    db = kwargs.get("_context", {}).get("db")
    incident_id = kwargs.get("_context", {}).get("incident_id")
    
    from app.models.incident import Incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    svc = RepositoryService(db)
    context = svc.get_context_for_incident(incident)
    
    repo_id = context.get("repository", {}).get("id")
    if not repo_id:
        return {"error": "No repository linked"}
        
    repo_dir = svc.storage.get_repo_path(repo_id)
    git_svc = GitService(repo_dir)
    return {"commits": git_svc.get_recent_commits(limit)}
