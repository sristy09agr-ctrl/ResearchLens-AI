"""
Agentic Q&A route: executes the LangGraph research workflow.
Provides grounded answers, paragraph citations, claim verification, and abstention diagnostics.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.requests import AskRequest
from app.agents.graph import research_graph
from app.db.database import get_document
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Reasoning"])


@router.post("/v1/conversations/{conversation_id}/messages")
@router.post("/ask")
def ask_research_agent(
    request: AskRequest,
    conversation_id: Optional[str] = None
):
    """
    Execute the agentic research graph to answer scientific questions across selected papers.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    selected_ids = list(dict.fromkeys(request.document_ids))
    if not selected_ids:
        raise HTTPException(status_code=400, detail="At least one paper must be selected.")

    # Validate that selected papers exist
    selected_docs = []
    for doc_id in selected_ids:
        doc = get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
        selected_docs.append({"document_id": doc_id, "filename": doc["filename"]})

    # Prepare initial agent state
    initial_state = {
        "query": query,
        "document_ids": selected_ids,
        "top_k": request.top_k,
        "candidate_k": request.candidate_k,
        "alpha": request.alpha,
        "conversation_id": conversation_id or request.conversation_id,
        "iteration": 0,
        "sub_questions": [],
        "all_candidates": [],
        "reranked_evidence": [],
        "context_text": "",
        "citations": [],
        "is_sufficient": False,
        "sufficiency_reason": "",
        "abstained": False,
        "findings": [],
        "comparison_matrix": None,
        "answer": "",
        "verification": None,
        "confidence": "high",
        "status": "pending"
    }

    try:
        final_state = research_graph.invoke(initial_state)

        return {
            "status": "success",
            "query": query,
            "selected_documents": selected_docs,
            "total_evidence_passages": len(final_state.get("citations", [])),
            "answer": final_state.get("answer", "No answer generated."),
            "citations": final_state.get("citations", []),
            "research_plan": final_state.get("sub_questions", [query]),
            "verification": final_state.get("verification"),
            "comparison_matrix": final_state.get("comparison_matrix"),
            "confidence": final_state.get("confidence", "medium"),
            "abstained": final_state.get("abstained", False),
            "iterations_run": final_state.get("iteration", 1)
        }
    except Exception as err:
        logger.error("Agent execution failed on query '%s': %s", query, err, exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"The agentic research pipeline encountered an error: {err}"
        )

