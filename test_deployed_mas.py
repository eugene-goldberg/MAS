#!/usr/bin/env python3
"""Comprehensive test of deployed Multi-Agent System coordinator."""

import os
import asyncio
import dotenv
from datetime import datetime
from vertexai import agent_engines
from google.genai import types

# Load environment variables
dotenv.load_dotenv()

# Deployed agent ID
AGENT_ENGINE_ID = "projects/843958766652/locations/us-central1/reasoningEngines/3986996288083197952"


async def test_mas_coordinator():
    """Test the MAS coordinator with various queries and document responses."""
    
    # Get the deployed agent
    agent_engine = agent_engines.get(AGENT_ENGINE_ID)
    
    # Create a session
    session = agent_engine.create_session(user_id="test_coordinator")
    
    # Test queries covering different intents and edge cases
    test_queries = [
        # Clear weather queries
        "What's the weather in New York City?",
        "Give me a 5-day forecast for London",
        "Is it raining in Seattle right now?",
        "What's the temperature in Tokyo?",
        
        # Clear calculation queries
        "Calculate 15% tip on $85.50",
        "What's 256 divided by 8?",
        "Convert 100 degrees Fahrenheit to Celsius",
        "Calculate compound interest on $1000 at 5% for 3 years",
        
        # Edge cases and ambiguous queries
        "What's 20 degrees in Fahrenheit?",  # Could be weather or conversion
        "I need help with the temperature",  # Ambiguous
        "Calculate the weather",  # Mixed intent
        "What's the square root of 144?",
        "How many miles is 10 kilometers?",
        
        # Complex queries
        "First tell me the weather in Paris, then calculate 20% of 150",
        "I want to know if I need an umbrella in Chicago",
        "Help me plan for tomorrow's weather in Miami",
        
        # Fun features
        "Give me my lucky number for today",
        "What's my BMI if I weigh 70kg and I'm 1.75m tall?",
        
        # Error cases
        "What's the weather in Xyzabcdefg123?",  # Invalid location
        "Calculate 10 divided by 0",  # Division by zero
        "Convert -300 Celsius to Fahrenheit",  # Edge case temperature
    ]
    
    print("=" * 80)
    print(f"MULTI-AGENT SYSTEM COORDINATOR TEST - {datetime.now()}")
    print(f"Agent ID: {AGENT_ENGINE_ID}")
    print(f"Session ID: {session['id']}")
    print("=" * 80)
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"QUERY: {query}")
        print("-" * 80)
        print("COORDINATOR RESPONSE:")
        print()
        
        full_response = ""
        
        # Stream the response
        for event in agent_engine.stream_query(
            user_id="test_coordinator",
            session_id=session["id"],
            message=query
        ):
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        text = part["text"]
                        print(text, end="", flush=True)
                        full_response += text
        
        print()
        print()
        print("ANALYSIS:")
        
        # Analyze the response
        response_lower = full_response.lower()
        
        # Check which agent was used
        if "weather agent" in response_lower or "routing to weather" in response_lower:
            print("✓ Routed to: WEATHER AGENT")
        elif "calculator agent" in response_lower or "routing to calculator" in response_lower:
            print("✓ Routed to: CALCULATOR AGENT")
        else:
            print("? Routing unclear from response")
        
        # Check for key indicators
        if any(word in response_lower for word in ["°f", "°c", "degrees", "temperature", "forecast", "rain", "sunny", "cloudy"]):
            print("✓ Contains weather information")
        
        if any(word in response_lower for word in ["result", "equals", "total", "sum", "product", "quotient"]):
            print("✓ Contains calculation result")
        
        if "error" in response_lower or "cannot" in response_lower or "unable" in response_lower:
            print("⚠ Contains error handling")
        
        # Wait a bit between queries to avoid rate limiting
        await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print("Testing deployed Multi-Agent System Coordinator...")
    asyncio.run(test_mas_coordinator())