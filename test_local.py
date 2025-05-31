#!/usr/bin/env python3
"""Local test script for the Multi-Agent System."""

import asyncio
import dotenv
from mas_system.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables
dotenv.load_dotenv()


async def test_mas():
    """Test the multi-agent system with various queries."""
    runner = InMemoryRunner(agent=root_agent)
    
    # Create a session
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    
    # Test queries
    test_queries = [
        "What's the weather in San Francisco?",
        "Calculate 15% tip on $85.50",
        "Convert 20 degrees Celsius to Fahrenheit",
        "Give me a 3-day forecast for Tokyo",
        "What's 145 divided by 5?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        content = types.UserContent(parts=[types.Part(text=query)])
        
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                print(event.content.parts[0].text, end="")
        
        print("\n")


if __name__ == "__main__":
    print("Testing Multi-Agent System locally...")
    asyncio.run(test_mas())