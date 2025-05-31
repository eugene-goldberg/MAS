#!/usr/bin/env python3
"""Test MAS with mixed queries to verify routing."""

import os
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/3429675834196099072"

def test_mixed():
    """Test mixed routing between weather and calculator."""
    
    print("Testing MAS Coordinator with mixed queries...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_mixed")
    print(f"Session ID: {session['id']}")
    print()
    
    # Test 1: Weather query
    query1 = "What's the weather in Paris?"
    print(f"Query 1 (Weather): {query1}")
    print("-" * 40)
    
    for event in agent_engine.stream_query(
        user_id="test_mixed",
        session_id=session["id"],
        message=query1
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    print(part["text"], end="", flush=True)
    
    print("\n")
    
    # Test 2: Calculator query
    query2 = "What is 100 divided by 4?"
    print(f"\nQuery 2 (Calculator): {query2}")
    print("-" * 40)
    
    for event in agent_engine.stream_query(
        user_id="test_mixed",
        session_id=session["id"],
        message=query2
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    print(part["text"], end="", flush=True)
    
    print("\n")
    
    # Test 3: Non-supported query
    query3 = "Tell me a joke"
    print(f"\nQuery 3 (Non-supported): {query3}")
    print("-" * 40)
    
    for event in agent_engine.stream_query(
        user_id="test_mixed",
        session_id=session["id"],
        message=query3
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    print(part["text"], end="", flush=True)
    
    print("\n")
    print("=" * 60)

if __name__ == "__main__":
    test_mixed()