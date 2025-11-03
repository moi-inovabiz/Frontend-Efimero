"""
Configuration settings for Frontend Efímero API
Siguiendo las mejores prácticas de FastAPI
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App Configuration
    APP_NAME: str = "Frontend Efímero API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-for-testing-only"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-for-testing-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./frontend_efimero.db"  # SQLite for dev
    # For production PostgreSQL: "postgresql+asyncpg://user:password@localhost:5432/frontend_efimero"
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "test_credentials.json"
    FIREBASE_PROJECT_ID: str = "test-frontend-efimero"
    
    # ML Models Configuration
    MODELS_PATH: str = "models"
    # Modelos duales (preferidos)
    CLASSIFIER_MODEL_NAME: str = "xgboost_classifier_dual.joblib"
    REGRESSOR_MODEL_NAME: str = "xgboost_regressor_dual.joblib"
    SCALER_MODEL_NAME: str = "feature_scaler_dual.joblib"
    # Modelos individuales (fallback)
    CLASSIFIER_INDIVIDUAL_NAME: str = "xgboost_classifier.joblib"
    REGRESSOR_INDIVIDUAL_NAME: str = "xgboost_regressor.joblib"
    SCALER_INDIVIDUAL_NAME: str = "feature_scaler.joblib"
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = 100
    MODEL_CACHE_SIZE: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()