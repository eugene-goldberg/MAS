from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import json
import asyncio
import uuid
from datetime import datetime

from app.api.dependencies import get_mas_service, get_session_service
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
    mas_service: MASService = Depends(get_mas_service),
    session_service: SessionService = Depends(get_session_service)
):
    await manager.connect(websocket, session_id)
    print(f"WebSocket connected for session: {session_id}")
    
    # Create or get session
    session = await session_service.get_or_create_session(session_id)
    
    # Initialize heartbeat task variable
    heartbeat_task = None
    
    try:
        # Send initial connection message
        try:
            agent_info = await mas_service.get_agent_info()
            await websocket.send_json({
                "type": "connection_established",
                "session_id": session_id,
                "agent_info": agent_info
            })
            print(f"Sent connection_established message for session: {session_id}")
        except Exception as e:
            print(f"Error sending connection_established: {e}")
            raise
        
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
                    with open("debug.log", "a") as f:
                        f.write(f"Processing message: {message_data['content']}\n")
                    
                    response, execution_trace = await mas_service.process_message(
                        message_data["content"],
                        session_id,
                        websocket_callback=websocket.send_json
                    )
                    
                    with open("debug.log", "a") as f:
                        f.write(f"Got response from MAS: {response[:100] if response else 'None'}...\n")
                        f.write(f"Response length: {len(response) if response else 0}\n")
                    
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
                    
                    # Send the agent response to the client
                    print(f"Sending agent response: {response[:100] if response else 'None'}...")
                    await websocket.send_json({
                        "type": "agent_response",
                        "message_id": assistant_message.id,
                        "content": response,
                        "agent_responses": execution_trace.agent_responses
                    })
                    
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
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
        print(f"Client {session_id} disconnected via WebSocketDisconnect")
    except Exception as e:
        print(f"WebSocket error for {session_id}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        manager.disconnect(session_id)
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
        
async def heartbeat(websocket: WebSocket):
    """Send periodic heartbeat to keep connection alive"""
    try:
        while True:
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
            await websocket.send_json({"type": "heartbeat"})
    except Exception:
        pass