from fastapi.testclient import TestClient

from app.main import app
from app.session_store import InMemorySessionStore

# 使用内存 session store，不依赖 Redis
app.state.session_store = InMemorySessionStore()


def _make_client():
    """创建一个全新的 TestClient（无 cookie 污染）。"""
    return TestClient(app)


def test_login_success() -> None:
    client = _make_client()
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == "admin"
    assert "novel2script_session" in resp.cookies


def test_login_wrong_password_returns_401() -> None:
    client = _make_client()
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_wrong_username_returns_401() -> None:
    client = _make_client()
    resp = client.post("/api/auth/login", json={"username": "nobody", "password": "admin123"})
    assert resp.status_code == 401


def test_me_without_session() -> None:
    client = _make_client()
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is False


def test_me_after_login() -> None:
    client = _make_client()
    # 登录并捕获 cookie
    login_resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
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
    login_resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
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
