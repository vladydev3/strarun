"""Authentication endpoints for Strava OAuth."""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.models.auth import TokenResponse, AuthStatus, TokenRequest, RefreshTokenRequest
from app.services.strava_auth import StravaAuthService

router = APIRouter()
strava_auth = StravaAuthService()


@router.get("/strava")
async def strava_auth_redirect(request: Request):
    """
    Redirect to Strava authorization page.
    Initiates the OAuth2 flow with Strava.
    """
    if not settings.STRAVA_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Strava client ID not configured. Set STRAVA_CLIENT_ID env variable.",
        )

    auth_url, state = strava_auth.get_authorization_url()
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        "strava_oauth_state",
        state,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/",
    )
    return response


@router.get("/callback", response_model=TokenResponse)
async def strava_callback(
    request: Request,
    response: Response,
    code: str,
    scope: str = "",
    state: str | None = None,
):
    """
    Handle Strava OAuth callback.
    Exchanges authorization code for access tokens.
    """
    stored_state = request.cookies.get("strava_oauth_state")
    if not state or not stored_state or state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")

    try:
        tokens = await strava_auth.exchange_code(code)
        response.delete_cookie("strava_oauth_state")
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
