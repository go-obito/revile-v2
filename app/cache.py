import json
from collections.abc import Iterable

from redis.asyncio import Redis, from_url
from redis.exceptions import RedisError

from app.config import get_settings

settings = get_settings()
redis: Redis = from_url(settings.redis_url, decode_responses=True)


async def cache_get(key: str) -> dict | list | None:
    try:
        value = await redis.get(key)
        return json.loads(value) if value else None
    except RedisError:
        return None


async def cache_set(key: str, value: dict | list, ttl: int = 90) -> None:
    try:
        await redis.set(key, json.dumps(value, default=str), ex=ttl)
    except RedisError:
        return


async def cache_delete(*keys: str) -> None:
    if not keys:
        return
    try:
        await redis.delete(*keys)
    except RedisError:
        return


async def invalidate_post(post_id: int, slug: str | None = None, category_slugs: Iterable[str] = ()) -> None:
    keys = [f"post:{slug}", f"post:id:{post_id}", "posts:breaking"] if slug else [f"post:id:{post_id}", "posts:breaking"]
    keys.extend(f"posts:category:{category}" for category in category_slugs)
    keys.append("posts:list")
    await cache_delete(*keys)


async def rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    try:
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window_seconds)
        return current <= limit
    except RedisError:
        return True
