import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any
from app.utils.embeddings import get_embedding_model
from app.config import settings

# Global variables to cache the active index and metadata map in memory
_active_index = None
_metadata_map = {}

# Default directory for index storage
INDEX_DIR = settings.faiss_index_path

def build_index(chunks: List[Dict[str, Any]]) -> None:
    """
    Builds a FAISS index from document chunks containing precomputed embeddings.

    Args:
        chunks: List of dictionaries, each containing:
            {
                "text": "chunk content",
                "embedding": [0.1, -0.2, ...],
                "doc_name": "filename.md"
            }
    """
    global _active_index, _metadata_map
    if not chunks:
        raise ValueError("Cannot build index from an empty list of chunks")

    # Extract embedding list of lists and convert to a float32 numpy array
    embeddings_list = [chunk["embedding"] for chunk in chunks]
    embeddings_np = np.array(embeddings_list, dtype=np.float32)

    dimension = embeddings_np.shape[1]

    # Create L2 Flat FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    # Cache index and metadata lookup mapping in memory
    _active_index = index
    _metadata_map = {
        i: {
            "text": chunk.get("text", ""),
            "doc_name": chunk.get("doc_name", "")
        }
        for i, chunk in enumerate(chunks)
    }

def save_index() -> None:
    """
    Persists the currently active FAISS index and its metadata map to disk.
    """
    global _active_index, _metadata_map
    if _active_index is None:
        raise ValueError("No active FAISS index is available to save. Call build_index first.")

    os.makedirs(INDEX_DIR, exist_ok=True)
    index_file = os.path.join(INDEX_DIR, "index.faiss")
    meta_file = os.path.join(INDEX_DIR, "metadata.json")

    # Save index binary
    faiss.write_index(_active_index, index_file)

    # Save metadata as JSON (JSON requires string keys, so we cast indices)
    serialized_meta = {str(k): v for k, v in _metadata_map.items()}
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(serialized_meta, f, indent=2)

def load_index() -> None:
    """
    Loads a saved FAISS index and its metadata map from disk into memory.
    """
    global _active_index, _metadata_map
    index_file = os.path.join(INDEX_DIR, "index.faiss")
    meta_file = os.path.join(INDEX_DIR, "metadata.json")

    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        raise FileNotFoundError(f"FAISS index or metadata files missing in: {INDEX_DIR}")

    # Load FAISS index binary
    _active_index = faiss.read_index(index_file)

    # Load metadata JSON and convert keys back to integers
    with open(meta_file, "r", encoding="utf-8") as f:
        serialized_meta = json.load(f)
        _metadata_map = {int(k): v for k, v in serialized_meta.items()}

def search(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Embeds the search query and searches the FAISS index for top K matches.

    Args:
        query: The search query string.
        k: The number of top matches to return (default is 3).

    Returns:
        A list of dictionaries with structure:
        [
            {
                "text": "matching chunk text...",
                "doc_name": "filename.md",
                "score": 0.123  # L2 distance score
            }
        ]
    """
    global _active_index, _metadata_map
    if _active_index is None:
        try:
            load_index()
        except Exception as e:
            raise ValueError(f"FAISS index is not active or loaded: {e}")

    # Embed query string using the singleton embedding model
    model = get_embedding_model()
    query_vector = model.encode(query, convert_to_numpy=True).reshape(1, -1)

    # Run search on index
    distances, indices = _active_index.search(query_vector.astype('float32'), k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        # index returns -1 if less than k items are indexed
        if idx == -1 or idx not in _metadata_map:
            continue
        meta = _metadata_map[idx]
        results.append({
            "text": meta["text"],
            "doc_name": meta["doc_name"],
            "score": float(dist)
        })

    return results
