from typing import List, Dict, Any
from app.utils.vector_store import search

def retrieve(ticket_text: str, k: int = 3) -> List[Dict[str, Any]]:
    """
    Workflow:
    User ticket -> Generate embedding -> Search FAISS -> Return top K relevant chunks

    Args:
        ticket_text: String content of the user ticket (e.g. subject and/or body).
        k: Number of relevant chunks to retrieve (default is 3).

    Returns:
        List of matching document chunks, including:
        [
            {
                "doc_name": "filename.md",
                "text": "matching chunk text...",
                "score": 0.123  # L2 distance score
            }
        ]
    """
    # Exposes the search functionality which vectorizes the ticket text
    # using the singleton model and queries the active FAISS index.
    return search(ticket_text, k=k)
