import hashlib
import json

from redis.asyncio import Redis

PROMPT_LIST_CACHE_PREFIX = 'prompt:list:'


def build_prompt_list_cache_key(params: dict) -> str:
    serialized = json.dumps(params, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
    return f'{PROMPT_LIST_CACHE_PREFIX}{digest}'


async def get_cached_prompt_list(redis: Redis, key: str) -> dict | None:
    data = await redis.get(key)
    if not data:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


async def set_cached_prompt_list(redis: Redis, key: str, payload: dict, ttl_seconds: int = 60) -> None:
    await redis.set(key, json.dumps(payload, default=str), ex=ttl_seconds)


async def invalidate_prompt_list_cache(redis: Redis) -> None:
    async for key in redis.scan_iter(match=f'{PROMPT_LIST_CACHE_PREFIX}*'):
        await redis.delete(key)
