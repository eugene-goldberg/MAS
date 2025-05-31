#!/usr/bin/env python3
"""Direct test of RAG agent tools."""

import os
from dotenv import load_dotenv
import vertexai

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

if not project_id or not location:
    print(f"Error: Missing required environment variables")
    print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
    print(f"GOOGLE_CLOUD_LOCATION: {location}")
    exit(1)

vertexai.init(project=project_id, location=location)

def test_rag_tools_direct():
    """Test RAG tools directly."""
    print("Testing RAG Tools Directly...")
    print("=" * 60)
    
    # Import tools
    from mas_system.sub_agents.rag_agent.tools.list_corpora import list_corpora
    from mas_system.sub_agents.rag_agent.tools.create_corpus import create_corpus
    from mas_system.sub_agents.rag_agent.tools.get_corpus_info import get_corpus_info
    from mas_system.sub_agents.rag_agent.tools.delete_corpus import delete_corpus
    
    # Test 1: List corpora (no context needed)
    print("\n1. Testing list_corpora...")
    try:
        result = list_corpora()
        print(f"Result: {result}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Create corpus
    print("\n2. Testing create_corpus...")
    try:
        result = create_corpus(
            corpus_name="test-rag-integration",
            description="Test corpus for RAG integration"
        )
        print(f"Result: {result}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: List corpora again
    print("\n3. Testing list_corpora again...")
    try:
        result = list_corpora()
        print(f"Result: {result}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get corpus info
    print("\n4. Testing get_corpus_info...")
    try:
        result = get_corpus_info(corpus_name="test-rag-integration")
        print(f"Result: {result}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Delete corpus (cleanup)
    print("\n5. Testing delete_corpus...")
    try:
        result = delete_corpus(
            corpus_name="test-rag-integration",
            confirm=True
        )
        print(f"Result: {result}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("RAG Tools Direct Test Complete!")


if __name__ == "__main__":
    test_rag_tools_direct()