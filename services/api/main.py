"""
Reddit Worry Finder API

FastAPI application for semantic Reddit search and post drafting.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.db import init_db
from routes import health, search, draft, alerts


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Reddit Worry Finder API",
    description="Semantic Reddit search and post drafting API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(search.router, prefix="/v1", tags=["search"])
app.include_router(draft.router, prefix="/v1", tags=["draft"])
app.include_router(alerts.router, prefix="/v1", tags=["alerts"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Reddit Worry Finder API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
