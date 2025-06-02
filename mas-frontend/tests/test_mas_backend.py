#!/usr/bin/env python3
"""
Test MAS backend directly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))
mas_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(mas_path))

# Set environment
os.environ['GOOGLE_CLOUD_PROJECT'] = 'pickuptruckapp'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'

async def test():
    try:
        # Import and initialize
        import vertexai
        vertexai.init(project="pickuptruckapp", location="us-central1")
        
        from app.services.mas_service import MASService
        
        print("Creating MAS service...")
        service = MASService()
        
        print("Initializing MAS service...")
        await service.initialize()
        
        print("Checking connection...")
        connected = await service.check_connection()
        print(f"Connected: {connected}")
        
        if connected:
            print("\nSending test message...")
            response, trace = await service.process_message(
                "Hello", 
                "test-session",
                websocket_callback=None
            )
            
            print(f"\nResponse: {response}")
            print(f"Trace: {trace}")
        else:
            print("MAS not connected!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())