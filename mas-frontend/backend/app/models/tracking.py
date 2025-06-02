from pydantic import BaseModel, Field
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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }