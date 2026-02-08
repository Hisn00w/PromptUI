#!/usr/bin/env bash
set -euo pipefail

# 初始化数据库表
python scripts/init_db.py

# 种子数据（可选）
# python scripts/seed_prompt_library.py

UVICORN_ARGS=(app.main:app --host 0.0.0.0 --port 8000)

if [ "${UVICORN_RELOAD:-false}" = "true" ]; then
  UVICORN_ARGS+=(--reload --reload-dir /app/app --reload-dir /app/scripts)
fi

exec uvicorn "${UVICORN_ARGS[@]}"
