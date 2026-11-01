"""
Hybrid Retrieval engine combining BM25 and dense embeddings with
Reciprocal Rank Fusion (RRF) and linear score combination.
"""

import re
from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi

from modules.embeddings import EmbeddingGenerator
from app.retrieval.qdrant_store import vector_store


class HybridRetriever:
    """Combines BM25 keyword matching with dense semantic embeddings."""

    def __init__(self, chunks: List[Dict[str, Any]]):
        self.chunks = [
            c for c in chunks
            if isinstance(c.get("text"), str) and c.get("text", "").strip()
        ]
        self.paragraphs = [c["text"].strip() for c in self.chunks]

        self.bm25: Optional[BM25Okapi] = None
        self.embedding_model = EmbeddingGenerator()
        self.dense_embeddings = np.array([])

        if self.paragraphs:
            tokenized = [self._tokenize(p) for p in self.paragraphs]
            tokenized = [toks if toks else ["__empty__"] for toks in tokenized]
            self.bm25 = BM25Okapi(tokenized)

            self.dense_embeddings = np.asarray(
                self.embedding_model.generate_embeddings(self.paragraphs),
                dtype=np.float32
            )

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[\w]+(?:[.-][\w]+)*", text.lower())

    @staticmethod
    def _normalize(scores: np.ndarray) -> np.ndarray:
        if scores.size == 0:
            return scores
        s_min, s_max = float(np.min(scores)), float(np.max(scores))
        if s_max == s_min:
            return np.zeros_like(scores)
        return (scores - s_min) / (s_max - s_min)

    def retrieve_rrf(
        self,
        query: str,
        top_k: int = 20,
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion:
        RRF_score(doc) = 1 / (k + rank_bm25) + 1 / (k + rank_dense)
        """
        if not self.chunks or not query.strip():
            return []

        # BM25 ranks
        query_tokens = self._tokenize(query)
        bm25_scores = np.array(self.bm25.get_scores(query_tokens)) if self.bm25 else np.zeros(len(self.chunks))
        bm25_order = np.argsort(bm25_scores)[::-1]
        bm25_ranks = {idx: rank for rank, idx in enumerate(bm25_order)}

        # Dense ranks
        query_vector = self.embedding_model.generate_embedding(query)
        dense_scores = np.dot(self.dense_embeddings, query_vector)
        dense_order = np.argsort(dense_scores)[::-1]
        dense_ranks = {idx: rank for rank, idx in enumerate(dense_order)}

        # Compute RRF
        rrf_scores = np.zeros(len(self.chunks), dtype=np.float32)
        for idx in range(len(self.chunks)):
            r_bm25 = bm25_ranks.get(idx, len(self.chunks))
            r_dense = dense_ranks.get(idx, len(self.chunks))
            rrf_scores[idx] = (1.0 / (rrf_k + r_bm25)) + (1.0 / (rrf_k + r_dense))

        top_indices = np.argsort(rrf_scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            item = dict(self.chunks[idx])
            item["score"] = float(rrf_scores[idx])
            item["bm25_score"] = float(bm25_scores[idx])
            item["dense_score"] = float(dense_scores[idx])
            results.append(item)

        return results

    def retrieve(
        self,
        query: str,
        top_k: int = 20,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Weighted linear combination of normalized BM25 and dense scores.
        """
        if not self.chunks or not query.strip():
            return []

        query_tokens = self._tokenize(query)
        bm25_scores = self._normalize(
            np.array(self.bm25.get_scores(query_tokens)) if self.bm25 else np.zeros(len(self.chunks))
        )

        query_vector = self.embedding_model.generate_embedding(query)
        dense_scores = self._normalize(np.dot(self.dense_embeddings, query_vector))

        hybrid_scores = (alpha * dense_scores) + ((1.0 - alpha) * bm25_scores)
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            item = dict(self.chunks[idx])
            item["score"] = float(hybrid_scores[idx])
            results.append(item)

        return results

