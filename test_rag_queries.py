#!/usr/bin/env python3
"""Test RAG queries on the uploaded documents."""

import os
from dotenv import load_dotenv
import vertexai
from mas_system.sub_agents.rag_agent.tools.rag_query import rag_query
import time

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

if not project_id or not location:
    print(f"Error: Missing required environment variables")
    exit(1)

vertexai.init(project=project_id, location=location)

def test_rag_queries():
    """Test various queries against the RAG corpus."""
    
    print("Testing RAG Queries on Uploaded Documents")
    print("=" * 60)
    
    # Test queries
    queries = [
        "What is the hub-and-spoke architecture in MAS?",
        "Why must tools return dictionaries in MAS?", 
        "How do I handle errors in Google ADK?",
        "What's the difference between Agent and LlmAgent?",
        "How many sub-agents should I have in MAS?",
        "Tell me about tool development best practices"
    ]
    
    corpus_name = "test-rag-integration"
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print(f"{'='*60}")
        
        try:
            result = rag_query(
                corpus_name=corpus_name,
                query=query,
                tool_context=None
            )
            
            print(f"Status: {result['status']}")
            print(f"Message: {result['message'][:500]}...")  # Truncate long messages
            
            if result['status'] == 'success' and result['data']['results']:
                print(f"\nFound {result['data']['results_count']} results")
                print("Top result details:")
                top_result = result['data']['results'][0]
                print(f"  Source: {top_result.get('source_name', 'Unknown')}")
                print(f"  Score: {top_result.get('score', 0):.3f}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Small delay between queries
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("RAG Query Testing Complete!")


if __name__ == "__main__":
    # Wait a moment for indexing to complete
    print("Waiting 10 seconds for document indexing...")
    time.sleep(10)
    
    test_rag_queries()