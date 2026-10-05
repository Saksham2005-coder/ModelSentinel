import pytest
from app.models.patch import PatchProposal, PatchFileChange, PatchReview
from app.patch.service import PatchService
from app.patch.validator import PatchValidator, ValidationError
from app.schemas.patch import PatchGenerationOutput, PatchFileOutput, PatchHunk

def test_patch_risk_analyzer():
    from app.patch.risk import RiskAnalyzer
    from pydantic import BaseModel

    class DummyChange(BaseModel):
        file_path: str
        change_type: str
        additions: int = 0
        deletions: int = 0

    changes = [
        DummyChange(file_path="src/model.py", change_type="modify", additions=10, deletions=5)
    ]
    
    result = RiskAnalyzer.analyze(changes, ["tests/test_model.py"])
    assert result["level"] == "Low"

    # Test protected file
    changes.append(DummyChange(file_path=".env", change_type="modify", additions=1))
    result = RiskAnalyzer.analyze(changes, [])
    assert result["level"] == "Restricted"

def test_patch_validator_protected():
    validator = PatchValidator(None, "dummy", "/repo")
    
    output = PatchGenerationOutput(
        summary="Fix",
        rationale="Fix",
        expected_behavior="Fix",
        files=[
            PatchFileOutput(
                file_path=".env",
                change_type="modify",
                rationale="Change credentials",
                patch_hunks=[PatchHunk(added_lines="API_KEY=123")]
            )
        ],
        test_changes=[],
        risks=[],
        assumptions=[]
    )
    
    with pytest.raises(ValidationError, match="Cannot modify protected file"):
        validator.validate(output, [".env"])

def test_patch_validator_path_traversal():
    validator = PatchValidator(None, "dummy", "/repo")
    
    output = PatchGenerationOutput(
        summary="Fix",
        rationale="Fix",
        expected_behavior="Fix",
        files=[
            PatchFileOutput(
                file_path="../outside/file.py",
                change_type="modify",
                rationale="Hack",
                patch_hunks=[PatchHunk(added_lines="hack()")]
            )
        ],
        test_changes=[],
        risks=[],
        assumptions=[]
    )
    
    with pytest.raises(ValidationError, match="Path traversal detected"):
        validator.validate(output, ["../outside/file.py"])

def test_patch_validator_allowlist():
    validator = PatchValidator(None, "dummy", "/repo")
    
    output = PatchGenerationOutput(
        summary="Fix",
        rationale="Fix",
        expected_behavior="Fix",
        files=[
            PatchFileOutput(
                file_path="src/feature.py",
                change_type="modify",
                rationale="Fix feature",
                patch_hunks=[PatchHunk(added_lines="fix()")]
            )
        ],
        test_changes=[],
        risks=[],
        assumptions=[]
    )
    
    with pytest.raises(ValidationError, match="is not in the allowlist"):
        validator.validate(output, ["src/other.py"])
