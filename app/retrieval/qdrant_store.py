"""
Vector store integration for Qdrant with in-memory fallback.
Supports persistent dense indexing and document-level metadata filtering.
"""

from typing import List, Dict, Any, Optional
import numpy as np

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class VectorStore:
    """Manages dense embeddings with Qdrant and in-memory fallback."""

    def __init__(self):
        self.collection_name = settings.qdrant_collection
        self.client = None
        self.is_connected = False
        self._memory_vectors: Dict[str, np.ndarray] = {}  # doc_id -> np.ndarray
        self._memory_payloads: Dict[str, List[Dict[str, Any]]] = {}

        if QDRANT_AVAILABLE and settings.use_persistent_qdrant:
            try:
                self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=3.0)
                # Test connectivity
                self.client.get_collections()
                self._ensure_collection()
                self.is_connected = True
                logger.info("Connected successfully to Qdrant vector store at %s:%d", settings.qdrant_host, settings.qdrant_port)
            except Exception as e:
                logger.warning("Could not connect to Qdrant (%s). Operating in-memory vector fallback.", e)
                self.is_connected = False

    def _ensure_collection(self, vector_dim: int = 384):
        if not self.client:
            return
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_dim,
                    distance=qmodels.Distance.COSINE
                )
            )

    def upsert_chunks(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: np.ndarray
    ):
        """Index chunk vectors with metadata payload."""
        if len(chunks) == 0:
            return

        if self.is_connected and self.client:
            points = []
            for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                point_id = f"{document_id}_{chunk.get('chunk_id', idx)}"
                points.append(
                    qmodels.PointStruct(
                        id=idx + int(document_id[:8], 16) % 10000000,
                        vector=vector.tolist(),
                        payload={
                            "document_id": document_id,
                            "chunk_id": chunk.get("chunk_id"),
                            "text": chunk.get("text"),
                            "page_start": chunk.get("page_start"),
                            "page_end": chunk.get("page_end"),
                            "section": chunk.get("section"),
                            "filename": chunk.get("filename", "")
                        }
                    )
                )
            self.client.upsert(collection_name=self.collection_name, points=points)
        else:
            # In-memory storage fallback
            self._memory_vectors[document_id] = np.asarray(embeddings, dtype=np.float32)
            self._memory_payloads[document_id] = chunks

    def search(
        self,
        query_vector: np.ndarray,
        document_ids: Optional[List[str]] = None,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """Search similar vectors filtered by document_ids."""
        if self.is_connected and self.client:
            filter_conditions = None
            if document_ids:
                filter_conditions = qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchAny(any=document_ids)
                        )
                    ]
                )

            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                query_filter=filter_conditions,
                limit=top_k
            )

            results = []
            for hit in hits:
                payload = hit.payload or {}
                payload["score"] = float(hit.score)
                results.append(payload)
            return results
        else:
            # In-memory cosine similarity fallback
            target_ids = document_ids or list(self._memory_vectors.keys())
            all_chunks = []
            all_vectors = []

            for doc_id in target_ids:
                if doc_id in self._memory_vectors:
                    all_chunks.extend(self._memory_payloads[doc_id])
                    all_vectors.append(self._memory_vectors[doc_id])

            if not all_vectors:
                return []

            matrix = np.vstack(all_vectors)
            scores = np.dot(matrix, query_vector)
            top_indices = np.argsort(scores)[::-1][:top_k]

            results = []
            for idx in top_indices:
                chunk = dict(all_chunks[idx])
                chunk["score"] = float(scores[idx])
                results.append(chunk)
            return results


vector_store = VectorStore()

