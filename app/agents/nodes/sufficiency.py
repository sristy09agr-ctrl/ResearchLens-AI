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
    avg_score = sum(r.get("rerank_score", 0.0) for r in reranked) / len(reranked)

    # In cross-encoders, logit scores above -1.0 or positive scores indicate relevance
    is_sufficient = (top_score >= threshold) or (avg_score > -0.5)

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

