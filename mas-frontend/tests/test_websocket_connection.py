#!/usr/bin/env python3
"""Test WebSocket connection to the MAS backend"""

import asyncio
import websockets
import json
import uuid

async def test_websocket():
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chat/{session_id}"
    
    print(f"Connecting to {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            
            # Wait for initial connection message
            initial_msg = await websocket.recv()
            initial_data = json.loads(initial_msg)
            print(f"Initial message: {json.dumps(initial_data, indent=2)}")
            
            # Send a test message
            test_message = {
                "type": "chat_message",
                "content": "Hello, can you tell me about the weather?"
            }
            
            print(f"\nSending: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Listen for responses
            timeout = 10  # 10 seconds timeout
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    response_data = json.loads(response)
                    print(f"Received: {json.dumps(response_data, indent=2)}")
                    
                    # If we get the agent response, we're done
                    if response_data.get("type") == "agent_response":
                        print("\n✅ WebSocket connection is working properly!")
                        return True
                        
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("❌ Connection closed unexpectedly")
                    return False
                    
            print("❌ Timeout waiting for response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    exit(0 if result else 1)