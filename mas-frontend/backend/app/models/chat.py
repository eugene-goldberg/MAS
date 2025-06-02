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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    execution_trace: 'ExecutionTrace'
    session_id: str

# Forward reference for ExecutionTrace
from .tracking import ExecutionTrace
ChatResponse.model_rebuild()