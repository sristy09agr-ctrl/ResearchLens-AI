"""
Comparator node: analyzes cross-paper findings, detects contradictions/consensus,
and constructs structured comparative markdown matrices.
"""

from typing import Dict, Any, List
from app.agents.state import AgentState
from app.schemas.agent import ComparisonMatrix
from app.llm.client import gemini_client
from app.core.logging import get_logger

logger = get_logger(__name__)


def comparator_node(state: AgentState) -> dict:
    """Compare extracted findings across papers to detect consensus, conflicts, and trade-offs."""
    findings = state.get("findings", [])
    context_text = state.get("context_text", "")
    query = state["query"]

    # Only run full comparative matrix if evidence or findings span multiple papers or comparisons requested
    unique_papers = {f.get("paper_title") for f in findings if f.get("paper_title")}

    prompt = f"""
You are the comparative scientific reasoning component of ResearchLens AI.
Analyze the following extracted findings and source passages to detect agreements and contradictions.

RESEARCH QUERY:
{query}

EXTRACTED FINDINGS:
{findings}

SOURCE EVIDENCE:
{context_text}

TASK:
1. Identify shared evaluation tasks, metrics, or research claims evaluated across papers.
2. For each shared topic, classify the relationship:
   - 'consensus' (papers agree or corroborate findings)
   - 'conflict' (papers report contradicting results or divergent conclusions under similar conditions)
   - 'insufficient_evidence' (divergent results due to different datasets, baselines, or incomplete data)
3. Cite the exact passage IDs supporting each assessment.
4. Summarize overarching consensus, contradictions, and open research gaps.
"""
    try:
        matrix: ComparisonMatrix = gemini_client.generate_structured(
            prompt=prompt,
            schema=ComparisonMatrix,
            model=gemini_client.primary_model
        )
        return {"comparison_matrix": matrix.model_dump()}
    except Exception as e:
        logger.warning("Comparison matrix generation failed (%s).", e)
        return {"comparison_matrix": None}

