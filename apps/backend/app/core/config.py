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
    STRAVA_REDIRECT_URI: str = "http://localhost:4200/auth/callback"

    # Auth cookies
    ACCESS_TOKEN_COOKIE_NAME: str = "strava_access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "strava_refresh_token"
    CSRF_COOKIE_NAME: str = "strava_csrf"
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    REFRESH_COOKIE_MAX_AGE_DAYS: int = 30

    # Database (for future use)
    DATABASE_URL: str = "sqlite:///./strarun.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
