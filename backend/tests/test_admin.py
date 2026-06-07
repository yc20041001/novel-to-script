from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.generation_repository import InMemoryGenerationRepository

from .test_auth import _captcha_payload


def _client() -> TestClient:
    return TestClient(app)


def _login_admin(client: TestClient) -> None:
    settings = get_settings()
    resp = client.post(
        "/api/auth/login",
        json={
            "username": settings.demo_username,
            "password": settings.demo_password,
            **_captcha_payload(client),
        },
    )
    assert resp.status_code == 200


def test_admin_requires_login() -> None:
    client = _client()
    resp = client.get("/api/admin/stats")
    assert resp.status_code == 401


def test_admin_dashboard_stats() -> None:
    client = _client()
    _login_admin(client)

    resp = client.get("/api/admin/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_count"] >= 1
    assert data["active_user_count"] >= 1
    assert "generation_count" in data


def test_admin_lists_users() -> None:
    client = _client()
    _login_admin(client)

    resp = client.get("/api/admin/users")
    assert resp.status_code == 200
    users = resp.json()["users"]
    assert any(user["username"] == get_settings().demo_username for user in users)


def test_admin_updates_user_status() -> None:
    client = _client()
    _login_admin(client)
    register_resp = client.post(
        "/api/auth/register",
        json={
            "username": "status_user",
            "password": "secret123",
            **_captcha_payload(client),
        },
    )
    assert register_resp.status_code == 200

    _login_admin(client)
    users = client.get("/api/admin/users").json()["users"]
    target = next(user for user in users if user["username"] == "status_user")
    resp = client.patch(f"/api/admin/users/{target['id']}", json={"status": "disabled"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "disabled"


def test_admin_lists_generation_records() -> None:
    app.state.generation_repository = InMemoryGenerationRepository()
    client = _client()
    _login_admin(client)

    gen_resp = client.post(
        "/api/generate",
        json={
            "chapters": [
                {"title": "第一章", "content": "内容一"},
                {"title": "第二章", "content": "内容二"},
                {"title": "第三章", "content": "内容三"},
            ]
        },
    )
    assert gen_resp.status_code == 200

    resp = client.get("/api/admin/generations")
    assert resp.status_code == 200
    records = resp.json()["records"]
    assert len(records) >= 1
    assert records[0]["cache_key"]
