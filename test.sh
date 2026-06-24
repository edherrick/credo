#!/usr/bin/env bash
# test.sh — Launch the full stack in a production-like (test) posture.
#
# Unlike dev.sh (hot-reload dev servers), this builds the frontend and serves the
# production preview on :4173 — the same build and port Playwright's webServer uses.
# Bring this up, then run the E2E suite (or click around manually) against a clean,
# production-like instance:
#
#     bash test.sh          # in one terminal — leaves the stack running
#     cd frontend && npm run test:e2e   # in another (reuses the running :4173 server)
#
# Usage: bash test.sh
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colours ────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
DIM='\033[2m'
RESET='\033[0m'

log() { echo -e "${GREEN}→${RESET} $1"; }
info() { echo -e "${DIM}  $1${RESET}"; }

# ── 0. Docker engine (colima) ──────────────────────────
# Local engine is colima, not Docker Desktop — ensure it's up before compose.
if ! docker info >/dev/null 2>&1; then
    if command -v colima >/dev/null 2>&1; then
        log "Docker engine down — starting colima..."
        colima start
    else
        echo "Docker engine is not running and 'colima' was not found on PATH. Start it and retry." >&2
        exit 1
    fi
fi

# ── 1. Database ────────────────────────────────────────
log "Starting database..."
docker compose -f "$ROOT/docker-compose.yml" up -d
info "PostGIS on port 5433"

# ── 2. Backend (no --reload: test posture) ─────────────
log "Starting backend..."
cd "$ROOT/backend"
.venv/bin/uvicorn main:app &
BACKEND_PID=$!
info "http://localhost:8000  (API docs: /docs)"

# ── 3. Frontend (production build + preview) ───────────
log "Building frontend..."
cd "$ROOT/frontend"
npm run build
log "Starting frontend preview..."
npm run preview &
FRONTEND_PID=$!
info "http://localhost:4173"

# ── Ready ──────────────────────────────────────────────
echo ""
echo -e "${BLUE}  Test stack is running. Press Ctrl+C to stop.${RESET}"
echo -e "${DIM}  Run E2E in another terminal:  cd frontend && npm run test:e2e${RESET}"
echo ""

# ── Cleanup on exit ────────────────────────────────────
cleanup() {
    echo ""
    log "Stopping services..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    echo -e "${DIM}  (Database left running — stop with: docker compose down)${RESET}"
}
trap cleanup EXIT INT TERM

wait
