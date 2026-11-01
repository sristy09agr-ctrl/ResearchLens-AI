"""
Synthesizer node: generates evidence-grounded scientific responses citing passage numbers.
"""

from typing import Dict, Any
from app.agents.state import AgentState
from app.llm.client import gemini_client
from app.core.logging import get_logger

logger = get_logger(__name__)


def synthesizer_node(state: AgentState) -> dict:
    """Synthesize evidence-grounded answer citing only verified passage numbers."""
    query = state["query"]
    context_text = state.get("context_text", "")
    sub_questions = state.get("sub_questions", [])
    comparison_matrix = state.get("comparison_matrix")

    if not context_text:
        return {
            "answer": "The selected research papers do not contain sufficient evidence to answer this inquiry.",
            "status": "abstain"
        }

    sub_q_str = "\n".join(f"- {sq}" for sq in sub_questions)

    comparison_info = ""
    if comparison_matrix:
        consensus = comparison_matrix.get("consensus_summary", "")
        conflicts = comparison_matrix.get("contradictions_summary", "")
        gaps = comparison_matrix.get("research_gaps", "")
        comparison_info = f"""
CROSS-PAPER COMPARISON INSIGHTS:
- Consensus: {consensus}
- Conflicts: {conflicts}
- Research Gaps: {gaps}
"""

    prompt = f"""
You are ResearchLens AI, an expert scientific research reasoning assistant.

Answer the research query using ONLY the numbered evidence passages below.

RESEARCH INQUIRY:
{query}

DECOMPOSED SUB-QUESTIONS:
{sub_q_str}
{comparison_info}
NUMBERED EVIDENCE PASSAGES:
{context_text}

STRICT GROUNDING RULES:
1. Every major factual claim, method name, metric, and finding MUST cite its source passage number using brackets like [1] or [2].
2. If multiple passages support a claim, cite all of them, e.g. [1, 3].
3. DO NOT use outside general knowledge to assert facts about these specific papers.
4. If the evidence presents conflicting results across papers, explicitly highlight the discrepancy under a 'Consensus vs. Conflict' section.
5. If certain aspects of the question are not covered in the evidence, explicitly state: "The provided papers do not establish...".
6. Never cite a passage number greater than the total number of passages provided.
7. Format your response cleanly in Markdown with clear section headings.
"""

    try:
        answer = gemini_client.generate_text(
            prompt=prompt,
            model=gemini_client.primary_model,
            temperature=0.1
        )
    except Exception as e:
        logger.error("Synthesis generation failed: %s", e)
        answer = "An error occurred while synthesizing the scientific evidence."

    return {
        "answer": answer,
        "status": "success"
    }

