import sys
from app.db.base import *
from app.db.session import SessionLocal
from app.models.incident import Incident
from app.models.patch import PatchProposal
from app.models.investigation import Investigation

db = SessionLocal()

patch = db.query(PatchProposal).filter(PatchProposal.status == 'approved').order_by(PatchProposal.created_at.desc()).first()
if not patch:
    print("No patch")
    sys.exit(1)

incident = db.query(Incident).filter(Incident.id == patch.incident_id).first()

# Create investigation
inv = Investigation(
    id=patch.investigation_id,
    incident_id=incident.id,
    status="completed",
    summary="Data drift investigation"
)
db.add(inv)
try:
    db.commit()
    print("Investigation created.")
except Exception as e:
    print("Already exists or error:", e)
