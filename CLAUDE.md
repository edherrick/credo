# Credo — Claude Code Context

## Stack

- **Backend**: FastAPI (Python), PostgreSQL + PostGIS, Alembic migrations, FastAPI Users (auth)
- **Frontend**: SvelteKit + Leaflet (choropleth map)
- **Local dev**: Docker Compose for Postgres + PostGIS

## Repo Layout

```
credo/
├── CLAUDE.md              ← you are here
├── docker-compose.yml     ← local Postgres + PostGIS
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/versions/  ← 8 numbered migrations
│   ├── main.py            ← FastAPI app entry point
│   ├── database.py        ← async engine + get_db dep
│   ├── models/            ← SQLAlchemy ORM models
│   ├── schemas/           ← Pydantic response shapes
│   ├── routes/            ← API route handlers
│   └── scripts/           ← one-off data scripts
└── frontend/
    └── src/
        ├── app.css              ← design tokens + global reset (single source of truth)
        ├── lib/
        │   ├── api.ts           ← all API calls (no fetch in components)
        │   ├── types.ts
        │   ├── stores/auth.ts   ← auth store
        │   └── components/MetricMap.svelte
        └── routes/              ← SvelteKit pages (+layout imports app.css)
```

## Design Docs

`docs/` is a symlink to the notes vault at `/home/ed/Documents/notes/projects/credo`.

**At the start of every session, read these files to orient yourself:**

1. `docs/STATUS.md` — current phase, what's built, what's in progress, uncommitted changes
2. `docs/Roadmap.md` — phase overview and Phase 1 milestones

Then read these as needed:

```
docs/implementation/Phase 1 Schema.md   ← authoritative DB schema
docs/implementation/Phase 1 API.md      ← authoritative API contract
docs/Decisions.md                       ← architectural decisions log
docs/Tech Stack.md                      ← infrastructure and library choices
```

**Keep `docs/STATUS.md` up to date.** When meaningful progress is made or a session ends mid-task, update the "In Progress / Last Session" and milestone checklist sections.

## Running Locally

```bash
# 1. Start the database (PostGIS on port 5433 — avoids conflict with any local Postgres on 5432)
docker compose up -d

# 2. Backend — from /backend
pip install -e ".[dev]"          # first time only
cp .env.example .env             # first time only
alembic upgrade head             # first time, or after new migrations
uvicorn main:app --reload        # runs on http://localhost:8000

# 3. Load Cook County boundary (one-time, after backend is up)
python scripts/load_cook_county.py

# 4. Frontend — from /frontend
npm install                      # first time only
npm run dev                      # runs on http://localhost:5173
```

API docs available at `http://localhost:8000/docs` when backend is running.

The Vite dev server proxies `/api` → `http://localhost:8000`, so no CORS issues during development.

## Testing

```bash
# Backend unit tests
cd backend && pytest

# Frontend type check
cd frontend && npm run check

# Frontend unit tests
cd frontend && npm run test:unit

# Frontend E2E tests (requires both servers running)
cd frontend && npm run test:e2e
```

## Frontend Styling

All design tokens (colors, fonts, spacing, radii, shadows) are defined as CSS custom properties in `frontend/src/app.css` and imported once in `+layout.svelte`. This is the single source of truth for the visual theme.

**To change a color or spacing value**, edit `app.css` — it propagates everywhere automatically.

```
frontend/src/
├── app.css               ← ALL design tokens live here
└── routes/
    └── +layout.svelte    ← imports app.css, defines nav styles
```

**Token categories in `app.css`:**

| Prefix | Examples |
|--------|---------|
| `--color-*` | `--color-navy`, `--color-accent`, `--color-text-muted` |
| `--choropleth-*` | `--choropleth-1` … `--choropleth-5` (yellow → red map scale) |
| `--font-*` | `--font-sans`, `--font-serif`, `--font-mono` |
| `--space-*` | `--space-4` (1rem), `--space-8` (2rem), etc. |
| `--radius-*` | `--radius-sm`, `--radius-md`, `--radius-lg` |
| `--shadow-*` | `--shadow-md`, `--shadow-accent` |
| `--transition-*` | `--transition-fast`, `--transition-base` |

**Component styles** use scoped `<style>` blocks (class names don't leak) but reference `var(--token)` instead of raw hex values:

```svelte
<!-- ✓ correct -->
<style>
  .card { border: 1px solid var(--color-border); border-radius: var(--radius-lg); }
  .card:hover { border-color: var(--color-accent); box-shadow: var(--shadow-accent); }
</style>

<!-- ✗ avoid — hardcoded values make theming painful -->
<style>
  .card { border: 1px solid #e8e8e4; border-radius: 10px; }
</style>
```

Never add `:global()` CSS to component files — global rules belong in `app.css`.

## Key Rules

- All API calls go through `frontend/src/lib/api.ts` — never `fetch()` directly in components
- Geometry serialisation via PostGIS `ST_AsGeoJSON()` in SQL — never in Python
- All backend routes under `/api/v1/`
- No SSR for authenticated routes (`export const ssr = false` in `+page.ts`)
- Pydantic schemas in `schemas/` are separate from ORM models in `models/`
- Phase 1 scope only — do not add endpoints or tables not in the spec docs
- Icons: use `lucide-svelte` — never inline SVGs or Unicode arrows/symbols in markup
