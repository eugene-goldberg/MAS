#!/usr/bin/env python3
"""Test the weather agent directly within the MAS deployment."""

import os
import dotenv
from vertexai import agent_engines

# Load environment variables
dotenv.load_dotenv()

# MAS coordinator agent ID (which contains the weather agent)
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/2883614379377426432"

def test_weather_agent_direct():
    """Test weather agent directly."""
    
    print("Testing Weather Agent within MAS deployment...")
    print("=" * 60)
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_weather_direct")
    print(f"Session ID: {session['id']}")
    print()
    
    # Weather-specific queries
    test_queries = [
        "What's the current weather in New York?",
        "Will it rain tomorrow in London?",
        "What's the temperature in Tokyo right now?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 40)
        
        response_text = ""
        try:
            for event in agent_engine.stream_query(
                user_id="test_weather_direct",
                session_id=session["id"],
                message=query
            ):
                if "content" in event and "parts" in event["content"]:
                    for part in event["content"]["parts"]:
                        if "text" in part:
                            response_text += part["text"]
                            print(part["text"], end="", flush=True)
                
                # Check author field
                if "author" in event and event["author"]:
                    print(f"\n[Response from: {event['author']}]", end="")
                    
        except Exception as e:
            print(f"\nError: {e}")
        
        print("\n")
        
        # Analyze response
        if response_text:
            print(f"✅ Response received ({len(response_text)} chars)")
            if any(word in response_text.lower() for word in ["weather", "temperature", "rain", "forecast", "degrees"]):
                print("✅ Response contains weather information")
            else:
                print("❓ Response doesn't appear to contain weather data")
        else:
            print("⚠️  Empty response")
        
        print("=" * 60)
        
        # Wait between queries to avoid rate limit
        if i < len(test_queries):
            import time
            print("Waiting 15 seconds to avoid rate limits...")
            time.sleep(15)
            print()

if __name__ == "__main__":
    test_weather_agent_direct()