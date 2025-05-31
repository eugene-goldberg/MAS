#!/usr/bin/env python3
"""Clean up test RAG corpus."""

import os
from dotenv import load_dotenv
import vertexai
from vertexai.preview import rag

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

if not project_id or not location:
    print(f"Error: Missing required environment variables")
    exit(1)

vertexai.init(project=project_id, location=location)

try:
    print("Looking for test corpus...")
    corpora = rag.list_corpora()
    
    for corpus in corpora:
        if corpus.display_name == "test-rag-integration":
            print(f"Found test corpus: {corpus.name}")
            print("Deleting test corpus...")
            rag.delete_corpus(name=corpus.name)
            print("✓ Test corpus deleted successfully")
            break
    else:
        print("Test corpus not found.")
        
except Exception as e:
    print(f"Error: {e}")