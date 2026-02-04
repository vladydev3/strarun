"""
StraRun Backend - FastAPI Application
Main entry point for the Strava Dashboard API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.core.config import settings

app = FastAPI(
    title="StraRun API",
    description="API para el dashboard de Strava con estadísticas y visualizaciones",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "StraRun API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }
