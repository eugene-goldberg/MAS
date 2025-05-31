#!/usr/bin/env python3
"""Test MAS with a simple non-weather query."""

import os
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/312058992148873216"

def test_hello():
    """Test with a non-weather query."""
    
    print("Testing MAS Coordinator with non-weather query...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_hello")
    print(f"Session ID: {session['id']}")
    print()
    
    query = "Hello, can you help me?"
    print(f"Query: {query}")
    print("-" * 40)
    
    response_text = ""
    event_count = 0
    try:
        for event in agent_engine.stream_query(
            user_id="test_hello",
            session_id=session["id"],
            message=query
        ):
            event_count += 1
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        response_text += part["text"]
                        print(part["text"], end="", flush=True)
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n")
    
    # Analyze the response
    if response_text:
        print(f"✅ Response received (length: {len(response_text)} chars)")
        print(f"Events: {event_count}")
    else:
        print(f"⚠️  Empty response - received {event_count} events")
    
    print("=" * 60)

if __name__ == "__main__":
    test_hello()