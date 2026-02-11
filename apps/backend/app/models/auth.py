"""Authentication models."""

from typing import Optional
from pydantic import BaseModel


class TokenRequest(BaseModel):
    """Request model for token exchange."""
    code: str


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: Optional[str] = None


class StravaAthlete(BaseModel):
    """Strava athlete profile."""

    id: int
    firstname: str
    lastname: str
    profile: Optional[str] = None
    profile_medium: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class TokenResponse(BaseModel):
    """Response model for OAuth token exchange."""

    access_token: str
    refresh_token: str
    expires_at: int
    token_type: str = "Bearer"
    athlete: Optional[StravaAthlete] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "abc123...",
                    "refresh_token": "xyz789...",
                    "expires_at": 1704067200,
                    "token_type": "Bearer",
                    "athlete": {
                        "id": 12345,
                        "firstname": "John",
                        "lastname": "Doe"
                    },
                }
            ]
        }
    }


class AuthStatus(BaseModel):
    """Authentication status response."""

    authenticated: bool
    strava_connected: bool
    message: str
    refresh_available: Optional[bool] = None
    athlete_name: Optional[str] = None
    athlete: Optional[StravaAthlete] = None
