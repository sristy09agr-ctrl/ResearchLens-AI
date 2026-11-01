
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L6-v2"
    ):
        """
        Initialize the cross-encoder reranking model.
        """
        self.model = CrossEncoder(model_name)

    def rerank(self, query, results, top_k=5):
        """
        Rerank retrieved passages using query-passage relevance.

        Args:
            query: Research question.
            results: Candidate passages from HybridRetriever.
            top_k: Maximum number of results to return.

        Returns:
            Reranked passages with cross-encoder scores.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        if not results:
            return []

        # Prepare query-passage pairs.
        pairs = [
            (query, result.get("text") or result.get("paragraph", ""))
            for result in results
        ]

        # Calculate relevance scores.
        scores = self.model.predict(
            pairs,
            show_progress_bar=False
        )

        # Attach scores without changing original retrieval scores.
        reranked_results = []

        for result, score in zip(results, scores):
            if not (result.get("text") or result.get("paragraph", "")).strip():
                continue

            updated_result = result.copy()
            updated_result["rerank_score"] = float(score)

            reranked_results.append(updated_result)

        # Sort by cross-encoder relevance.
        reranked_results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        # Return the highest-ranked passages.
        return reranked_results[:top_k]
