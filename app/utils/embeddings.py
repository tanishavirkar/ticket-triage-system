from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# Module-level variable to cache the model instance so it only initializes once
_model_instance = None

def get_embedding_model() -> SentenceTransformer:
    """
    Retrieves the cached sentence-transformers model, initializing it if necessary.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SentenceTransformer("all-MiniLM-L6-v2")
    return _model_instance

def embed_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates sentence-transformer embeddings for a list of document chunks.

    Args:
        chunks: List of chunk dictionaries containing 'text' and 'doc_name'.

    Returns:
        List of dictionaries structured as:
        [
            {
                "text": "chunk text content...",
                "embedding": [0.12, -0.45, ...],  # list of floats
                "doc_name": "filename.md",
                ...other metadata remains attached...
            }
        ]
    """
    if not chunks:
        return []

    model = get_embedding_model()
    
    # Extract text strings for batch embedding generation
    texts = [chunk["text"] for chunk in chunks]
    
    # Generate embeddings and convert to numpy array
    embeddings_array = model.encode(texts, convert_to_numpy=True)
    
    embedded_chunks = []
    for chunk, embedding in zip(chunks, embeddings_array):
        # Convert numpy array vector to a standard Python list of floats
        embedding_list = [float(val) for val in embedding]

        embedded_chunk = {
            "text": chunk.get("text", ""),
            "embedding": embedding_list,
            "doc_name": chunk.get("doc_name", "")
        }

        # Keep other metadata keys (e.g. 'chunk_id', 'path') attached
        for key, val in chunk.items():
            if key not in ["text", "doc_name"]:
                embedded_chunk[key] = val

        embedded_chunks.append(embedded_chunk)

    return embedded_chunks
