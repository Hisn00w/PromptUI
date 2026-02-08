# PromptUI

[English](./README_EN.md) | 简体中文

PromptUI 是一个基于 `Vue 3 + FastAPI` 的 Prompt 管理系统，面向真实业务场景。
它支持分类浏览、搜索过滤、代码资产预览、Prompt 创建与发布，以及管理员审核流程。

![PromptUI Introduction](./public/introduction.png)
![PromptUI Page](./public/page.png)

## 功能概览

- 前后端一体化部署（`docker compose`）
- 登录/注册/鉴权（JWT + Refresh Token）
- 首次启动强制管理员初始化（无管理员时进入 `/admin-setup`）
- Prompt 管理（创建、编辑、发布、下线、删除）
- 分类与标签检索
- 代码资产存储（`code_assets`：HTML/CSS/JS）
- 前端基于后端数据渲染预览，不依赖固定本地 demo 组件
- 中英文切换（`vue-i18n`）

## 技术栈

- Frontend: `Vue 3`, `Pinia`, `Vue Router`, `vue-i18n`, `Axios`
- Backend: `FastAPI`, `SQLAlchemy`, `Pydantic`, `Alembic`
- Database: `PostgreSQL`
- Cache: `Redis`
- Deployment: `Docker Compose`

## 快速开始（Docker）

1. 启动全部服务

```bash
docker compose up -d --build
```

2. 访问前端

- `http://localhost:5173/#/`

3. 首次初始化

- 如果系统没有管理员账号，会自动跳转到 `/#/admin-setup`
- 创建第一个账号后，该账号自动成为管理员

## 本地开发（可选）

Frontend:

```bash
npm install
npm run dev
```

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 关键目录

- `src/` 前端源码
- `backend/app/` 后端源码
- `backend/alembic/` 数据库迁移
- `docker-compose.yml` 一体化编排

## 常见问题

- 预览为空：检查条目是否存在 `code_assets.html/css/js` 内容。
- 登录后被重定向：未登录访问受保护路由会跳转 `/#/login` 并携带 `redirect` 参数。
- 强制管理员初始化：当 `GET /api/v1/auth/status` 返回 `needs_admin_setup=true` 时，路由守卫会强制跳转到 `/#/admin-setup`。

## License

MIT
