import yaml

from app.models import ScriptDocument
from app.services.yaml_service import script_to_yaml, validate_yaml


def _make_dummy_script() -> ScriptDocument:
    """构造一个最简合法的 ScriptDocument 用于测试。"""
    return ScriptDocument(
        metadata={"title": "测试", "language": "zh-CN", "version": "1.0"},
        source={"chapter_count": 3, "chapter_titles": ["第一章", "第二章", "第三章"]},
        scenes=[
            {
                "id": "scene_001",
                "title": "测试场景",
                "chapter_refs": ["第一章"],
                "beats": [
                    {"type": "action", "content": "测试动作"},
                ],
            }
        ],
    )


def test_script_to_yaml_outputs_yaml() -> None:
    script = _make_dummy_script()
    result = script_to_yaml(script)
    # 可以再次解析回 dict
    parsed = yaml.safe_load(result)
    assert isinstance(parsed, dict)


def test_script_to_yaml_contains_metadata() -> None:
    script = _make_dummy_script()
    result = script_to_yaml(script)
    assert "metadata:" in result


def test_script_to_yaml_contains_chinese() -> None:
    script = _make_dummy_script()
    result = script_to_yaml(script)
    assert "测试" in result


def test_validate_yaml_valid() -> None:
    script = _make_dummy_script()
    yaml_str = script_to_yaml(script)
    valid, errors = validate_yaml(yaml_str)
    assert valid is True
    assert errors == []


def test_validate_yaml_empty() -> None:
    valid, errors = validate_yaml("")
    assert valid is False
    assert any("空" in e for e in errors)


def test_validate_yaml_non_dict_root() -> None:
    valid, errors = validate_yaml("[1, 2, 3]")
    assert valid is False
    assert any("根节点" in e for e in errors)


def test_validate_yaml_syntax_error() -> None:
    valid, errors = validate_yaml("unbalanced: [")
    assert valid is False
    assert len(errors) > 0
