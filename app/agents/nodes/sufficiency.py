"""
Sufficiency node: checks whether retrieved evidence is strong enough to answer the inquiry.
Decides whether to proceed, reformulate queries (loop), or abstain.
"""

from app.agents.state import AgentState
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def sufficiency_node(state: AgentState) -> dict:
    """Evaluate whether top reranked passages meet evidence quality threshold."""
    reranked = state.get("reranked_evidence", [])
    iteration = state.get("iteration", 1)
    threshold = settings.sufficiency_threshold

    if not reranked:
        return {
            "is_sufficient": False,
            "sufficiency_reason": "No relevant evidence passages were found in the selected papers.",
            "abstained": (iteration >= settings.max_agent_iterations)
        }

    # Best rerank score across passages
    top_score = reranked[0].get("rerank_score", -99.0)

    # CrossEncoder MS-MARCO MiniLM outputs logits.
    # Empirical calibration:
    #   - Directly relevant passages: logits >= -2.0 to +10.0
    #   - General conceptual context: logits between -9.5 and -2.0
    #   - Completely unrelated queries (negative controls): logits < -10.5
    is_sufficient = (top_score >= threshold)

    if not is_sufficient:
        reason = (
            f"Top evidence relevance score ({top_score:.2f}) falls below required threshold ({threshold:.2f})."
        )
        logger.info("Sufficiency check failed at iteration %d: %s", iteration, reason)
        return {
            "is_sufficient": False,
            "sufficiency_reason": reason,
            "abstained": (iteration >= settings.max_agent_iterations)
        }

    return {
        "is_sufficient": True,
        "sufficiency_reason": "Evidence meets sufficiency threshold.",
        "abstained": False
    }


def sufficiency_router(state: AgentState) -> str:
    """Conditional edge router: returns next node name."""
    if state.get("is_sufficient", False):
        return "extractor"
    
    iteration = state.get("iteration", 1)
    if iteration < settings.max_agent_iterations:
        return "reformulate"
    else:
        return "abstain"

