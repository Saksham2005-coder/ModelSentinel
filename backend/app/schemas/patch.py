from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# -----------------
# API Models
# -----------------

class PatchFileChangeBase(BaseModel):
    file_path: str
    change_type: str
    target_symbol: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    rationale: str
    original_hash: Optional[str] = None
    proposed_hash: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    diff_text: str

class PatchFileChangeResponse(PatchFileChangeBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class PatchReviewBase(BaseModel):
    decision: str
    comment: Optional[str] = None

class PatchReviewCreate(PatchReviewBase):
    reviewer_type: str = "human"

class PatchReviewResponse(PatchReviewBase):
    id: str
    reviewer_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class PatchProposalBase(BaseModel):
    summary: str
    rationale: str
    expected_behavior: str
    risk_summary: Optional[dict] = None

class PatchProposalResponse(PatchProposalBase):
    id: str
    investigation_id: str
    incident_id: str
    repository_id: str
    repository_snapshot_id: str
    version: int
    parent_patch_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    file_changes: List[PatchFileChangeResponse] = []
    reviews: List[PatchReviewResponse] = []

    class Config:
        from_attributes = True

# -----------------
# LLM Output Schemas
# -----------------

class AffectedFile(BaseModel):
    file_path: str
    target_symbol: Optional[str] = None
    change_type: str
    rationale: str
    expected_effect: str

class PatchPlanOutput(BaseModel):
    problem_statement: str
    evidence_summary: str
    intended_behavior: str
    affected_files: List[AffectedFile]
    test_changes: List[str]
    risks: List[str]
    assumptions: List[str]

class PatchHunk(BaseModel):
    context_lines_before: str = ""
    deleted_lines: str = ""
    added_lines: str = ""
    context_lines_after: str = ""

class PatchFileOutput(BaseModel):
    file_path: str
    target_symbol: Optional[str] = None
    change_type: str # modify, add, delete
    rationale: str
    patch_hunks: List[PatchHunk]

class PatchGenerationOutput(BaseModel):
    summary: str
    rationale: str
    expected_behavior: str
    files: List[PatchFileOutput]
    test_changes: List[str]
    risks: List[str]
    assumptions: List[str]
