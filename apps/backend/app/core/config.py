"""
Application configuration using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "StraRun API"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]

    # Strava API
    STRAVA_CLIENT_ID: str = ""
    STRAVA_CLIENT_SECRET: str = ""
    STRAVA_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"

    # Database (for future use)
    DATABASE_URL: str = "sqlite:///./strarun.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
