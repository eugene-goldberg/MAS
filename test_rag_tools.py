#!/usr/bin/env python3
"""Direct test of RAG agent tools."""

import os
from dotenv import load_dotenv
from google.adk.tools.tool_context import ToolContext
from mas_system.sub_agents.rag_agent.tools.list_corpora import list_corpora
from mas_system.sub_agents.rag_agent.tools.create_corpus import create_corpus
from mas_system.sub_agents.rag_agent.tools.get_corpus_info import get_corpus_info
from mas_system.sub_agents.rag_agent.tools.add_data import add_data
from mas_system.sub_agents.rag_agent.tools.rag_query import rag_query
from mas_system.sub_agents.rag_agent.tools.delete_corpus import delete_corpus

# Load environment variables
load_dotenv()

def test_rag_tools():
    """Test RAG tools directly."""
    print("Starting RAG Tools Test...")
    print("=" * 60)
    
    # Create a tool context
    tool_context = ToolContext()
    
    # Test 1: List corpora
    print("\n1. Testing list_corpora...")
    result = list_corpora(tool_context=tool_context)
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test 2: Create corpus
    print("\n2. Testing create_corpus...")
    result = create_corpus(
        corpus_name="test-rag-corpus",
        description="Test corpus for RAG verification",
        tool_context=tool_context
    )
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test 3: Get corpus info
    print("\n3. Testing get_corpus_info...")
    result = get_corpus_info(
        corpus_name="test-rag-corpus",
        tool_context=tool_context
    )
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test 4: Query empty corpus
    print("\n4. Testing rag_query on empty corpus...")
    result = rag_query(
        corpus_name="test-rag-corpus",
        query="machine learning",
        tool_context=tool_context
    )
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test 5: Add data
    print("\n5. Testing add_data...")
    # Using a public Google Docs example
    result = add_data(
        corpus_name="test-rag-corpus",
        paths=["https://docs.google.com/document/d/1kULqEEBxIGMPCQtrmbwP_Mh4WoJfcKXFoZiIdAW8zWA/edit"],
        tool_context=tool_context
    )
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test 6: Query corpus with content (wait a moment for indexing)
    print("\n6. Waiting for document indexing...")
    import time
    time.sleep(10)
    
    print("Testing rag_query after adding document...")
    result = rag_query(
        corpus_name="test-rag-corpus",
        query="AI applications",
        tool_context=tool_context
    )
    print(f"Result: {result}")
    print("-" * 40)
    
    # Test 7: Delete corpus
    print("\n7. Testing delete_corpus...")
    result = delete_corpus(
        corpus_name="test-rag-corpus",
        confirm=True,
        tool_context=tool_context
    )
    print(f"Result: {result}")
    print("-" * 40)
    
    print("\n" + "=" * 60)
    print("RAG Tools Test Complete!")


if __name__ == "__main__":
    # Verify required environment variables
    required_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file or environment.")
        exit(1)
    
    # Run the test
    test_rag_tools()