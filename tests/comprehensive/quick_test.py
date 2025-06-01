#!/usr/bin/env python3
"""
Quick test to verify basic functionality of each agent.
Useful for rapid validation without running full comprehensive tests.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
# We'll test agents directly without InMemoryRunner
import vertexai

# Import agents
from mas_system.agent import mas_coordinator
from mas_system.sub_agents.weather_agent import weather_agent
from mas_system.sub_agents.rag_agent import rag_agent

# Load environment
load_dotenv()

def quick_test():
    """Run quick validation tests"""
    print("QUICK VALIDATION TEST")
    print("=" * 50)
    
    # Initialize Vertex AI
    project = os.environ.get('GOOGLE_CLOUD_PROJECT')
    location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
    vertexai.init(project=project, location=location)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Weather Agent Tools
    print("\n1. Testing Weather Agent Tools...")
    tests_total += 1
    try:
        from mas_system.sub_agents.weather_agent.tools import get_weather
        result = get_weather("London")
        if result['status'] == 'success':
            print("   ✅ Weather Agent Tools: Working")
            tests_passed += 1
        else:
            print("   ❌ Weather Agent Tools: Failed")
    except Exception as e:
        print(f"   ❌ Weather Agent Tools: Error - {str(e)}")
        
    # Test 2: RAG Agent Tools
    print("\n2. Testing RAG Agent Tools...")
    tests_total += 1
    try:
        from mas_system.sub_agents.rag_agent.tools import list_corpora
        from google.adk.tools import ToolContext
        result = list_corpora(ToolContext())
        if result['status'] == 'success':
            print("   ✅ RAG Agent Tools: Working")
            tests_passed += 1
        else:
            print("   ❌ RAG Agent Tools: Failed")
    except Exception as e:
        print(f"   ❌ RAG Agent Tools: Error - {str(e)}")
        
    # Test 3: Greeter Agent
    print("\n3. Testing Greeter Agent...")
    tests_total += 1
    try:
        # Greeter agent has no tools, so we just verify it exists
        from mas_system.sub_agents.greeter_agent import greeter_agent
        if greeter_agent and greeter_agent.name == "greeter_agent":
            print("   ✅ Greeter Agent: Working")
            tests_passed += 1
        else:
            print("   ❌ Greeter Agent: Failed")
    except Exception as e:
        print(f"   ❌ Greeter Agent: Error - {str(e)}")
        
    # Summary
    print("\n" + "=" * 50)
    print(f"SUMMARY: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("✅ All agents are functioning correctly!")
        return True
    else:
        print("⚠️  Some agents have issues. Run full test for details.")
        return False


if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)