from fastapi.testclient import TestClient

from app.config import get_settings
from app.captcha_store import InMemoryCaptchaStore
from app.main import app
from app.session_store import InMemorySessionStore
from app.services.user_repository import InMemoryUserRepository

# 使用内存 store，不依赖 Redis / MySQL
app.state.session_store = InMemorySessionStore()
app.state.captcha_store = InMemoryCaptchaStore()
app.state.user_repository = InMemoryUserRepository(get_settings())


def _make_client():
    """创建一个全新的 TestClient（无 cookie 污染）。"""
    return TestClient(app)


def _captcha_payload(client: TestClient) -> dict:
    captcha_resp = client.get("/api/auth/captcha")
    assert captcha_resp.status_code == 200
    data = captcha_resp.json()
    assert data["captcha_id"]
    assert data["image"].startswith("data:image/svg+xml;base64,")
    assert data["expires_in"] == 60

    code = app.state.captcha_store._store[data["captcha_id"]][0]
    return {"captcha_id": data["captcha_id"], "captcha_code": code}


def _login_payload(client: TestClient, username: str = "admin", password: str = "admin123") -> dict:
    return {
        "username": username,
        "password": password,
        **_captcha_payload(client),
    }


def test_login_success() -> None:
    client = _make_client()
    resp = client.post("/api/auth/login", json=_login_payload(client))
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == "admin"
    assert "novel2script_session" in resp.cookies


def test_login_wrong_password_returns_401() -> None:
    client = _make_client()
    resp = client.post("/api/auth/login", json=_login_payload(client, password="wrong"))
    assert resp.status_code == 401


def test_login_wrong_username_returns_401() -> None:
    client = _make_client()
    resp = client.post("/api/auth/login", json=_login_payload(client, username="nobody"))
    assert resp.status_code == 401


def test_login_wrong_captcha_returns_400() -> None:
    client = _make_client()
    payload = _login_payload(client)
    payload["captcha_code"] = "WRONG"
    resp = client.post("/api/auth/login", json=payload)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "验证码错误或已过期"


def test_me_without_session() -> None:
    client = _make_client()
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is False


def test_me_after_login() -> None:
    client = _make_client()
    # 登录并捕获 cookie
    login_resp = client.post("/api/auth/login", json=_login_payload(client))
    session_cookie = login_resp.cookies.get("novel2script_session")
    assert session_cookie is not None

    # 用同一 client 发 /me（httpx 自动携带 cookie）
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == "admin"


def test_logout_clears_session() -> None:
    client = _make_client()
    # 登录
    login_resp = client.post("/api/auth/login", json=_login_payload(client))
    assert login_resp.status_code == 200

    # 退出（同一 client，cookie 自动携带）
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    data = logout_resp.json()
    assert data["authenticated"] is False

    # 退出后 /me 应返回未登录
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["authenticated"] is False


def test_register_success_and_auto_login() -> None:
    client = _make_client()
    username = "author_new"
    resp = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "secret123",
            "display_name": "新作者",
            **_captcha_payload(client),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == username
    assert data["user"]["display_name"] == "新作者"
    assert "novel2script_session" in resp.cookies


def test_register_duplicate_username_returns_409() -> None:
    client = _make_client()
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "admin",
            "password": "secret123",
            **_captcha_payload(client),
        },
    )
    assert resp.status_code == 409


def test_existing_endpoints_still_work() -> None:
    client = _make_client()
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/schema").status_code == 200

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
