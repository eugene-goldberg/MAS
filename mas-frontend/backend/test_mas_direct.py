#!/usr/bin/env python3
"""Test MAS directly to debug authentication issues."""

import asyncio
import os
import sys
import dotenv
import vertexai

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Load environment variables
dotenv.load_dotenv()
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

print("Environment check:")
print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"GOOGLE_CLOUD_LOCATION: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS exists: {os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', ''))}")

# Initialize vertexai
project = os.getenv('GOOGLE_CLOUD_PROJECT')
location = os.getenv('GOOGLE_CLOUD_LOCATION')

if project and location:
    print(f"\nInitializing vertexai with project={project}, location={location}")
    vertexai.init(project=project, location=location)
else:
    print("\nERROR: Missing project or location")
    sys.exit(1)

async def test_mas():
    """Test the multi-agent system."""
    from mas_system.agent import root_agent
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    
    print("\nCreating InMemoryRunner...")
    runner = InMemoryRunner(agent=root_agent)
    
    print("Creating session...")
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    print(f"Session created: {session.id}")
    
    query = "Hello!"
    print(f"\nTesting query: {query}")
    
    content = types.UserContent(parts=[types.Part(text=query)])
    
    response_text = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            response_text += event.content.parts[0].text
            print(event.content.parts[0].text, end="")
    
    print(f"\n\nFull response: {response_text}")
    return response_text

if __name__ == "__main__":
    try:
        result = asyncio.run(test_mas())
        print(f"\nTest {'PASSED' if result else 'FAILED'}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()