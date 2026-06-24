#!/usr/bin/env bash
# seed.sh — Bring a fresh database to a fully-seeded, working state.
#
# Run this ONCE after a fresh checkout, on a new machine, or after wiping the
# volume (`docker compose down -v`). Day-to-day you do NOT need it — the named
# volume (credo_pgdata) persists data between runs. It's idempotent, so re-running
# is harmless.
#
#   1. ensure the Docker engine (colima) + Postgres are up
#   2. apply all Alembic migrations (schema + the rows seeded inside migrations)
#   3. load county boundary geometry — the one seed step that is NOT a migration
#      (migrations must stay deterministic/offline; this downloads a Census shapefile)
#
# Usage: bash seed.sh
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'; DIM='\033[2m'; RESET='\033[0m'
log()  { echo -e "${GREEN}→${RESET} $1"; }
info() { echo -e "${DIM}  $1${RESET}"; }

if [ ! -x "$ROOT/backend/.venv/bin/python" ]; then
    echo "No venv at backend/.venv — run first:" >&2
    echo "  cd backend && python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
    exit 1
fi

# ── 1. Docker engine + database ────────────────────────
if ! docker info >/dev/null 2>&1; then
    if command -v colima >/dev/null 2>&1; then
        log "Docker engine down — starting colima..."
        colima start
    else
        echo "Docker engine is not running and 'colima' was not found on PATH. Start it and retry." >&2
        exit 1
    fi
fi

log "Starting database..."
docker compose -f "$ROOT/docker-compose.yml" up -d
info "PostGIS on port 5433"

log "Waiting for Postgres to accept connections..."
for _ in $(seq 1 30); do
    if docker compose -f "$ROOT/docker-compose.yml" exec -T db pg_isready -U credo -d credo >/dev/null 2>&1; then
        info "ready"
        break
    fi
    sleep 1
done

cd "$ROOT/backend"

# ── 2. Migrations (schema + seeded rows) ───────────────
log "Applying migrations (alembic upgrade head)..."
.venv/bin/alembic upgrade head

# ── 3. County boundary geometry (downloads Census shapefile) ──
log "Loading county boundaries..."
.venv/bin/python scripts/load_chicago_counties.py

echo ""
log "Database seeded and ready."
info "Inspect it in Beekeeper:  host localhost  port 5433  user credo  pass credo  db credo"
info "Start the app with:  bash dev.sh"
