"""
Reformulate and Abstain nodes for agentic loop iterations.
"""

from app.agents.state import AgentState
from app.llm.client import gemini_client
from app.schemas.agent import ResearchPlan
from app.core.logging import get_logger

logger = get_logger(__name__)


def reformulate_node(state: AgentState) -> dict:
    """Reformulate research sub-questions when initial retrieval evidence was insufficient."""
    query = state["query"]
    sub_questions = state.get("sub_questions", [])
    reason = state.get("sufficiency_reason", "")
    iteration = state.get("iteration", 1)

    logger.info("Executing agentic loop reformulate (iteration %d). Reason: %s", iteration, reason)

    prompt = f"""
You are the query reformulation component of ResearchLens AI.
The initial retrieval for the scientific question did not retrieve sufficient evidence.

ORIGINAL QUERY:
{query}

PREVIOUS SUB-QUESTIONS:
{sub_questions}

DIAGNOSTIC FEEDBACK:
{reason}

Generate 2 to 3 alternative, broader, or synonym-expanded sub-questions targeting
methodology sections, benchmark tables, and discussion sections.
"""
    try:
        new_plan: ResearchPlan = gemini_client.generate_structured(
            prompt=prompt,
            schema=ResearchPlan,
            model=gemini_client.cheap_model
        )
        new_sub_questions = new_plan.sub_questions if new_plan.sub_questions else [query]
    except Exception:
        new_sub_questions = [query, f"{query} methodology", f"{query} empirical results"]

    return {
        "sub_questions": new_sub_questions,
        "iteration": iteration + 1
    }


def abstain_node(state: AgentState) -> dict:
    """Provide a transparent, evidence-grounded abstention statement."""
    query = state["query"]
    reason = state.get("sufficiency_reason", "No relevant passages were found in the uploaded papers.")

    abstention_message = (
        f"### ResearchLens AI: Evidence Abstention\n\n"
        f"The selected research papers do not contain sufficient evidence to answer this question responsibly.\n\n"
        f"**Reason for Abstention:**\n"
        f"{reason}\n\n"
        f"**What is missing:**\n"
        f"The uploaded papers do not report direct metrics, methodology details, or empirical data addressing `{query}`. "
        f"To avoid generating hallucinated or unverified scientific claims, ResearchLens AI has withheld an answer."
    )

    return {
        "answer": abstention_message,
        "confidence": "abstained",
        "abstained": True,
        "verification": {
            "overall_status": "unsupported",
            "confidence_score": 0.0,
            "claims": [],
            "warnings": ["System abstained due to lack of ground-truth evidence."]
        }
    }

