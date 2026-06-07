import abc
import hashlib
import json
from typing import Any

from app.models import GenerateRequest


def build_generation_cache_key(request: GenerateRequest) -> str:
    payload = request.model_dump(mode="json")
    normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"generation:{digest}"


class GenerationCache(abc.ABC):
    @abc.abstractmethod
    async def get(self, cache_key: str) -> dict[str, Any] | None: ...

    @abc.abstractmethod
    async def set(self, cache_key: str, payload: dict[str, Any], ttl_seconds: int) -> None: ...


class InMemoryGenerationCache(GenerationCache):
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        return self._store.get(cache_key)

    async def set(self, cache_key: str, payload: dict[str, Any], ttl_seconds: int) -> None:
        self._store[cache_key] = payload


class RedisGenerationCache(GenerationCache):
    def __init__(self, redis_url: str, password: str | None = None) -> None:
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(
            redis_url,
            decode_responses=True,
            password=password,
        )

    async def ping(self) -> None:
        await self._redis.ping()

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        raw = await self._redis.get(cache_key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, cache_key: str, payload: dict[str, Any], ttl_seconds: int) -> None:
        await self._redis.setex(cache_key, ttl_seconds, json.dumps(payload, ensure_ascii=False))
