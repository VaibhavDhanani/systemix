# Systemix

A platform for learning system design: structured lessons, interview-style practice, progress tracking, and 1:1 mentorship.

- Architecture and phase plan: [docs/ROADMAP.md](docs/ROADMAP.md)
- `apps/web` — Next.js (TypeScript, Tailwind)
- `apps/api` — FastAPI (Python 3.13, managed with `uv`)
- `infra/` — local Postgres and Redis (Docker Compose)

## Local development

Requirements: Docker, [uv](https://docs.astral.sh/uv/), Node 24 and pnpm.

```bash
# 1. Postgres (localhost:5442) and Redis (localhost:6389)
docker compose -f infra/docker-compose.yml up -d --wait

# 2. API on http://localhost:8010
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8010

# 3. Web on http://localhost:3000 (proxies /api/* to the API)
cd apps/web
pnpm install
pnpm dev
```

Open http://localhost:3000/status to confirm the web app, API, database and Redis are connected.
API docs: http://localhost:8010/api/docs

## Checks

```bash
# API
cd apps/api && uv run ruff format --check . && uv run ruff check . && uv run mypy && uv run pytest -m "integration or not integration"

# Web
cd apps/web && pnpm format:check && pnpm lint && pnpm typecheck && pnpm test && pnpm build
```

CI runs the same checks on every pull request.

## Workflow

`main` is protected. Each phase has a branch `phase/<n>-<name>`; work happens on `feat/<n>-<topic>` branches that merge into the phase branch through pull requests. The phase branch merges into `main` after review.
