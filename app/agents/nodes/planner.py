"""
Planner node: decomposes complex scientific queries into targeted sub-questions.
"""

from typing import List
from app.agents.state import AgentState
from app.schemas.agent import ResearchPlan
from app.llm.client import gemini_client
from app.core.logging import get_logger

logger = get_logger(__name__)


def planner_node(state: AgentState) -> dict:
    """Decompose research query into atomic sub-questions."""
    query = state["query"]
    iteration = state.get("iteration", 0)

    prompt = f"""
You are the scientific query planning component of ResearchLens AI.
Your objective is to decompose the following user research inquiry into 2 to 4 focused,
orthogonal sub-questions that interrogate methodology, experimental datasets, metrics, and empirical findings.

USER INQUIRY:
{query}

Generate a concise research plan.
"""
    try:
        plan: ResearchPlan = gemini_client.generate_structured(
            prompt=prompt,
            schema=ResearchPlan,
            model=gemini_client.cheap_model
        )
        sub_questions = plan.sub_questions if plan.sub_questions else [query]
    except Exception as e:
        logger.warning("Planner failed to generate structured plan (%s); falling back to original query.", e)
        sub_questions = [query]

    # Ensure original query context is preserved
    if query not in sub_questions and len(sub_questions) < 4:
        sub_questions.append(query)

    return {
        "sub_questions": sub_questions,
        "iteration": iteration + 1
    }

