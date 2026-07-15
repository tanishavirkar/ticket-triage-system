from typing import List, Dict, Any

def chunk_documents(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chunks a list of documents using a character-based sliding window.

    Requirements:
    - Chunk size = 500 characters
    - Overlap = 100 characters

    Returns:
        A list of dictionaries with structure:
        [
            {
                "text": "chunk text content...",
                "doc_name": "filename.md",
                "chunk_id": "filename.md#chunk-index",
                ...other metadata (e.g. "path") remains attached...
            }
        ]
    """
    chunk_size = 500
    overlap = 100
    step = chunk_size - overlap  # 400 characters step size

    all_chunks = []

    for doc in docs:
        content = doc.get("content", "")
        doc_name = doc.get("doc_name", "")
        
        # Extract and preserve all other metadata fields (e.g. 'path')
        metadata = {k: v for k, v in doc.items() if k not in ["content", "doc_name"]}

        if not content:
            continue

        start = 0
        chunk_idx = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end]

            chunk_data = {
                "text": chunk_text,
                "doc_name": doc_name,
                "chunk_id": f"{doc_name}#chunk-{chunk_idx}"
            }
            # Attach the rest of the metadata
            chunk_data.update(metadata)

            all_chunks.append(chunk_data)
            chunk_idx += 1

            if end == len(content):
                break

            start += step

    return all_chunks
