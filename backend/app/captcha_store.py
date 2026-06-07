import abc
import base64
import html
import random
import secrets
import string
import time


class CaptchaStore(abc.ABC):
    """验证码存储抽象基类。"""

    @abc.abstractmethod
    async def create_captcha(self, ttl: int) -> dict: ...

    @abc.abstractmethod
    async def verify_captcha(self, captcha_id: str, code: str) -> bool: ...


def _random_code(length: int = 4) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _captcha_svg_data_url(code: str) -> str:
    escaped = html.escape(code)
    lines = []
    for _ in range(6):
        x1, y1 = random.randint(0, 120), random.randint(0, 40)
        x2, y2 = random.randint(0, 120), random.randint(0, 40)
        lines.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            'stroke="rgba(20,83,79,0.25)" stroke-width="1" />'
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40">'
        '<rect width="120" height="40" rx="8" fill="#ecfeff"/>'
        '<rect x="1" y="1" width="118" height="38" rx="7" fill="none" stroke="#99f6e4"/>'
        f'{"".join(lines)}'
        f'<text x="60" y="27" text-anchor="middle" font-family="Menlo, Consolas, monospace" '
        f'font-size="22" font-weight="700" letter-spacing="4" fill="#134e4a">{escaped}</text>'
        "</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


class InMemoryCaptchaStore(CaptchaStore):
    """内存验证码存储（测试 / Redis 不可用时回退）。"""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}

    async def create_captcha(self, ttl: int) -> dict:
        captcha_id = secrets.token_hex(16)
        code = _random_code()
        self._store[captcha_id] = (code, time.time() + ttl)
        return {
            "captcha_id": captcha_id,
            "image": _captcha_svg_data_url(code),
            "expires_in": ttl,
        }

    async def verify_captcha(self, captcha_id: str, code: str) -> bool:
        entry = self._store.pop(captcha_id, None)
        if entry is None:
            return False
        expected, expiry = entry
        if time.time() > expiry:
            return False
        return secrets.compare_digest(expected.lower(), code.strip().lower())


class RedisCaptchaStore(CaptchaStore):
    """Redis 验证码存储。"""

    def __init__(self, redis_url: str, password: str | None = None) -> None:
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(
            redis_url,
            decode_responses=True,
            password=password,
        )

    async def ping(self) -> None:
        await self._redis.ping()

    async def create_captcha(self, ttl: int) -> dict:
        captcha_id = secrets.token_hex(16)
        code = _random_code()
        await self._redis.setex(f"captcha:{captcha_id}", ttl, code)
        return {
            "captcha_id": captcha_id,
            "image": _captcha_svg_data_url(code),
            "expires_in": ttl,
        }

    async def verify_captcha(self, captcha_id: str, code: str) -> bool:
        key = f"captcha:{captcha_id}"
        expected = await self._redis.get(key)
        await self._redis.delete(key)
        if expected is None:
            return False
        return secrets.compare_digest(expected.lower(), code.strip().lower())
