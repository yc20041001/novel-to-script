from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _get_valid_yaml() -> str:
    """生成一个合法的完整 YAML 用于测试。"""
    chapters = [
        {"title": "第一章", "content": "内容一"},
        {"title": "第二章", "content": "内容二"},
        {"title": "第三章", "content": "内容三"},
    ]
    resp = client.post("/api/generate", json={"chapters": chapters})
    return resp.json()["yaml"]


def test_validate_valid_yaml() -> None:
    yaml_text = _get_valid_yaml()
    resp = client.post("/api/validate-yaml", json={"yaml": yaml_text})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["errors"] == []


def test_validate_yaml_syntax_error() -> None:
    """YAML 语法错误 : 列表不能作为 mapping 的值。"""
    resp = client.post("/api/validate-yaml", json={"yaml": "metadata:\n  - bad"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0


def test_validate_yaml_not_matching_schema() -> None:
    """YAML 语法合法但缺少 scenes 必填字段。"""
    yaml_str = (
        "metadata:\n"
        '  title: test\n'
        '  language: zh-CN\n'
        "  version: '1.0'\n"
        "source:\n"
        "  chapter_count: 1\n"
        "  chapter_titles: ['a']\n"
    )
    resp = client.post("/api/validate-yaml", json={"yaml": yaml_str})
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0
