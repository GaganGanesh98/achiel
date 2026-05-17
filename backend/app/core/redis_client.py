from typing import AsyncIterator
from redis.asyncio import Redis, from_url

from app.core.config import settings

_pool: Redis | None = None


def get_redis_pool() -> Redis:
    global _pool
    if _pool is None:
        _pool = from_url(settings.REDIS_URL, decode_responses=False)
    return _pool


async def get_redis() -> AsyncIterator[Redis]:
    yield get_redis_pool()
