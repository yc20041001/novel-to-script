import json
import re

import httpx

from app.config import Settings
from app.models import GenerateOptions, NovelChapter, ScriptDocument
from app.prompts.script_prompt import SYSTEM_PROMPT, build_script_prompt


class DeepSeekError(RuntimeError):
    pass


def extract_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise DeepSeekError("DeepSeek 未返回可解析的 JSON")
        return json.loads(match.group(0))


async def generate_script_with_deepseek(
    chapters: list[NovelChapter],
    settings: Settings,
    options: GenerateOptions | None = None,
) -> ScriptDocument:
    if not settings.deepseek_api_key:
        raise DeepSeekError("未配置 DeepSeek API Key")

    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_script_prompt(chapters, options)},
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }

    url = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code >= 400:
        raise DeepSeekError(f"DeepSeek API 调用失败：{response.status_code} {response.text}")

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return ScriptDocument.model_validate(extract_json(content))

