import aioredis
from typing import Any
from app.config.settings import settings

_redis: aioredis.Redis | None = None

def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASS or None,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis

async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None