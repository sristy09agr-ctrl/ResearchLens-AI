"""
Retriever node: executes hybrid search across all planned sub-questions.
"""

from typing import List, Dict, Any
from app.agents.state import AgentState
from app.db.database import get_document_chunks, get_document
from app.retrieval.hybrid import HybridRetriever
from app.core.logging import get_logger

logger = get_logger(__name__)


def retriever_node(state: AgentState) -> dict:
    """Retrieve candidate passages for every sub-question."""
    document_ids = state["document_ids"]
    sub_questions = state.get("sub_questions", [state["query"]])
    candidate_k = state.get("candidate_k", 30)
    top_k = state.get("top_k", 5)
    alpha = state.get("alpha", 0.5)

    # 1. Fetch chunks from SQLite for selected documents
    selected_chunks = []
    for doc_id in document_ids:
        doc = get_document(doc_id)
        filename = doc["filename"] if doc else "Paper"
        chunks = get_document_chunks(doc_id)
        for c in chunks:
            c["document_id"] = doc_id
            c["filename"] = filename
            selected_chunks.append(c)

    if not selected_chunks:
        return {
            "all_candidates": [],
            "is_sufficient": False,
            "sufficiency_reason": "No text content found in selected documents."
        }

    # 2. Build HybridRetriever
    retriever = HybridRetriever(selected_chunks)

    # 3. Retrieve per sub-question and deduplicate
    all_candidates: List[Dict[str, Any]] = []
    seen = set()

    for sub_q in sub_questions:
        candidates = retriever.retrieve(
            query=sub_q,
            top_k=max(candidate_k, top_k * 2),
            alpha=alpha
        )

        for cand in candidates:
            chunk_id = cand.get("chunk_id")
            key = (cand.get("document_id"), chunk_id if chunk_id is not None else cand.get("text", "")[:50])
            if key not in seen:
                seen.add(key)
                all_candidates.append(cand)

    logger.info("Retrieved %d unique candidate passages across %d sub-questions.", len(all_candidates), len(sub_questions))

    return {
        "all_candidates": all_candidates
    }

