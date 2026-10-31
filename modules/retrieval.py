
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
from modules.embeddings import EmbeddingGenerator


class HybridRetriever:
    def __init__(self, paragraphs):
        """
        Initialize the hybrid retrieval system.
        """
        self.paragraphs = paragraphs

        # Initialize BM25
        tokenized_corpus = [
            paragraph.lower().split()
            for paragraph in paragraphs
        ]

        self.bm25 = BM25Okapi(tokenized_corpus)

        # Generate semantic embeddings
        self.embedding_model = EmbeddingGenerator()

        self.paragraph_embeddings = (
            self.embedding_model.generate_embeddings(paragraphs)
        )

    def retrieve(self, query, top_k=5, alpha=0.5):
        """
        Retrieve relevant paragraphs using hybrid search.

        alpha controls the balance:
        alpha = 1.0: BM25 only
        alpha = 0.0: Semantic search only
        alpha = 0.5: Equal weighting
        """

        # BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Semantic similarity scores
        query_embedding = (
            self.embedding_model.generate_embedding(query)
        )

        semantic_scores = cosine_similarity(
            [query_embedding],
            self.paragraph_embeddings
        )[0]

        # Normalize BM25 scores
        if bm25_scores.max() > bm25_scores.min():
            bm25_scores = (
                (bm25_scores - bm25_scores.min()) /
                (bm25_scores.max() - bm25_scores.min())
            )
        else:
            bm25_scores = bm25_scores * 0

        # Hybrid scoring
        hybrid_scores = (
            alpha * bm25_scores +
            (1 - alpha) * semantic_scores
        )

        # Rank results
        top_indices = hybrid_scores.argsort()[::-1][:top_k]

        results = []

        for index in top_indices:
            results.append({
                "paragraph": self.paragraphs[index],
                "bm25_score": float(bm25_scores[index]),
                "semantic_score": float(semantic_scores[index]),
                "hybrid_score": float(hybrid_scores[index])
            })

        return results
