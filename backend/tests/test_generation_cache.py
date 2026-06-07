from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.generation_cache_service import InMemoryGenerationCache
from app.services.generation_repository import InMemoryGenerationRepository

get_settings().deepseek_api_key = ""
get_settings().generation_cache_ttl_seconds = 60

client = TestClient(app)

sample_payload = {
    "chapters": [
        {"title": "第一章", "content": "内容一"},
        {"title": "第二章", "content": "内容二"},
        {"title": "第三章", "content": "内容三"},
    ],
    "options": {"genre": "悬疑", "style": "短剧", "target_scene_count": 6},
}


def _reset_stores() -> None:
    app.state.generation_cache = InMemoryGenerationCache()
    app.state.generation_repository = InMemoryGenerationRepository()


def test_generate_writes_to_cache_and_mysql_repository() -> None:
    _reset_stores()

    resp = client.post("/api/generate", json=sample_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["cache_hit"] is False
    assert data["storage"] == "generated"
    assert data["cache_key"].startswith("generation:")

    cached = client.post("/api/generate", json=sample_payload).json()
    assert cached["cache_hit"] is True
    assert cached["storage"] == "redis"
    assert cached["cache_key"] == data["cache_key"]
    assert cached["yaml"] == data["yaml"]


def test_generate_can_restore_from_mysql_when_redis_misses() -> None:
    _reset_stores()

    first = client.post("/api/generate", json=sample_payload).json()
    app.state.generation_cache = InMemoryGenerationCache()

    restored = client.post("/api/generate", json=sample_payload).json()
    assert restored["cache_hit"] is True
    assert restored["storage"] == "mysql"
    assert restored["cache_key"] == first["cache_key"]
    assert restored["yaml"] == first["yaml"]
