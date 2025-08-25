from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    S3_BUCKET_PREFIX: str = "recaplab"
    
    # Application Configuration
    APP_NAME: str = "RecapLab"
    DEBUG: bool = False
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_FORMATS: list = ["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm"]
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Redis Configuration (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()