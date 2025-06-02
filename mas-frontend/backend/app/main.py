from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime
import os
import vertexai

from app.api.routes import chat, agents, sessions, websocket, test
from app.core.config import settings
from app.services.session_service import SessionService
from app.services.mas_service import MASService
from app.services.tracking_service import TrackingService
from app.api.dependencies import init_services

# Initialize Vertex AI at module level, just like test_local.py
project = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project, location=location)

# Initialize services
session_service = SessionService()
mas_service = MASService()
tracking_service = TrackingService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting MAS Frontend API...")
    await mas_service.initialize()
    # Initialize dependency injection
    init_services(mas_service, session_service, tracking_service)
    yield
    # Shutdown
    print("Shutting down MAS Frontend API...")
    await mas_service.cleanup()

app = FastAPI(
    title="MAS Testing Interface",
    description="Real-time testing and visualization for Multi-Agent System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(test.router, prefix="/api/test", tags=["testing"])

@app.get("/")
async def root():
    return {
        "message": "MAS Testing Interface API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mas_connected": await mas_service.check_connection()
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint for development"""
    return {
        "message": "MAS Testing Interface is running",
        "timestamp": datetime.now().isoformat(),
        "agents": [
            "Weather Agent",
            "RAG Agent", 
            "Academic WebSearch",
            "Academic NewResearch",
            "Greeter Agent"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )