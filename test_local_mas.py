#!/usr/bin/env python3
"""Test the MAS locally before deployment."""

from mas_system.agent import root_agent

def test_mas():
    """Test the MAS with various queries."""
    test_queries = [
        "What's 25 + 17?",
        "What's the weather in London?",
        "Calculate 15% tip on $85",
        "Is it going to rain tomorrow in Paris?",
    ]
    
    print("Testing MAS Coordinator Locally...")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            response = root_agent.run(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_mas()