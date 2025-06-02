# MAS Testing Frontend - Complete Implementation Plan

## Executive Summary

Build a comprehensive testing and visualization interface for the Multi-Agent System (MAS) using FastAPI (backend) and React.js (frontend). This system will provide real-time visibility into agent interactions, tool usage, and response generation, making it ideal for testing, debugging, and demonstrating the MAS capabilities.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Backend Implementation (FastAPI)](#backend-implementation-fastapi)
3. [Frontend Implementation (React.js)](#frontend-implementation-reactjs)
4. [Data Models and Interfaces](#data-models-and-interfaces)
5. [Real-time Communication](#real-time-communication)
6. [UI/UX Design](#uiux-design)
7. [Deployment Strategy](#deployment-strategy)
8. [Implementation Timeline](#implementation-timeline)
9. [Testing Strategy](#testing-strategy)

## Architecture Overview

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     React.js Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  • Chat Interface (left panel)                              │
│  • Agent Response Viewer (right panel)                      │
│  • Tool Usage Timeline                                      │
│  • Real-time updates via WebSocket                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket + REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  • REST endpoints for chat                                  │
│  • WebSocket for real-time updates                          │
│  • Agent execution tracking                                 │
│  • Tool call interception                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Integrates with
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MAS Coordinator                          │
│          (Existing Multi-Agent System)                      │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure
```
mas-frontend/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py        # Chat endpoints
│   │   │   │   ├── agents.py      # Agent information endpoints
│   │   │   │   ├── sessions.py    # Session management
│   │   │   │   └── websocket.py   # WebSocket handler
│   │   │   └── dependencies.py    # Shared dependencies
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Configuration settings
│   │   │   ├── mas_client.py      # MAS system integration
│   │   │   ├── tracking.py        # Agent/tool execution tracking
│   │   │   └── exceptions.py      # Custom exceptions
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # Chat-related models
│   │   │   ├── agent.py           # Agent and tool models
│   │   │   ├── session.py         # Session models
│   │   │   └── tracking.py        # Tracking models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── mas_service.py     # MAS interaction logic
│   │   │   ├── tracking_service.py # Tracking service
│   │   │   ├── session_service.py  # Session management
│   │   │   └── export_service.py   # Export functionality
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py          # Utility functions
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_integration/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── Message.tsx
│   │   │   │   └── index.ts
│   │   │   ├── AgentPanel/
│   │   │   │   ├── AgentResponsePanel.tsx
│   │   │   │   ├── AgentCard.tsx
│   │   │   │   ├── ToolTimeline.tsx
│   │   │   │   ├── ToolCallDetail.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── SplitLayout.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Metrics/
│   │   │   │   ├── MetricsPanel.tsx
│   │   │   │   ├── MetricCard.tsx
│   │   │   │   └── index.ts
│   │   │   └── Common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       ├── ConnectionStatus.tsx
│   │   │       └── index.ts
│   │   ├── contexts/
│   │   │   ├── ChatContext.tsx
│   │   │   ├── AgentTrackingContext.tsx
│   │   │   └── WebSocketContext.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useChat.ts
│   │   │   ├── useAgentTracking.ts
│   │   │   └── useMetrics.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── export.ts
│   │   ├── types/
│   │   │   ├── chat.ts
│   │   │   ├── agent.ts
│   │   │   └── common.ts
│   │   ├── utils/
│   │   │   ├── formatters.ts
│   │   │   └── helpers.ts
│   │   ├── styles/
│   │   │   ├── main.scss
│   │   │   ├── components/
│   │   │   └── themes/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Backend Implementation (FastAPI)

### Core Application Setup

#### main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api.routes import chat, agents, sessions, websocket
from app.core.config import settings
from app.services.session_service import SessionService
from app.services.mas_service import MASService

# Initialize services
session_service = SessionService()
mas_service = MASService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting MAS Frontend API...")
    await mas_service.initialize()
    yield
    # Shutdown
    print("Shutting down MAS Frontend API...")
    await mas_service.cleanup()

app = FastAPI(
    title="MAS Testing Interface",
    description="Real-time testing and visualization for Multi-Agent System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {
        "message": "MAS Testing Interface API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mas_connected": await mas_service.check_connection()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

### Configuration Management

#### core/config.py
```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "MAS Testing Interface"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # MAS Integration
    MAS_PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    MAS_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    MAS_AGENT_ID: str = os.getenv("MAS_AGENT_ID", "")
    
    # Session Settings
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_SESSIONS_PER_USER: int = 5
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    # Export Settings
    EXPORT_MAX_MESSAGES: int = 1000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### MAS Integration Service

#### services/mas_service.py
```python
import asyncio
from typing import Dict, List, Tuple, Optional, Callable
import time
import uuid
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
            await websocket_callback({
                "type": "execution_start",
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            })
        
        try:
            # Create wrapped coordinator with tracking
            tracked_coordinator = self.tracking_interceptor.wrap_coordinator(
                self.mas_client.get_coordinator(),
                request_id,
                websocket_callback
            )
            
            # Execute request
            start_time = time.time()
            response = await tracked_coordinator.send(message)
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
                await websocket_callback({
                    "type": "execution_complete",
                    "request_id": request_id,
                    "response": response,
                    "execution_trace": execution_trace.dict(),
                    "timestamp": datetime.now().isoformat()
                })
            
            return response, execution_trace
            
        except Exception as e:
            # Notify error
            if websocket_callback:
                await websocket_callback({
                    "type": "execution_error",
                    "request_id": request_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
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
```

### Tracking System

#### core/tracking.py
```python
from typing import Dict, List, Callable, Optional, Any
import functools
import time
import asyncio
from datetime import datetime
import inspect

from app.models.agent import AgentResponse, ToolCall

class TrackingInterceptor:
    """Intercepts and tracks agent and tool execution"""
    
    def __init__(self):
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        
    def start_request(self, request_id: str, session_id: str):
        """Initialize tracking for a new request"""
        self.active_requests[request_id] = {
            "session_id": session_id,
            "agent_responses": [],
            "agent_sequence": [],
            "current_agent": None,
            "tool_calls": []
        }
        
    def end_request(self, request_id: str):
        """Cleanup tracking for completed request"""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
            
    def get_responses(self, request_id: str) -> List[AgentResponse]:
        """Get all agent responses for a request"""
        if request_id in self.active_requests:
            return self.active_requests[request_id]["agent_responses"]
        return []
        
    def get_agent_sequence(self, request_id: str) -> List[str]:
        """Get the sequence of agents called"""
        if request_id in self.active_requests:
            return self.active_requests[request_id]["agent_sequence"]
        return []
        
    def wrap_coordinator(self, coordinator, request_id: str, websocket_callback: Optional[Callable] = None):
        """Wrap the MAS coordinator to track agent calls"""
        
        class TrackedCoordinator:
            def __init__(self, original_coordinator, interceptor, req_id, ws_callback):
                self.coordinator = original_coordinator
                self.interceptor = interceptor
                self.request_id = req_id
                self.websocket_callback = ws_callback
                
            async def send(self, message: str) -> str:
                # Track the coordinator processing
                if self.websocket_callback:
                    await self.websocket_callback({
                        "type": "coordinator_start",
                        "message": message,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Intercept sub-agent calls
                # This would require patching the coordinator's tool calls
                # For now, we'll simulate tracking
                response = await self._execute_with_tracking(message)
                
                return response
                
            async def _execute_with_tracking(self, message: str) -> str:
                # This is where we'd intercept actual agent calls
                # For demonstration, we'll call the original coordinator
                return await self.coordinator.send(message)
                
        return TrackedCoordinator(coordinator, self, request_id, websocket_callback)
        
    def wrap_agent(self, agent, agent_name: str, request_id: str, websocket_callback: Optional[Callable] = None):
        """Wrap an agent to track its execution"""
        
        class TrackedAgent:
            def __init__(self, original_agent, interceptor, name, req_id, ws_callback):
                self.agent = original_agent
                self.interceptor = interceptor
                self.agent_name = name
                self.request_id = req_id
                self.websocket_callback = ws_callback
                
            async def process(self, message: str) -> str:
                # Record agent start
                start_time = time.time()
                
                if self.request_id in self.interceptor.active_requests:
                    self.interceptor.active_requests[self.request_id]["current_agent"] = self.agent_name
                    self.interceptor.active_requests[self.request_id]["agent_sequence"].append(self.agent_name)
                
                if self.websocket_callback:
                    await self.websocket_callback({
                        "type": "agent_start",
                        "agent": self.agent_name,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Wrap agent tools
                wrapped_tools = self._wrap_agent_tools()
                
                # Execute agent
                response = await self.agent.process(message)
                
                # Record agent completion
                duration = (time.time() - start_time) * 1000
                
                # Get tool calls for this agent
                agent_tool_calls = []
                if self.request_id in self.interceptor.active_requests:
                    all_tool_calls = self.interceptor.active_requests[self.request_id]["tool_calls"]
                    agent_tool_calls = [tc for tc in all_tool_calls if tc.get("agent") == self.agent_name]
                
                # Create agent response
                agent_response = AgentResponse(
                    agent_name=self.agent_name,
                    agent_type=self.agent.__class__.__name__,
                    response=response,
                    tools_used=[self._convert_tool_call(tc) for tc in agent_tool_calls],
                    processing_time_ms=duration,
                    timestamp=datetime.now()
                )
                
                if self.request_id in self.interceptor.active_requests:
                    self.interceptor.active_requests[self.request_id]["agent_responses"].append(agent_response)
                
                if self.websocket_callback:
                    await self.websocket_callback({
                        "type": "agent_complete",
                        "agent": self.agent_name,
                        "duration_ms": duration,
                        "response_preview": response[:100] + "..." if len(response) > 100 else response,
                        "timestamp": datetime.now().isoformat()
                    })
                
                return response
                
            def _wrap_agent_tools(self):
                """Wrap all tools of the agent"""
                # This would wrap each tool function
                # Implementation depends on how tools are attached to agents
                pass
                
            def _convert_tool_call(self, tool_call_data: Dict) -> ToolCall:
                """Convert tracked tool call data to ToolCall model"""
                return ToolCall(
                    tool_name=tool_call_data["tool_name"],
                    tool_type=tool_call_data["tool_type"],
                    parameters=tool_call_data["parameters"],
                    result=tool_call_data["result"],
                    duration_ms=tool_call_data["duration_ms"],
                    timestamp=tool_call_data["timestamp"]
                )
                
        return TrackedAgent(agent, self, agent_name, request_id, websocket_callback)
        
    def wrap_tool(self, tool_func: Callable, tool_name: str, agent_name: str, request_id: str, websocket_callback: Optional[Callable] = None):
        """Wrap a tool function to track its execution"""
        
        @functools.wraps(tool_func)
        async def wrapped_tool(*args, **kwargs):
            start_time = time.time()
            
            # Notify tool start
            if websocket_callback:
                await websocket_callback({
                    "type": "tool_start",
                    "agent": agent_name,
                    "tool": tool_name,
                    "parameters": self._serialize_parameters(kwargs),
                    "timestamp": datetime.now().isoformat()
                })
            
            try:
                # Execute tool
                if inspect.iscoroutinefunction(tool_func):
                    result = await tool_func(*args, **kwargs)
                else:
                    result = tool_func(*args, **kwargs)
                
                duration = (time.time() - start_time) * 1000
                
                # Record tool call
                tool_call_data = {
                    "agent": agent_name,
                    "tool_name": tool_name,
                    "tool_type": "function",
                    "parameters": kwargs,
                    "result": result,
                    "duration_ms": duration,
                    "timestamp": datetime.now(),
                    "success": True
                }
                
                if request_id in self.active_requests:
                    self.active_requests[request_id]["tool_calls"].append(tool_call_data)
                
                # Notify tool completion
                if websocket_callback:
                    await websocket_callback({
                        "type": "tool_complete",
                        "agent": agent_name,
                        "tool": tool_name,
                        "duration_ms": duration,
                        "success": True,
                        "result_preview": self._preview_result(result),
                        "timestamp": datetime.now().isoformat()
                    })
                
                return result
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                
                # Record failed tool call
                tool_call_data = {
                    "agent": agent_name,
                    "tool_name": tool_name,
                    "tool_type": "function",
                    "parameters": kwargs,
                    "result": {"error": str(e)},
                    "duration_ms": duration,
                    "timestamp": datetime.now(),
                    "success": False
                }
                
                if request_id in self.active_requests:
                    self.active_requests[request_id]["tool_calls"].append(tool_call_data)
                
                # Notify tool error
                if websocket_callback:
                    await websocket_callback({
                        "type": "tool_error",
                        "agent": agent_name,
                        "tool": tool_name,
                        "duration_ms": duration,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                
                raise
                
        return wrapped_tool
        
    def _serialize_parameters(self, params: Dict) -> Dict:
        """Serialize parameters for transmission"""
        # Convert complex objects to strings
        serialized = {}
        for key, value in params.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                serialized[key] = value
            else:
                serialized[key] = str(value)
        return serialized
        
    def _preview_result(self, result: Any) -> str:
        """Create a preview of the result"""
        if isinstance(result, dict):
            return f"Dict with {len(result)} keys"
        elif isinstance(result, list):
            return f"List with {len(result)} items"
        elif isinstance(result, str):
            return result[:100] + "..." if len(result) > 100 else result
        else:
            return str(result)[:100]
```

### WebSocket Handler

#### api/routes/websocket.py
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import json
import asyncio
import uuid

from app.services.mas_service import MASService
from app.services.session_service import SessionService
from app.models.chat import ChatMessage
from app.core.config import settings

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            
    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)
            
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/chat/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    mas_service: MASService = Depends(),
    session_service: SessionService = Depends()
):
    await manager.connect(websocket, session_id)
    
    # Create or get session
    session = await session_service.get_or_create_session(session_id)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "agent_info": await mas_service.get_agent_info()
        })
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(heartbeat(websocket))
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "chat_message":
                # Create message ID
                message_id = str(uuid.uuid4())
                
                # Save user message
                user_message = ChatMessage(
                    id=message_id,
                    content=message_data["content"],
                    role="user",
                    session_id=session_id,
                    timestamp=datetime.now()
                )
                await session_service.add_message(session_id, user_message)
                
                # Send message received confirmation
                await websocket.send_json({
                    "type": "message_received",
                    "message_id": message_id
                })
                
                # Process with MAS
                try:
                    response, execution_trace = await mas_service.process_message(
                        message_data["content"],
                        session_id,
                        websocket_callback=lambda update: websocket.send_json(update)
                    )
                    
                    # Save assistant message
                    assistant_message = ChatMessage(
                        id=str(uuid.uuid4()),
                        content=response,
                        role="assistant",
                        session_id=session_id,
                        timestamp=datetime.now(),
                        agent_responses=execution_trace.agent_responses
                    )
                    await session_service.add_message(session_id, assistant_message)
                    
                    # Save execution trace
                    await session_service.add_execution_trace(session_id, execution_trace)
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e),
                        "message_id": message_id
                    })
                    
            elif message_data["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        heartbeat_task.cancel()
        print(f"Client {session_id} disconnected")
        
async def heartbeat(websocket: WebSocket):
    """Send periodic heartbeat to keep connection alive"""
    try:
        while True:
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
            await websocket.send_json({"type": "heartbeat"})
    except Exception:
        pass
```

### API Routes

#### api/routes/chat.py
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.mas_service import MASService
from app.services.session_service import SessionService

router = APIRouter()

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    mas_service: MASService = Depends(),
    session_service: SessionService = Depends()
):
    """Send a message to MAS and get response"""
    try:
        # Process message
        response, execution_trace = await mas_service.process_message(
            request.message,
            request.session_id or "default"
        )
        
        return ChatResponse(
            response=response,
            execution_trace=execution_trace,
            session_id=request.session_id or "default"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    session_service: SessionService = Depends()
):
    """Get chat history for a session"""
    messages = await session_service.get_messages(session_id, limit)
    return messages

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    session_service: SessionService = Depends()
):
    """Clear chat history for a session"""
    await session_service.clear_messages(session_id)
    return {"message": "Chat history cleared"}
```

## Frontend Implementation (React.js)

### Application Entry Point

#### src/App.tsx
```tsx
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { ChatProvider } from './contexts/ChatContext';
import { AgentTrackingProvider } from './contexts/AgentTrackingContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { SplitLayout } from './components/Layout/SplitLayout';
import { ChatInterface } from './components/Chat/ChatInterface';
import { AgentResponsePanel } from './components/AgentPanel/AgentResponsePanel';
import { Header } from './components/Layout/Header';
import { theme } from './styles/theme';

import './styles/main.scss';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <WebSocketProvider>
          <ChatProvider>
            <AgentTrackingProvider>
              <div className="app-container">
                <Header />
                <SplitLayout
                  left={<ChatInterface />}
                  right={<AgentResponsePanel />}
                />
              </div>
            </AgentTrackingProvider>
          </ChatProvider>
        </WebSocketProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
```

### Core Components

#### components/Chat/ChatInterface.tsx
```tsx
import React, { useState, useRef, useEffect } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ConnectionStatus } from '../Common/ConnectionStatus';
import { useChat } from '../../hooks/useChat';
import { useWebSocket } from '../../hooks/useWebSocket';
import './ChatInterface.scss';

export const ChatInterface: React.FC = () => {
  const { messages, addMessage, isLoading } = useChat();
  const { sendMessage, isConnected } = useWebSocket();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !isConnected) return;
    
    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    });
    
    // Send to backend
    await sendMessage({
      type: 'chat_message',
      content
    });
  };
  
  return (
    <Paper className="chat-interface" elevation={0}>
      <Box className="chat-header">
        <Typography variant="h6">MAS Chat</Typography>
        <ConnectionStatus connected={isConnected} />
      </Box>
      
      <Box className="chat-messages">
        <MessageList messages={messages} isLoading={isLoading} />
        <div ref={messagesEndRef} />
      </Box>
      
      <Box className="chat-input">
        <MessageInput 
          onSend={handleSendMessage} 
          disabled={!isConnected || isLoading}
        />
      </Box>
    </Paper>
  );
};
```

#### components/AgentPanel/AgentResponsePanel.tsx
```tsx
import React, { useState } from 'react';
import { Box, Paper, Typography, Tabs, Tab, Chip } from '@mui/material';
import { AgentCard } from './AgentCard';
import { ToolTimeline } from './ToolTimeline';
import { MetricsPanel } from '../Metrics/MetricsPanel';
import { useAgentTracking } from '../../hooks/useAgentTracking';
import './AgentResponsePanel.scss';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box p={2}>{children}</Box>}
    </div>
  );
};

export const AgentResponsePanel: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const { 
    currentExecution, 
    agentResponses, 
    isExecuting,
    executionProgress 
  } = useAgentTracking();
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  return (
    <Paper className="agent-response-panel" elevation={0}>
      <Box className="panel-header">
        <Typography variant="h6">Agent Activity</Typography>
        {isExecuting && (
          <Chip 
            label={`Processing... ${executionProgress}%`} 
            color="primary" 
            size="small"
          />
        )}
      </Box>
      
      <Tabs value={tabValue} onChange={handleTabChange}>
        <Tab label="Timeline" />
        <Tab label="Responses" />
        <Tab label="Metrics" />
      </Tabs>
      
      <TabPanel value={tabValue} index={0}>
        <ToolTimeline execution={currentExecution} />
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <Box className="agents-list">
          {agentResponses.map((response, idx) => (
            <AgentCard key={idx} response={response} />
          ))}
        </Box>
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        <MetricsPanel />
      </TabPanel>
    </Paper>
  );
};
```

#### components/AgentPanel/ToolTimeline.tsx
```tsx
import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';
import Timeline from '@mui/lab/Timeline';
import TimelineItem from '@mui/lab/TimelineItem';
import TimelineSeparator from '@mui/lab/TimelineSeparator';
import TimelineConnector from '@mui/lab/TimelineConnector';
import TimelineContent from '@mui/lab/TimelineContent';
import TimelineDot from '@mui/lab/TimelineDot';
import { ExecutionTrace, ToolCall } from '../../types/agent';
import { getAgentColor, getAgentIcon, formatDuration } from '../../utils/formatters';
import './ToolTimeline.scss';

interface TimelineEvent {
  type: 'agent_start' | 'tool_call' | 'agent_complete';
  agent: string;
  tool?: string;
  timestamp: Date;
  duration?: number;
  status?: 'running' | 'complete' | 'error';
}

export const ToolTimeline: React.FC<{ execution?: ExecutionTrace }> = ({ execution }) => {
  if (!execution) {
    return (
      <Box className="timeline-empty">
        <Typography variant="body2" color="textSecondary">
          No execution data yet. Send a message to see the agent activity timeline.
        </Typography>
      </Box>
    );
  }
  
  // Convert execution data to timeline events
  const events: TimelineEvent[] = [];
  
  execution.agent_responses.forEach(agentResponse => {
    // Agent start
    events.push({
      type: 'agent_start',
      agent: agentResponse.agent_name,
      timestamp: new Date(agentResponse.timestamp),
      status: 'complete'
    });
    
    // Tool calls
    agentResponse.tools_used.forEach(tool => {
      events.push({
        type: 'tool_call',
        agent: agentResponse.agent_name,
        tool: tool.tool_name,
        timestamp: new Date(tool.timestamp),
        duration: tool.duration_ms,
        status: 'complete'
      });
    });
    
    // Agent complete
    events.push({
      type: 'agent_complete',
      agent: agentResponse.agent_name,
      timestamp: new Date(agentResponse.timestamp),
      duration: agentResponse.processing_time_ms,
      status: 'complete'
    });
  });
  
  // Sort by timestamp
  events.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  
  return (
    <Box className="tool-timeline">
      <Timeline position="right">
        {events.map((event, index) => (
          <TimelineItem key={index}>
            <TimelineSeparator>
              <TimelineDot 
                sx={{ 
                  bgcolor: getAgentColor(event.agent),
                  width: event.type === 'tool_call' ? 8 : 12,
                  height: event.type === 'tool_call' ? 8 : 12
                }}
              >
                {event.type !== 'tool_call' && getAgentIcon(event.agent)}
              </TimelineDot>
              {index < events.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            
            <TimelineContent>
              <Box className={`timeline-event ${event.type}`}>
                <Typography variant="subtitle2" className="event-title">
                  {event.type === 'agent_start' && `${event.agent} Started`}
                  {event.type === 'tool_call' && `Tool: ${event.tool}`}
                  {event.type === 'agent_complete' && `${event.agent} Complete`}
                </Typography>
                
                {event.duration && (
                  <Typography variant="caption" color="textSecondary">
                    {formatDuration(event.duration)}
                  </Typography>
                )}
                
                {event.status === 'running' && (
                  <LinearProgress 
                    variant="indeterminate" 
                    sx={{ mt: 0.5, height: 2 }}
                  />
                )}
              </Box>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
      
      <Box className="timeline-summary">
        <Typography variant="caption" color="textSecondary">
          Total execution time: {formatDuration(execution.total_time_ms)}
        </Typography>
      </Box>
    </Box>
  );
};
```

### Context Providers

#### contexts/WebSocketContext.tsx
```tsx
import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { useChat } from '../hooks/useChat';
import { useAgentTracking } from '../hooks/useAgentTracking';
import { WebSocketMessage, WebSocketStatus } from '../types/websocket';

interface WebSocketContextType {
  sendMessage: (message: any) => void;
  status: WebSocketStatus;
  isConnected: boolean;
  sessionId: string;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [sessionId] = useState(() => uuidv4());
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const { addMessage, setLoading } = useChat();
  const { updateExecution, addToolCall, updateProgress } = useAgentTracking();
  
  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;
    
    setStatus('connecting');
    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/chat/${sessionId}`;
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setStatus('connected');
    };
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setStatus('disconnected');
      // Attempt to reconnect after 3 seconds
      reconnectTimeout.current = setTimeout(connect, 3000);
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('error');
    };
    
    ws.current.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        handleMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };
  }, [sessionId]);
  
  const handleMessage = (data: WebSocketMessage) => {
    switch (data.type) {
      case 'connection_established':
        console.log('Connection established with agent info:', data.agent_info);
        break;
        
      case 'message_received':
        setLoading(true);
        break;
        
      case 'coordinator_start':
        updateProgress(10);
        break;
        
      case 'agent_start':
        updateProgress(30);
        addToolCall({
          agent: data.agent,
          type: 'agent_start',
          timestamp: new Date(data.timestamp)
        });
        break;
        
      case 'tool_start':
        addToolCall({
          agent: data.agent,
          tool: data.tool,
          type: 'tool_start',
          parameters: data.parameters,
          timestamp: new Date(data.timestamp)
        });
        break;
        
      case 'tool_complete':
        updateProgress(70);
        addToolCall({
          agent: data.agent,
          tool: data.tool,
          type: 'tool_complete',
          duration: data.duration_ms,
          result: data.result_preview,
          timestamp: new Date(data.timestamp)
        });
        break;
        
      case 'agent_complete':
        updateProgress(90);
        break;
        
      case 'execution_complete':
        setLoading(false);
        updateProgress(100);
        
        // Add assistant message
        addMessage({
          id: uuidv4(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          execution_trace: data.execution_trace
        });
        
        // Update execution trace
        updateExecution(data.execution_trace);
        break;
        
      case 'error':
        setLoading(false);
        console.error('Execution error:', data.error);
        break;
        
      case 'heartbeat':
        // Respond with pong if needed
        break;
    }
  };
  
  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);
  
  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      ws.current?.close();
    };
  }, [connect]);
  
  return (
    <WebSocketContext.Provider value={{
      sendMessage,
      status,
      isConnected: status === 'connected',
      sessionId
    }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
};
```

### Styling

#### styles/main.scss
```scss
@import './variables';
@import './mixins';

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $background-color;
}

