"""
Application configuration management.
"""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _API_DIR.parent.parent


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", _API_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database (optional in mock mode)
    DATABASE_URL: str = Field(default="")
    DATABASE_URL_SYNC: str = Field(default="")

    # Redis (optional in mock mode)
    REDIS_URL: str = Field(default="")

    # Reddit API (optional when USE_REDDIT_MOCK)
    REDDIT_CLIENT_ID: str = Field(default="")
    REDDIT_SECRET: str = Field(default="")
    REDDIT_USER_AGENT: str = Field(default="reddit-worry-finder:v0.1.0")

    # Optional LLM
    OPENROUTER_API_KEY: str = Field(default="")

    # App URLs
    APP_BASE_URL: str = Field(default="http://localhost:3000")
    API_BASE_URL: str = Field(default="http://localhost:8000")

    # Development flags — local demo boots with no Postgres, Redis, or Reddit keys
    USE_REDDIT_MOCK: bool = Field(default=True)
    USE_EMBEDDING_MOCK: bool = Field(default=True)
    USE_DB_MOCK: bool = Field(default=True)
    USE_REDIS_MOCK: bool = Field(default=True)

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


settings = Settings()
