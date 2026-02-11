"""
Application configuration using Pydantic Settings.
"""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "StraRun API"
    DEBUG: bool = False
    SECRET_KEY: str

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]

    # Strava API
    STRAVA_CLIENT_ID: str = ""
    STRAVA_CLIENT_SECRET: str
    STRAVA_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"

    # Database (for future use)
    DATABASE_URL: str = "sqlite:///./strarun.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_secure(cls, value: str) -> str:
        if value.strip() in {
            "change-this-in-production",
            "change-this-to-a-secure-random-string",
            "your_secret_key_here",
        }:
            raise ValueError("SECRET_KEY must be set to a secure, non-placeholder value.")
        return value


settings = Settings()
