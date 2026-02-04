"""API Router - Combines all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import health, auth, activities, stats

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(activities.router, prefix="/activities", tags=["Activities"])
router.include_router(stats.router, prefix="/stats", tags=["Statistics"])