// Split Layout
.split-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  
  .split-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    
    &.left {
      flex: 3;
      border-right: 1px solid $border-color;
    }
    
    &.right {
      flex: 2;
      background-color: $panel-background;
    }
  }
}

// Chat Interface
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $spacing-md;
    border-bottom: 1px solid $border-color;
    background-color: white;
  }
  
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: $spacing-md;
    background-color: $chat-background;
  }
  
  .chat-input {
    padding: $spacing-md;
    background-color: white;
    border-top: 1px solid $border-color;
  }
}

// Agent Response Panel
.agent-response-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $spacing-md;
    border-bottom: 1px solid $border-color;
  }
  
  .agents-list {
    padding: $spacing-md;
    overflow-y: auto;
  }
}

// Agent Cards
.agent-card {
  margin-bottom: $spacing-md;
  border-radius: $border-radius;
  overflow: hidden;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .agent-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $spacing-md;
    cursor: pointer;
    
    .agent-info {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      
      .agent-icon {
        font-size: 1.5rem;
      }
    }
    
    .agent-stats {
      display: flex;
      gap: $spacing-md;
      font-size: 0.875rem;
      color: $text-secondary;
    }
  }
  
  .agent-details {
    padding: $spacing-md;
    background-color: $background-light;
    
    .tools-section {
      margin-top: $spacing-md;
      
      h5 {
        margin-bottom: $spacing-sm;
        font-size: 0.875rem;
        text-transform: uppercase;
        color: $text-secondary;
      }
    }
  }
  
  // Agent-specific colors
  &.weather_agent {
    border-left: 4px solid $agent-weather;
  }
  
  &.rag_agent {
    border-left: 4px solid $agent-rag;
  }
  
  &.academic_agent {
    border-left: 4px solid $agent-academic;
  }
  
  &.greeter_agent {
    border-left: 4px solid $agent-greeter;
  }
}

