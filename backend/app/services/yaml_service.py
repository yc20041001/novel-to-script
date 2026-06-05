import yaml

from app.models import ScriptDocument


def script_to_yaml(script: ScriptDocument) -> str:
    data = script.model_dump(exclude_none=True)
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)

