"""Statistics models."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Dashboard overview statistics."""

    total_activities: int
    total_distance: float = Field(description="Total distance in kilometers")
    total_time: int = Field(description="Total time in seconds")
    total_elevation: float = Field(description="Total elevation gain in meters")
    this_week_activities: int
    this_week_distance: float
    this_month_activities: int
    this_month_distance: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_activities": 150,
                    "total_distance": 1250.5,
                    "total_time": 180000,
                    "total_elevation": 15000.0,
                    "this_week_activities": 5,
                    "this_week_distance": 45.2,
                    "this_month_activities": 20,
                    "this_month_distance": 180.5,
                }
            ]
        }
    }


class WeeklyStats(BaseModel):
    """Weekly statistics breakdown."""

    weeks: List[Dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "weeks": [
                        {"week": "2024-W03", "distance": 45.2, "time": 14400, "activities": 5},
                        {"week": "2024-W02", "distance": 38.5, "time": 12000, "activities": 4},
                    ]
                }
            ]
        }
    }


class MonthlyStats(BaseModel):
    """Monthly statistics breakdown."""

    months: List[Dict[str, Any]]


class ActivityTypeStats(BaseModel):
    """Statistics grouped by activity type."""

    types: List[Dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "types": [
                        {
                            "type": "Run",
                            "count": 100,
                            "total_distance": 850.0,
                            "total_time": 120000,
                            "average_pace": 5.5,
                        },
                        {
                            "type": "Ride",
                            "count": 40,
                            "total_distance": 350.0,
                            "total_time": 50000,
                            "average_speed": 25.2,
                        },
                    ]
                }
            ]
        }
    }
