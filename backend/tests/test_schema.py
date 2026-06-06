from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_schema_returns_200() -> None:
    resp = client.get("/api/schema")
    assert resp.status_code == 200


def test_schema_title_is_script_document() -> None:
    resp = client.get("/api/schema")
    data = resp.json()
    assert data["title"] == "ScriptDocument"


def test_schema_contains_required_properties() -> None:
    resp = client.get("/api/schema")
    props = resp.json()["properties"]
    for key in ("metadata", "source", "characters", "locations", "scenes", "notes"):
        assert key in props, f"缺少顶层属性 {key}"
