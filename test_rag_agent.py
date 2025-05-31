#!/usr/bin/env python3
"""Test script for RAG agent functionality."""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import Session
from mas_system.sub_agents.rag_agent import rag_agent

# Load environment variables
load_dotenv()

async def test_rag_agent():
    """Test RAG agent functionality."""
    print("Starting RAG Agent Test...")
    print("=" * 60)
    
    # Initialize session
    session = Session(agent=rag_agent)
    
    # Test 1: List corpora (should be empty initially)
    print("\n1. Testing list corpora...")
    response = await session.send("list all my corpora")
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 2: Create a test corpus
    print("\n2. Testing create corpus...")
    response = await session.send("create a new corpus called 'test-corpus' with description 'Test corpus for RAG agent verification'")
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 3: List corpora again (should show the new corpus)
    print("\n3. Testing list corpora again...")
    response = await session.send("list my corpora")
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 4: Get corpus info
    print("\n4. Testing get corpus info...")
    response = await session.send("show me details about test-corpus")
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 5: Try to query empty corpus
    print("\n5. Testing query on empty corpus...")
    response = await session.send("search for 'machine learning' in test-corpus")
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 6: Add a sample document (we'll use a public Google Doc)
    print("\n6. Testing add document...")
    # Using a public Google Docs link as an example
    response = await session.send(
        "add this document to test-corpus: https://docs.google.com/document/d/1kULqEEBxIGMPCQtrmbwP_Mh4WoJfcKXFoZiIdAW8zWA/edit"
    )
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 7: Query the corpus with content
    print("\n7. Testing query after adding document...")
    response = await session.send("search for 'AI' in test-corpus")
    print(f"Response: {response}")
    print("-" * 40)
    
    # Test 8: Delete the test corpus
    print("\n8. Testing delete corpus...")
    response = await session.send("delete the corpus test-corpus with confirmation")
    print(f"Response: {response}")
    print("-" * 40)
    
    print("\n" + "=" * 60)
    print("RAG Agent Test Complete!")


if __name__ == "__main__":
    # Verify required environment variables
    required_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file or environment.")
        exit(1)
    
    # Run the test
    asyncio.run(test_rag_agent())