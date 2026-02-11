"""Activities endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Header, Cookie

from app.models.activity import Activity, ActivityDetail, ActivitySummary
from app.core.config import settings
from app.services.strava_client import StravaApiClient

router = APIRouter()


def get_access_token(
    authorization: str | None = Header(None),
    access_token: str | None = Cookie(None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
) -> str:
    """Extract access token from cookie or Authorization header."""
    if access_token:
        return access_token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    return authorization[7:]


@router.get("", response_model=List[ActivitySummary])
async def get_activities(
    authorization: str | None = Header(None),
    access_token: str | None = Cookie(None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type (Run, Ride, etc.)"),
    after: Optional[int] = Query(None, description="Unix timestamp - activities after this time"),
    before: Optional[int] = Query(None, description="Unix timestamp - activities before this time"),
):
    """
    Get list of activities.
    Returns paginated list of activity summaries.
    """
    token = get_access_token(authorization, access_token)
    client = StravaApiClient(token)
    
    try:
        activities = await client.get_activities(page=page, per_page=per_page, before=before, after=after)
        
        result = []
        for a in activities:
            # Filter by type if specified
            if activity_type and a.get("type") != activity_type:
                continue
                
            result.append(ActivitySummary(
                id=a["id"],
                name=a.get("name", "Untitled"),
                type=a.get("type", "Unknown"),
                distance=a.get("distance", 0.0),
                moving_time=a.get("moving_time", 0),
                elapsed_time=a.get("elapsed_time", 0),
                total_elevation_gain=a.get("total_elevation_gain", 0.0),
                start_date=a.get("start_date", ""),
                average_speed=a.get("average_speed", 0.0),
                max_speed=a.get("max_speed", 0.0),
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{activity_id}", response_model=ActivityDetail)
async def get_activity(
    activity_id: int,
    authorization: str | None = Header(None),
    access_token: str | None = Cookie(None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
):
    """
    Get detailed activity by ID.
    Returns full activity details including segments and streams.
    """
    token = get_access_token(authorization, access_token)
    client = StravaApiClient(token)
    
    try:
        a = await client.get_activity(activity_id)
        
        return ActivityDetail(
            id=a["id"],
            name=a.get("name", "Untitled"),
            type=a.get("type", "Unknown"),
            sport_type=a.get("sport_type", a.get("type", "Unknown")),
            distance=a.get("distance", 0.0),
            moving_time=a.get("moving_time", 0),
            elapsed_time=a.get("elapsed_time", 0),
            total_elevation_gain=a.get("total_elevation_gain", 0.0),
            start_date=a.get("start_date", ""),
            start_date_local=a.get("start_date_local", ""),
            timezone=a.get("timezone", ""),
            average_speed=a.get("average_speed", 0.0),
            max_speed=a.get("max_speed", 0.0),
            average_heartrate=a.get("average_heartrate"),
            max_heartrate=a.get("max_heartrate"),
            calories=a.get("calories"),
            description=a.get("description"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{activity_id}/laps")
async def get_activity_laps(
    activity_id: int,
    authorization: str | None = Header(None),
    access_token: str | None = Cookie(None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
):
    """
    Get activity laps.
    Returns the laps of an activity.
    """
    token = get_access_token(authorization, access_token)
    client = StravaApiClient(token)
    
    try:
        laps = await client.get_activity_laps(activity_id)
        return laps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{activity_id}/streams")
async def get_activity_streams(
    activity_id: int,
    authorization: str | None = Header(None),
    access_token: str | None = Cookie(None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
    keys: str = Query("time,distance,heartrate,altitude", description="Comma-separated stream types"),
):
    """
    Get activity streams (time-series data).
    Returns GPS, heartrate, altitude, and other data streams.
    """
    token = get_access_token(authorization, access_token)
    client = StravaApiClient(token)
    
    try:
        requested_keys = keys.split(",")
        streams_data = await client.get_activity_streams(activity_id, requested_keys)
        
        streams = {}
        for stream in streams_data:
            stream_type = stream.get("type")
            if stream_type:
                streams[stream_type] = stream.get("data", [])

        return {
            "activity_id": activity_id,
            "streams": streams,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
