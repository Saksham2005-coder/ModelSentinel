import sys
import traceback
import app.main
from app.db.session import SessionLocal
from app.models.repository import Repository
from app.repository.service import RepositoryService
from sqlalchemy import desc

db = SessionLocal()
# get latest repository
repo = db.query(Repository).order_by(desc(Repository.created_at)).first()
if not repo:
    print("No repo found")
    sys.exit(1)

print(f"Testing repo: {repo.name} - {repo.id}")
svc = RepositoryService(db)

try:
    svc.indexer.index_repository(repo.id)
    print("SUCCESS")
except Exception as e:
    print("FAILED")
    traceback.print_exc()

db.close()
