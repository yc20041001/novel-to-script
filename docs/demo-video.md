# Novel2Script 演示视频

本文档用于记录 Novel2Script 项目的演示视频地址，便于评审、答辩或项目展示时快速访问。

## 视频链接

- Bilibili 演示视频：<https://www.bilibili.com/video/BV1QbEb6DEr7/>

## 演示内容建议

视频可重点展示以下功能流程：

1. 打开 Novel2Script 前端页面。
2. 使用管理员账号登录。
3. 查看创作工作台的四步流程：章节输入、生成选项、确认生成、完成内容。
4. 导入或编辑 3 个章节以上的小说文本。
5. 设置剧本类型、改编风格、目标场景数量和语言。
6. 调用 AI 生成结构化 YAML 剧本。
7. 在 Monaco Editor 中查看和编辑 YAML。
8. 使用 YAML 校验、复制、下载和 Schema 查看功能。
9. 进入管理员后台，展示 Dashboard、用户管理和生成记录管理。
10. 演示注册普通用户，并说明普通用户与管理员权限差异。

## 项目说明

Novel2Script 是一款 AI 小说转结构化剧本 YAML 工具。系统支持输入 3 个章节以上的小说文本，通过 DeepSeek API 自动生成结构化剧本初稿，并提供 YAML 编辑、Schema 校验、Redis 缓存、MySQL 落库、登录注册、验证码和管理员后台等功能。

## 运行说明

演示视频中的完整功能需要同时启动：

- FastAPI 后端：`http://127.0.0.1:8000`
- React/Vite 前端：`http://127.0.0.1:5173/`
- Redis
- MySQL

GitHub Pages 仅部署前端静态页面，后端服务仍需本地运行。

## 更新时间

2026-06-07
