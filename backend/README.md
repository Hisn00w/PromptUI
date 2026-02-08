# PromptUI Backend

Production-ready backend scaffold for PromptUI:

- FastAPI + PostgreSQL + Redis
- SQLAlchemy + Alembic
- JWT + Refresh Token rotation
- Strict request/response validation with Pydantic
- Docker Compose deployment

## Quick Start

1. Start services:

```bash
docker compose up --build
```

2. API health check:

```bash
curl http://localhost:8000/health
```

3. API docs:

```text
http://localhost:8000/docs
```

## Environment

Copy `.env.example` to `.env` and update secrets:

```bash
cp backend/.env.example backend/.env
```

For local venv run (without Docker network), use `backend/.env.local.example` as template and point DB/Redis to `localhost`.

## Core API capabilities

- Auth: register/login/refresh/logout/me
- Category management: CRUD
- Prompt lifecycle: draft, submit review, publish, offline, rollback, versions
- Prompt query: server-side search, pagination, sorting
- Interactions: favorite, copy event tracking
- Audit logs: admin query and review queue

## Migration

Inside backend container (or local venv):

```bash
alembic upgrade head
```

## Seed real prompt data

After migration, run inside `backend/` directory:

```bash
python scripts/seed_prompt_library.py
```

## Important routes

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/categories`
- `POST /api/v1/prompts`
- `GET /api/v1/prompts`
- `POST /api/v1/prompts/{id}/submit-review`
- `POST /api/v1/prompts/{id}/publish`
- `POST /api/v1/prompts/{id}/offline`
- `POST /api/v1/interactions/prompts/{id}/favorite`
- `POST /api/v1/interactions/prompts/{id}/copy`
- `GET /api/v1/admin/logs`

