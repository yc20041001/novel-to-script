# Prompt Agent 设计

## 1. 角色

Prompt Agent 负责维护 Novel2Script 内部调用 DeepSeek 的 Prompt。它的目标是让 DeepSeek 输出稳定、可解析、可校验的剧本 JSON。

## 2. 当前 Prompt 位置

```text
backend/app/prompts/script_prompt.py
```

## 3. 输入

```text
至少 3 个小说章节，每章包含 title 和 content。
```

## 4. 输出

DeepSeek 必须输出合法 JSON，结构符合：

```text
ScriptDocument
```

后端再转换为 YAML。

## 5. 必须约束

Prompt 必须要求 DeepSeek：

- 只输出 JSON。
- 不输出 Markdown。
- 不输出解释文字。
- 不直接输出 YAML。
- 生成 metadata、source、characters、locations、scenes、notes。
- 人物 ID 使用 `char_001` 格式。
- 地点 ID 使用 `loc_001` 格式。
- 场景 ID 使用 `scene_001` 格式。
- 每个场景保留 `chapter_refs`。
- `beats` 类型只能使用 action、dialogue、narration、transition、sound、shot。
- dialogue 类型尽量提供 `speaker_id`。

## 6. 质量标准

模型输出必须：

- 能被 `json.loads` 解析。
- 能通过 `ScriptDocument.model_validate`。
- 至少包含一个 scene。
- 每个 scene 至少包含一个 beat。
- 中文内容正常保留。

## 7. 失败处理

如果 DeepSeek 调用失败、输出非法 JSON 或无法通过 Pydantic 校验：

```text
返回 mock_service 演示剧本
used_mock=true
```

Claude 修改 Prompt 时必须同时测试 `/api/generate`。

