
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np


class EmbeddingGenerator:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the semantic embedding model.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for a single text.
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple paragraphs.
        """
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,  
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings
