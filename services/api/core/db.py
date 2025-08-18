"""
Database configuration and session management.
"""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Async engine for normal operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Sync engine for Alembic migrations
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    # Import all models to ensure they are registered
    from models import subreddit, post, alert, notification  # noqa: F401

    # Create tables (in production, use Alembic migrations)
    if settings.DEBUG:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
