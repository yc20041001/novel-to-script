# Novel2Script

Novel2Script 是一款 **AI 小说转结构化剧本 YAML 工具**。它面向希望把小说改编成短剧、影视剧、广播剧或舞台剧初稿的作者，支持输入 3 个章节以上的小说文本，通过 DeepSeek API 自动生成可编辑、可校验、可下载的结构化剧本。

项目不仅包含 AI 生成能力，也实现了登录注册、验证码、Redis 缓存、MySQL 数据落库、管理员后台和 GitHub Pages 前端部署，适合作为完整 AI Web 应用进行演示。

## 在线前端

GitHub Pages 前端地址：

```text
https://yc20041001.github.io/novel-to-script/
```

注意：GitHub Pages 只托管静态前端页面。后端 FastAPI、Redis、MySQL 仍需在本地启动，部署版前端默认连接 `http://localhost:8000`。

## 核心功能

- 小说章节输入：支持至少 3 个章节的小说文本
- 文件导入：支持 `.txt` / `.md` 小说文件导入并自动拆分章节
- 生成选项：支持剧本类型、改编风格、目标场景数量、语言设置
- AI 生成：接入 DeepSeek API，将小说章节转换为结构化剧本
- Mock fallback：未配置 API Key 或 AI 调用失败时返回演示剧本
- YAML 工作区：使用 Monaco Editor 编辑生成结果
- YAML 校验：前端 YAML 语法校验 + 后端 Pydantic Schema 校验
- 结果操作：支持复制、下载 YAML、查看 JSON Schema
- 用户认证：登录、注册、退出
- 验证码：验证码存储在 Redis，有效期 1 分钟
- Session：基于 Redis Session + HttpOnly Cookie
- 生成缓存：Redis 优先缓存，MySQL 持久化兜底
- 数据落库：保存用户、项目、章节、生成任务、剧本版本和生成记录
- 管理员后台：Dashboard、用户管理、生成记录管理
- CI：GitHub Actions 前端构建和后端测试

## 技术栈

前端：

- React
- Vite
- Tailwind CSS
- shadcn/ui 风格本地组件
- motion
- Monaco Editor
- axios
- js-yaml

后端：

- Python
- FastAPI
- Pydantic
- PyYAML
- httpx
- Redis
- MySQL

AI：

- DeepSeek API

部署：

- GitHub 托管代码
- GitHub Pages 部署前端
- 后端本地运行

## 项目结构

```text
.
├── backend/
│   ├── app/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── captcha_store.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── session_store.py
│   │   ├── prompts/
│   │   └── services/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docs/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── vite.config.js
├── .claude/
├── .github/workflows/
├── README.md
└── 三章小说样例.txt
```

## 环境要求

- Python 3.11+
- Node.js 20+
- Redis 7+
- MySQL 8+

## 后端配置

进入后端目录：

```bash
cd backend
cp .env.example .env
```

`.env` 中常用配置：

```env
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

FRONTEND_ORIGIN=http://localhost:5173
GITHUB_PAGES_ORIGIN=https://yc20041001.github.io

REDIS_URL=redis://127.0.0.1:6379/0
REDIS_PASSWORD=
SESSION_COOKIE_NAME=novel2script_session
SESSION_TTL_SECONDS=86400
CAPTCHA_TTL_SECONDS=60
GENERATION_CACHE_TTL_SECONDS=604800

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=novel_to_script

DEMO_USERNAME=admin
DEMO_PASSWORD=admin123
```

不要把真实 `.env` 提交到 GitHub。

## 启动 Redis 和 MySQL

Redis 示例：

```bash
redis-server
```

或使用 Docker：

```bash
docker run --name novel2script-redis -p 6379:6379 -d redis:7
```

MySQL 可使用本机服务或 Docker。数据库名默认为：

```text
novel_to_script
```

后端启动时会自动创建需要的数据表。

## 启动后端

```bash
cd /Users/macbbokair/Desktop/七牛云/backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

后端地址：

```text
http://127.0.0.1:8000
```

启动成功时会看到类似输出：

```text
✓ Redis session store connected
✓ Redis captcha store connected
✓ Redis generation cache connected
✓ MySQL generation repository connected
✓ MySQL user repository connected
```

如果 Redis 或 MySQL 不可用，部分功能会回退到内存或跳过落库，适合调试，但完整演示建议启动 Redis 和 MySQL。

## 启动前端

新开一个终端：

```bash
cd /Users/macbbokair/Desktop/七牛云/frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

