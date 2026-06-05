# Claude 编码任务模板

把下面模板复制给 Claude，用于开始一次明确的编码任务。

```text
你是 Novel2Script 项目的 Claude 编码 Agent。

任务名称：

任务目标：

背景说明：

相关设计文档：
- docs/development-standards.md
- docs/api-design.md
- docs/yaml-schema.md
- docs/system-architecture.md

允许修改的文件/目录：
-

禁止修改的文件/目录：
-

实现要求：
1.
2.
3.

验收标准：
1.
2.
3.

需要运行的验证命令：
前端：
cd frontend && npm run build

后端：
cd backend && source .venv/bin/activate && python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
assert client.get("/api/health").status_code == 200
assert client.get("/api/schema").status_code == 200
PY

输出要求：
- 说明完成内容
- 列出修改文件
- 给出验证结果
- 说明风险或未完成事项
```

