from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.models.session import Session
from app.api.dependencies import get_session_service
from app.services.session_service import SessionService

router = APIRouter()

@router.get("/active", response_model=List[Session])
async def list_active_sessions(
    session_service: SessionService = Depends(get_session_service)
):
    """List all active sessions"""
    return await session_service.list_active_sessions()

@router.get("/{session_id}", response_model=Optional[Session])
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Get session details"""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/create")
async def create_session(
    session_service: SessionService = Depends(get_session_service)
):
    """Create a new session"""
    session = await session_service.get_or_create_session()
    return {"session_id": session.id, "created_at": session.created_at}