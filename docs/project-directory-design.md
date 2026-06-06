# 项目目录设计

## 1. 设计目标

Novel2Script 采用前后端分离结构。项目目录设计的目标是让代码、文档、示例和部署配置边界清晰，便于开发、答辩展示、后续扩展和 GitHub 托管。

目录设计原则：

- 前端、后端、文档、示例分区明确。
- 核心代码和生成产物分离。
- 配置模板可以提交，真实密钥不能提交。
- 文档与代码放在同一仓库，保证评审可以完整理解项目。
- 当前保持轻量结构，后续扩展时再拆分更多模块。

## 2. 当前目录总览

```text
novel-to-script/
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       ├── models.py
│       ├── prompts/
│       │   ├── __init__.py
│       │   └── script_prompt.py
│       └── services/
│           ├── __init__.py
│           ├── deepseek_service.py
│           ├── mock_service.py
│           └── yaml_service.py
├── docs/
│   ├── api-design.md
│   ├── database-design.md
│   ├── module-breakdown.md
│   ├── project-directory-design.md
│   ├── requirements-analysis.md
│   ├── system-architecture.md
│   └── yaml-schema.md
├── examples/
│   ├── sample-novel.txt
│   └── sample-output.yaml
└── frontend/
    ├── index.html
    ├── package-lock.json
    ├── package.json
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── styles.css
        ├── api/
        │   └── scriptApi.js
        ├── components/
        │   ├── AppHeader.jsx
        │   ├── ChapterCard.jsx
        │   ├── ChapterList.jsx
        │   ├── GenerationOptions.jsx
        │   ├── SchemaModal.jsx
        │   ├── YamlWorkspace.jsx
        │   └── ui/
        └── lib/
            └── utils.js
```

## 3. 根目录设计

| 路径 | 职责 |
| --- | --- |
| `.gitignore` | 忽略依赖、构建产物、虚拟环境、密钥和缓存文件 |
| `README.md` | 项目入口说明，包括技术栈、运行方式和文档索引 |
| `backend/` | FastAPI 后端代码 |
| `frontend/` | React + Vite 前端代码 |
| `docs/` | 项目设计文档 |
| `examples/` | 示例输入和示例输出 |

根目录不直接放业务代码，避免前端、后端和文档互相混杂。

## 4. backend 目录设计

后端目录负责 API、模型定义、DeepSeek 调用、YAML 转换和配置读取。

```text
backend/
├── .env.example
├── requirements.txt
└── app/
    ├── __init__.py
    ├── config.py
    ├── main.py
    ├── models.py
    ├── prompts/
    └── services/
```

### 4.1 backend/.env.example

配置模板文件，可以提交到 GitHub。

包含：

```text
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
FRONTEND_ORIGIN=http://localhost:5173
```

真实 `.env` 文件不能提交，因为里面会保存 DeepSeek API Key。

### 4.2 backend/requirements.txt

Python 后端依赖列表。

当前包含：

- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- PyYAML
- httpx
- requests
- redis
- python-dotenv

设计原因：使用 `requirements.txt` 便于课程项目快速安装依赖，避免引入更复杂的 Python 包管理工具。

### 4.3 backend/app/main.py

FastAPI 应用入口。

职责：

- 创建 FastAPI 应用。
- 配置 CORS。
- 定义 `/api/health`、`/api/schema`、`/api/generate`、`/api/validate-yaml`。
- 注册认证路由。
- 通过 lifespan 初始化 Redis SessionStore，Redis 不可用时回退到内存存储。
- 串联 DeepSeek 服务、演示回退和 YAML 转换。

### 4.3.1 backend/app/auth.py

登录认证路由。

职责：

- 定义 `/api/auth/login`、`/api/auth/me`、`/api/auth/logout`。
- 登录成功后写入 HttpOnly Session Cookie。
- 退出时删除服务端 Session 并清除 Cookie。

### 4.3.2 backend/app/session_store.py

Session 存储模块。

职责：

- 定义 SessionStore 抽象接口。
- 提供 RedisSessionStore。
- 提供 InMemorySessionStore 作为测试和本地回退方案。

### 4.4 backend/app/models.py

Pydantic 模型定义文件。

职责：

- 定义请求结构。
- 定义剧本 Schema。
- 定义响应结构。
- 支持 `/api/schema` 导出 JSON Schema。

设计原因：当前模型数量不多，集中在一个文件中更容易阅读。后续模型增多后可以拆分为 `schemas/` 或 `models/` 子目录。

### 4.5 backend/app/config.py

配置读取模块。

职责：

- 从环境变量和 `.env` 读取后端配置。
- 提供 `get_settings()` 给其他模块使用。
- 避免在业务代码中直接读取环境变量。

### 4.6 backend/app/prompts/

Prompt 模板目录。

当前文件：

```text
script_prompt.py
```

职责：

- 保存 DeepSeek system prompt。
- 根据小说章节构造 user prompt。
- 约束 AI 输出合法 JSON。

