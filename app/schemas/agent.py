"""
Pydantic schemas used for Gemini structured outputs (JSON schema response enforcement).
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ResearchPlan(BaseModel):
    """Decomposition of a complex scientific inquiry into atomic sub-questions."""
    sub_questions: List[str] = Field(
        ...,
        min_items=1,
        max_items=5,
        description="2 to 5 targeted sub-questions investigating methodology, metrics, and findings."
    )
    rationale: str = Field(
        default="",
        description="Brief reasoning for this decomposition strategy."
    )


class ExtractedFinding(BaseModel):
    """Structured extraction of empirical evidence per paper."""
    document_id: str = Field(..., description="ID of the source paper")
    paper_title: str = Field(..., description="Title or filename of the paper")
    methodology: str = Field(..., description="Architecture, algorithm, or methodology proposed")
    dataset: str = Field(..., description="Benchmarks or datasets evaluated on")
    metric_name: str = Field(..., description="Primary metric (e.g. F1, BLEU, Accuracy, Latency)")
    metric_value: str = Field(..., description="Reported score or value (e.g. 84.2%, 12ms)")
    baseline_comparison: str = Field(..., description="Prior work or baseline compared against")
    limitations: str = Field(..., description="Reported failure modes, compute constraints, or bounds")
    source_passage_ids: List[int] = Field(
        ...,
        description="List of integer passage IDs in evidence grounding this finding"
    )


class ExtractionList(BaseModel):
    findings: List[ExtractedFinding] = Field(default_factory=list)


class ContradictionItem(BaseModel):
    """Pairwise NLI conflict or consensus assessment between findings."""
    topic: str = Field(..., description="Shared task, dataset, or claim being compared")
    papers_involved: List[str] = Field(..., description="Names or IDs of papers being compared")
    relationship: Literal["consensus", "conflict", "insufficient_evidence"] = Field(
        ...,
        description="Whether papers agree, contradict, or have non-comparable setups"
    )
    explanation: str = Field(
        ...,
        description="Concrete explanation citing what specifically conflicts or agrees"
    )
    passage_ids: List[int] = Field(
        default_factory=list,
        description="Evidence passage numbers supporting this relationship"
    )


class ComparisonMatrix(BaseModel):
    """Comparative synthesis across multiple papers."""
    items: List[ContradictionItem] = Field(default_factory=list)
    consensus_summary: str = Field(default="", description="Key shared findings across papers")
    contradictions_summary: str = Field(default="", description="Key conflicting results or discrepancies")
    research_gaps: str = Field(default="", description="Open questions or unexplored dimensions")


class AtomicClaimVerification(BaseModel):
    """Verification of a single atomic factual assertion against cited evidence."""
    claim: str = Field(..., description="Atomic factual statement from generated answer")
    status: Literal["supported", "partially_supported", "unsupported"] = Field(
        ...,
        description="Strict NLI entailment classification"
    )
    cited_passage_ids: List[int] = Field(
        default_factory=list,
        description="Passage numbers referenced by the claim"
    )
    reasoning: str = Field(
        ...,
        description="Entailment explanation based solely on cited passages"
    )


class VerificationReport(BaseModel):
    """Complete claim-level verification result."""
    overall_status: Literal["verified", "partially_verified", "unsupported"] = Field(
        ...,
        description="Overall confidence status of the answer"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Composite confidence score [0.0 - 1.0]"
    )
    claims: List[AtomicClaimVerification] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

