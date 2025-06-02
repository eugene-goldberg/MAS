import asyncio
from typing import Dict, List, Tuple, Optional, Callable
import time
import uuid
import json
from datetime import datetime

from app.models.agent import AgentResponse, ToolCall
from app.models.tracking import ExecutionTrace
from app.core.tracking import TrackingInterceptor
from app.core.mas_client import MASClient

class MASService:
    def __init__(self):
        self.mas_client = MASClient()
        self.tracking_interceptor = TrackingInterceptor()
        self._initialized = False
        
    async def initialize(self):
        """Initialize MAS connection"""
        await self.mas_client.connect()
        self._initialized = True
        
    async def cleanup(self):
        """Cleanup MAS connection"""
        await self.mas_client.disconnect()
        
    async def check_connection(self) -> bool:
        """Check if MAS is connected and healthy"""
        return self._initialized and await self.mas_client.is_healthy()
        
    async def process_message(
        self, 
        message: str, 
        session_id: str,
        websocket_callback: Optional[Callable] = None
    ) -> Tuple[str, ExecutionTrace]:
        """
        Process message through MAS with comprehensive tracking
        
        Args:
            message: User message to process
            session_id: Session identifier
            websocket_callback: Callback for real-time updates
            
        Returns:
            Tuple of (response_text, execution_trace)
        """
        request_id = str(uuid.uuid4())
        
        # Start tracking
        self.tracking_interceptor.start_request(request_id, session_id)
        
        # Notify start
        if websocket_callback:
            try:
                # Check if callback is async
                import inspect
                if inspect.iscoroutinefunction(websocket_callback):
                    await websocket_callback({
                        "type": "execution_start",
                        "request_id": request_id,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    # Call synchronously
                    websocket_callback({
                        "type": "execution_start",
                        "request_id": request_id,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error in websocket callback: {e}")
        
        try:
            # Execute request directly through MAS client
            start_time = time.time()
            response = await self.mas_client.send_message(message)
            total_time = (time.time() - start_time) * 1000
            
            # Get tracking data
            agent_responses = self.tracking_interceptor.get_responses(request_id)
            agent_sequence = self.tracking_interceptor.get_agent_sequence(request_id)
            
            # Create execution trace
            execution_trace = ExecutionTrace(
                session_id=session_id,
                request_id=request_id,
                user_message=message,
                coordinator_response=response,
                agent_sequence=agent_sequence,
                total_time_ms=total_time,
                agent_responses=agent_responses,
                timestamp=datetime.now()
            )
            
            # Notify completion
            if websocket_callback:
                try:
                    import inspect
                    if inspect.iscoroutinefunction(websocket_callback):
                        await websocket_callback({
                            "type": "execution_complete",
                            "request_id": request_id,
                            "response": response,
                            "execution_trace": json.loads(execution_trace.json()),
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        websocket_callback({
                            "type": "execution_complete",
                            "request_id": request_id,
                            "response": response,
                            "execution_trace": json.loads(execution_trace.json()),
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"Error in websocket callback: {e}")
            
            return response, execution_trace
            
        except Exception as e:
            # Notify error
            if websocket_callback:
                try:
                    import inspect
                    if inspect.iscoroutinefunction(websocket_callback):
                        await websocket_callback({
                            "type": "execution_error",
                            "request_id": request_id,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        websocket_callback({
                            "type": "execution_error",
                            "request_id": request_id,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e2:
                    print(f"Error in websocket callback: {e2}")
            raise
        finally:
            # Cleanup tracking
            self.tracking_interceptor.end_request(request_id)
            
    async def get_agent_info(self) -> Dict[str, any]:
        """Get information about available agents"""
        return {
            "coordinator": {
                "name": "MAS Coordinator",
                "model": "gemini-2.0-flash-001",
                "description": "Routes requests to specialized agents"
            },
            "agents": [
                {
                    "name": "Weather Agent",
                    "type": "weather_agent",
                    "description": "Provides weather information and forecasts",
                    "tools": ["get_current_weather", "get_weather_forecast", "get_random_lucky_number", "get_random_temperature_adjustment"],
                    "color": "#3498db",
                    "icon": "🌤️"
                },
                {
                    "name": "RAG Agent",
                    "type": "rag_agent",
                    "description": "Manages document collections and queries",
                    "tools": ["create_corpus", "list_corpora", "add_data", "rag_query", "get_corpus_info", "delete_document", "delete_corpus"],
                    "color": "#9b59b6",
                    "icon": "📚"
                },
                {
                    "name": "Academic WebSearch",
                    "type": "academic_websearch",
                    "description": "Searches for academic papers",
                    "tools": ["google_search"],
                    "color": "#e74c3c",
                    "icon": "🔍"
                },
                {
                    "name": "Academic NewResearch",
                    "type": "academic_newresearch",
                    "description": "Suggests research directions",
                    "tools": [],
                    "color": "#e67e22",
                    "icon": "🔬"
                },
                {
                    "name": "Greeter Agent",
                    "type": "greeter_agent",
                    "description": "Handles greetings and farewells",
                    "tools": [],
                    "color": "#2ecc71",
                    "icon": "👋"
                }
            ]
        }