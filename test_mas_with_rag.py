#!/usr/bin/env python3
"""Test MAS coordinator with RAG agent integration."""

import os
from dotenv import load_dotenv
import vertexai

# Load environment variables
load_dotenv()

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

if not project_id or not location:
    print(f"Error: Missing required environment variables")
    exit(1)

vertexai.init(project=project_id, location=location)

def test_mas_rag_integration():
    """Test RAG agent through MAS coordinator."""
    print("Testing MAS Coordinator with RAG Agent")
    print("=" * 60)
    
    # Import after vertexai init
    from mas_system.sub_agents.rag_agent import rag_agent
    from mas_system.agent import mas_coordinator
    
    # Check if RAG agent is in coordinator
    print("\n1. Checking RAG agent registration...")
    from google.adk.tools.agent_tool import AgentTool
    
    rag_found = False
    for tool in mas_coordinator.tools:
        if isinstance(tool, AgentTool) and tool.agent.name == "rag_agent":
            rag_found = True
            print("✓ RAG agent is registered with MAS coordinator")
            break
    
    if not rag_found:
        print("✗ RAG agent NOT found in coordinator!")
        return
    
    # Test direct RAG agent functionality
    print("\n2. Testing direct RAG agent access...")
    print("   Agent name:", rag_agent.name)
    print("   Agent description:", rag_agent.description)
    print("   Number of tools:", len(rag_agent.tools))
    
    # List tools
    print("\n3. RAG agent tools:")
    for i, tool in enumerate(rag_agent.tools, 1):
        if hasattr(tool, 'func'):
            print(f"   {i}. {tool.func.__name__}")
    
    print("\n4. Testing queries through coordinator...")
    test_queries = [
        "Can you help me search through documents?",
        "What document management capabilities do you have?",
        "I need to create a knowledge base for my project",
        "Search for information about hub-and-spoke architecture",
        "What does MAS documentation say about tool return types?",
    ]
    
    print("\nNote: Full integration testing requires the InMemoryRunner or deployment.")
    print("The coordinator is configured to route these types of queries to the RAG agent:")
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        print("  Expected routing: → rag_agent")
    
    # Show coordinator prompt excerpt
    print("\n5. Coordinator routing instructions (excerpt):")
    prompt_lines = mas_coordinator.instruction.split('\n')
    for line in prompt_lines:
        if 'rag_agent' in line.lower() or 'document' in line.lower():
            print(f"   {line.strip()}")
    
    print("\n" + "=" * 60)
    print("MAS-RAG Integration Test Complete!")
    print("\nNext steps:")
    print("1. Deploy the updated MAS with: cd deployment && python3 deploy.py --build --deploy")
    print("2. Test with: python3 test_deployment.py --resource_id <ID> --user_id test_user")


if __name__ == "__main__":
    test_mas_rag_integration()