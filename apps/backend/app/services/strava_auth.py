"""Strava Authentication Service."""

import secrets
from typing import Optional

import httpx

from app.core.config import settings
from app.models.auth import TokenResponse, StravaAthlete


class StravaAuthService:
    """Service for handling Strava OAuth2 authentication."""

    AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
    TOKEN_URL = "https://www.strava.com/oauth/token"

    def __init__(self):
        self.client_id = settings.STRAVA_CLIENT_ID
        self.client_secret = settings.STRAVA_CLIENT_SECRET
        self.redirect_uri = settings.STRAVA_REDIRECT_URI

    def get_authorization_url(
        self,
        scope: str = "read,activity:read_all",
        approval_prompt: str = "auto",
        state: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Generate Strava authorization URL.

        Args:
            scope: Comma-separated list of permissions
            approval_prompt: 'auto' or 'force'
            state: Optional OAuth state (generated if not provided)

        Returns:
            Tuple with authorization URL and state value
        """
        oauth_state = state or secrets.token_urlsafe(32)
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "approval_prompt": approval_prompt,
            "scope": scope,
            "state": oauth_state,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZE_URL}?{query_string}", oauth_state

    async def exchange_code(self, authorization_code: str) -> TokenResponse:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            authorization_code: Code received from OAuth callback

        Returns:
            TokenResponse with access_token, refresh_token, expires_at
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": authorization_code,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            data = response.json()

            athlete_data = data.get("athlete", {})
            athlete = StravaAthlete(
                id=athlete_data.get("id", 0),
                firstname=athlete_data.get("firstname", ""),
                lastname=athlete_data.get("lastname", ""),
                profile=athlete_data.get("profile"),
                profile_medium=athlete_data.get("profile_medium"),
                city=athlete_data.get("city"),
                state=athlete_data.get("state"),
                country=athlete_data.get("country"),
            ) if athlete_data else None

            return TokenResponse(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=data["expires_at"],
                athlete=athlete,
            )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """
        Refresh expired access token.

        Args:
            refresh_token: Current refresh token

        Returns:
            TokenResponse with new tokens
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()

            return TokenResponse(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=data["expires_at"],
            )
