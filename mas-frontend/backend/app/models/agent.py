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
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentResponse(BaseModel):
    agent_name: str
    agent_type: str
    response: str
    tools_used: List[ToolCall]
    processing_time_ms: float
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentInfo(BaseModel):
    name: str
    type: str
    description: str
    tools: List[str]
    color: str
    icon: str
    model: Optional[str] = None