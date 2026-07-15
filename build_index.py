import os
import json
import argparse
from app.config import settings
from app.utils import load_markdown_documents, chunk_documents
from app.services import EmbedderService, VectorStoreService

def main():
    parser = argparse.ArgumentParser(description="Build and save the FAISS vector indices for both the KB and tickets.")
    parser.add_argument(
        "--kb-dir", 
        type=str, 
        default=settings.kb_directory_path, 
        help="Directory path to the knowledge base markdown files."
    )
    parser.add_argument(
        "--kb-index-path", 
        type=str, 
        default=settings.faiss_index_path, 
        help="Path where the KB FAISS index and metadata should be saved."
    )
    parser.add_argument(
        "--tickets-file",
        type=str,
        default=settings.tickets_file_path,
        help="Path to the tickets.json dataset file."
    )
    parser.add_argument(
        "--tickets-index-path",
        type=str,
        default=settings.tickets_index_path,
        help="Path where the historical tickets FAISS index should be saved."
    )
    args = parser.parse_args()

    # Initialize Embedder (used for both indexes)
    print("Initializing embedding service (sentence-transformers)...")
    embedder = EmbedderService()

    # === SECTION 1: INDEX THE KNOWLEDGE BASE ===
    print(f"\n--- Building Knowledge Base Index ---")
    print(f"Loading markdown documents from: {args.kb_dir}")
    if not os.path.exists(args.kb_dir):
        print(f"Error: Knowledge base directory '{args.kb_dir}' does not exist.")
        return

    docs = load_markdown_documents(args.kb_dir)
    print(f"Loaded {len(docs)} documents.")

    print("Splitting documents into sliding window chunks...")
    chunks = chunk_documents(docs)
    print(f"Generated {len(chunks)} total text chunks.")

    if chunks:
        texts = [c["text"] for c in chunks]
        metadata = chunks

        print("Encoding chunks and constructing FAISS index...")
        kb_store = VectorStoreService(index_path=args.kb_index_path, embedder=embedder)
        kb_store.build_index(texts, metadata)

        print(f"Saving KB index and metadata files to: {args.kb_index_path}")
        kb_store.save_index()
    else:
        print("Warning: No documentation content was found to index.")

    # === SECTION 2: INDEX HISTORICAL TICKETS ===
    print(f"\n--- Building Historical Tickets Index ---")
    print(f"Loading tickets from: {args.tickets_file}")
    if not os.path.exists(args.tickets_file):
        print(f"Error: Tickets file '{args.tickets_file}' does not exist.")
        return

    with open(args.tickets_file, "r", encoding="utf-8") as f:
        tickets = json.load(f)
    print(f"Loaded {len(tickets)} historical tickets.")

    ticket_texts = []
    ticket_metadata = []

    for ticket in tickets:
        # Create a text representation combining subject and body for vector similarity search
        text_to_embed = f"Subject: {ticket.get('subject', '')}\n\nBody: {ticket.get('body', '')}"
        ticket_texts.append(text_to_embed)
        ticket_metadata.append(ticket)

    if ticket_texts:
        print("Encoding tickets and constructing FAISS index...")
        ticket_store = VectorStoreService(index_path=args.tickets_index_path, embedder=embedder)
        ticket_store.build_index(ticket_texts, ticket_metadata)

        print(f"Saving tickets index and metadata files to: {args.tickets_index_path}")
        ticket_store.save_index()
    else:
        print("Warning: No tickets were found to index.")

    print("\nAll indices successfully built and saved!")

if __name__ == "__main__":
    main()
