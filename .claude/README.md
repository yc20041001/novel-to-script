# Claude Agent Workspace

本目录用于给 Claude 提供项目级 Agent 设计、协作规则和任务模板。

项目分工：

```text
Codex：负责需求分析、架构设计、API/Schema/数据库/目录/规范等设计方案。
Claude：负责根据 Codex 设计文档生成前端、后端、测试和必要实现代码。
```

Claude 在本项目中不应重新设计系统，而应以 `docs/` 中的设计文档和 `.claude/` 中的工作指令为准完成代码实现。

推荐阅读顺序：

1. `.claude/project-instructions.md`
2. `.claude/agents.md`
3. `.claude/task-template.md`
4. `.claude/implementation-tasks.md`
5. `docs/task-breakdown.md`
6. `docs/development-standards.md`
7. `docs/api-design.md`
8. `docs/yaml-schema.md`
9. `docs/system-architecture.md`
