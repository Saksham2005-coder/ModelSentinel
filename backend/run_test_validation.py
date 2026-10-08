import time
import requests
import sys

from app.db.base import *
from app.db.session import SessionLocal
from app.models.patch import PatchProposal

db = SessionLocal()
patch = db.query(PatchProposal).filter(PatchProposal.status == 'approved').order_by(PatchProposal.created_at.desc()).first()

if not patch:
    print("No patch found")
    sys.exit(1)

res = requests.post(f"http://127.0.0.1:8000/api/v1/patches/{patch.id}/validation")
if res.status_code != 200:
    print("Failed to start validation:", res.text)
    sys.exit(1)

data = res.json()
run_id = data["validation_id"]
print(f"Started validation run {run_id}")

import time
time.sleep(2) # Give background task a moment
status_res = requests.get(f"http://127.0.0.1:8000/api/v1/validation/{run_id}")
status_data = status_res.json()
print("Run Details:", status_data)

checks_res = requests.get(f"http://127.0.0.1:8000/api/v1/validation/{run_id}/checks")
print("Checks:", checks_res.json())

metrics_res = requests.get(f"http://127.0.0.1:8000/api/v1/validation/{run_id}/metrics")
print("Metrics:", metrics_res.json())
