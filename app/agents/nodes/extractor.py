"""
Extractor node: extracts structured scientific findings from evidence passages.
"""

from typing import List, Dict, Any
from app.agents.state import AgentState
from app.schemas.agent import ExtractionList
from app.llm.client import gemini_client
from app.core.logging import get_logger

logger = get_logger(__name__)


def extractor_node(state: AgentState) -> dict:
    """Extract structured empirical findings (method, dataset, metric, value, limitation) per paper."""
    query = state["query"]
    context_text = state.get("context_text", "")

    if not context_text:
        return {"findings": []}

    prompt = f"""
You are the scientific information extraction component of ResearchLens AI.
Analyze the following numbered evidence passages and extract a structured empirical record
for each research paper represented.

USER QUERY:
{query}

EVIDENCE PASSAGES:
{context_text}

INSTRUCTIONS:
For each distinct paper in the evidence, extract:
- document_id (from the passage header)
- paper_title
- methodology (key architecture or approach)
- dataset (evaluation benchmark)
- metric_name (e.g. Accuracy, F1, Latency, Perplexity)
- metric_value (exact reported number or 'N/A')
- baseline_comparison (what they compared against)
- limitations (noted weaknesses or bounds)
- source_passage_ids (the integer [n] passage IDs supporting this)

Be strictly faithful to the text. Do not invent any values.
"""
    try:
        extraction: ExtractionList = gemini_client.generate_structured(
            prompt=prompt,
            schema=ExtractionList,
            model=gemini_client.primary_model
        )
        findings = [f.model_dump() for f in extraction.findings]
    except Exception as e:
        logger.warning("Structured extraction failed (%s); continuing with empty findings.", e)
        findings = []

    return {"findings": findings}

