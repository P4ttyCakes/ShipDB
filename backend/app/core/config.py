from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_TITLE: str = "ShipDB API"
    API_VERSION: str = "0.1.0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # Claude AI
    CLAUDE_API_KEY: Optional[str] = None
    
    # Other
    PASSWORD: Optional[str] = None
    
    # AWS Additional Settings
    AWS_DEFAULT_VPC_ID: Optional[str] = None  # For RDS security group
    RDS_MASTER_USERNAME: str = "shipdb_admin"
    RDS_MASTER_PASSWORD: str = "ShipDB_temp_pass_123!"  # Generated per deployment
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./shipdb.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
