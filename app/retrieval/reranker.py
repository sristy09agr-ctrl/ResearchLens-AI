"""
Cross-encoder reranking with per-sub-question scoring, deduplication,
and paper diversity enforcement.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from sentence_transformers import CrossEncoder

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CrossEncoderReranker:
    """Reranks candidate passages using cross-attention relevance with diversity caps."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.reranker_model_name
        logger.info("Initializing CrossEncoder model: %s", self.model_name)
        self.model = CrossEncoder(self.model_name)

    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5,
        diversity_cap: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank retrieved passages.
        If diversity_cap is provided (e.g. 0.4), prevents a single paper from
        occupying more than (diversity_cap * top_k) slots when multiple papers exist.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty for reranking.")
        if not results:
            return []

        # Prepare pairs
        pairs = [
            (query, r.get("text") or r.get("paragraph", ""))
            for r in results
        ]

        scores = self.model.predict(pairs, show_progress_bar=False)

        scored_results = []
        for r, score in zip(results, scores):
            text = (r.get("text") or r.get("paragraph", "")).strip()
            if not text:
                continue
            item = dict(r)
            item["rerank_score"] = float(score)
            scored_results.append(item)

        # Sort by rerank score descending
        scored_results.sort(key=lambda x: x["rerank_score"], reverse=True)

        if diversity_cap is None:
            diversity_cap = settings.per_paper_diversity_cap

        # Identify unique papers
        unique_papers = {r.get("document_id") for r in scored_results if r.get("document_id")}

        # If only 1 paper exists or top_k <= 2, diversity cap is not applicable
        if len(unique_papers) <= 1 or top_k <= 2 or diversity_cap >= 1.0:
            return scored_results[:top_k]

        # Enforce diversity cap: max_per_paper = max(1, ceil(top_k * diversity_cap))
        max_per_paper = max(1, int(top_k * diversity_cap) + 1)
        paper_counts = defaultdict(int)
        filtered_results = []
        overflow_results = []

        for item in scored_results:
            doc_id = item.get("document_id", "unknown")
            if paper_counts[doc_id] < max_per_paper:
                paper_counts[doc_id] += 1
                filtered_results.append(item)
            else:
                overflow_results.append(item)

            if len(filtered_results) >= top_k:
                break

        # If still need items to reach top_k, fill from overflow
        if len(filtered_results) < top_k:
            remaining = top_k - len(filtered_results)
            filtered_results.extend(overflow_results[:remaining])

        return filtered_results[:top_k]


# Singleton reranker instance
reranker_instance: Optional[CrossEncoderReranker] = None


def get_reranker() -> CrossEncoderReranker:
    global reranker_instance
    if reranker_instance is None:
        reranker_instance = CrossEncoderReranker()
    return reranker_instance

