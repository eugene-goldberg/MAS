from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from app.models.session import Session
from app.models.chat import ChatMessage
from app.models.tracking import ExecutionTrace
from app.core.config import settings

class SessionService:
    """Service for managing user sessions and chat history"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        
    async def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get existing session or create new one"""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        if session_id in self.sessions:
            # Update last activity
            self.sessions[session_id].last_activity = datetime.now()
            return self.sessions[session_id]
            
        # Create new session
        session = Session(
            id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        
        # Cleanup old sessions
        await self._cleanup_old_sessions()
        
        return session
        
    async def add_message(self, session_id: str, message: ChatMessage):
        """Add a message to session history"""
        if session_id in self.sessions:
            self.sessions[session_id].messages.append(message)
            self.sessions[session_id].last_activity = datetime.now()
            
    async def add_execution_trace(self, session_id: str, trace: ExecutionTrace):
        """Add execution trace to session"""
        if session_id in self.sessions:
            self.sessions[session_id].execution_traces.append(trace)
            
    async def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat messages for a session"""
        if session_id in self.sessions:
            messages = self.sessions[session_id].messages
            return messages[-limit:] if len(messages) > limit else messages
        return []
        
    async def clear_messages(self, session_id: str):
        """Clear chat history for a session"""
        if session_id in self.sessions:
            self.sessions[session_id].messages = []
            self.sessions[session_id].execution_traces = []
            
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self.sessions.get(session_id)
        
    async def list_active_sessions(self) -> List[Session]:
        """List all active sessions"""
        await self._cleanup_old_sessions()
        return list(self.sessions.values())
        
    async def _cleanup_old_sessions(self):
        """Remove sessions older than timeout"""
        cutoff_time = datetime.now() - timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        
        sessions_to_remove = [
            session_id 
            for session_id, session in self.sessions.items()
            if session.last_activity < cutoff_time
        ]
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]