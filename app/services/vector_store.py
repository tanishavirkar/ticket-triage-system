import os
import json
from typing import List, Tuple, Dict, Any, Optional
import faiss
import numpy as np
from app.config import settings
from app.services.embedder import EmbedderService

class VectorStoreService:
    """
    Service for building, loading, saving, and searching FAISS vector indices.
    """
    def __init__(self, index_path: str = settings.faiss_index_path, embedder: Optional[EmbedderService] = None):
        self.index_path = index_path
        self.embedder = embedder or EmbedderService()
        self.index: Optional[faiss.Index] = None
        # Maps index ID in FAISS to the corresponding source document metadata
        self.metadata_map: Dict[int, Any] = {}

    def build_index(self, texts: List[str], metadata: List[Dict[str, Any]]) -> None:
        """
        Builds a new FAISS index from a list of texts and links them to the metadata.
        """
        if not texts:
            raise ValueError("Cannot build index with empty text list")
        if len(texts) != len(metadata):
            raise ValueError("Mismatch between texts and metadata list lengths")

        embeddings = self.embedder.get_embeddings(texts)
        dimension = embeddings.shape[1]

        # Using IndexFlatL2 for standard L2 (Euclidean) distance search
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Build metadata mapping
        self.metadata_map = {i: meta for i, meta in enumerate(metadata)}

    def save_index(self, path: Optional[str] = None) -> None:
        """
        Persists the current FAISS index and its associated metadata to disk.
        """
        if self.index is None:
            raise ValueError("No FAISS index is currently active to save")

        target_path = path or self.index_path
        os.makedirs(target_path, exist_ok=True)

        index_file = os.path.join(target_path, "index.faiss")
        meta_file = os.path.join(target_path, "metadata.json")

        # Write FAISS index binary
        faiss.write_index(self.index, index_file)

        # Write metadata mapping (JSON key must be string, so cast integer key to string)
        serialized_meta = {str(k): v for k, v in self.metadata_map.items()}
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(serialized_meta, f, indent=2)

    def load_index(self, path: Optional[str] = None) -> None:
        """
        Loads a persisted FAISS index and its associated metadata from disk.
        """
        target_path = path or self.index_path
        index_file = os.path.join(target_path, "index.faiss")
        meta_file = os.path.join(target_path, "metadata.json")

        if not os.path.exists(index_file) or not os.path.exists(meta_file):
            raise FileNotFoundError(f"FAISS index files not found in: {target_path}")

        # Load index binary
        self.index = faiss.read_index(index_file)

        # Load metadata JSON
        with open(meta_file, "r", encoding="utf-8") as f:
            serialized_meta = json.load(f)
            # Reconstruct dictionary with integer keys
            self.metadata_map = {int(k): v for k, v in serialized_meta.items()}

    def search_similar(self, query: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the index for the top k items similar to the query.
        Returns a list of tuples containing (metadata, distance/score).
        """
        if self.index is None:
            # Attempt to auto-load index if file exists
            try:
                self.load_index()
            except Exception as e:
                raise ValueError(f"FAISS index is not initialized or loaded: {e}")

        # Generate query vector embedding and reshape for FAISS
        query_vector = self.embedder.get_embedding(query).reshape(1, -1)
        
        # Search index
        distances, indices = self.index.search(query_vector.astype('float32'), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # FAISS returns -1 if there are fewer indexed elements than k
            if idx == -1 or idx not in self.metadata_map:
                continue
            results.append((self.metadata_map[idx], float(dist)))

        return results
