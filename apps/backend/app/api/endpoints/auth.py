"""Authentication endpoints for Strava OAuth."""

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.auth import TokenResponse, AuthStatus, TokenRequest, RefreshTokenRequest
from app.services.strava_auth import StravaAuthService

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


@router.get("/status", response_model=AuthStatus)
async def auth_status():
    """
    Check current authentication status.
    Returns whether the user is authenticated with Strava.
    """
    # TODO: Implement actual auth status check
    return AuthStatus(
        authenticated=False,
        strava_connected=False,
        message="Not authenticated",
    )


@router.post("/token", response_model=TokenResponse)
async def exchange_token(request: TokenRequest):
    """
    Exchange authorization code for tokens.
    Called by frontend after OAuth callback.
    """
    try:
        tokens = await strava_auth.exchange_code(request.code)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh expired access token.
    """
    try:
        tokens = await strava_auth.refresh_tokens(request.refresh_token)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
