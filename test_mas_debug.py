#!/usr/bin/env python3
"""Debug test to see full event data from MAS coordinator."""

import os
import json
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/312058992148873216"

def test_debug():
    """Test with debug output to see what's happening."""
    
    print("Testing MAS Coordinator with debug output...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_debug")
    print(f"Session ID: {session['id']}")
    print()
    
    query = "What's the weather in London?"
    print(f"Query: {query}")
    print("-" * 40)
    
    event_count = 0
    try:
        for event in agent_engine.stream_query(
            user_id="test_debug",
            session_id=session["id"],
            message=query
        ):
            event_count += 1
            print(f"\nEvent {event_count}:")
            print(json.dumps(event, indent=2))
            
            # Break after first few events to avoid spam
            if event_count >= 3:
                print("\n... (stopping after 3 events)")
                break
                
    except Exception as e:
        print(f"\nError: {e}")
    
    if event_count == 0:
        print("\n⚠️  No events received - coordinator may not be responding")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_debug()