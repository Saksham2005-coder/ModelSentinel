import os
import sys
from datetime import datetime, timezone

from app.db.base import *
from app.db.session import SessionLocal
from app.models.model import Model, ModelVersion
from app.models.incident import Incident
from app.models.patch import PatchProposal, PatchFileChange
from app.models.repository import RepositorySnapshot, Repository, RepositoryFile

db = SessionLocal()

# Get model
m = db.query(Model).filter(Model.slug == 'email-spam-classifier').first()
v = m.versions[1]

# Create repo
repo = Repository(
    name="Email Spam Classifier Repo",
    source_type="git",
    source_reference="internal/email-spam",
    status="active"
)
db.add(repo)
db.commit()

snapshot = RepositorySnapshot(
    repository_id=repo.id,
    commit_sha="abc123def456",
    status="ready"
)
db.add(snapshot)
db.commit()

# Add a dummy file to repo
repo_file = RepositoryFile(
    repository_snapshot_id=snapshot.id,
    path="model.py",
    language="python",
    size_bytes=1024,
    sha256="dummy"
)
db.add(repo_file)
db.commit()

# Create incident
import uuid
inc = Incident(
    incident_key=f"spam-drift-{uuid.uuid4().hex[:8]}",
    model_id=m.id,
    model_version_id=v.id,
    title="Email Spam Classifier Data Drift",
    severity="high",
    status="validation",
    category="data_drift"
)
db.add(inc)
db.commit()

from app.models.investigation import Investigation
inv = Investigation(
    id="dummy-inv",
    incident_id=inc.id,
    status="completed",
    summary="Data drift investigation"
)
db.add(inv)
db.commit()

# Create patch
patch = PatchProposal(
    investigation_id="dummy-inv",
    incident_id=inc.id,
    repository_id=repo.id,
    repository_snapshot_id=snapshot.id,
    version=1,
    status="approved",
    summary="Fix preprocessing to handle drifted URL length",
    rationale="The URL length feature drifted, causing false negatives.",
    expected_behavior="The model will cap URL length at the 99th percentile, improving F1 score."
)
db.add(patch)
db.commit()

fc = PatchFileChange(
    patch_proposal_id=patch.id,
    file_path="model.py",
    change_type="modify",
    rationale="Update preprocessing logic",
    diff_text="@@\n-        url_length = len(url)\n+        url_length = min(len(url), 100)\n"
)
db.add(fc)
db.commit()

# Generate patched dataset
import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 1000
data_dir = os.path.join(os.path.dirname(__file__), 'data')
c_target = np.random.choice([0, 1], p=[0.61, 0.39], size=n_samples) 
# Patched model fixes the predictions (improved F1)
c_prob = np.where(c_target == 1, np.random.beta(7, 3, n_samples), np.random.beta(3, 7, n_samples))
c_pred = (c_prob > 0.5).astype(int)

patched_df = pd.DataFrame({
    'target': c_target,
    'prediction': c_pred,
    'probability': c_prob,
    'url_length': np.random.normal(25, 5, n_samples),
    'url_count': np.random.poisson(2, n_samples),
    'sender_domain': np.random.choice(['gmail.com', 'yahoo.com'], size=n_samples)
})
patched_df.to_csv(os.path.join(data_dir, f'{m.slug}_patched.csv'), index=False)

print(f"Setup complete. Incident ID: {inc.id}, Patch ID: {patch.id}")