// Tool Timeline
.tool-timeline {
  .timeline-event {
    padding: $spacing-sm;
    border-radius: $border-radius-sm;
    background-color: $background-light;
    
    &.tool_call {
      margin-left: $spacing-md;
      font-size: 0.875rem;
    }
    
    .event-title {
      font-weight: 500;
    }
  }
  
  .timeline-summary {
    margin-top: $spacing-lg;
    padding-top: $spacing-md;
    border-top: 1px solid $border-color;
    text-align: center;
  }
}

// Animations
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.loading-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

// Responsive
@media (max-width: 768px) {
  .split-layout {
    flex-direction: column;
    
    .split-panel {
      &.left,
      &.right {
        flex: 1;
        border-right: none;
        border-bottom: 1px solid $border-color;
      }
    }
  }
}
```

#### styles/_variables.scss
```scss
// Colors
$primary-color: #1976d2;
$secondary-color: #dc004e;
$success-color: #4caf50;
$warning-color: #ff9800;
$error-color: #f44336;

// Agent Colors
$agent-weather: #3498db;
$agent-rag: #9b59b6;
$agent-academic: #e74c3c;
$agent-greeter: #2ecc71;
$agent-coordinator: #34495e;

// Neutral Colors
$text-primary: #212121;
$text-secondary: #757575;
$border-color: #e0e0e0;
$background-color: #fafafa;
$background-light: #f5f5f5;
$panel-background: #ffffff;
$chat-background: #f8f9fa;

