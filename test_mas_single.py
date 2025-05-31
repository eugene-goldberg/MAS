#!/usr/bin/env python3
"""Test MAS with a single query to check routing."""

import os
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/1123832824982405120"

def test_single_query():
    """Test with a single weather query."""
    
    print("Testing MAS Coordinator with single query...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_single")
    print(f"Session ID: {session['id']}")
    print()
    
    query = "What's the weather in London?"
    print(f"Query: {query}")
    print("-" * 40)
    
    response_text = ""
    try:
        for event in agent_engine.stream_query(
            user_id="test_single",
            session_id=session["id"],
            message=query
        ):
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        response_text += part["text"]
                        print(part["text"], end="", flush=True)
            
            # Also check for author to see if routing happened
            if "author" in event:
                print(f"\n[Author: {event['author']}]", end="")
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n")
    
    # Analyze the response
    if response_text:
        print(f"✅ Response received (length: {len(response_text)} chars)")
        if "weather" in response_text.lower() or "temperature" in response_text.lower():
            print("✅ Response appears to be weather-related")
        else:
            print("❓ Response content unclear")
    else:
        print("⚠️  Empty response - coordinator may not be routing properly")
    
    print("=" * 60)

if __name__ == "__main__":
    test_single_query()