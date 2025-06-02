#!/usr/bin/env python3
"""Test script to verify MAS connection"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.mas_client import MASClient

async def test_connection():
    """Test MAS connection and basic functionality"""
    print("Testing MAS connection...")
    
    client = MASClient()
    
    try:
        # Test connection
        await client.connect()
        print("✅ Successfully connected to MAS system")
        
        # Test health check
        is_healthy = await client.is_healthy()
        print(f"✅ Health check: {'Healthy' if is_healthy else 'Unhealthy'}")
        
        # Test sending a simple message
        print("\nTesting message processing...")
        response = await client.send_message("Hello!")
        print(f"✅ Response received: {response[:100]}...")
        
        # Test another message
        print("\nTesting weather query...")
        response = await client.send_message("What's the weather in London?")
        print(f"✅ Response received: {response[:200]}...")
        
        await client.disconnect()
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())