#!/usr/bin/env python3
"""Test calculator agent locally."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mas_system.sub_agents.calculator_agent import calculator_agent

def test_local():
    """Test calculator agent locally."""
    
    print("Testing Calculator Agent Locally...")
    print("=" * 60)
    
    # Test simple addition
    query = "What is 10 plus 5?"
    print(f"Query: {query}")
    print("-" * 40)
    
    try:
        result = calculator_agent.run(query)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_local()