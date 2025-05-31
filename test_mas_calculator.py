#!/usr/bin/env python3
"""Test MAS with calculator queries."""

import os
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/6606543158840918016"

def test_calculator():
    """Test calculator routing."""
    
    print("Testing MAS Coordinator with calculator queries...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_calculator")
    print(f"Session ID: {session['id']}")
    print()
    
    # Test 1: Basic arithmetic
    query1 = "What is 25 + 37?"
    print(f"Query 1: {query1}")
    print("-" * 40)
    
    response_text = ""
    for event in agent_engine.stream_query(
        user_id="test_calculator",
        session_id=session["id"],
        message=query1
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    response_text += part["text"]
                    print(part["text"], end="", flush=True)
    
    print("\n")
    
    # Test 2: More complex calculation
    query2 = "Calculate 20% of 150"
    print(f"\nQuery 2: {query2}")
    print("-" * 40)
    
    response_text2 = ""
    for event in agent_engine.stream_query(
        user_id="test_calculator",
        session_id=session["id"],
        message=query2
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    response_text2 += part["text"]
                    print(part["text"], end="", flush=True)
    
    print("\n")
    
    # Test 3: Advanced math
    query3 = "What is the square root of 144?"
    print(f"\nQuery 3: {query3}")
    print("-" * 40)
    
    response_text3 = ""
    for event in agent_engine.stream_query(
        user_id="test_calculator",
        session_id=session["id"],
        message=query3
    ):
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part:
                    response_text3 += part["text"]
                    print(part["text"], end="", flush=True)
    
    print("\n")
    print("=" * 60)
    
    # Check results
    if response_text and response_text2 and response_text3:
        print("✅ All calculator queries received responses")
        if "62" in response_text:
            print("✅ Basic arithmetic correct (25 + 37 = 62)")
        if "30" in response_text2:
            print("✅ Percentage calculation correct (20% of 150 = 30)")
        if "12" in response_text3:
            print("✅ Square root calculation correct (√144 = 12)")

if __name__ == "__main__":
    test_calculator()