// Spacing
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// Border Radius
$border-radius-sm: 4px;
$border-radius: 8px;
$border-radius-lg: 12px;

// Shadows
$shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
$shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.15);

// Transitions
$transition-fast: 0.15s ease;
$transition-normal: 0.25s ease;
$transition-slow: 0.35s ease;
```

## Data Models and Interfaces

### Backend Models (Pydantic)

#### models/chat.py
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .agent import AgentResponse

class ChatMessage(BaseModel):
    id: str
    content: str
    role: str  # "user" or "assistant"
    session_id: str
    timestamp: datetime
    agent_responses: Optional[List[AgentResponse]] = []

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    execution_trace: 'ExecutionTrace'
    session_id: str
```

#### models/agent.py
```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ToolCall(BaseModel):
    tool_name: str
    tool_type: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    duration_ms: float
    timestamp: datetime
    success: bool = True

class AgentResponse(BaseModel):
    agent_name: str
    agent_type: str
    response: str
    tools_used: List[ToolCall]
    processing_time_ms: float
    timestamp: datetime
```

#### models/tracking.py
```python
from pydantic import BaseModel
from typing import List
from datetime import datetime
from .agent import AgentResponse

class ExecutionTrace(BaseModel):
    session_id: str
    request_id: str
    user_message: str
    coordinator_response: str
    agent_sequence: List[str]
    total_time_ms: float
    agent_responses: List[AgentResponse]
    timestamp: datetime
```

