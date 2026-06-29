# Credo Backend

FastAPI + PostgreSQL/PostGIS API. Async SQLAlchemy, Alembic migrations, FastAPI Users for auth. All routes live under `/api/v1/`.

## Setup (first time)

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env          # set DATABASE_URL + SECRET_KEY
```

The database runs in Docker (Postgres + PostGIS). From the **repo root**, `bash seed.sh` brings a fresh DB to a working state — engine up, all migrations applied, county boundaries loaded. It's idempotent; run it once after a fresh checkout or after `docker compose down -v`.

## Running

```sh
# From the repo root — starts DB + backend + frontend together
bash dev.sh
```

The API is then at http://localhost:8000, with interactive docs at **http://localhost:8000/docs**.

## Database & migrations

Schema changes are Alembic migrations in `alembic/versions/`. `alembic/env.py` reads `DATABASE_URL` from the environment and strips the `+asyncpg` driver suffix (Alembic runs sync via `psycopg2`).

```sh
.venv/bin/alembic upgrade head                       # apply all migrations
.venv/bin/alembic revision --autogenerate -m "msg"   # create a new migration
.venv/bin/alembic downgrade -1                        # roll back one
```

Conventions:

- **Geometry is serialised in SQL** via PostGIS `ST_AsGeoJSON()` — never in Python.
- ORM models (`models/`) and Pydantic schemas (`schemas/`) are kept separate.
- Migrations must stay deterministic and offline. The one seed step that isn't a migration — loading county boundary geometry from a Census shapefile — lives in `scripts/` and is run by `seed.sh`.

## Testing

```sh
pytest          # or: .venv/bin/python -m pytest
```

Config is in `pyproject.toml` (`[tool.pytest.ini_options]`): `asyncio_mode = "auto"` (write `async def test_*` with no decorator) and `pythonpath = "."` (so tests can `from main import app`).

`tests/conftest.py` provides a `client` fixture that drives the app in-process over ASGI (no running server, no network). DB-backed tests can add a session fixture alongside it. `tests/test_health.py` is the seed smoke test — copy its shape for new route tests.

## Structure

```
backend/
├── main.py         ← FastAPI app entry point (router wiring, /health, /api/v1/auth/me)
├── database.py     ← async engine + get_db dependency
├── models/         ← SQLAlchemy ORM models
├── schemas/        ← Pydantic request/response shapes
├── serializers.py  ← shared response serialisation helpers
├── routes/         ← API route handlers (one module per domain)
├── scripts/        ← one-off data scripts (boundary loading, scraping, seeding)
├── alembic/        ← migration environment + versions/
└── tests/          ← pytest suite
```

See the root [`CLAUDE.md`](../CLAUDE.md) for project-wide conventions and `docs/implementation/Phase 1 API.md` for the authoritative API contract.
