from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbedderService:
    """
    Service for generating vector embeddings using sentence-transformers.
    """
    def __init__(self, model_name: str = settings.embedding_model_name):
        self.model_name = model_name
        # The model is initialized lazily to avoid loading heavy weights on startup/import
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for a single text input.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embedding vectors for a batch of text inputs.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)
