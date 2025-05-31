#!/usr/bin/env python3
"""Test RAG agent using InMemoryRunner."""

import asyncio
import os
from dotenv import load_dotenv
import vertexai
from google.adk.runners import InMemoryRunner
from google.genai import types
from mas_system.agent import mas_coordinator

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
if project_id and location:
    vertexai.init(project=project_id, location=location)

async def test_rag_with_runner():
    """Test RAG agent through MAS coordinator using InMemoryRunner."""
    print("Testing RAG Agent with InMemoryRunner...")
    print("=" * 60)
    
    # Create runner with MAS coordinator
    runner = InMemoryRunner(agent=mas_coordinator)
    
    # Create session
    session = await runner.session_service.create_session(
        app_name=runner.app_name, 
        user_id="test_user"
    )
    print(f"Created session: {session.id}")
    
    # Test queries
    test_queries = [
        "Can you help me manage documents and create a knowledge base?",
        "List all my document collections or corpora",
        "Create a new corpus called test-rag-corpus for testing",
        "What corpora do I have?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        # Create user content
        content = types.UserContent(parts=[types.Part(text=query)])
        
        # Run query and collect response
        response_text = ""
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text
        
        print(f"Response: {response_text}")
    
    print("\n" + "=" * 60)
    print("RAG Agent Runner Test Complete!")


if __name__ == "__main__":
    # Verify required environment variables
    required_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file or environment.")
        exit(1)
    
    # Run the test
    asyncio.run(test_rag_with_runner())