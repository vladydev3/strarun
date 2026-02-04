"""Strava API Client Service with rate limiting."""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx

from app.core.config import settings


class RateLimiter:
    """Simple rate limiter for Strava API."""
    
    def __init__(self, requests_per_15min: int = 100, requests_per_day: int = 1000):
        self.requests_per_15min = requests_per_15min
        self.requests_per_day = requests_per_day
        self.requests_15min: List[datetime] = []
        self.requests_day: List[datetime] = []
    
    async def acquire(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = datetime.now()
        
        # Clean old requests
        cutoff_15min = now - timedelta(minutes=15)
        cutoff_day = now - timedelta(days=1)
        self.requests_15min = [t for t in self.requests_15min if t > cutoff_15min]
        self.requests_day = [t for t in self.requests_day if t > cutoff_day]
        
        # Check limits
        if len(self.requests_15min) >= self.requests_per_15min:
            wait_time = (self.requests_15min[0] - cutoff_15min).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time + 1)
        
        if len(self.requests_day) >= self.requests_per_day:
            wait_time = (self.requests_day[0] - cutoff_day).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time + 1)
        
        # Record request
        self.requests_15min.append(now)
        self.requests_day.append(now)


class StravaApiClient:
    """Client for Strava API v3 with rate limiting."""
    
    BASE_URL = "https://www.strava.com/api/v3"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.rate_limiter = RateLimiter()
    
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Any:
        """Make rate-limited request to Strava API."""
        await self.rate_limiter.acquire()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self._headers(),
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        return await self._request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return await self._request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        return await self._request("PUT", endpoint, data=data)
    
    # Athlete Endpoints
    async def get_athlete(self) -> Dict[str, Any]:
        """GET /athlete - Get authenticated athlete profile."""
        return await self.get("/athlete")
    
    async def get_athlete_zones(self) -> Dict[str, Any]:
        """GET /athlete/zones - Get heart rate and power zones."""
        return await self.get("/athlete/zones")
    
    async def get_athlete_stats(self, athlete_id: int) -> Dict[str, Any]:
        """GET /athletes/{id}/stats - Get athlete stats."""
        return await self.get(f"/athletes/{athlete_id}/stats")
    
    # Activities Endpoints
    async def get_activities(
        self,
        page: int = 1,
        per_page: int = 30,
        before: Optional[int] = None,
        after: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """GET /athlete/activities - List athlete activities."""
        params = {"page": page, "per_page": per_page}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return await self.get("/athlete/activities", params=params)
    
    async def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> Dict[str, Any]:
        """GET /activities/{id} - Get activity details."""
        params = {"include_all_efforts": include_all_efforts}
        return await self.get(f"/activities/{activity_id}", params=params)
    
    async def get_activity_streams(
        self, 
        activity_id: int, 
        keys: List[str],
        key_by_type: bool = True
    ) -> Dict[str, Any]:
        """GET /activities/{id}/streams - Get activity streams (GPS, HR, etc)."""
        params = {
            "keys": ",".join(keys),
            "key_by_type": key_by_type
        }
        return await self.get(f"/activities/{activity_id}/streams", params=params)
    
    async def get_activity_laps(self, activity_id: int) -> List[Dict[str, Any]]:
        """GET /activities/{id}/laps - Get activity laps."""
        return await self.get(f"/activities/{activity_id}/laps")
    
    # Segments Endpoints
    async def get_segment(self, segment_id: int) -> Dict[str, Any]:
        """GET /segments/{id} - Get segment details."""
        return await self.get(f"/segments/{segment_id}")
    
    async def get_starred_segments(self, page: int = 1, per_page: int = 30) -> List[Dict[str, Any]]:
        """GET /segments/starred - Get starred segments."""
        return await self.get("/segments/starred", params={"page": page, "per_page": per_page})
