#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"
BACKEND_DIR="${ROOT_DIR}/backend"
PIDS=()
LABELS=()

log() {
  printf '[dev] %s\n' "$1"
}

cleanup() {
  local pid

  for pid in "${PIDS[@]:-}"; do
    if kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
    fi
  done
}

trap cleanup EXIT INT TERM

start_process() {
  local label="$1"
  shift

  log "Starting ${label}."
  "$@" &
  PIDS+=("$!")
  LABELS+=("${label}")
}

has_backend_node_dev_script() {
  [[ -f "${BACKEND_DIR}/package.json" ]] || return 1

  node -e "const pkg=require(process.argv[1]); process.exit(pkg.scripts && pkg.scripts.dev ? 0 : 1)" \
    "${BACKEND_DIR}/package.json"
}

has_backend_python_entrypoint() {
  [[ -f "${BACKEND_DIR}/app/main.py" ]]
}

start_frontend() {
  [[ -f "${FRONTEND_DIR}/package.json" ]] || return 1
  start_process "frontend" bash -lc "cd '${FRONTEND_DIR}' && npm run dev"
}

start_backend() {
  if has_backend_node_dev_script; then
    start_process "backend" bash -lc "cd '${BACKEND_DIR}' && npm run dev"
    return 0
  fi

  if has_backend_python_entrypoint; then
    if python3 -c "import uvicorn" >/dev/null 2>&1; then
      start_process "backend" bash -lc "cd '${BACKEND_DIR}' && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
      return 0
    fi

    log "backend/app/main.py exists but uvicorn is not installed; skipping backend."
    return 0
  fi

  log "No backend entrypoint found yet; starting frontend only."
  return 0
}

monitor_processes() {
  while true; do
    local index

    for index in "${!PIDS[@]}"; do
      local pid="${PIDS[$index]}"
      local label="${LABELS[$index]}"

      if ! kill -0 "${pid}" 2>/dev/null; then
        local status=0
        wait "${pid}" || status=$?
        log "${label} exited."
        return "${status}"
      fi
    done

    sleep 1
  done
}

echo "=========================================="
echo "  Scivly Development Environment"
echo "=========================================="

start_frontend || {
  log "frontend/package.json is missing, nothing to start."
  exit 1
}

start_backend

log "Frontend expected at http://localhost:3000"
if ((${#PIDS[@]} > 1)); then
  log "Backend expected at http://localhost:8000"
fi

monitor_processes
