from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Load the nearest .env file (searching upwards), so both repo root and backend/.env work
load_dotenv(find_dotenv(usecwd=True))


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_TITLE: str = "ShipDB API"
    API_VERSION: str = "0.1.0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_FALLBACK_MODEL: Optional[str] = None
    
    # Anthropic (Claude)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    ANTHROPIC_FALLBACK_MODEL: Optional[str] = None
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_DEFAULT_VPC_ID: Optional[str] = None
    
    
    # RDS
    RDS_MASTER_USERNAME: Optional[str] = None
    RDS_MASTER_PASSWORD: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    SUPABASE_DB_URL: Optional[str] = None
    
    # Other
    PASSWORD: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./shipdb.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
