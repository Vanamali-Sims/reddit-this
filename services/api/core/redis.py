"""
Redis client and rate limiting utilities.
"""

import json
import logging
from typing import Any, Optional

from core.config import settings

logger = logging.getLogger(__name__)

redis_client = None

if not settings.USE_REDIS_MOCK:
    import redis.asyncio as redis

    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL is required when USE_REDIS_MOCK=false")

    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RateLimiter:
    """Rate limiter. Always allows traffic when Redis is mocked."""

    def __init__(self, client: Optional[Any]):
        self.client = client

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
    ) -> bool:
        if self.client is None:
            return True

        current_count = await self.client.incr(f"rate_limit:{key}")
        if current_count == 1:
            await self.client.expire(f"rate_limit:{key}", window_seconds)

        return current_count <= limit


rate_limiter = RateLimiter(redis_client)


class Cache:
    """Redis cache. No-ops when Redis is mocked."""

    def __init__(self, client: Optional[Any]):
        self.client = client

    async def get(self, key: str) -> Optional[Any]:
        if self.client is None:
            return None
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
        if self.client is None:
            return
        await self.client.setex(
            f"cache:{key}",
            expire_seconds,
            json.dumps(value, default=str),
        )

    async def delete(self, key: str) -> None:
        if self.client is None:
            return
        await self.client.delete(f"cache:{key}")


cache = Cache(redis_client)
