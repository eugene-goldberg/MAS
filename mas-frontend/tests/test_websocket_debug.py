#!/usr/bin/env python3
"""
Debug script to test WebSocket connection issues
"""

import asyncio
import websockets
import json
import sys
import time

async def test_websocket_debug():
    session_id = f"debug-{int(time.time())}"
    uri = f"ws://localhost:8000/ws/chat/{session_id}"
    
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected successfully")
            
            # Wait for connection established message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                print(f"Received: {data}")
                
                if data.get("type") == "connection_established":
                    print("✓ Connection established message received")
                    print(f"  Session ID: {data.get('session_id')}")
                    print(f"  Agent info: {data.get('agent_info')}")
                    
                    # Keep connection open and listen for messages
                    print("\nListening for messages (press Ctrl+C to stop)...")
                    
                    while True:
                        try:
                            # Use wait_for with a timeout to handle heartbeats
                            message = await asyncio.wait_for(websocket.recv(), timeout=35)
                            data = json.loads(message)
                            print(f"Received: {data}")
                            
                            if data.get("type") == "heartbeat":
                                print("  → Sending pong")
                                await websocket.send(json.dumps({"type": "pong"}))
                                
                        except asyncio.TimeoutError:
                            print("No message received in 35 seconds")
                            # Send a ping to check if connection is alive
                            print("Sending ping...")
                            await websocket.send(json.dumps({"type": "ping"}))
                            
                else:
                    print(f"✗ Unexpected first message type: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("✗ Timeout waiting for connection established message")
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"✗ Connection closed: code={e.code}, reason={e.reason}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket_debug())
    except KeyboardInterrupt:
        print("\nTest stopped by user")