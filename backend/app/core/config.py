import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017/cognivigil_ai"
    database_name: str = "cognivigil_ai"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Admin Credentials
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    # AI Engine Configuration
    ai_engine_url: str = "http://localhost:8001"
    detection_confidence_threshold: float = 0.5
    risk_threshold_high: int = 75
    risk_threshold_medium: int = 50
    
    # File Storage
    evidence_storage_path: str = "./evidence"
    max_file_size: int = 10485760  # 10MB
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Application
    app_name: str = "Cognivigil AI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


settings = Settings()