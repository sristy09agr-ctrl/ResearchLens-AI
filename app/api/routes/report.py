"""
Structured Research Report generation route.
Produces comprehensive multi-section comparative literature syntheses.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.requests import ReportRequest
from app.agents.graph import research_graph
from app.db.database import get_document
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Reports"])


@router.post("/v1/reports")
@router.post("/report")
def generate_literature_report(request: ReportRequest):
    """
    Generate an evidence-backed literature report covering summary, comparison table,
    consensus vs conflicts, research gaps, limitations, and citations.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Research query cannot be empty.")

    selected_ids = list(dict.fromkeys(request.document_ids))
    if not selected_ids:
        raise HTTPException(status_code=400, detail="At least one paper must be selected.")

    selected_docs = []
    for doc_id in selected_ids:
        doc = get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
        selected_docs.append({"document_id": doc_id, "filename": doc["filename"]})

    # Prepare agent run with larger top_k suitable for report generation
    initial_state = {
        "query": f"Comprehensive Literature Review & Comparative Analysis: {query}",
        "document_ids": selected_ids,
        "top_k": request.top_k,
        "candidate_k": request.candidate_k,
        "alpha": request.alpha,
        "conversation_id": None,
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
            "research_plan": final_state.get("sub_questions", [query]),
            "total_evidence_passages": len(final_state.get("citations", [])),
            "report": final_state.get("answer", "No report generated."),
            "comparison_matrix": final_state.get("comparison_matrix"),
            "citations": final_state.get("citations", []),
            "verification": final_state.get("verification"),
            "confidence": final_state.get("confidence", "high")
        }
    except Exception as err:
        logger.error("Report generation failed: %s", err, exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"Report generation encountered an error: {err}"
        )