### Frontend Types (TypeScript)

#### types/chat.ts
```typescript
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  execution_trace?: ExecutionTrace;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}
```

#### types/agent.ts
```typescript
export interface ToolCall {
  tool_name: string;
  tool_type: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
  duration_ms: number;
  timestamp: Date;
  success: boolean;
}

export interface AgentResponse {
  agent_name: string;
  agent_type: string;
  response: string;
  tools_used: ToolCall[];
  processing_time_ms: number;
  timestamp: Date;
}

export interface ExecutionTrace {
  session_id: string;
  request_id: string;
  user_message: string;
  coordinator_response: string;
  agent_sequence: string[];
  total_time_ms: number;
  agent_responses: AgentResponse[];
  timestamp: Date;
}

export interface AgentInfo {
  name: string;
  type: string;
  description: string;
  tools: string[];
  color: string;
  icon: string;
}
```

## Real-time Communication

### WebSocket Protocol

#### Message Types
```typescript
// Client to Server
interface ClientMessage {
  type: 'chat_message' | 'ping';
  content?: string;
}

// Server to Client
interface ServerMessage {
  type: 'connection_established' | 'message_received' | 'coordinator_start' | 
        'agent_start' | 'tool_start' | 'tool_complete' | 'agent_complete' |
        'execution_complete' | 'error' | 'heartbeat' | 'pong';
  [key: string]: any;
}
```

