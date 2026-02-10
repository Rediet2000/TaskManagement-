from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Base paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    LOGOS_DIR: str = os.path.join(STATIC_DIR, "logos")

    PROJECT_NAME: str = "TaskManagement API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/taskmanagement"
    
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Initial Setup
    FIRST_SUPERADMIN_EMAIL: str = "admin@system.com"
    FIRST_SUPERADMIN_PASSWORD: str = "12345"
    FIRST_ALLOWED_DOMAIN: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
