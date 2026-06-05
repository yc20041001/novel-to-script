# Novel2Script

Novel2Script 是一款 AI 小说转结构化剧本工具，面向希望把小说改编为剧本初稿的作者。系统支持输入 3 个章节以上的小说文本，通过 DeepSeek API 生成符合 YAML Schema 的结构化剧本，便于作者继续编辑、校验和下载。

## 技术栈

- 前端：React + Vite + Ant Design + Monaco Editor + axios + js-yaml
- 后端：Python + FastAPI + PyYAML + Pydantic + httpx
- AI：DeepSeek API
- Schema：Markdown 文档 + Pydantic 模型 + JSON Schema 思路
- 部署：本地运行 + GitHub 托管代码 + GitHub Pages 部署前端

## 项目结构

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── config.py
│   │   ├── prompts/
│   │   └── services/
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── requirements-analysis.md
│   └── yaml-schema.md
├── examples/
│   ├── sample-novel.txt
│   └── sample-output.yaml
└── frontend/
    ├── src/
    ├── package.json
    └── vite.config.js
```

## 本地运行

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

在 `.env` 中配置 `DEEPSEEK_API_KEY` 后即可调用真实模型。未配置 API Key 时，后端会返回示例脚本，方便本地演示。

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。

## GitHub Pages 部署前端

```bash
cd frontend
npm install
npm run deploy
```

GitHub Pages 只能托管静态前端，FastAPI 后端仍需本地运行，或后续部署到 Render、Railway、Fly.io 等服务。

## 文档

- [需求分析文档](docs/requirements-analysis.md)
- [系统架构设计](docs/system-architecture.md)
- [YAML Schema 文档](docs/yaml-schema.md)
