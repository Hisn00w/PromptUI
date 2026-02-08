# AGENTS.md

## Scope
- This file applies to the whole repository.

## Goals
- Keep frontend and backend behavior consistent.
- Prefer real backend data over local demo data.
- Avoid duplicate templates and repetitive preview content.

## UI Rules
- Do not use blue/purple as primary action colors.
- Primary buttons should use black or neutral dark styles.
- Keep card previews visually distinct; no repeated placeholder template.

## Data Rules
- New prompts must include real `prompt_text`.
- If available, store `code_assets` with `html`, `css`, and `js`.
- Preview should render from backend `code_assets` when present.

## Routing and Auth
- Home entry: `/#/`.
- Force admin setup when backend reports `needs_admin_setup=true`.
- Login/register should support i18n text.

## Quality Checks
- Run with Docker: `docker compose up -d --build`.
- Verify API status: `GET /api/v1/auth/status`.
- Verify no hardcoded Chinese/English in shared layout components.

## Docker Hot Reload
- Start dev services with hot reload:
  - Frontend: `docker compose up -d frontend` (bind-mounted source, Vite watch mode).
  - Backend: `docker compose up -d backend` (uvicorn should run with `--reload` in dev).
- View live logs:
  - Frontend logs: `docker compose logs -f frontend`
  - Backend logs: `docker compose logs -f backend`
- Rebuild when dependency files change (e.g. `package.json`, Python deps, Dockerfile):
  - `docker compose up -d --build`
- If file watching is unstable on Windows/WSL, enable polling in container env:
  - `CHOKIDAR_USEPOLLING=true` (frontend)

## Notes
- Keep docs (`README.md`, `README_EN.md`) aligned with actual behavior.
- Remove dead code and unused style/demo modules promptly.
