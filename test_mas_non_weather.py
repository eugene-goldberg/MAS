#!/usr/bin/env python3
"""Test MAS with a non-weather query."""

import os
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/1123832824982405120"

def test_non_weather():
    """Test with a non-weather query."""
    
    print("Testing MAS Coordinator with non-weather query...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_non_weather")
    print(f"Session ID: {session['id']}")
    print()
    
    query = "Can you help me with math calculations?"
    print(f"Query: {query}")
    print("-" * 40)
    
    response_text = ""
    try:
        for event in agent_engine.stream_query(
            user_id="test_non_weather",
            session_id=session["id"],
            message=query
        ):
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
        if "weather" in response_text.lower() and "only" in response_text.lower():
            print("✅ Correctly declined non-weather request")
        else:
            print("❓ Response unclear")
    else:
        print("⚠️  Empty response")
    
    print("=" * 60)

if __name__ == "__main__":
    test_non_weather()