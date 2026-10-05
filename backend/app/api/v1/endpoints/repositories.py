from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Any
import os
import tempfile
import uuid

from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.models.repository import Repository
from app.repository.service import RepositoryService

router = APIRouter()

@router.post("/", status_code=202)
def create_repository(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    source_type: str = Form(...),
    url: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    service = RepositoryService(db)
    
    if source_type == "public_git":
        if not url:
            raise HTTPException(status_code=400, detail="URL is required for public_git")
        repo = Repository(
            name=name,
            source_type="public_git",
            source_reference=url,
            status="pending"
        )
        db.add(repo)
        db.commit()
        
        # We would run this in background
        def bg_task(repo_id: str):
            with get_db() as db_session:
                svc = RepositoryService(db_session)
                try:
                    repo_obj = db_session.query(Repository).filter(Repository.id == repo_id).first()
                    repo_obj.status = "cloning"
                    db_session.commit()
                    
                    from app.repository.git_service import GitService
                    repo_path = svc.storage.get_repo_path(repo_id)
                    GitService.clone_public_repo(url, repo_path)
                    
                    svc.indexer.index_repository(repo_id)
                except Exception as e:
                    repo_obj = db_session.query(Repository).filter(Repository.id == repo_id).first()
                    if repo_obj:
                        repo_obj.status = "failed"
                        db_session.commit()

        background_tasks.add_task(bg_task, repo.id)
        return {"id": repo.id, "status": repo.status}

    elif source_type == "zip":
        if not file:
            raise HTTPException(status_code=400, detail="File is required for zip")
            
        repo = Repository(
            name=name,
            source_type="zip",
            source_reference=file.filename,
            status="pending"
        )
        db.add(repo)
        db.commit()
        
        # Save uploaded file to temp
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.zip")
        with open(temp_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
            
        def bg_task_zip(repo_id: str, zip_path: str):
            with get_db() as db_session:
                svc = RepositoryService(db_session)
                try:
                    svc.storage.extract_zip(repo_id, zip_path)
                    svc.indexer.index_repository(repo_id)
                except Exception as e:
                    repo_obj = db_session.query(Repository).filter(Repository.id == repo_id).first()
                    if repo_obj:
                        repo_obj.status = "failed"
                        db_session.commit()
                finally:
                    # Cleanup temp zip
                    try:
                        os.remove(zip_path)
                        os.rmdir(os.path.dirname(zip_path))
                    except:
                        pass
                        
        background_tasks.add_task(bg_task_zip, repo.id, temp_path)
        return {"id": repo.id, "status": repo.status}

    raise HTTPException(status_code=400, detail="Invalid source_type")

@router.get("/")
def list_repositories(db: Session = Depends(get_db)):
    repos = db.query(Repository).all()
    return [{
        "id": r.id,
        "name": r.name,
        "source_type": r.source_type,
        "status": r.status,
        "indexed_at": r.indexed_at,
        "current_commit": r.current_commit
    } for r in repos]

@router.get("/{repository_id}")
def get_repository(repository_id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {
        "id": repo.id,
        "name": repo.name,
        "source_type": repo.source_type,
        "status": repo.status,
        "indexed_at": repo.indexed_at,
        "current_commit": repo.current_commit
    }

@router.get("/{repository_id}/search")
def search_repository(repository_id: str, q: str, db: Session = Depends(get_db)):
    svc = RepositoryService(db)
    return svc.search_code(repository_id, q)

@router.get("/{repository_id}/files")
def get_repository_files(repository_id: str, file_path: str, db: Session = Depends(get_db)):
    svc = RepositoryService(db)
    # just return snippet for whole file
    content = svc.get_snippet(repository_id, file_path, 1, 999999)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"path": file_path, "content": content}
