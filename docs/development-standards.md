# 开发规范

## 1. 规范目标

本开发规范用于约束 Novel2Script 项目的代码编写、分支管理、提交、文档、接口、AI Prompt、安全和测试流程。目标是让项目在课程开发、答辩演示和后续扩展中保持一致、清晰、可维护。

适用范围：

- React + Vite 前端开发。
- FastAPI 后端开发。
- DeepSeek Prompt 和 AI 编排开发。
- YAML Schema 和技术文档维护。
- GitHub 分支、提交和部署流程。

## 2. Git 分支规范

### 2.1 基本原则

所有功能、文档和修复都必须先创建独立分支，不直接在 `main` 上开发。

开发流程：

```text
main
  -> 新建 feature/* 分支
  -> 完成单一任务
  -> 本地验证
  -> 推送 feature/* 分支
  -> 合并回 main
  -> 推送 main
```

### 2.2 分支命名

| 类型 | 命名格式 | 示例 |
| --- | --- | --- |
| 功能开发 | `feature/<topic>` | `feature/frontend-editor` |
| 文档设计 | `feature/<doc-topic>` | `feature/api-design` |
| Bug 修复 | `fix/<topic>` | `fix/yaml-validation` |
| 重构 | `refactor/<topic>` | `refactor/backend-services` |
| 部署配置 | `chore/<topic>` | `chore/github-pages` |

分支名要求：

- 使用英文小写。
- 单词之间使用短横线。
- 一个分支只完成一个明确主题。
- 不使用 `temp`、`test`、`new` 这类含义模糊的名字。

## 3. 提交规范

### 3.1 Commit Message 格式

推荐格式：

```text
<type>: <summary>
```

示例：

```text
docs: add API design document
feat: add YAML editor toolbar
fix: handle missing DeepSeek API key
```

当前项目也允许简洁描述式提交，例如：

```text
Add API design document
Merge API design document
```

### 3.2 提交类型

| type | 用途 |
| --- | --- |
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档 |
| refactor | 重构 |
| test | 测试 |
| chore | 工程配置 |
| style | 代码格式 |

### 3.3 提交要求

- 每次提交只表达一个主题。
- 不提交 `node_modules/`、`dist/`、`.venv/`、`.env`。
- 提交前执行必要验证。
- 文档更新要同步 README 入口。
- 不能把真实 DeepSeek API Key 写入提交。

## 4. 前端开发规范

### 4.1 技术栈

前端固定使用：

```text
React + Vite + Ant Design + Monaco Editor + axios + js-yaml
```

不使用 Element Plus，因为 Element Plus 属于 Vue 生态。

### 4.2 目录规范

当前结构：

```text
frontend/src/
  App.jsx
  main.jsx
  styles.css
  api/
    scriptApi.js
```

后续扩展建议：

```text
frontend/src/
  api/
  components/
  pages/
  hooks/
  utils/
```

### 4.3 React 编码规范

- 使用函数组件。
- 使用 Hooks 管理状态。
- 组件名使用 PascalCase，例如 `YamlEditor.jsx`。
- API 调用统一放在 `src/api/`。
- 页面组件不直接拼接后端 URL。
- 不在组件中保存 API Key。
- 复杂逻辑优先提取到自定义 Hook 或工具函数。

### 4.4 UI 规范

- 使用 Ant Design 组件保持界面一致。
- 编辑器使用 Monaco Editor。
- 用户操作必须有 loading、success 或 error 反馈。
- 生成按钮请求期间应禁用或显示 loading。
- 删除章节等操作要避免误操作。
- 页面在移动端不应出现内容重叠。

### 4.5 前端校验规范

提交生成前必须校验：

- 章节数量不少于 3。
- 每个章节标题非空。
- 每个章节正文非空。

前端校验只用于提升体验，后端必须重复校验。

### 4.6 前端构建验证

修改前端后至少执行：

```bash
cd frontend
npm run build
```

如果修改依赖，需要确认：

```bash
npm install
```

并提交更新后的 `package-lock.json`。

## 5. 后端开发规范

### 5.1 技术栈

后端固定使用：

```text
Python + FastAPI + Pydantic + PyYAML + httpx
```

### 5.2 目录规范

当前结构：

```text
backend/app/
  main.py
  models.py
  config.py
  prompts/
  services/
```

职责划分：

- `main.py` 只负责 API 路由和模块串联。
- `models.py` 负责 Pydantic 请求、响应和剧本结构。
- `config.py` 负责配置读取。
- `prompts/` 负责 Prompt 模板。
- `services/` 负责业务服务。

### 5.3 Python 编码规范

- 使用类型标注。
- 使用 Pydantic 做请求和输出校验。
- 函数职责保持单一。
- 外部 API 调用使用 `httpx`。
- 不在业务代码中硬编码 API Key。
- 错误处理要返回可理解的信息。
- 中文输出必须保证 UTF-8。

### 5.4 API 规范

- API 路径统一以 `/api/` 开头。
- 请求和响应使用 JSON。
- 字段命名使用 snake_case。
- 新增字段优先设计为可选，保持向后兼容。
- API 变更要同步更新 [API 设计](api-design.md)。

