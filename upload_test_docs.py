#!/usr/bin/env python3
"""Upload test documents to RAG corpus."""

import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview import rag
import glob

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

if not project_id or not location:
    print(f"Error: Missing required environment variables")
    exit(1)

vertexai.init(project=project_id, location=location)

def upload_documents():
    """Upload test documents to the test corpus."""
    
    # Find the test corpus
    corpus_name = None
    try:
        corpora = rag.list_corpora()
        for corpus in corpora:
            if corpus.display_name == "test-rag-integration":
                corpus_name = corpus.name
                print(f"Found corpus: {corpus_name}")
                break
    except Exception as e:
        print(f"Error listing corpora: {e}")
        return
    
    if not corpus_name:
        print("Test corpus 'test-rag-integration' not found!")
        return
    
    # Get all markdown files from test_documents
    doc_dir = os.path.join(os.path.dirname(__file__), "test_documents")
    doc_files = glob.glob(os.path.join(doc_dir, "*.md"))
    
    if not doc_files:
        print(f"No markdown files found in {doc_dir}")
        return
    
    print(f"Found {len(doc_files)} documents to upload")
    
    # Upload each document
    uploaded = 0
    failed = 0
    
    for doc_path in doc_files:
        filename = os.path.basename(doc_path)
        print(f"\nUploading {filename}...")
        
        try:
            rag_file = rag.upload_file(
                corpus_name=corpus_name,
                path=doc_path,
                display_name=filename,
                description=f"Test document: {filename}"
            )
            print(f"✓ Successfully uploaded {filename}")
            uploaded += 1
        except Exception as e:
            print(f"✗ Failed to upload {filename}: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Upload Summary:")
    print(f"  Successful: {uploaded}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(doc_files)}")
    
    # List files in corpus
    print(f"\n{'='*60}")
    print("Files in corpus:")
    try:
        files = list(rag.list_files(corpus_name=corpus_name))
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file.display_name}")
    except Exception as e:
        print(f"Error listing files: {e}")


if __name__ == "__main__":
    upload_documents()