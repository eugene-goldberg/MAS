"""MAS System Client for Integration"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
import vertexai
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add MAS system to path for imports
# Go up from: backend/app/core/mas_client.py to MAS directory
mas_parent_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(mas_parent_path))
mas_path = mas_parent_path / "mas_system"
logger.info(f"Adding to path: {mas_parent_path}")
logger.info(f"MAS system path: {mas_path}")
logger.info(f"Path exists: {mas_path.exists()}")

# Load environment variables - try both locations
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # backend/.env
    mas_parent_path / ".env"  # MAS/.env
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)

# Initialize Vertex AI before importing agents
project = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project, location=location)

# Set environment variable to ensure ADK uses Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'

# Also set these to ensure the API client works
os.environ['VERTEXAI'] = 'true'
os.environ['GOOGLE_CLOUD_PROJECT'] = project
os.environ['GOOGLE_CLOUD_LOCATION'] = location

class MASClient:
    """Client for interacting with the MAS system"""
    
    def __init__(self):
        self.coordinator = None
        self._connected = False
        
    async def connect(self):
        """Initialize connection to MAS system"""
        try:
            # Import MAS coordinator
            from mas_system.agent import mas_coordinator
            self.coordinator = mas_coordinator
            self._connected = True
            logger.info("Successfully connected to MAS system")
        except Exception as e:
            logger.error(f"Failed to connect to MAS system: {e}")
            self._connected = False
            raise
            
    async def disconnect(self):
        """Cleanup connection"""
        self.coordinator = None
        self._connected = False
        
    async def is_healthy(self) -> bool:
        """Check if MAS connection is healthy"""
        return self._connected and self.coordinator is not None
        
    def get_coordinator(self):
        """Get the MAS coordinator instance"""
        if not self._connected:
            raise RuntimeError("MAS client not connected")
        return self.coordinator
        
    async def send_message(self, message: str) -> str:
        """Send a message to the MAS coordinator"""
        if not self._connected:
            raise RuntimeError("MAS client not connected")
            
        try:
            # Replicate the exact pattern from test_local.py
            from google.adk.runners import InMemoryRunner
            from google.genai import types
            
            if not hasattr(self, '_runner'):
                # Create runner exactly like in test_local.py
                self._runner = InMemoryRunner(agent=self.coordinator)
                self._session = await self._runner.session_service.create_session(
                    app_name=self._runner.app_name, user_id="test_user"
                )
                logger.info(f"Created MAS runner and session: {self._session.id}")
            
            # Create user content exactly like in test_local.py
            content = types.UserContent(parts=[types.Part(text=message)])
            logger.info(f"Sending message to MAS: {message}")
            
            # Execute through runner exactly like in test_local.py
            response_text = ""
            event_count = 0
            
            # Collect all events first
            events = []
            async for event in self._runner.run_async(
                user_id=self._session.user_id,
                session_id=self._session.id,
                new_message=content,
            ):
                events.append(event)
                event_count += 1
            
            # Process events to extract text
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
                            logger.info(f"Got text from MAS: {part.text[:100]}...")
            
            # If no text found but we have events, the response might be in the last event
            if not response_text and events:
                # Check the last event more thoroughly
                last_event = events[-1]
                if hasattr(last_event, 'content'):
                    # Try to get text from Content object
                    if hasattr(last_event.content, 'text'):
                        response_text = last_event.content.text
                    elif hasattr(last_event.content, 'parts'):
                        # Sometimes the response is in a different format
                        for part in last_event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text
            
            logger.info(f"MAS processing complete. Events: {event_count}, Response length: {len(response_text)}")
            return response_text if response_text else "No response generated"
        except Exception as e:
            logger.error(f"Error sending message to MAS: {e}")
            raise