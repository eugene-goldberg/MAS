#!/usr/bin/env python3
"""List RAG corpora."""

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
    print("Listing all RAG corpora...")
    corpora = rag.list_corpora()
    
    if not corpora:
        print("No corpora found.")
    else:
        print(f"Found {len(list(corpora))} corpus(es):")
        for corpus in corpora:
            print(f"  - {corpus.display_name} ({corpus.name})")
            
except Exception as e:
    print(f"Error: {e}")