### 5.5 后端验证

修改后端后至少执行：

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

如果修改生成接口，需要额外测试 `/api/generate`。

## 6. AI Prompt 开发规范

### 6.1 Prompt 存放

所有 Prompt 必须放在：

```text
backend/app/prompts/
```

不要把大段 Prompt 直接写在 API 路由中。

### 6.2 输出格式规范

DeepSeek 应优先输出 JSON，再由后端转换为 YAML。

禁止直接依赖 AI 输出最终 YAML，原因：

- YAML 缩进敏感。
- AI 容易混入解释文本。
- JSON 更适合 Pydantic 校验。

### 6.3 Prompt 约束

Prompt 必须明确：

- 模型角色。
- 输入内容。
- 输出字段。
- 输出必须为合法 JSON。
- 不输出 Markdown。
- 不输出解释文字。
- 人物、地点、场景需要稳定 ID。
- 场景要保留来源章节。

### 6.4 AI 失败处理

AI 调用失败时必须有降级策略。

当前策略：

```text
DeepSeek 失败或未配置 API Key
  -> mock_service 返回演示剧本
  -> used_mock=true
```

后续可增加：

- 自动重试。
- JSON 修复。
- 分章摘要。
- 错误报告。

## 7. YAML Schema 规范

### 7.1 Schema 来源

运行时 Schema 以 Pydantic 模型为准：

```text
backend/app/models.py
```

人工说明文档为：

```text
docs/yaml-schema.md
```

### 7.2 修改规则

修改剧本结构时必须同步更新：

- `backend/app/models.py`
- `docs/yaml-schema.md`
- `docs/api-design.md`
- `examples/sample-output.yaml`

### 7.3 字段设计规则

- 必填字段要有明确用途。
- 可选字段要设置合理默认值。
- ID 字段保持稳定，例如 `char_001`、`loc_001`、`scene_001`。
- 列表字段默认使用空数组，不使用 null。
- 对白类 beat 使用 `speaker_id` 引用人物 ID。

## 8. 文档规范

### 8.1 文档位置

所有设计文档放在：

```text
docs/
```

README 只作为项目入口，不承载过长设计内容。

### 8.2 文档命名

使用 kebab-case：

```text
requirements-analysis.md
system-architecture.md
module-breakdown.md
database-design.md
api-design.md
project-directory-design.md
development-standards.md
yaml-schema.md
```

### 8.3 文档更新要求

- 新增文档必须在 README 加入口。
- 文档应包含目标、设计原因和验收标准。
- 文档内容要与当前代码保持一致。
- 如果写未来规划，必须明确说明“当前未实现”。

## 9. 安全规范

### 9.1 密钥管理

- 真实 DeepSeek API Key 只写在 `backend/.env`。
- `.env` 不提交 GitHub。
- 只提交 `.env.example`。
- 前端不得出现 API Key。

### 9.2 用户内容

小说文本和剧本属于用户创作内容。

要求：

- 不在日志中完整打印用户小说正文。
- 后续上线公网时限制单次请求大小。
- 后续引入数据库时需要支持项目级隔离。

### 9.3 CORS

本地开发允许：

```text
http://localhost:5173
http://127.0.0.1:5173
```

生产部署时应改为明确前端域名。

## 10. 测试规范

### 10.1 当前最小验证

前端：

```bash
cd frontend
npm run build
```

后端：

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

### 10.2 后续测试建议

前端：

- 章节数量校验。
- 生成按钮 loading 状态。
- YAML 复制和下载。
- Schema 弹窗。

后端：

- `/api/generate` 正常生成。
- 章节不足 3 个返回 422。
- DeepSeek 无 Key 时走 mock。
- AI 返回非法 JSON 时走异常处理。
- PyYAML 中文输出正常。

## 11. 部署规范

### 11.1 前端部署

前端部署到 GitHub Pages：

```bash
cd frontend
npm run deploy
```

部署前需要确保：

```bash
npm run build
```

通过。

### 11.2 后端运行

本地运行：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

GitHub Pages 不能运行 FastAPI，因此前端静态部署后仍需本地或云端后端。

## 12. 代码评审清单

提交前自查：

- 是否在独立分支开发？
- 是否只完成本分支主题？
- 是否更新相关文档？
- 是否没有提交 `.env`、`.venv`、`node_modules`、`dist`？
- 前端修改是否通过 `npm run build`？
- 后端修改是否通过接口冒烟测试？
- API 或 Schema 修改是否同步文档和示例？
- 是否没有暴露 DeepSeek API Key？

## 13. 当前项目推荐工作流

示例：

```bash
git checkout main
git pull
git checkout -b feature/new-topic

# 完成代码或文档

git status
git add .
git commit -m "Add new topic document"
git push -u origin feature/new-topic

git checkout main
git merge --no-ff feature/new-topic -m "Merge new topic document"
git push
```

该流程保证每次开发都有清晰分支记录，也符合当前项目的提交要求。

