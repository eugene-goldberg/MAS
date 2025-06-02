"""Shared dependencies for API routes"""

from typing import Generator
from app.services.mas_service import MASService
from app.services.session_service import SessionService
from app.services.tracking_service import TrackingService

# Singleton instances - initialized in main.py
_mas_service = None
_session_service = None
_tracking_service = None

def init_services(mas_service: MASService, session_service: SessionService, tracking_service: TrackingService):
    """Initialize service instances"""
    global _mas_service, _session_service, _tracking_service
    _mas_service = mas_service
    _session_service = session_service
    _tracking_service = tracking_service

def get_mas_service() -> MASService:
    """Get MAS service instance"""
    if _mas_service is None:
        raise RuntimeError("MAS service not initialized")
    return _mas_service

def get_session_service() -> SessionService:
    """Get session service instance"""
    if _session_service is None:
        raise RuntimeError("Session service not initialized")
    return _session_service

def get_tracking_service() -> TrackingService:
    """Get tracking service instance"""
    if _tracking_service is None:
        raise RuntimeError("Tracking service not initialized")
    return _tracking_service