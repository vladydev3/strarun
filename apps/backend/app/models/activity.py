"""Activity models."""

from typing import Optional, List
from pydantic import BaseModel, Field


class ActivitySummary(BaseModel):
    """Summary model for activity list."""

    id: int
    name: str
    type: str
    distance: float = Field(description="Distance in meters")
    moving_time: int = Field(description="Moving time in seconds")
    elapsed_time: int = Field(description="Total elapsed time in seconds")
    total_elevation_gain: float = Field(description="Elevation gain in meters")
    start_date: str = Field(description="ISO 8601 datetime string")
    average_speed: float = Field(description="Average speed in m/s")
    max_speed: float = Field(description="Max speed in m/s")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 12345678,
                    "name": "Morning Run",
                    "type": "Run",
                    "distance": 5000.0,
                    "moving_time": 1800,
                    "elapsed_time": 1850,
                    "total_elevation_gain": 50.0,
                    "start_date": "2024-01-15T08:00:00Z",
                    "average_speed": 2.78,
                    "max_speed": 4.5,
                }
            ]
        }
    }


class ActivityDetail(BaseModel):
    """Detailed activity model."""

    id: int
    name: str
    type: str
    sport_type: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    start_date: str
    start_date_local: str
    timezone: str
    average_speed: float
    max_speed: float
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[int] = None
    calories: Optional[float] = None
    description: Optional[str] = None
    average_cadence: Optional[float] = None
    average_watts: Optional[float] = None
    kilojoules: Optional[float] = None


class Activity(BaseModel):
    """Full activity model including all fields."""

    id: int
    name: str
    type: str
    sport_type: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    elev_high: Optional[float] = None
    elev_low: Optional[float] = None
    start_date: str
    start_date_local: str
    timezone: str
    utc_offset: Optional[float] = None
    start_latlng: Optional[List[float]] = None
    end_latlng: Optional[List[float]] = None
    achievement_count: Optional[int] = None
    kudos_count: Optional[int] = None
    comment_count: Optional[int] = None
    athlete_count: Optional[int] = None
    photo_count: Optional[int] = None
    map_id: Optional[str] = None
    map_polyline: Optional[str] = None
    map_summary_polyline: Optional[str] = None
    trainer: bool = False
    commute: bool = False
    manual: bool = False
    private: bool = False
    average_speed: float
    max_speed: float
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[int] = None
    average_cadence: Optional[float] = None
    average_watts: Optional[float] = None
    weighted_average_watts: Optional[int] = None
    kilojoules: Optional[float] = None
    device_watts: Optional[bool] = None
    has_heartrate: bool = False
    calories: Optional[float] = None
    description: Optional[str] = None
    gear_id: Optional[str] = None
