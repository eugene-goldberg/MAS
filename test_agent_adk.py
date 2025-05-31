#!/usr/bin/env python3
"""Test the calculator agent using ADK methods."""

import asyncio
from mas_system.sub_agents.calculator_agent import calculator_agent

async def test_calculator():
    """Test calculator using ADK methods."""
    
    print("Testing calculator agent with ADK methods...")
    print("=" * 60)
    
    # Test 1: Using run_async
    print("\nTest 1 - Using run_async:")
    try:
        full_response = ""
        async for chunk in calculator_agent.run_async("What is 15 + 27?"):
            if isinstance(chunk, str):
                full_response += chunk
            else:
                full_response += str(chunk)
        print(f"Result: {full_response}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        
    # Test 2: Try another calculation
    print("\nTest 2 - Multiplication:")
    try:
        full_response = ""
        async for chunk in calculator_agent.run_async("Calculate 25 times 4"):
            if isinstance(chunk, str):
                full_response += chunk
            else:
                full_response += str(chunk)
        print(f"Result: {full_response}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

# Run the async test
if __name__ == "__main__":
    asyncio.run(test_calculator())