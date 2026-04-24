# docuview

Document parser service.

## Stack

- Backend: FastAPI + SQLAlchemy + psycopg3 (PostgreSQL 16)
- Frontend: Next.js 14 (App Router, TypeScript, Tailwind)
- PostgreSQL runs on the host (not containerized in dev)

## Quick start

Prerequisites: Python 3.12, Node 20+, PostgreSQL 16 with `archive` database and `archive_agent` role.

```bash
# 1. Python deps
uv sync --extra dev

# 2. Frontend deps
(cd web && npm install)

# 3. Environment
cp .env.example .env
# edit .env: set POSTGRES_PASSWORD

# 4. Run both services
uv run honcho start
```

Then:
- API: http://127.0.0.1:8000
- Web: http://127.0.0.1:3000
- API docs (Swagger): http://127.0.0.1:8000/docs

## Layout

- `src/docuview/` — FastAPI application
- `web/` — Next.js application
- `migrations/` — Alembic migrations
- `tests/` — pytest tests
- `scripts/` — dev/ops shell scripts
- `configs/` — shared configuration files
- `docker/` — Docker files (planned for later)
- `docs/` — project documentation

## Common commands

```bash
uv run uvicorn docuview.main:app --reload   # API only
cd web && npm run dev                        # Web only
uv run pytest                                # Tests
uv run pre-commit run --all-files            # Lint/format
```
