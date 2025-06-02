#!/usr/bin/env python3
"""
Direct test of MAS system to debug response issues
"""

import asyncio
import sys
import os
from pathlib import Path

# Add MAS to path
mas_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(mas_path))

# Initialize Vertex AI
import vertexai
vertexai.init(project="pickuptruckapp", location="us-central1")
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'

async def test_mas():
    try:
        # Import MAS
        from mas_system.agent import mas_coordinator
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        
        print("✅ Imported MAS system")
        
        # Create runner
        runner = InMemoryRunner(agent=mas_coordinator)
        session = await runner.session_service.create_session(
            app_name=runner.app_name, user_id="test_user"
        )
        
        print("✅ Created runner and session")
        
        # Test message
        test_message = "Hello"
        print(f"\n📤 Sending: '{test_message}'")
        
        content = types.UserContent(parts=[types.Part(text=test_message)])
        
        # Process message and inspect full response
        print("\n📥 Response events:")
        response_text = ""
        event_count = 0
        
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            event_count += 1
            print(f"\nEvent {event_count}:")
            print(f"  Type: {type(event)}")
            
            if hasattr(event, 'content') and event.content:
                print(f"  Content type: {type(event.content)}")
                
                if hasattr(event.content, 'parts') and event.content.parts:
                    print(f"  Parts count: {len(event.content.parts)}")
                    
                    for i, part in enumerate(event.content.parts):
                        print(f"  Part {i}:")
                        print(f"    Type: {type(part)}")
                        
                        # Check different part types
                        if hasattr(part, 'text') and part.text:
                            print(f"    Text: {part.text[:100]}...")
                            response_text += part.text
                        elif hasattr(part, 'function_call'):
                            print(f"    Function call: {part.function_call}")
                        else:
                            print(f"    Other type: {part}")
                            
        print(f"\n📊 Summary:")
        print(f"  Total events: {event_count}")
        print(f"  Final response text: {response_text[:200]}...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mas())