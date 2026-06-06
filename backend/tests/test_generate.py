from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

sample_chapters = [
    {"title": "第一章", "content": "内容一"},
    {"title": "第二章", "content": "内容二"},
    {"title": "第三章", "content": "内容三"},
]


def _generate(payload: dict) -> dict:
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_generate_old_format_returns_200() -> None:
    resp = client.post("/api/generate", json={"chapters": sample_chapters})
    assert resp.status_code == 200
    data = resp.json()
    assert "yaml" in data
    assert "script" in data
    assert "used_mock" in data


def test_generate_old_format_yaml_contains_metadata() -> None:
    data = _generate({"chapters": sample_chapters})
    assert "metadata:" in data["yaml"]


def test_generate_old_format_script_source_ge_3() -> None:
    data = _generate({"chapters": sample_chapters})
    assert data["script"]["source"]["chapter_count"] >= 3


def test_generate_with_options_returns_200() -> None:
    payload = {
        "chapters": sample_chapters,
        "options": {
            "genre": "悬疑",
            "style": "短剧",
            "target_scene_count": 6,
            "language": "zh-CN",
        },
    }
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "yaml" in data
    assert "script" in data


def test_generate_with_partial_options() -> None:
    payload = {
        "chapters": sample_chapters,
        "options": {"genre": "奇幻"},
    }
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 200
    assert "yaml" in resp.json()


def test_generate_less_than_3_chapters_returns_422() -> None:
    payload = {"chapters": [{"title": "仅一章", "content": "正文"}]}
    resp = client.post("/api/generate", json=payload)
    assert resp.status_code == 422