设计原因：Prompt 是 AI 应用的重要资产，单独放在 `prompts/` 下方便调优、版本化和后续增加多种生成风格。

### 4.7 backend/app/services/

后端服务模块目录。

当前文件：

| 文件 | 职责 |
| --- | --- |
| `deepseek_service.py` | 调用 DeepSeek API，解析 JSON，校验为 ScriptDocument |
| `mock_service.py` | 无 API Key 或 AI 失败时返回演示剧本 |
| `yaml_service.py` | 将 ScriptDocument 转换为 YAML |

设计原因：服务模块承载业务流程，避免把所有逻辑写在 API 路由中。

## 5. frontend 目录设计

前端目录负责页面交互、章节输入、YAML 展示、复制下载和 Schema 查看。

```text
frontend/
├── index.html
├── package-lock.json
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── vite.config.js
└── src/
    ├── App.jsx
    ├── main.jsx
    ├── styles.css
    ├── api/
    │   └── scriptApi.js
    ├── components/
    │   ├── AppHeader.jsx
    │   ├── ChapterCard.jsx
    │   ├── ChapterList.jsx
    │   ├── GenerationOptions.jsx
    │   ├── SchemaModal.jsx
    │   ├── YamlWorkspace.jsx
    │   └── ui/
    └── lib/
        └── utils.js
```

### 5.1 frontend/package.json

前端依赖和脚本配置。

核心脚本：

| 脚本 | 说明 |
| --- | --- |
| `npm run dev` | 本地启动 Vite 开发服务器 |
| `npm run build` | 构建生产静态资源 |
| `npm run preview` | 本地预览构建产物 |
| `npm run deploy` | 构建并发布到 GitHub Pages |

### 5.2 frontend/vite.config.js

Vite 配置文件。

当前职责：

- 启用 React 插件。
- 配置开发端口 `5173`。
- 配置 GitHub Pages 子路径 `base: '/novel-to-script/'`。

### 5.3 frontend/tailwind.config.js 和 frontend/postcss.config.js

Tailwind CSS 配置文件。

职责：

- 配置 Tailwind 扫描的文件范围。
- 定义 shadcn/ui 风格的颜色 token、圆角和主题变量。
- 配置 PostCSS 让 Vite 构建 Tailwind 样式。

### 5.4 frontend/src/main.jsx

React 应用入口。

职责：

- 挂载 React 应用。
- 引入 Tailwind CSS 全局样式。
- 挂载 TooltipProvider 和 ToastProvider。
- 为 shadcn/ui 风格组件和 motion toast 动效提供运行环境。

### 5.5 frontend/src/App.jsx

当前主页面组件。

职责：

- 管理章节输入状态。
- 调用后端生成接口。
- 展示 YAML 编辑器。
- 支持复制、下载和 YAML 格式校验。
- 展示 JSON Schema 弹窗。

设计原因：`App.jsx` 保留页面状态和业务方法，具体 UI 交给 `components/` 内的组件负责。

### 5.6 frontend/src/components/

前端页面组件目录。

当前文件：

| 文件 | 职责 |
| --- | --- |
| `AppHeader.jsx` | 顶部标题、章节数和 API 地址 |
| `ChapterCard.jsx` | 单个章节标题和正文编辑 |
| `ChapterList.jsx` | 章节列表、添加章节和章节校验提示 |
| `GenerationOptions.jsx` | 剧本类型、改编风格、目标场景数量和语言设置 |
| `YamlWorkspace.jsx` | YAML 编辑器、生成、校验、复制、下载和 Schema 按钮 |
| `SchemaModal.jsx` | JSON Schema 弹窗 |
| `ui/` | shadcn/ui 风格基础组件 |

### 5.7 frontend/src/components/ui/

本地 UI 基础组件目录。

职责：

- 保存 shadcn/ui 风格的 Button、Card、Input、Dialog、Tooltip、Toast 等基础组件。
- 避免引入大型运行时 UI 框架。
- 让页面样式由 Tailwind CSS 控制。

### 5.8 frontend/src/lib/

前端工具函数目录。

当前文件：

```text
utils.js
```

职责：

- 提供 `cn()` 工具函数，用于合并 Tailwind className。

### 5.9 frontend/src/api/

前端 API 封装目录。

当前文件：

```text
scriptApi.js
authApi.js
```

职责：

- 配置 API Base URL。
- 封装 `generateScript`。
- 封装 `fetchSchema`。
- 封装 `validateYaml`。
- 封装 `login`、`checkAuth`、`logout`。

设计原因：API 调用集中封装，页面组件不直接拼接 URL，便于后续替换后端地址和统一错误处理。

### 5.10 frontend/src/styles.css

全局样式文件。

职责：

- 引入 Tailwind base、components、utilities。
- 定义 shadcn/ui 风格主题变量。
- 定义页面布局。
- 定义左右工作区。
- 定义编辑器容器样式。
- 处理移动端响应式布局。

