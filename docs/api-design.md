# API 设计

## 1. 设计目标

Novel2Script 的 API 负责连接 React 前端、FastAPI 后端和 DeepSeek AI 服务。API 设计目标是让前端可以稳定提交小说章节、获取结构化剧本 YAML、查看 Schema，并为后续项目保存、版本管理和导出能力预留扩展空间。

核心原则：

- 使用 REST 风格接口。
- 请求和响应均使用 JSON。
- 后端统一负责 DeepSeek API 调用，前端不接触 API Key。
- 当前 MVP 只保留必要接口，避免过早复杂化。
- API 返回结构尽量稳定，后续扩展优先新增字段，不随意改名或删除字段。

## 2. 基础约定

### 2.1 Base URL

本地后端默认地址：

```text
http://localhost:8000
```

前端默认通过环境变量配置：

```text
VITE_API_BASE_URL=http://localhost:8000
```

如果未设置该环境变量，前端默认请求 `http://localhost:8000`。

### 2.2 数据格式

请求头：

```http
Content-Type: application/json
```

响应头：

```http
Content-Type: application/json
```

### 2.3 时间格式

当前 MVP 接口暂无时间字段。未来涉及时间字段时，统一使用 ISO 8601 字符串：

```text
2026-06-04T20:30:00Z
```

### 2.4 命名风格

JSON 字段使用 snake_case，与 FastAPI/Pydantic 后端保持一致。

示例：

```json
{
  "used_mock": true,
  "chapter_count": 3
}
```

## 3. 当前 API 总览

| 接口 | 方法 | 说明 | 当前状态 |
| --- | --- | --- | --- |
| `/api/health` | GET | 健康检查 | 已实现 |
| `/api/schema` | GET | 获取 ScriptDocument JSON Schema | 已实现 |
| `/api/generate` | POST | 输入章节并生成剧本 YAML | 已实现 |

## 4. 通用错误格式

当前 FastAPI 默认错误响应格式如下：

```json
{
  "detail": "错误说明"
}
```

校验错误示例：

```json
{
  "detail": [
    {
      "type": "too_short",
      "loc": ["body", "chapters"],
      "msg": "List should have at least 3 items after validation, not 2",
      "input": []
    }
  ]
}
```

