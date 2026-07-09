# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Panah is a private messaging platform built for meaningful conversations between two people. The repo is a monorepo split into `backend/` (FastAPI + SQLAlchemy + Alembic, Python 3.14, PostgreSQL) and `frontend/` (currently empty — not yet started). The backend is in an early, scaffolding stage.

## Commands

All backend commands are run from the `backend/` directory, which is its own `uv` project (separate `pyproject.toml`/`uv.lock` from the repo root).

```bash
cd backend

# Install dependencies (creates .venv, resolves against uv.lock)
uv sync

# Run the dev server with autoreload (needs DATABASE_URL reachable, e.g. `docker compose up -d db`)
uv run fastapi dev app/main.py

# Add a dependency
uv add <package>

# Create a new migration after changing app/models.py
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

Full stack (Postgres + backend) via Docker, from the repo root:

```bash
docker compose up -d --build
```

The backend container's entrypoint (`backend/docker-entrypoint.sh`) runs `alembic upgrade head` before starting the server, so migrations are applied automatically on every container start. The compose Postgres is exposed on host port `5433` (not `5432`, to avoid clashing with a local Postgres install) — `backend/.env.example` and `app/config.py`'s defaults match this.

There is no test suite, linter, or CI configuration yet — do not assume `pytest`, `ruff`, or similar are set up until you see them added.

## Architecture

- `backend/app/main.py` — FastAPI app instance; mounts routers.
- `backend/app/models.py` — SQLAlchemy ORM models (2.0 `DeclarativeBase`/`Mapped`/`mapped_column` style, not legacy `Column`). `Base` is defined here and reused by all models and by Alembic's `target_metadata`. `User` uses a UUID primary key (`uuid.uuid4` default).
- `backend/app/schemas.py` — Pydantic request/response models (`UserCreate`, `UserRead`, `Token`).
- `backend/app/config.py` — `pydantic-settings` `Settings`, reads from `.env` (see `.env.example`) and env vars: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
- `backend/app/database.py` — async SQLAlchemy engine/session (`asyncpg` driver). `get_db()` is the FastAPI dependency yielding an `AsyncSession`.
- `backend/app/security.py` — password hashing (`bcrypt`) and JWT encode/decode (`pyjwt`).
- `backend/app/deps.py` — `get_current_user` dependency: extracts the bearer token via `OAuth2PasswordBearer`, decodes it, loads the `User` by id.
- `backend/app/routers/auth.py` — `/auth/register` (create user, hashes password), `/auth/login` (OAuth2 password flow, returns a JWT), `/auth/me` (protected, demonstrates `get_current_user`).
- `backend/alembic/` — migrations. `env.py` is wired to `app.config.settings.database_url` and `app.models.Base.metadata`, so autogenerate reflects real model changes; it does not read `sqlalchemy.url` from `alembic.ini`.
- `docker-compose.yml` (repo root) — `db` (Postgres 17) + `backend` services; expects a `frontend` service to be added once that side of the project starts.

Because `app/` has no top-level package name collision issues to worry about, and `fastapi run`/`fastapi dev` rely on `app/__init__.py` existing to resolve `app.*` imports correctly — don't delete it, even though it's empty.
