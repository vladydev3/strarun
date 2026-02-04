"""Statistics endpoints."""

from typing import Optional
from fastapi import APIRouter, Query, Header, HTTPException

from app.models.stats import (
    DashboardStats,
    WeeklyStats,
    MonthlyStats,
    ActivityTypeStats,
)
from app.services.strava_client import StravaApiClient

router = APIRouter()


def get_access_token(authorization: str = Header(None)) -> str:
    """Extract access token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    return authorization[7:]


@router.get("/{athlete_id}")
async def get_athlete_stats(
    athlete_id: int,
    authorization: str = Header(None),
):
    """
    Get athlete statistics from Strava.
    Returns aggregated stats for the athlete.
    """
    access_token = get_access_token(authorization)
    client = StravaApiClient(access_token)
    
    try:
        stats = await client.get_athlete_stats(athlete_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(
    authorization: str = Header(None),
):
    """
    Get general dashboard statistics.
    Returns aggregated stats for the dashboard overview.
    """
    access_token = get_access_token(authorization)
    client = StravaApiClient(access_token)
    
    try:
        # Get athlete to find ID
        athlete = await client.get_athlete()
        athlete_id = athlete.get("id")
        
        if not athlete_id:
            raise HTTPException(status_code=400, detail="Could not determine athlete ID")
        
        stats = await client.get_athlete_stats(athlete_id)
        
        run_ytd = stats.get("ytd_run_totals", {})
        ride_ytd = stats.get("ytd_ride_totals", {})
        run_recent = stats.get("recent_run_totals", {})
        ride_recent = stats.get("recent_ride_totals", {})
        
        return DashboardStats(
            total_activities=run_ytd.get("count", 0) + ride_ytd.get("count", 0),
            total_distance=(run_ytd.get("distance", 0) + ride_ytd.get("distance", 0)) / 1000,
            total_time=run_ytd.get("moving_time", 0) + ride_ytd.get("moving_time", 0),
            total_elevation=run_ytd.get("elevation_gain", 0) + ride_ytd.get("elevation_gain", 0),
            this_week_activities=run_recent.get("count", 0) + ride_recent.get("count", 0),
            this_week_distance=(run_recent.get("distance", 0) + ride_recent.get("distance", 0)) / 1000,
            this_month_activities=0,
            this_month_distance=0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
