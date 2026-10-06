import os
import sys

from app.db.base import *
from app.db.session import SessionLocal
from app.models.repository import RepositorySnapshot, RepositoryFile

db = SessionLocal()

incidents = db.query(Incident).all()
for inc in incidents:
    print(inc.title, inc.id)

if not incidents:
    print("No incidents found.")
    sys.exit(1)

incident = incidents[0]

print(f"Incident: {incident.title}")

patch = db.query(PatchProposal).filter(PatchProposal.incident_id == incident.id, PatchProposal.status == 'approved').order_by(PatchProposal.created_at.desc()).first()
if not patch:
    print("No approved patch found for incident.")
    sys.exit(1)
    
print(f"Patch: {patch.id} - {patch.summary}")
print("Files changed:")
for fc in patch.file_changes:
    print(f" - {fc.file_path} ({fc.change_type})")
    print(fc.diff_text)
    
snapshot = db.query(RepositorySnapshot).filter(RepositorySnapshot.id == patch.repository_snapshot_id).first()
if snapshot:
    print(f"Snapshot: {snapshot.id}")
    files = db.query(RepositoryFile).filter(RepositoryFile.snapshot_id == snapshot.id).all()
    print("Files in repo:")
    for f in files:
        print(f" - {f.path}")
else:
    print("Snapshot not found.")
