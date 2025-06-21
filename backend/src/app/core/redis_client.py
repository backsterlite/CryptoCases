import redis.asyncio as redis_client
from typing import Any

from fastapi import Depends
from app.core.config.settings import Settings
from app.core.config.settings import get_settings

_redis: redis_client.Redis | None = None

def get_redis(
    ) -> redis_client.Redis:
    global _redis
    settings: Settings = get_settings()
    if _redis is None:
        _redis = redis_client.from_url(
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