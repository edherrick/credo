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
docs/implementation/Library Architecture.md  ← library-first schema design (Phase 2+)
docs/implementation/Phase 1 Schema.md        ← historical Phase 1 schema (still valid for existing tables)
docs/implementation/Phase 1 API.md           ← authoritative API contract
docs/Decisions.md                            ← architectural decisions log
docs/Tech Stack.md                           ← infrastructure and library choices
```

**Keep `docs/STATUS.md` up to date.** When meaningful progress is made or a session ends mid-task, update the "In Progress / Last Session" and milestone checklist sections.

## Running Locally

```bash
# Regular dev start — starts DB, backend, and frontend in one command
bash dev.sh       # or just: credo  (if .bashrc alias is loaded)
```

- Backend: http://localhost:8000 (API docs: /docs)
- Frontend: http://localhost:5173
- Ctrl+C stops backend + frontend; DB stays running (stop with `docker compose down`)

**First-time / one-off setup steps** (run manually when needed):
```bash
# Backend — from /backend (first time only)
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env

# Database — bootstrap a fresh DB: engine + all migrations + county boundaries.
# Idempotent; run once (or after `docker compose down -v`). From the repo root:
bash seed.sh

# Frontend — from /frontend (first time only)
npm install
```

> The local Docker engine is **colima** (not Docker Desktop) — `dev.sh` / `test.sh` / `seed.sh` start it automatically. Backend commands run through the venv (`.venv/bin/...`); `seed.sh` replaces the old manual `alembic upgrade` + `load_cook_county.py` steps.

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
├── app.css                 ← ALL design tokens live here
├── lib/components/ui/       ← reusable primitives (Button, Field, Card, Section, Badge, EmptyState)
└── routes/
    └── +layout.svelte      ← imports app.css, defines nav styles
```

**Token categories in `app.css`:**

| Prefix | Examples |
|--------|---------|
| `--color-*` | `--color-navy`, `--color-accent`, `--color-text-muted` |
| `--choropleth-*` | `--choropleth-1` … `--choropleth-5` (yellow → red map scale) |
| `--font-*` | `--font-sans` (Inter Variable), `--font-serif`, `--font-mono` |
| `--space-*` | `--space-4` (1rem), `--space-8` (2rem), etc. |
| `--radius-*` | `--radius-sm`, `--radius-md`, `--radius-lg` |
| `--shadow-*` | `--shadow-md`, `--shadow-accent` |
| `--transition-*` | `--transition-fast`, `--transition-base` |
| `--score-*` | `--score-hero` … `--score-villain` (entity accountability scale, green→crimson) |
| `--overlay-*` | white fills/borders/text on the always-navy chrome |

### Design System

`DESIGN.md` (project root) is the source of truth for the visual language — the **"civic cartographic ledger"** identity, palette, the three type voices, and the component primitives. **Reference it when building or modifying any UI.** Key principles:

- **Identity**: deep **navy** surfaces + a **warm accent** reserved for *interactive* signals (CTA, active tab, focus ring) + an **editorial serif**. Data has its own scales (`--choropleth-*` for the map, `--score-*` green→crimson for entity scoring) — never use the brand red to mean "bad."
- **Three type voices**: `--font-serif` = authority (titles, beliefs, hero numbers), `--font-sans` = UI/body (Inter, `"cv01","ss03"` global), `--font-mono` = data & labels (metric values, geo codes, eyebrows, badge labels).
- **Elevation**: background luminance stepping (`--color-bg` → `--color-surface`) + thin cool borders — not heavy shadows.

**Build UI from the primitives** in `lib/components/ui/` (`Button`, `Field`, `Card`, `Section`, `Badge`, `EmptyState`) — typed `variant` props give autocomplete. Don't re-define a button/field/card in a feature file; extend an existing primitive or add a new one.

**Component styles** use scoped `<style>` blocks referencing `var(--token)`, never raw values. Never add `:global()` to a component — global rules belong in `app.css`.

**Stylelint enforces this**: `npm run lint` (or `npm run lint:css`) flags raw `#hex`/`rgba()` where a token belongs and any `var(--typo)` not defined in `app.css` — keeping the token set discoverable and catching drift. (It already caught a missing `--radius-full` and the duplicated score-tier palette.)

## Key Rules

- All API calls go through `frontend/src/lib/api.ts` — never `fetch()` directly in components
- Geometry serialisation via PostGIS `ST_AsGeoJSON()` in SQL — never in Python
- All backend routes under `/api/v1/`
- No SSR for authenticated routes (`export const ssr = false` in `+page.ts`)
- Pydantic schemas in `schemas/` are separate from ORM models in `models/`
- Phase 1 scope only — do not add endpoints or tables not in the spec docs
- Icons: use `lucide-svelte` — never inline SVGs or Unicode arrows/symbols in markup
