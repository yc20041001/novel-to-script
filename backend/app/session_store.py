import abc
import json
import secrets
import time


class SessionStore(abc.ABC):
    """Session 存储抽象基类。"""

    @abc.abstractmethod
    async def create_session(self, data: dict, ttl: int) -> str: ...

    @abc.abstractmethod
    async def get_session(self, session_id: str) -> dict | None: ...

    @abc.abstractmethod
    async def delete_session(self, session_id: str) -> None: ...


class InMemorySessionStore(SessionStore):
    """内存 session 存储（测试 / Redis 不可用时回退）。"""

    def __init__(self) -> None:
        self._store: dict[str, tuple[dict, float]] = {}

    async def create_session(self, data: dict, ttl: int) -> str:
        session_id = secrets.token_hex(32)
        self._store[session_id] = (data, time.time() + ttl)
        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        entry = self._store.get(session_id)
        if entry is None:
            return None
        data, expiry = entry
        if time.time() > expiry:
            del self._store[session_id]
            return None
        return data

    async def delete_session(self, session_id: str) -> None:
        self._store.pop(session_id, None)


class RedisSessionStore(SessionStore):
    """Redis session 存储。"""

    def __init__(self, redis_url: str) -> None:
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def ping(self) -> None:
        await self._redis.ping()

    async def create_session(self, data: dict, ttl: int) -> str:
        session_id = secrets.token_hex(32)
        key = f"session:{session_id}"
        await self._redis.setex(key, ttl, json.dumps(data, ensure_ascii=False))
        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        key = f"session:{session_id}"
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def delete_session(self, session_id: str) -> None:
        key = f"session:{session_id}"
        await self._redis.delete(key)
