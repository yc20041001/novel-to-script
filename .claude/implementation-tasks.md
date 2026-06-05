# Claude 实施任务清单

本文件是给 Claude 使用的编码任务清单。Claude 应一次只执行一个任务，严格遵守允许修改范围和验收标准。

## 任务 1：新增 YAML 校验接口

任务名称：新增 YAML 校验接口

目标：新增 `POST /api/validate-yaml`，校验用户编辑后的 YAML 是否符合 `ScriptDocument`。

相关文档：

- `docs/api-design.md`
- `docs/yaml-schema.md`
- `docs/development-standards.md`

允许修改：

- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/services/yaml_service.py`
- `frontend/src/api/scriptApi.js`

禁止修改：

- `docs/yaml-schema.md`
- `docs/api-design.md`
- `frontend/src/App.jsx`

实现要求：

1. 新增请求模型 `ValidateYamlRequest`，字段为 `yaml`。
2. 新增响应模型 `ValidateYamlResponse`，字段为 `valid` 和 `errors`。
3. 后端解析 YAML 后使用 `ScriptDocument.model_validate` 校验。
4. 前端 API 文件新增 `validateYaml` 方法。

验收标准：

1. 合法 YAML 返回 `valid=true`。
2. 非法 YAML 返回 `valid=false`。
3. 不符合 Schema 的 YAML 返回 `valid=false`。
4. 不破坏 `/api/generate`。

验证命令：

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

## 任务 2：前端组件化

任务名称：前端组件化

目标：将 `frontend/src/App.jsx` 拆分为多个职责清晰的组件。

相关文档：

- `docs/module-breakdown.md`
- `docs/project-directory-design.md`
- `docs/development-standards.md`

允许修改：

- `frontend/src/App.jsx`
- `frontend/src/styles.css`
- `frontend/src/components/`

建议新增：

```text
frontend/src/components/
  AppHeader.jsx
  ChapterCard.jsx
  ChapterList.jsx
  YamlWorkspace.jsx
  SchemaModal.jsx
```

禁止修改：

- `backend/`
- `docs/`

验收标准：

1. 页面功能保持不变。
2. 章节输入、生成、复制、下载、Schema 查看仍可用。
3. `npm run build` 通过。

验证命令：

```bash
cd frontend
npm run build
```

## 任务 3：前端接入 YAML 后端校验

任务名称：前端接入 YAML 后端校验

依赖：任务 1 完成。

目标：将当前前端 js-yaml 本地格式校验升级为“本地格式校验 + 后端 Schema 校验”。

允许修改：

- `frontend/src/App.jsx`
- `frontend/src/components/YamlWorkspace.jsx`
- `frontend/src/api/scriptApi.js`

实现要求：

1. 点击校验按钮时调用 `validateYaml`。
2. 后端返回 `valid=true` 时提示校验通过。
3. 后端返回 `valid=false` 时展示错误。
4. 后端不可用时显示友好提示。

验收标准：

1. 合法 YAML 显示成功。
2. 非法 YAML 显示失败。
3. 不影响复制和下载。
4. `npm run build` 通过。

## 任务 4：新增生成选项

任务名称：新增生成选项

目标：支持用户指定剧本类型、风格、目标场景数和语言。

相关文档：

- `docs/api-design.md`
- `docs/yaml-schema.md`

允许修改：

- `backend/app/models.py`
- `backend/app/prompts/script_prompt.py`
- `backend/app/main.py`
- `frontend/src/App.jsx`
- `frontend/src/components/`

实现要求：

1. 后端 `GenerateRequest` 新增可选 `options`。
2. `options` 包含 `genre`、`style`、`target_scene_count`、`language`。
3. Prompt 中使用这些选项。
4. 前端新增选项面板。
5. 旧请求不带 `options` 仍可用。

验收标准：

1. 不填写选项可以生成。
2. 填写选项后会随请求提交。
3. 后端接口兼容旧格式。
4. 前端构建通过。

## 任务 5：后端测试

任务名称：新增后端测试

目标：建立后端基础测试，覆盖核心接口和 YAML 服务。

允许修改：

- `backend/tests/`
- `backend/requirements.txt`

建议新增：

```text
backend/tests/
  test_health.py
  test_schema.py
  test_generate.py
  test_yaml_service.py
```

验收标准：

1. `pytest` 能运行。
2. `/api/health` 测试通过。
3. `/api/schema` 测试通过。
4. `/api/generate` mock 回退测试通过。
5. YAML 输出包含 `metadata:`。

## 任务 6：GitHub Actions

任务名称：新增 GitHub Actions

目标：新增前端构建和后端测试 CI。

允许修改：

- `.github/workflows/`

建议新增：

```text
.github/workflows/frontend-build.yml
.github/workflows/backend-test.yml
```

验收标准：

1. push 或 pull_request 时运行。
2. 前端执行 `npm ci` 和 `npm run build`。
3. 后端安装依赖并运行 pytest。

## 任务 7：答辩演示文档

任务名称：准备答辩演示文档

目标：新增演示脚本和验收清单。

允许修改：

- `docs/demo-script.md`
- `docs/acceptance-checklist.md`
- `README.md`

验收标准：

1. 演示脚本包含完整演示流程。
2. 验收清单覆盖题目要求。
3. README 增加文档入口。

