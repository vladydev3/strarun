"""Authentication endpoints for Strava OAuth."""

import secrets
import time

from fastapi import APIRouter, HTTPException, Response, Cookie, Header
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.models.auth import (
    TokenResponse,
    AuthStatus,
    TokenRequest,
    RefreshTokenRequest,
    StravaAthlete,
)
from app.services.strava_auth import StravaAuthService
from app.services.strava_client import StravaApiClient

router = APIRouter()
strava_auth = StravaAuthService()


@router.get("/strava")
async def strava_auth_redirect():
    """
    Get Strava authorization URL.
    Returns the URL for frontend to redirect user to Strava OAuth page.
    """
    if not settings.STRAVA_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Strava client ID not configured. Set STRAVA_CLIENT_ID env variable.",
        )

    auth_url, state = strava_auth.get_authorization_url()
    return {"auth_url": auth_url, "state": state}


def _set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    access_max_age = max(tokens.expires_at - int(time.time()), 0)
    refresh_max_age = settings.REFRESH_COOKIE_MAX_AGE_DAYS * 24 * 60 * 60

    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=tokens.access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=access_max_age,
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=refresh_max_age,
    )
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=secrets.token_urlsafe(32),
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=refresh_max_age,
    )


@router.get("/status", response_model=AuthStatus)
async def auth_status(
    access_token: str | None = Cookie(None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
    refresh_token: str | None = Cookie(None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
):
    """
    Check current authentication status.
    Returns whether the user is authenticated with Strava.
    """
    if not access_token:
        # Check if refresh token is available
        if refresh_token:
            return AuthStatus(
                authenticated=False,
                strava_connected=False,
                message="Access token expired; refresh available",
                refresh_available=True,
            )
        return AuthStatus(
            authenticated=False,
            strava_connected=False,
            message="Not authenticated",
            refresh_available=False,
        )

    try:
        client = StravaApiClient(access_token)
        athlete = await client.get_athlete()
        athlete_name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip()
        athlete_profile = StravaAthlete(
            id=athlete.get("id", 0),
            firstname=athlete.get("firstname", ""),
            lastname=athlete.get("lastname", ""),
            profile=athlete.get("profile"),
            profile_medium=athlete.get("profile_medium"),
            city=athlete.get("city"),
            state=athlete.get("state"),
            country=athlete.get("country"),
        )
        return AuthStatus(
            authenticated=True,
            strava_connected=True,
            message="Authenticated",
            refresh_available=None,
            athlete_name=athlete_name or None,
            athlete=athlete_profile,
        )
    except Exception:
        # Access token invalid; check if refresh is available
        if refresh_token:
            return AuthStatus(
                authenticated=False,
                strava_connected=False,
                message="Access token expired; refresh available",
                refresh_available=True,
            )
        return AuthStatus(
            authenticated=False,
            strava_connected=False,
            message="Not authenticated",
            refresh_available=False,
        )


@router.post("/token", response_model=TokenResponse)
async def exchange_token(request: TokenRequest, response: Response):
    """
    Exchange authorization code for tokens.
    Called by frontend after OAuth callback.
    """
    try:
        tokens = await strava_auth.exchange_code(request.code)
        _set_auth_cookies(response, tokens)
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    request: RefreshTokenRequest | None = None,
    refresh_token_cookie: str | None = Cookie(None, alias=settings.REFRESH_TOKEN_COOKIE_NAME),
    csrf_header: str | None = Header(None, alias="X-CSRF-Token"),
    csrf_cookie: str | None = Cookie(None, alias=settings.CSRF_COOKIE_NAME),
):
    """
    Refresh expired access token.
    """
    try:
        refresh_token = request.refresh_token if request else None
        if refresh_token_cookie:
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                raise HTTPException(status_code=403, detail="Missing or invalid CSRF token")
            refresh_token = refresh_token_cookie
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        tokens = await strava_auth.refresh_tokens(refresh_token)
        
        # Fetch athlete information to include in the refresh response
        try:
            client = StravaApiClient(tokens.access_token)
            athlete = await client.get_athlete()
            tokens.athlete = StravaAthlete(
                id=athlete.get("id", 0),
                firstname=athlete.get("firstname", ""),
                lastname=athlete.get("lastname", ""),
                profile=athlete.get("profile"),
                profile_medium=athlete.get("profile_medium"),
                city=athlete.get("city"),
                state=athlete.get("state"),
                country=athlete.get("country"),
            )
        except Exception:
            # If fetching athlete fails, proceed without athlete data
            pass
        
        _set_auth_cookies(response, tokens)
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
