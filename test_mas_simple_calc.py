#!/usr/bin/env python3
"""Test MAS with a very simple calculator query."""

import os
import json
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/6606543158840918016"

def test_simple():
    """Test with simple calc."""
    
    print("Testing MAS Calculator...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_simple_calc")
    print(f"Session ID: {session['id']}")
    print()
    
    query = "What is 10 plus 5?"
    print(f"Query: {query}")
    print("-" * 40)
    
    event_count = 0
    response_text = ""
    try:
        for event in agent_engine.stream_query(
            user_id="test_simple_calc",
            session_id=session["id"],
            message=query
        ):
            event_count += 1
            if event_count <= 5:  # Show first 5 events
                print(f"\nEvent {event_count}:")
                print(json.dumps(event, indent=2))
            
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        response_text += part["text"]
                        
    except Exception as e:
        print(f"\nError: {e}")
    
    print(f"\n\nTotal events: {event_count}")
    print(f"Response text: '{response_text}'")
    print("=" * 60)

if __name__ == "__main__":
    test_simple()