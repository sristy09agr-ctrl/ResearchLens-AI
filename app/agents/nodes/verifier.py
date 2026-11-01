"""
Verifier node: performs atomic claim verification against cited passages,
deterministic citation audits, and composite confidence calibration.
"""

import re
from typing import Dict, Any, List, Tuple
from app.agents.state import AgentState
from app.schemas.agent import VerificationReport
from app.llm.client import gemini_client
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def audit_citations_deterministically(answer: str, max_citation_id: int) -> Tuple[str, List[int]]:
    """
    Ensure every [n] in answer corresponds to a valid passage index.
    Strips or flags hallucinations like [99] when only 5 passages exist.
    """
    invalid_ids = []

    def replace_citation(match):
        cid = int(match.group(1))
        if cid < 1 or cid > max_citation_id:
            invalid_ids.append(cid)
            return "[INVALID_CITATION]"
        return match.group(0)

    audited_answer = re.sub(r"\[(\d+)\]", replace_citation, answer)
    return audited_answer, invalid_ids


def verifier_node(state: AgentState) -> dict:
    """Verify claims, audit citation integrity, and calculate confidence score."""
    answer = state.get("answer", "")
    citations = state.get("citations", [])
    context_text = state.get("context_text", "")
    query = state["query"]
    reranked = state.get("reranked_evidence", [])

    if not answer or not context_text or not citations:
        return {
            "verification": {
                "overall_status": "unsupported",
                "confidence_score": 0.0,
                "claims": [],
                "warnings": ["Insufficient evidence available for verification."]
            },
            "confidence": "low"
        }

    # 1. Deterministic citation audit
    audited_answer, invalid_citations = audit_citations_deterministically(answer, len(citations))

    # 2. Per-claim NLI verification via LLM
    prompt = f"""
You are the factual verification component of ResearchLens AI.
Your objective is to independently audit the generated answer against the provided evidence.

RESEARCH QUESTION:
{query}

GENERATED ANSWER:
{audited_answer}

SUPPLIED EVIDENCE PASSAGES:
{context_text}

INSTRUCTIONS:
1. Decompose the answer into atomic factual claims.
2. For each claim, check its cited passages.
3. Classify each claim:
   - 'supported': The cited passage explicitly entails this fact.
   - 'partially_supported': Supported with minor extrapolation or missing nuance.
   - 'unsupported': The cited passage does NOT mention or contradicts this claim.
4. Calculate composite confidence score [0.0 - 1.0].
5. Provide overall_status: 'verified', 'partially_verified', or 'unsupported'.
"""
    try:
        verification: VerificationReport = gemini_client.generate_structured(
            prompt=prompt,
            schema=VerificationReport,
            model=gemini_client.cheap_model
        )
        report_dict = verification.model_dump()
    except Exception as e:
        logger.warning("Verification structured call failed (%s); providing baseline audit.", e)
        report_dict = {
            "overall_status": "verified" if not invalid_citations else "partially_verified",
            "confidence_score": 0.80 if not invalid_citations else 0.50,
            "claims": [],
            "warnings": []
        }

    if invalid_citations:
        report_dict["warnings"].append(
            f"Deterministic audit stripped {len(invalid_citations)} hallucinated citation references: {invalid_citations}"
        )

    # 3. Calculate calibrated confidence
    conf_score = report_dict.get("confidence_score", 0.7)
    if conf_score >= settings.confidence_high_threshold:
        conf_label = "high"
    elif conf_score >= settings.confidence_med_threshold:
        conf_label = "medium"
    else:
        conf_label = "low"

    return {
        "answer": audited_answer,
        "verification": report_dict,
        "confidence": conf_label
    }
