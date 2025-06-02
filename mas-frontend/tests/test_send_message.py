#!/usr/bin/env python3
"""
Test sending a message through WebSocket
"""

import asyncio
import websockets
import json

async def test_send_message():
    uri = "ws://localhost:8000/ws/chat/test-message"
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected!")
            
            # Wait for connection established
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            # Send a test message
            test_message = {
                "type": "chat_message",
                "content": "Hello, MAS! What's the weather like?"
            }
            await websocket.send(json.dumps(test_message))
            print("Sent test message")
            
            # Wait for acknowledgment
            ack = await websocket.recv()
            ack_data = json.loads(ack)
            print(f"Acknowledgment: {ack_data}")
            
            # Wait for response (with timeout)
            print("Waiting for agent response...")
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=30)
                response_data = json.loads(response)
                print(f"Received: {response_data['type']}")
                
                if response_data['type'] == 'agent_response':
                    print(f"Agent response: {response_data['content']}")
                    break
                elif response_data['type'] == 'error':
                    print(f"Error: {response_data['error']}")
                    break
                    
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_send_message())