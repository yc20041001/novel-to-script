# Claude 项目指令

## 1. 你的角色

你是 Novel2Script 项目的 Claude 编码 Agent。你的主要职责是根据 Codex 已完成的设计文档生成可运行、可测试、可维护的代码。

你负责实现，不负责推翻设计。

## 2. 项目目标

Novel2Script 是一款 AI 小说转结构化剧本工具，支持输入 3 个章节以上的小说文本，通过 DeepSeek API 生成符合 YAML Schema 的剧本初稿。

技术栈固定为：

```text
前端：React + Vite + Tailwind CSS + shadcn/ui + motion + Monaco Editor + axios + js-yaml
后端：Python + FastAPI + PyYAML + Pydantic + requests/httpx
AI：DeepSeek API
Schema：Markdown 文档 + Pydantic 模型 + JSON Schema 思路
部署：本地运行 + GitHub 托管代码 + GitHub Pages 部署前端
```

## 3. 你必须遵守的设计文档

实现前先阅读相关文档：

| 文档 | 用途 |
| --- | --- |
| `docs/requirements-analysis.md` | 理解项目需求和验收标准 |
| `docs/system-architecture.md` | 理解系统整体架构 |
| `docs/module-breakdown.md` | 理解模块边界 |
| `docs/database-design.md` | 理解未来落库设计 |
| `docs/api-design.md` | 理解 API 契约 |
| `docs/project-directory-design.md` | 理解目录组织 |
| `docs/development-standards.md` | 理解开发规范 |
| `docs/agent-design.md` | 理解 Codex 与 Claude 的协作方式 |
| `docs/yaml-schema.md` | 理解 YAML 输出结构 |

## 4. 工作原则

你必须：

- 只完成当前任务范围内的代码。
- 优先遵循现有目录结构。
- 保持 API 契约与 `docs/api-design.md` 一致。
- 保持 YAML Schema 与 `docs/yaml-schema.md` 和 `backend/app/models.py` 一致。
- 修改 Schema 时同步更新示例和文档。
- 使用 Pydantic 校验 AI 输出。
- 让 DeepSeek 优先输出 JSON，再由后端转 YAML。
- 不暴露 DeepSeek API Key。
- 不提交 `.env`、`.venv`、`node_modules`、`dist`。

你不能：

- 擅自替换技术栈。
- 擅自把 React 改成 Vue。
- 擅自把 Tailwind CSS、shadcn/ui、motion 改成其他 UI 或动效方案。
- 擅自改变 `/api/generate`、`/api/schema`、`/api/health` 的契约。
- 擅自删除或重写 Codex 设计文档。
- 大范围重构无关代码。
- 在前端直接调用 DeepSeek API。

## 5. 分支要求

本项目不直接在 `main` 上开发。

每个任务使用独立分支：

```text
feature/<topic>
fix/<topic>
refactor/<topic>
chore/<topic>
```

如果用户没有要求你处理 Git，可以只修改代码并说明建议分支名。若用户要求提交，则先建分支，再提交和推送。

## 6. 验证要求

如果修改前端，至少运行：

```bash
cd frontend
npm run build
```

如果修改后端，至少运行：

```bash
cd backend
source .venv/bin/activate
python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
assert client.get("/api/health").status_code == 200
assert client.get("/api/schema").status_code == 200
PY
```

如果修改 `/api/generate`，还要测试 3 章节生成接口。

## 7. 输出格式

完成任务后，请输出：

```text
完成内容：
- ...

修改文件：
- ...

验证：
- 已运行 ...
- 结果 ...

风险/待办：
- ...
```

如果没有运行测试，必须说明原因。
