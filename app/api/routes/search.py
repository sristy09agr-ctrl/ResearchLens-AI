"""
Retrieval search endpoint for evaluation benchmarks, debugging, and direct search.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.requests import SearchRequest
from app.db.database import get_all_documents, get_document_chunks
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import get_reranker

router = APIRouter(tags=["Search"])


@router.post("/v1/search")
@router.post("/search")
def search_passages(request: SearchRequest):
    """
    Direct hybrid search + cross-encoder reranker endpoint (used by eval benchmark).
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    # 1. Gather chunks
    chunks = []
    if request.document_ids:
        for doc_id in request.document_ids:
            chunks.extend(get_document_chunks(doc_id))
    else:
        for doc in get_all_documents():
            chunks.extend(get_document_chunks(doc["document_id"]))

    if not chunks:
        return {
            "status": "success",
            "query": query,
            "total_candidates": 0,
            "results": []
        }

    # 2. Hybrid retrieval
    retriever = HybridRetriever(chunks)
    candidates = retriever.retrieve(
        query=query,
        top_k=max(request.candidate_k, request.top_k),
        alpha=request.alpha
    )

    if not candidates:
        return {
            "status": "success",
            "query": query,
            "total_candidates": 0,
            "results": []
        }

    # 3. Rerank
    reranker = get_reranker()
    reranked = reranker.rerank(
        query=query,
        results=candidates,
        top_k=request.top_k
    )

    return {
        "status": "success",
        "query": query,
        "total_candidates": len(candidates),
        "returned_results": len(reranked),
        "results": reranked
    }

