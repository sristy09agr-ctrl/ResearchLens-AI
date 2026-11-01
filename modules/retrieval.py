
import re
import numpy as np
from rank_bm25 import BM25Okapi

from modules.embeddings import EmbeddingGenerator


class HybridRetriever:
    def __init__(self, paragraphs):
        """
        Initialize BM25 and dense semantic indexes.

        Accepts either:
        1. A list of plain text strings.
        2. A list of database chunk dictionaries containing
           text and citation metadata.
        """

        self.chunks = []
        self.paragraphs = []

        # Keep only chunks containing usable text.
        for item in paragraphs:
            if isinstance(item, dict):
                text = item.get("text") or item.get("paragraph") or ""

                if not isinstance(text, str) or not text.strip():
                    continue

                chunk = item.copy()
                chunk["text"] = text.strip()

            elif isinstance(item, str):
                if not item.strip():
                    continue

                chunk = {"text": item.strip()}

            else:
                continue

            self.chunks.append(chunk)
            self.paragraphs.append(chunk["text"])

        self.bm25 = None
        self.embedding_model = None
        self.paragraph_embeddings = np.array([])

        # An empty corpus does not need an embedding model.
        if not self.paragraphs:
            return

        # Build the BM25 index.
        tokenized_corpus = [
            self._tokenize(paragraph)
            for paragraph in self.paragraphs
        ]

        # BM25 requires a token list for every document.
        tokenized_corpus = [
            tokens if tokens else ["__empty__"]
            for tokens in tokenized_corpus
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

        # Generate dense semantic embeddings.
        self.embedding_model = EmbeddingGenerator()

        self.paragraph_embeddings = np.asarray(
            self.embedding_model.generate_embeddings(
                self.paragraphs
            ),
            dtype=np.float32
        )

    @staticmethod
    def _tokenize(text):
        """
        Convert text into lowercase word tokens.
        Supports Unicode text and common technical terms.
        """
        return re.findall(r"[\w]+(?:[.-][\w]+)*", text.lower())

    @staticmethod
    def _normalize_scores(scores):
        """
        Min-max normalize scores to the range [0, 1].
        """
        scores = np.asarray(scores, dtype=np.float32)

        if scores.size == 0:
            return scores

        minimum = float(np.min(scores))
        maximum = float(np.max(scores))

        if maximum == minimum:
            return np.zeros_like(scores)

        return (scores - minimum) / (maximum - minimum)

    def retrieve(self, query, top_k=5, alpha=0.5):
        """
        Retrieve relevant chunks using hybrid search.

        alpha = 1.0 : BM25 only
        alpha = 0.0 : Semantic search only
        alpha = 0.5 : Equal weighting

        Each result retains its original document and citation metadata.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        if not isinstance(alpha, (int, float)) or not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1.")

        if not self.chunks:
            return []

        query = query.strip()
        tokenized_query = self._tokenize(query)

        # BM25 scores.
        if tokenized_query:
            bm25_scores = self.bm25.get_scores(tokenized_query)
        else:
            bm25_scores = np.zeros(len(self.chunks), dtype=np.float32)

        bm25_scores = self._normalize_scores(bm25_scores)

        # Dense semantic similarity.
        query_embedding = self.embedding_model.generate_embedding(query)

        # Embeddings are normalized, so their dot product gives cosine
        # similarity.
        semantic_scores = np.dot(
            self.paragraph_embeddings,
            query_embedding
        )

        # Convert cosine similarity from [-1, 1] to [0, 1].
        semantic_scores = (semantic_scores + 1.0) / 2.0

        # Combine lexical and semantic relevance.
        hybrid_scores = (
            alpha * bm25_scores
            + (1.0 - alpha) * semantic_scores
        )

        # Get the highest-scoring chunks.
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            chunk = self.chunks[index]

            result = {
                "paragraph": chunk["text"],
                "text": chunk["text"],
                "bm25_score": float(bm25_scores[index]),
                "semantic_score": float(semantic_scores[index]),
                "hybrid_score": float(hybrid_scores[index])
            }

            # Preserve citation and document metadata when available.
            metadata_fields = [
                "document_id",
                "filename",
                "chunk_id",
                "page_start",
                "page_end",
                "section",
                "word_start",
                "word_end"
            ]

            for field in metadata_fields:
                if field in chunk:
                    result[field] = chunk[field]

            results.append(result)

        return results
