import yaml
from pydantic import ValidationError

from app.models import ScriptDocument


def script_to_yaml(script: ScriptDocument) -> str:
    data = script.model_dump(exclude_none=True)
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def validate_yaml(yaml_str: str) -> tuple[bool, list[str]]:
    """校验 YAML 字符串是否符合 ScriptDocument Schema。

    返回 (valid: bool, errors: list[str])。
    """
    # 1) 用 PyYAML 解析
    try:
        data = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        return False, [f"YAML 语法错误: {e}"]

    # 2) 空内容
    if data is None:
        return False, ["YAML 内容为空"]

    # 3) 根节点必须是 dict
    if not isinstance(data, dict):
        return False, ["YAML 根节点必须是一个映射（键值对）"]

    # 4) 用 Pydantic 校验结构
    try:
        ScriptDocument.model_validate(data)
    except ValidationError as e:
        errors: list[str] = []
        for err in e.errors():
            loc = " -> ".join(str(x) for x in err.get("loc", []))
            msg = err.get("msg", "未知错误")
            errors.append(f"{loc}: {msg}")
        return False, errors

    return True, []

