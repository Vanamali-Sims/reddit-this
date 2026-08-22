"""
Database configuration and session management.
"""

from typing import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


async_engine = None
sync_engine = None
AsyncSessionLocal = None
SessionLocal = None

if not settings.USE_DB_MOCK:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import sessionmaker

    if not settings.DATABASE_URL or not settings.DATABASE_URL_SYNC:
        raise RuntimeError(
            "DATABASE_URL and DATABASE_URL_SYNC are required when USE_DB_MOCK=false"
        )

    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

    sync_engine = create_engine(
        settings.DATABASE_URL_SYNC,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    SessionLocal = sessionmaker(
        sync_engine,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator:
    """Dependency to get database session."""
    if settings.USE_DB_MOCK or AsyncSessionLocal is None:
        raise RuntimeError("Database is disabled (USE_DB_MOCK=true)")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    if settings.USE_DB_MOCK or async_engine is None:
        return

    from models import subreddit, post, alert, notification  # noqa: F401

    if settings.DEBUG:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
