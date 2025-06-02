#!/usr/bin/env python3
"""
Simple WebSocket test to check connection
"""

import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8000/ws/chat/test-simple"
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected!")
            
            # Try to receive a message
            print("Waiting for initial message...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                print(f"Received: {message}")
                data = json.loads(message)
                print(f"Parsed data: {data}")
            except asyncio.TimeoutError:
                print("Timeout waiting for initial message")
            except Exception as e:
                print(f"Error receiving message: {type(e).__name__}: {e}")
            
            # Check if still connected
            print(f"Connection state: {websocket.state}")
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())