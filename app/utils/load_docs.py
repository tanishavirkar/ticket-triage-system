from pathlib import Path
from typing import List, Dict, Union

def load_markdown_documents(directory_path: Union[str, Path]) -> List[Dict[str, str]]:
    """
    Recursively reads every non-hidden Markdown (.md) file from the specified directory path.

    Args:
        directory_path: Path to the knowledge base directory.

    Returns:
        A list of dictionaries with structure:
        [
            {
                "doc_name": "filename.md",
                "content": "file text content...",
                "path": "absolute or relative path to file"
            }
        ]
    """
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Knowledge base directory not found at: {directory_path}")

    documents = []

    # Recursively find all files matching *.md
    for file_path in path.rglob("*.md"):
        # Ignore hidden files (starts with .) and files in hidden directories (starts with .)
        # file_path.parts splits path into components (e.g. ['onboarding', '.guide', 'file.md'])
        if any(part.startswith('.') for part in file_path.parts):
            continue

        if file_path.is_file():
            try:
                # Resolve file content with UTF-8 encoding
                content = file_path.read_text(encoding="utf-8")
                documents.append({
                    "doc_name": file_path.name,
                    "content": content,
                    "path": str(file_path)
                })
            except Exception as e:
                # Log error and continue reading remaining files
                print(f"Warning: Failed to read document '{file_path}': {e}")

    return documents
