from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .chat import ChatMessage
from .tracking import ExecutionTrace

class Session(BaseModel):
    id: str
    created_at: datetime
    last_activity: datetime
    user_id: Optional[str] = None
    messages: List[ChatMessage] = []
    execution_traces: List[ExecutionTrace] = []
    is_active: bool = True