本地访问：

```text
http://127.0.0.1:5173/
```

也可以访问：

```text
http://127.0.0.1:5173/novel-to-script/
```

## 默认账号

管理员账号：

```text
用户名：admin
密码：admin123
```

普通用户可以在登录页注册。注册需要验证码，验证码有效期 1 分钟。

## 主要页面说明

### 登录 / 注册

- 支持管理员登录
- 支持普通用户注册
- 支持 Redis 验证码
- 支持错误信息格式化，避免接口校验错误导致页面白屏

### 创作工作台

工作流分为四步：

1. 章节输入
2. 生成选项
3. 确认生成
4. 完成内容

生成结果为 YAML，可继续编辑、校验、复制和下载。

### 管理员后台

管理员登录后，顶部会出现“管理后台”入口。

后台功能包括：

- Dashboard 统计
- 用户管理
- 用户角色切换
- 用户启用 / 禁用
- 生成记录查看
- 缓存键、模型、Mock 状态、YAML 行数展示

## YAML 剧本结构

生成结果主要包含：

- `metadata`：剧本标题、类型、语言、版本、梗概
- `source`：来源章节数量和章节标题
- `characters`：人物信息
- `locations`：地点信息
- `scenes`：场景列表
- `beats`：动作、对白、旁白、转场、音效等剧本节拍
- `notes`：补充说明

详细 Schema 见：

```text
docs/yaml-schema.md
```

## 后端接口概览

```text
GET  /api/health
GET  /api/schema
POST /api/generate
POST /api/validate-yaml

GET  /api/auth/captcha
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
POST /api/auth/register

GET   /api/admin/stats
GET   /api/admin/users
PATCH /api/admin/users/{user_id}
GET   /api/admin/generations
```

## 测试

后端测试：

```bash
cd backend
pytest -q
```

当前测试覆盖：

- 健康检查
- Schema 获取
- AI 生成接口
- YAML 校验
- Redis 生成缓存
- 登录 / 注册 / 验证码
- 用户仓库
- 管理员接口

前端构建：

```bash
cd frontend
npm run build
```

## GitHub Pages 部署前端

```bash
cd frontend
npm run deploy
```

部署成功后访问：

```text
https://yc20041001.github.io/novel-to-script/
```

说明：

- GitHub Pages 只部署前端静态页面
- 后端仍需本地启动在 `http://localhost:8000` 或 `http://127.0.0.1:8000`
- 后端 CORS 已允许 GitHub Pages 域名

## GitHub Actions

项目包含两个 CI 工作流：

```text
.github/workflows/frontend-build.yml
.github/workflows/backend-test.yml
```

它们会在相关路径发生变更时运行：

- 前端：安装依赖并执行 `npm run build`
- 后端：安装依赖并执行 `pytest -q`

## 常见问题

### 1. 登录或注册后页面异常

先确认前后端地址一致：

```text
前端：http://127.0.0.1:5173/
后端：http://127.0.0.1:8000
```

如果浏览器缓存了旧前端代码，可以强制刷新：

```text
Cmd + Shift + R
```

### 2. 验证码无法加载

确认后端已启动，并检查 Redis 是否连接成功。

### 3. 生成结果是 Mock

通常是以下原因：

- 未配置 `DEEPSEEK_API_KEY`
- DeepSeek API 调用失败
- 网络不可用

### 4. 管理员后台没有入口

只有角色为 `admin` 的用户会显示“管理后台”入口。

## 项目文档

- [Claude Agent 工作区](.claude/README.md)
- [需求分析文档](docs/requirements-analysis.md)
- [系统架构设计](docs/system-architecture.md)
- [模块拆分设计](docs/module-breakdown.md)
- [数据库设计](docs/database-design.md)
- [API 设计](docs/api-design.md)
- [项目目录设计](docs/project-directory-design.md)
- [开发规范](docs/development-standards.md)
- [Agent 设计](docs/agent-design.md)
- [任务拆分](docs/task-breakdown.md)
- [YAML Schema 文档](docs/yaml-schema.md)
