from pydantic_settings import BaseSettings
from typing import Optional, List


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
    
    # AI Service Configuration
    anthropic_api_key: Optional[str] = None  # New fallback option
    ai_provider: str = "anthropic"  # Primary provider
    ai_model: str = "claude-3-5-sonnet-20241022"  # Default model
    ai_max_tokens: int = 4000  # Response limit
    ai_temperature: float = 0.3  # Consistency over creativity
    ai_timeout_seconds: int = 120  # Request timeout
    
    # Baseline Generation Settings
    baseline_max_documents: int = 10  # Limit documents per baseline
    baseline_max_text_length: int = 50000  # Character limit for analysis
    baseline_prompt_version: str = "v1.0"  # For tracking prompt iterations
    
    # API
    api_v1_str: str = "/api/v1"
    frontend_url: str = "http://localhost:3000"
    
    # Beta Access Control
    coach_whitelist_emails: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def coach_whitelist_emails_list(self) -> List[str]:
        """Convert comma-separated email string to list"""
        if not self.coach_whitelist_emails:
            return []
        return [email.strip().lower() for email in self.coach_whitelist_emails.split(",") if email.strip()]


settings = Settings()