#!/usr/bin/env python3
"""Simple test to verify RAG agent imports and basic functionality."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        from mas_system.sub_agents.rag_agent import rag_agent
        print("✓ RAG agent imported successfully")
        
        from mas_system.agent import mas_coordinator
        print("✓ MAS coordinator imported successfully")
        
        # Check if RAG agent is in coordinator tools
        from google.adk.tools.agent_tool import AgentTool
        coordinator_tools = mas_coordinator.tools
        rag_tool_found = False
        
        for tool in coordinator_tools:
            if isinstance(tool, AgentTool) and tool.agent.name == "rag_agent":
                rag_tool_found = True
                break
        
        if rag_tool_found:
            print("✓ RAG agent found in coordinator tools")
        else:
            print("✗ RAG agent NOT found in coordinator tools")
            
        # Test individual tool imports
        from mas_system.sub_agents.rag_agent.tools.create_corpus import create_corpus
        from mas_system.sub_agents.rag_agent.tools.list_corpora import list_corpora
        from mas_system.sub_agents.rag_agent.tools.add_data import add_data
        from mas_system.sub_agents.rag_agent.tools.rag_query import rag_query
        from mas_system.sub_agents.rag_agent.tools.get_corpus_info import get_corpus_info
        from mas_system.sub_agents.rag_agent.tools.delete_document import delete_document
        from mas_system.sub_agents.rag_agent.tools.delete_corpus import delete_corpus
        print("✓ All RAG tools imported successfully")
        
        # Check tool signatures
        import inspect
        print("\nTool signatures:")
        for name, func in [
            ("create_corpus", create_corpus),
            ("list_corpora", list_corpora),
            ("add_data", add_data),
            ("rag_query", rag_query),
        ]:
            sig = inspect.signature(func)
            print(f"  {name}: {sig}")
            
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mas_session():
    """Test MAS coordinator with RAG agent."""
    print("\n\nTesting MAS coordinator session...")
    
    try:
        import asyncio
        from google.adk.sessions import Session
        from mas_system.agent import mas_coordinator
        
        async def run_test():
            # Initialize session with MAS coordinator
            session = Session(agent=mas_coordinator)
            
            # Test 1: Ask about document management
            print("\n1. Testing document management query...")
            response = await session.send("How can I manage documents and create a knowledge base?")
            print(f"Response: {response}")
            
            # Test 2: Try to list corpora
            print("\n2. Testing list corpora through coordinator...")
            response = await session.send("Can you list all my document collections or corpora?")
            print(f"Response: {response}")
            
            return True
            
        result = asyncio.run(run_test())
        if result:
            print("\n✅ MAS session test successful!")
        return result
        
    except Exception as e:
        print(f"\n❌ Session test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Verify required environment variables
    required_vars = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file or environment.")
        exit(1)
    
    print("=" * 60)
    print("RAG Agent Integration Test")
    print("=" * 60)
    
    # Run tests
    import_success = test_imports()
    
    if import_success:
        session_success = test_mas_session()
        
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    if import_success:
        print(f"  MAS Session: {'✅ PASS' if session_success else '❌ FAIL'}")
    print("=" * 60)