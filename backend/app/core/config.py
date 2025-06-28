from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    database_name: str = "arete_mvp"
    
    # Clerk
    clerk_secret_key: str
    clerk_webhook_secret: str
    
    # External Services
    sendgrid_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # API
    api_v1_str: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()