后续建议扩展为统一错误结构：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请至少输入 3 个章节",
    "details": []
  }
}
```

错误码建议：

| code | 说明 |
| --- | --- |
| VALIDATION_ERROR | 请求参数不合法 |
| AI_PROVIDER_ERROR | DeepSeek API 调用失败 |
| AI_OUTPUT_PARSE_ERROR | AI 返回内容无法解析 |
| SCHEMA_VALIDATION_ERROR | AI 输出不符合剧本 Schema |
| YAML_PARSE_ERROR | YAML 校验失败 |
| INTERNAL_ERROR | 服务端内部错误 |

## 5. GET /api/health

### 5.1 用途

检查后端服务是否正常启动。前端或部署脚本可以用它判断 FastAPI 服务是否可用。

### 5.2 请求

```http
GET /api/health
```

无请求体。

### 5.3 响应

状态码：`200 OK`

```json
{
  "status": "ok",
  "service": "novel2script-api"
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| status | string | 服务状态 |
| service | string | 服务名称 |

## 6. GET /api/schema

### 6.1 用途

返回 `ScriptDocument` 的 JSON Schema。前端可以用它展示 Schema，未来也可以用于编辑器提示和自动校验。

### 6.2 请求

```http
GET /api/schema
```

无请求体。

### 6.3 响应

状态码：`200 OK`

响应内容为 Pydantic 生成的 JSON Schema。

示例节选：

```json
{
  "title": "ScriptDocument",
  "type": "object",
  "properties": {
    "metadata": {
      "$ref": "#/$defs/ScriptMetadata"
    },
    "source": {
      "$ref": "#/$defs/ScriptSource"
    },
    "characters": {
      "type": "array"
    },
    "locations": {
      "type": "array"
    },
    "scenes": {
      "type": "array",
      "minItems": 1
    },
    "notes": {
      "type": "array"
    }
  }
}
```

## 7. POST /api/generate

### 7.1 用途

接收至少 3 个小说章节，调用 DeepSeek API 生成结构化剧本，并返回剧本对象和 YAML 文本。

### 7.2 请求

```http
POST /api/generate
```

请求体：

```json
{
  "chapters": [
    {
      "title": "第一章 雨夜",
      "content": "雨下得很急。林晚走进巷尾的旧书店..."
    },
    {
      "title": "第二章 手稿",
      "content": "手稿第一页写着她的名字..."
    },
    {
      "title": "第三章 旧书店",
      "content": "楼上传来脚步声..."
    }
  ]
}
```

### 7.3 请求字段说明

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| chapters | array | 是 | 至少 3 项 | 小说章节数组 |
| chapters[].title | string | 是 | 非空 | 章节标题 |
| chapters[].content | string | 是 | 非空 | 章节正文 |

### 7.4 成功响应

状态码：`200 OK`

```json
{
  "script": {
    "metadata": {
      "title": "雨夜来信",
      "genre": "悬疑",
      "language": "zh-CN",
      "version": "1.0",
      "logline": "一名编辑在雨夜收到一份能预写现实的神秘手稿。"
    },
    "source": {
      "chapter_count": 3,
      "chapter_titles": ["第一章 雨夜", "第二章 手稿", "第三章 旧书店"]
    },
    "characters": [],
    "locations": [],
    "scenes": [],
    "notes": []
  },
  "yaml": "metadata:\n  title: 雨夜来信\n...",
  "used_mock": false
}
```

### 7.5 响应字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| script | object | 结构化剧本对象，符合 ScriptDocument Schema |
| yaml | string | 由 script 转换得到的 YAML 文本 |
| used_mock | boolean | 是否使用演示回退数据 |

`used_mock=true` 表示后端未配置 DeepSeek API Key 或 AI 调用失败，返回了本地演示剧本。

### 7.6 校验失败

章节不足 3 个时：

状态码：`422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "loc": ["body", "chapters"],
      "msg": "List should have at least 3 items after validation, not 2",
      "type": "too_short"
    }
  ]
}
```

### 7.7 兼容性说明

后续可以在请求体中新增可选字段，不影响当前前端：

```json
{
  "chapters": [],
  "options": {
    "genre": "悬疑",
    "style": "短剧",
    "target_scene_count": 12,
    "language": "zh-CN"
  }
}
```

新增字段应为可选字段，避免破坏当前调用方。

## 8. 剧本对象结构

`script` 字段遵循 `ScriptDocument`。

```json
{
  "metadata": {},
  "source": {},
  "characters": [],
  "locations": [],
  "scenes": [],
  "notes": []
}
```

核心子对象：

| 对象 | 说明 |
| --- | --- |
| metadata | 剧本标题、类型、语言、版本和一句话梗概 |
| source | 原小说章节数量和章节标题 |
| characters | 人物列表 |
| locations | 地点列表 |
| scenes | 场景列表 |
| notes | 生成备注或改稿建议 |

详细字段以 [YAML Schema 文档](yaml-schema.md) 和 `/api/schema` 为准。

## 9. 前端调用设计

前端 API 封装位于：

```text
frontend/src/api/scriptApi.js
```

### 9.1 generateScript

```js
export async function generateScript(chapters) {
  const response = await client.post('/api/generate', { chapters });
  return response.data;
}
```

调用方：

```text
frontend/src/App.jsx
```

用途：

- 生成剧本 YAML。
- 接收 `used_mock`，提示是否为演示输出。

### 9.2 fetchSchema

```js
export async function fetchSchema() {
  const response = await client.get('/api/schema');
  return response.data;
}
```

用途：

- 在前端 Schema 弹窗中展示后端 JSON Schema。

## 10. AI 供应商接口边界

前端不直接访问 DeepSeek。后端的 `deepseek_service.py` 负责调用：

```text
POST {DEEPSEEK_BASE_URL}/chat/completions
```

请求关键字段：

```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "你是专业编剧助手..."
    },
    {
      "role": "user",
      "content": "请将以下小说改编为结构化剧本..."
    }
  ],
  "temperature": 0.4,
  "response_format": {
    "type": "json_object"
  }
}
```

设计原因：

- API Key 留在服务端。
- 后端可以统一处理重试、超时、解析和 Schema 校验。
- 前端只关心业务接口，不关心模型供应商细节。

## 11. 未来扩展 API

以下接口当前未实现，用于说明数据库版本的 API 蓝图。

### 11.1 项目接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/projects` | POST | 创建小说改编项目 |
| `/api/projects` | GET | 查询项目列表 |
| `/api/projects/{project_id}` | GET | 获取项目详情 |
| `/api/projects/{project_id}` | PATCH | 更新项目标题或说明 |
| `/api/projects/{project_id}` | DELETE | 删除项目 |

### 11.2 章节接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/projects/{project_id}/chapters` | PUT | 批量保存章节 |
| `/api/projects/{project_id}/chapters` | GET | 获取项目章节 |

### 11.3 生成任务接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/projects/{project_id}/generation-jobs` | POST | 创建 AI 生成任务 |
| `/api/generation-jobs/{job_id}` | GET | 查询任务状态 |

### 11.4 剧本版本接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/projects/{project_id}/script-versions` | GET | 查询剧本版本 |
| `/api/script-versions/{version_id}` | GET | 获取某个剧本版本 |
| `/api/script-versions/{version_id}` | PATCH | 保存人工修改后的 YAML |

### 11.5 导出接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/script-versions/{version_id}/exports` | POST | 导出 YAML、JSON、TXT 或 DOCX |

## 12. API 版本策略

当前 MVP 使用 `/api/*`，暂不引入版本号。

如果后续公开部署或对接第三方，建议改为：

```text
/api/v1/generate
/api/v1/schema
```

版本策略：

- 非破坏性字段新增保留在同一版本。
- 字段重命名、类型变化、响应结构变化应进入新版本。
- 旧版本至少保留到前端完成迁移。

## 13. 幂等性与超时

当前 `/api/generate` 是即时生成接口，不保证幂等。相同章节多次调用可能得到不同剧本，因为 AI 生成具有随机性。

当前建议：

- 前端生成按钮在请求期间进入 loading 状态，避免重复点击。
- 后端 AI 调用超时时间设置为 90 秒。

后续引入数据库和生成任务后，可以通过 `generation_jobs` 支持：

- 任务状态查询。
- 请求去重。
- 失败重试。
- 历史结果复用。

## 14. 安全与权限

当前本地 MVP：

- 无用户认证。
- API 仅用于本地运行。
- DeepSeek API Key 仅存在后端 `.env`。

如果部署到公网，需要增加：

- 请求体大小限制。
- 用户认证。
- 速率限制。
- CORS 白名单。
- 日志脱敏。
- AI 调用成本控制。

## 15. API 验收标准

| 项目 | 标准 |
| --- | --- |
| 健康检查 | `GET /api/health` 返回 200 |
| Schema | `GET /api/schema` 返回 ScriptDocument JSON Schema |
| 生成接口 | `POST /api/generate` 接收 3 个以上章节并返回 YAML |
| 校验 | 章节不足 3 个时返回 422 |
| 安全 | 前端不直接暴露 DeepSeek API Key |
| 兼容性 | 后续新增字段应保持向后兼容 |

