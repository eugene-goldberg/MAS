from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.api.dependencies import get_mas_service, get_session_service
from app.services.mas_service import MASService
from app.services.session_service import SessionService

router = APIRouter()

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    mas_service: MASService = Depends(get_mas_service),
    session_service: SessionService = Depends(get_session_service)
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
    session_service: SessionService = Depends(get_session_service)
):
    """Get chat history for a session"""
    messages = await session_service.get_messages(session_id, limit)
    return messages

@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Clear chat history for a session"""
    await session_service.clear_messages(session_id)
    return {"message": "Chat history cleared"}