## 6. docs 目录设计

文档目录用于保存项目分析、设计和说明类交付物。

```text
docs/
├── requirements-analysis.md
├── system-architecture.md
├── module-breakdown.md
├── database-design.md
├── api-design.md
├── project-directory-design.md
└── yaml-schema.md
```

文档职责：

| 文档 | 说明 |
| --- | --- |
| `requirements-analysis.md` | 说明项目背景、用户、需求和验收标准 |
| `system-architecture.md` | 说明系统整体如何实现 |
| `module-breakdown.md` | 说明前端、后端、AI、部署等模块拆分 |
| `database-design.md` | 说明未来落库时的实体、表结构和索引 |
| `api-design.md` | 说明前后端 API 契约 |
| `project-directory-design.md` | 说明项目目录组织方式 |
| `yaml-schema.md` | 定义剧本 YAML Schema 并说明设计原因 |

设计原因：课程或答辩项目通常需要文档完整性，`docs/` 可以作为评审入口。

## 7. examples 目录设计

示例目录用于稳定演示。

```text
examples/
├── sample-novel.txt
└── sample-output.yaml
```

### 7.1 sample-novel.txt

包含至少 3 个章节的示例小说文本。用于演示输入，也用于说明题目要求已覆盖。

### 7.2 sample-output.yaml

包含一份示例 YAML 剧本输出。用于：

- 展示最终效果。
- 在 AI API 不可用时辅助答辩。
- 帮助理解 YAML Schema。

## 8. 不应提交的目录和文件

以下内容不应提交到 GitHub：

| 路径 | 原因 |
| --- | --- |
| `frontend/node_modules/` | 前端依赖，可通过 npm install 生成 |
| `frontend/dist/` | 前端构建产物，可通过 npm run build 生成 |
| `backend/.venv/` | Python 虚拟环境，可重新创建 |
| `backend/.env` | 包含真实 DeepSeek API Key |
| `__pycache__/` | Python 运行缓存 |
| `.DS_Store` | macOS 系统文件 |
| `*.log` | 日志文件 |

这些规则已经写入 `.gitignore`。

## 9. 后续扩展目录建议

如果项目继续扩展，建议按以下方式演进。

### 9.1 前端组件化

```text
frontend/src/
├── api/
├── components/
│   ├── AppHeader.jsx
│   ├── ChapterCard.jsx
│   ├── ChapterList.jsx
│   ├── SchemaModal.jsx
│   ├── Toolbar.jsx
│   └── YamlEditor.jsx
├── pages/
│   └── Home.jsx
├── hooks/
│   └── useScriptGeneration.js
└── utils/
    └── yamlUtils.js
```

适用场景：前端交互变复杂，需要复用组件或增加页面。

### 9.2 后端数据库化

```text
backend/app/
├── api/
│   └── routes/
├── db/
│   ├── session.py
│   └── models.py
├── repositories/
├── schemas/
├── services/
└── migrations/
```

适用场景：引入数据库、项目保存、剧本版本管理和用户系统。

### 9.3 测试目录

```text
backend/tests/
frontend/src/__tests__/
```

建议测试内容：

- 后端 API 接口测试。
- Pydantic Schema 校验测试。
- YAML 转换测试。
- 前端章节校验和按钮交互测试。

### 9.4 CI/CD 目录

```text
.github/
└── workflows/
    ├── frontend-build.yml
    └── backend-test.yml
```

适用场景：需要 GitHub Actions 自动构建、测试和部署。

## 10. 命名规范

### 10.1 文件和目录

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| 文档文件 | kebab-case | `api-design.md` |
| Python 文件 | snake_case | `deepseek_service.py` |
| React 组件 | PascalCase | `ChapterCard.jsx` |
| JS 工具文件 | camelCase 或 kebab-case | `scriptApi.js` |
| 分支名 | feature/主题 | `feature/api-design` |

### 10.2 后端模块

- API 路由放在 `main.py` 或后续 `api/routes/`。
- 数据模型放在 `models.py` 或后续 `schemas/`。
- 业务逻辑放在 `services/`。
- Prompt 模板放在 `prompts/`。

### 10.3 前端模块

- 页面级组件放在 `pages/`。
- 可复用 UI 放在 `components/`。
- API 请求放在 `api/`。
- 通用工具函数放在 `utils/`。
- 自定义 Hook 放在 `hooks/`。

## 11. 目录验收标准

| 项目 | 标准 |
| --- | --- |
| 前后端分离 | `frontend/` 和 `backend/` 职责明确 |
| 文档完整 | 设计文档统一放在 `docs/` |
| 示例可见 | 示例输入和输出放在 `examples/` |
| 配置安全 | 只提交 `.env.example`，不提交 `.env` |
| 构建产物隔离 | `node_modules`、`dist`、`.venv` 不进入 Git |
| 扩展清晰 | 文档说明后续组件化、数据库化和测试目录 |
