from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_health_returns_status_ok() -> None:
    resp = client.get("/api/health")
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "novel2script-api"
