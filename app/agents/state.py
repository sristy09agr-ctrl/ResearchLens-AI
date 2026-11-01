"""
State representation for the ResearchLens LangGraph agent.
"""

from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.agent import ComparisonMatrix, VerificationReport, ExtractedFinding


class AgentState(TypedDict):
    # Inputs
    query: str
    document_ids: List[str]
    top_k: int
    candidate_k: int
    alpha: float
    conversation_id: Optional[str]

    # Reasoning state
    iteration: int
    sub_questions: List[str]
    all_candidates: List[Dict[str, Any]]
    reranked_evidence: List[Dict[str, Any]]
    context_text: str
    citations: List[Dict[str, Any]]

    # Sufficiency & Abstention
    is_sufficient: bool
    sufficiency_reason: str
    abstained: bool

    # Structured extractions & comparisons
    findings: List[Dict[str, Any]]
    comparison_matrix: Optional[Dict[str, Any]]

    # Outputs
    answer: str
    verification: Optional[Dict[str, Any]]
    confidence: str
    status: str

