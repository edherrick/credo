# Credo

A civic accountability platform: browse a shared library of **beliefs, issues, axes, metrics, and entities**, and view any one person's *credo* — their interpretation of that shared data — including a PostGIS-backed choropleth map.

> **Status:** Phase 1, in active development. See [`docs/STATUS.md`](docs/STATUS.md) for what's built and in progress.

## Stack

- **Backend** — FastAPI (Python), PostgreSQL + PostGIS, SQLAlchemy (async), Alembic migrations, FastAPI Users (auth)
- **Frontend** — SvelteKit + Leaflet (choropleth map)
- **Local dev** — Docker Compose for Postgres + PostGIS (engine: [colima](https://github.com/abiosoft/colima))

## Quick start

```sh
# First time only — see backend/ and frontend/ READMEs for the full setup
bash seed.sh          # bootstrap a fresh DB: engine + migrations + county boundaries

# Day-to-day — starts DB, backend, and frontend together
bash dev.sh
```

- Frontend: http://localhost:5173
- Backend API + docs: http://localhost:8000 (`/docs`)

The Vite dev server proxies `/api` → `:8000`, so there are no CORS issues in development. `Ctrl+C` stops backend + frontend; the DB stays up (`docker compose down` to stop it).

## Repo layout

```
credo/
├── README.md            ← you are here
├── CLAUDE.md            ← orientation + working agreements (read this for the full picture)
├── DESIGN.md            ← visual language ("civic cartographic ledger")
├── docs/                ← design docs (symlink to the notes vault): STATUS, Roadmap, Decisions…
├── docker-compose.yml   ← local Postgres + PostGIS
├── dev.sh / seed.sh / test.sh
├── backend/             ← FastAPI app — see backend/README.md
└── frontend/            ← SvelteKit app — see frontend/README.md
```

## Documentation

| Doc | What it covers |
|-----|----------------|
| [`backend/README.md`](backend/README.md) | Backend setup, migrations, testing, structure |
| [`frontend/README.md`](frontend/README.md) | Frontend setup and the lint/check toolchain |
| [`CLAUDE.md`](CLAUDE.md) | Project conventions, route IA, key rules |
| [`DESIGN.md`](DESIGN.md) | Palette, type voices, component primitives |
| `docs/STATUS.md`, `docs/Roadmap.md` | Current phase and milestones |

## Testing

```sh
cd backend && pytest          # backend unit tests
cd frontend && npm run check  # type check
cd frontend && npm run lint   # format + lint + token discipline
cd frontend && npm run test:e2e   # Playwright (needs both servers — bash test.sh)
```

CI runs the frontend (lint, check, build) and backend (migrations, pytest) on every PR and on pushes to `master` — see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
