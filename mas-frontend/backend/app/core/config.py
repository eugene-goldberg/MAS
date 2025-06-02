from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "MAS Testing Interface"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # MAS Integration
    MAS_PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    MAS_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    MAS_AGENT_ID: str = os.getenv("MAS_AGENT_ID", "")
    
    # Session Settings
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_SESSIONS_PER_USER: int = 5
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    # Export Settings
    EXPORT_MAX_MESSAGES: int = 1000
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()