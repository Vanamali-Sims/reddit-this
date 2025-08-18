"""
Redis client and rate limiting utilities.
"""

import json
from typing import Any, Optional

import redis.asyncio as redis

from core.config import settings

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RateLimiter:
    """Simple Redis-based rate limiter."""

    def __init__(self, client: redis.Redis):
        self.client = client

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
    ) -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier (e.g., IP address, user ID)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        current_count = await self.client.incr(f"rate_limit:{key}")
        if current_count == 1:
            await self.client.expire(f"rate_limit:{key}", window_seconds)

        return current_count <= limit


# Global rate limiter instance
rate_limiter = RateLimiter(redis_client)


class Cache:
    """Simple Redis-based cache."""

    def __init__(self, client: redis.Redis):
        self.client = client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.client.get(f"cache:{key}")
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire_seconds: int = 300,
    ) -> None:
        """Set value in cache with expiration."""
        await self.client.setex(
            f"cache:{key}",
            expire_seconds,
            json.dumps(value, default=str),
        )

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        await self.client.delete(f"cache:{key}")


# Global cache instance
cache = Cache(redis_client)
