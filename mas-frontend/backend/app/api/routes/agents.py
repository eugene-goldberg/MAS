from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.api.dependencies import get_mas_service, get_tracking_service
from app.services.mas_service import MASService
from app.services.tracking_service import TrackingService

router = APIRouter()

@router.get("/info")
async def get_agent_info(mas_service: MASService = Depends(get_mas_service)) -> Dict[str, Any]:
    """Get information about available agents and their capabilities"""
    return await mas_service.get_agent_info()

@router.get("/metrics")
async def get_agent_metrics(tracking_service: TrackingService = Depends(get_tracking_service)) -> Dict[str, Any]:
    """Get performance metrics for all agents"""
    return await tracking_service.get_agent_metrics()

@router.get("/tools")
async def get_tool_usage(tracking_service: TrackingService = Depends(get_tracking_service)) -> Dict[str, int]:
    """Get tool usage statistics"""
    return await tracking_service.get_tool_usage_stats()