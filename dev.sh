#!/usr/bin/env bash
# dev.sh — Start all Credo services for local development
# Usage: bash dev.sh  (or: credo from anywhere via .bashrc alias)

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colours ────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
DIM='\033[2m'
RESET='\033[0m'

log() { echo -e "${GREEN}→${RESET} $1"; }
info() { echo -e "${DIM}  $1${RESET}"; }

# ── 1. Database ────────────────────────────────────────
log "Starting database..."
docker compose -f "$ROOT/docker-compose.yml" up -d
info "PostGIS on port 5433"

# ── 2. Backend ─────────────────────────────────────────
log "Starting backend..."
cd "$ROOT/backend"
uvicorn main:app --reload &
BACKEND_PID=$!
info "http://localhost:8000  (API docs: /docs)"

# ── 3. Frontend ────────────────────────────────────────
log "Starting frontend..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
info "http://localhost:5173"

# ── Ready ──────────────────────────────────────────────
echo ""
echo -e "${BLUE}  Credo is running. Press Ctrl+C to stop all services.${RESET}"
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
