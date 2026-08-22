"""Health check endpoints."""

from fastapi import APIRouter

from core.config import settings

router = APIRouter()


@router.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "reddit-worry-finder-api",
        "version": "0.1.0",
        "mock": {
            "reddit": settings.USE_REDDIT_MOCK,
            "embeddings": settings.USE_EMBEDDING_MOCK,
            "db": settings.USE_DB_MOCK,
            "redis": settings.USE_REDIS_MOCK,
        },
    }
