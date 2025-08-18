"""
Application configuration management.
"""

import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database
    DATABASE_URL: str = Field(...)
    DATABASE_URL_SYNC: str = Field(...)

    # Redis
    REDIS_URL: str = Field(...)

    # Reddit API
    REDDIT_CLIENT_ID: str = Field(...)
    REDDIT_SECRET: str = Field(...)
    REDDIT_USER_AGENT: str = Field(default="reddit-worry-finder:v0.1.0")

    # Optional LLM
    OPENROUTER_API_KEY: str = Field(default="")

    # App URLs
    APP_BASE_URL: str = Field(default="http://localhost:3000")
    API_BASE_URL: str = Field(default="http://localhost:8000")

    # Development flags
    USE_REDDIT_MOCK: bool = Field(default=True)
    USE_EMBEDDING_MOCK: bool = Field(default=False)

    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_BURST: int = Field(default=10)

    # Search configuration
    MAX_SUBREDDITS_TO_SEARCH: int = Field(default=10)
    MAX_POSTS_PER_SUBREDDIT: int = Field(default=20)
    EMBEDDING_DIMENSION: int = Field(default=384)

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
