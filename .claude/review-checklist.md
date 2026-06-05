# Claude 代码提交前检查清单

## 1. 范围检查

- [ ] 是否只修改了本任务相关文件？
- [ ] 是否没有删除 Codex 设计文档？
- [ ] 是否没有大范围重构无关模块？

## 2. 安全检查

- [ ] 是否没有提交 `.env`？
- [ ] 是否没有把 DeepSeek API Key 写入代码？
- [ ] 是否没有在前端调用 DeepSeek API？
- [ ] 是否没有完整打印用户小说正文到日志？

## 3. 前端检查

- [ ] 是否仍使用 React + Vite？
- [ ] 是否仍使用 Ant Design？
- [ ] 是否没有引入 Element Plus？
- [ ] API 请求是否放在 `frontend/src/api/`？
- [ ] 是否运行 `npm run build`？

## 4. 后端检查

- [ ] API 路径是否仍以 `/api/` 开头？
- [ ] 请求/响应字段是否使用 snake_case？
- [ ] Pydantic 模型是否同步更新？
- [ ] YAML 输出是否由 PyYAML 生成？
- [ ] DeepSeek 输出是否先按 JSON 解析？
- [ ] 是否运行后端冒烟测试？

## 5. Schema 检查

- [ ] 是否保持 `docs/yaml-schema.md` 与 `backend/app/models.py` 一致？
- [ ] 是否更新 `examples/sample-output.yaml`？
- [ ] 是否更新 `docs/api-design.md`？

## 6. 交付检查

- [ ] 是否列出修改文件？
- [ ] 是否说明验证命令和结果？
- [ ] 是否说明未完成事项或风险？

