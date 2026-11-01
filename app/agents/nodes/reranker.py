"""
Reranker node: scores passages with cross-encoder and builds numbered evidence contexts.
"""

from typing import List, Dict, Any, Tuple
from app.agents.state import AgentState
from app.retrieval.reranker import get_reranker
from app.core.security import wrap_evidence_boundary
from app.core.logging import get_logger

logger = get_logger(__name__)


def prepare_evidence_passages(results: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Format numbered evidence context and citation metadata."""
    context_parts = []
    citations = []

    for index, r in enumerate(results, start=1):
        citation = {
            "citation_number": index,
            "document_id": r.get("document_id", "unknown"),
            "filename": r.get("filename", "Unknown Paper"),
            "chunk_id": r.get("chunk_id"),
            "page_start": r.get("page_start"),
            "page_end": r.get("page_end"),
            "section": r.get("section") or "General",
            "text_snippet": (r.get("text") or "")[:200]
        }
        citations.append(citation)

        p_start = citation["page_start"]
        p_end = citation["page_end"]
        page_str = f"Page {p_start}" if p_start == p_end or not p_end else f"Pages {p_start}-{p_end}"

        passage_text = r.get("text") or r.get("paragraph") or ""
        bounded_text = wrap_evidence_boundary(passage_text, index)

        header = f"[{index}] Paper: {citation['filename']} | Location: {page_str} | Section: {citation['section']}"
        context_parts.append(f"{header}\n{bounded_text}")

    return "\n\n".join(context_parts), citations


def reranker_node(state: AgentState) -> dict:
    """Rerank candidates using cross-encoder and enforce paper diversity."""
    query = state["query"]
    candidates = state.get("all_candidates", [])
    top_k = state.get("top_k", 5)

    if not candidates:
        return {
            "reranked_evidence": [],
            "context_text": "",
            "citations": []
        }

    reranker = get_reranker()
    reranked = reranker.rerank(
        query=query,
        results=candidates,
        top_k=top_k
    )

    context_text, citations = prepare_evidence_passages(reranked)

    return {
        "reranked_evidence": reranked,
        "context_text": context_text,
        "citations": citations
    }

