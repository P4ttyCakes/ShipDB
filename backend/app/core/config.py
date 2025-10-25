from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_TITLE: str = "ShipDB API"
    API_VERSION: str = "0.1.0"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./shipdb.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
