#!/usr/bin/env python3
"""Simple test of deployed MAS coordinator with delays to avoid rate limits."""

import os
import time
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/2883614379377426432"

def test_mas_simple():
    """Test the MAS coordinator with a few key queries."""
    
    print("Testing deployed Multi-Agent System Coordinator...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_simple")
    print(f"Session ID: {session['id']}")
    print()
    
    # Test with weather queries and non-weather queries
    test_queries = [
        "What's the weather in London?",
        "Is it going to rain in Paris tomorrow?",
        "What's 25 + 17?",  # Non-weather query to test rejection
        "What's the temperature in Tokyo?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 40)
        
        response_text = ""
        try:
            for event in agent_engine.stream_query(
                user_id="test_simple",
                session_id=session["id"],
                message=query
            ):
                if "content" in event and "parts" in event["content"]:
                    for part in event["content"]["parts"]:
                        if "text" in part:
                            response_text += part["text"]
                            print(part["text"], end="", flush=True)
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n")
        
        # Analyze the response
        if response_text:
            print(f"Response received (length: {len(response_text)} chars)")
        else:
            print("⚠️  Empty response - coordinator may not be routing properly")
        
        print("=" * 60)
        
        # Add delay to avoid rate limits (except after last query)
        if i < len(test_queries):
            print("Waiting 10 seconds to avoid rate limits...")
            time.sleep(10)
            print()

if __name__ == "__main__":
    test_mas_simple()