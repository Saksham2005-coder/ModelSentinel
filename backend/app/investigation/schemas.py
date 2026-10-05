from pydantic import BaseModel, Field
from typing import List, Optional

class InvestigationPlan(BaseModel):
    questions: List[str] = Field(description="Questions to answer during the investigation")
    evidence_types: List[str] = Field(description="Types of evidence to look for")
    priority: str = Field(description="Priority of the investigation")
    tools_to_run: List[str] = Field(description="List of exact tool names to run from the registry")

class EvidenceAssessment(BaseModel):
    evidence_id: str = Field(description="The unique identifier for this evidence item")
    relationship: str = Field(description="supports, contradicts, neutral, or context")
    explanation: str = Field(description="Why this evidence relates to the hypothesis in this way")

class HypothesisBase(BaseModel):
    title: str = Field(description="Short title for the hypothesis")
    description: str = Field(description="Detailed explanation of the hypothesis")
    status: str = Field(description="supported, plausible, weak, rejected, insufficient_evidence")
    evidence_strength: str = Field(description="high, moderate, low, insufficient")
    assessments: List[EvidenceAssessment] = Field(description="List of evidence assessments for this hypothesis")

class InvestigationConclusion(BaseModel):
    summary: str = Field(description="Summary of the investigation")
    primary_hypothesis_id: Optional[str] = Field(None, description="The ID (from the generated hypotheses list) of the most supported explanation")
    limitations: str = Field(description="Limitations of the investigation")
    recommended_next_steps: str = Field(description="What a human operator should do next")