#### Event Flow
1. Client connects to WebSocket
2. Server sends `connection_established` with agent info
3. Client sends `chat_message`
4. Server sends real-time updates:
   - `coordinator_start`
   - `agent_start`
   - `tool_start`
   - `tool_complete`
   - `agent_complete`
   - `execution_complete`
5. Client updates UI in real-time

## Deployment Strategy

### Docker Configuration

#### Backend Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
# Build stage
FROM node:16-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
      - MAS_AGENT_ID=${MAS_AGENT_ID}
    volumes:
      - ${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json
    env_file:
      - ./backend/.env
    networks:
      - mas-network

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://backend:8000
      - REACT_APP_WS_URL=ws://backend:8000
    networks:
      - mas-network

networks:
  mas-network:
    driver: bridge
```

### Production Deployment

#### Google Cloud Run Deployment
```bash
# Build and push backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/mas-frontend-backend ./backend
gcloud run deploy mas-frontend-backend \
  --image gcr.io/$PROJECT_ID/mas-frontend-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and push frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/mas-frontend ./frontend
gcloud run deploy mas-frontend \
  --image gcr.io/$PROJECT_ID/mas-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Implementation Timeline

### Week 1: Backend Foundation (Days 1-7)
- **Day 1-2**: Project setup and configuration
  - Initialize FastAPI project
  - Set up Docker environment
  - Configure MAS integration
  
- **Day 3-4**: Core services implementation
  - MAS service with coordinator integration
  - Tracking interceptor
  - Session management
  
- **Day 5-6**: API development
  - REST endpoints
  - WebSocket handler
  - Real-time tracking
  
- **Day 7**: Testing and documentation
  - Unit tests for services
  - Integration tests
  - API documentation

### Week 2: Frontend Core (Days 8-14)
- **Day 8-9**: React setup and architecture
  - Project initialization
  - Component structure
  - Context providers
  
- **Day 10-11**: Chat interface
  - Message list
  - Input component
  - WebSocket integration
  
- **Day 12-13**: Agent panel
  - Agent cards
  - Basic timeline
  - Response display
  
- **Day 14**: Styling and responsiveness
  - SCSS implementation
  - Theme setup
  - Mobile responsiveness

### Week 3: Advanced Features (Days 15-21)
- **Day 15-16**: Tool timeline
  - Timeline visualization
  - Real-time updates
  - Animation
  
- **Day 17-18**: Metrics and analytics
  - Performance tracking
  - Agent statistics
  - Export functionality
  
- **Day 19-20**: Error handling
  - Connection recovery
  - Error boundaries
  - User notifications
  
- **Day 21**: Performance optimization
  - Code splitting
  - Lazy loading
  - Caching

### Week 4: Polish and Deploy (Days 22-28)
- **Day 22-23**: UI/UX improvements
  - Animation polish
  - Loading states
  - Accessibility
  
- **Day 24-25**: Testing
  - Frontend unit tests
  - E2E tests
  - Performance tests
  
- **Day 26-27**: Deployment
  - Docker configuration
  - CI/CD setup
  - Production deployment
  
- **Day 28**: Documentation and handoff
  - User guide
  - Developer documentation
  - Deployment guide

## Testing Strategy

### Backend Testing

#### Unit Tests
```python
# tests/test_services/test_mas_service.py
import pytest
from app.services.mas_service import MASService

@pytest.mark.asyncio
async def test_process_message():
    service = MASService()
    await service.initialize()
    
    response, trace = await service.process_message(
        "What's the weather in London?",
        "test-session"
    )
    
    assert response is not None
    assert trace.agent_responses
    assert any(ar.agent_name == "Weather Agent" for ar in trace.agent_responses)
```

### Frontend Testing

#### Component Tests
```typescript
// tests/ChatInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInterface } from '../components/Chat/ChatInterface';

test('sends message when enter is pressed', () => {
  render(<ChatInterface />);
  
  const input = screen.getByPlaceholderText('Type a message...');
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyPress(input, { key: 'Enter', code: 13 });
  
  expect(screen.getByText('Test message')).toBeInTheDocument();
});
```

### E2E Testing

#### Cypress Tests
```javascript
// cypress/integration/chat.spec.js
describe('Chat Flow', () => {
  it('completes a full chat interaction', () => {
    cy.visit('/');
    cy.get('[data-testid="message-input"]').type('What is the weather in Paris?');
    cy.get('[data-testid="send-button"]').click();
    
    // Wait for response
    cy.get('[data-testid="agent-card"]', { timeout: 10000 }).should('exist');
    cy.get('[data-testid="weather-agent-card"]').should('contain', 'Weather Agent');
    cy.get('[data-testid="tool-timeline"]').should('contain', 'get_current_weather');
  });
});
```

## Success Metrics

### Performance Metrics
- **Response Time**: < 3s for simple queries
- **WebSocket Latency**: < 100ms for updates
- **UI Responsiveness**: 60 FPS animations
- **Connection Recovery**: < 5s reconnection

### User Experience Metrics
- **Tool Visibility**: 100% of tool calls displayed
- **Real-time Updates**: All execution steps shown
- **Error Recovery**: Graceful handling of all errors
- **Mobile Support**: Full functionality on tablets

### Technical Metrics
- **Test Coverage**: > 80% for both frontend and backend
- **Code Quality**: ESLint/Pylint compliance
- **Bundle Size**: < 500KB for initial load
- **Docker Image Size**: < 200MB for each service

## Conclusion

This comprehensive plan provides a complete implementation roadmap for building a sophisticated testing and visualization interface for the Multi-Agent System. The solution offers real-time visibility into agent interactions, tool usage, and response generation, making it an invaluable tool for testing, debugging, and demonstrating the MAS capabilities.

Key deliverables include:
- Fully functional FastAPI backend with MAS integration
- React.js frontend with real-time updates
- WebSocket-based communication for live tracking
- Comprehensive agent and tool visualization
- Production-ready Docker deployment
- Complete testing strategy

The implementation follows modern best practices and provides a scalable, maintainable solution that can grow with the MAS system.