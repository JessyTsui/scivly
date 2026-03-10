#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAST_MODE="false"
NO_START="false"

print_help() {
  cat <<'EOF'
Usage: ./rebuild.sh [--fast] [--no-start]

Options:
  --fast, -f      Skip dependency reinstall and perform a lighter cleanup
  --no-start      Clean and reinstall without starting development servers
  --help, -h      Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast|-f)
      FAST_MODE="true"
      shift
      ;;
    --no-start)
      NO_START="true"
      shift
      ;;
    --help|-h)
      print_help
      exit 0
      ;;
    *)
      echo "[rebuild] Unknown option: $1" >&2
      print_help
      exit 1
      ;;
  esac
done

log() {
  printf '[rebuild] %s\n' "$1"
}

kill_port() {
  local port="$1"

  if ! command -v lsof >/dev/null 2>&1; then
    log "lsof is not available, skipping port ${port} cleanup."
    return 0
  fi

  local pids
  pids="$(lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)"

  if [[ -z "${pids}" ]]; then
    log "Port ${port} is already free."
    return 0
  fi

  log "Releasing port ${port} (${pids})."
  for pid in ${pids}; do
    kill "${pid}" 2>/dev/null || true
  done

  sleep 1

  for pid in ${pids}; do
    if kill -0 "${pid}" 2>/dev/null; then
      kill -9 "${pid}" 2>/dev/null || true
    fi
  done
}

clean_frontend() {
  log "Removing frontend caches and generated files."
  rm -rf "${ROOT_DIR}/frontend/.next"
  rm -rf "${ROOT_DIR}/frontend/out"
  rm -rf "${ROOT_DIR}/frontend/dist"
  rm -rf "${ROOT_DIR}/frontend/coverage"

  if [[ "${FAST_MODE}" == "false" ]]; then
    rm -rf "${ROOT_DIR}/frontend/node_modules"
  fi
}

clean_backend() {
  log "Removing backend caches and generated files."
  rm -rf "${ROOT_DIR}/backend/.pytest_cache"
  rm -rf "${ROOT_DIR}/backend/.mypy_cache"
  rm -rf "${ROOT_DIR}/backend/.ruff_cache"
  rm -rf "${ROOT_DIR}/backend/build"
  rm -rf "${ROOT_DIR}/backend/dist"
  rm -rf "${ROOT_DIR}/backend/htmlcov"
  rm -f "${ROOT_DIR}/backend/.coverage"
  rm -f "${ROOT_DIR}/backend/coverage.xml"

  if [[ -d "${ROOT_DIR}/backend" ]]; then
    find "${ROOT_DIR}/backend" -type d -name "__pycache__" -prune -exec rm -rf {} +
    find "${ROOT_DIR}/backend" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
  fi

  if [[ "${FAST_MODE}" == "false" ]]; then
    rm -rf "${ROOT_DIR}/backend/node_modules"
  fi
}

install_frontend() {
  if [[ ! -f "${ROOT_DIR}/frontend/package.json" ]]; then
    log "Frontend package.json not found, skipping frontend install."
    return 0
  fi

  log "Installing frontend dependencies."
  (cd "${ROOT_DIR}/frontend" && npm install)
}

install_backend() {
  if [[ -f "${ROOT_DIR}/backend/package.json" ]]; then
    log "Installing backend Node dependencies."
    (cd "${ROOT_DIR}/backend" && npm install)
    return 0
  fi

  if [[ -f "${ROOT_DIR}/backend/requirements.txt" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      log "Installing backend Python dependencies."
      (cd "${ROOT_DIR}/backend" && python3 -m pip install -r requirements.txt)
    else
      log "Python 3 is not available, skipping backend dependency install."
    fi
    return 0
  fi

  log "No backend dependency manifest found, skipping backend install."
}

echo "=========================================="
if [[ "${FAST_MODE}" == "true" ]]; then
  echo "  Scivly - Fast Rebuild"
else
  echo "  Scivly - Clean Rebuild"
fi
echo "=========================================="

kill_port 3000
kill_port 8000

clean_frontend
clean_backend

if [[ "${FAST_MODE}" == "false" ]]; then
  install_frontend
  install_backend
else
  log "Skipping dependency reinstall in fast mode."
fi

if [[ "${NO_START}" == "true" ]]; then
  log "Rebuild completed without starting development servers."
  exit 0
fi

log "Starting development environment."
exec "${ROOT_DIR}/scripts/dev.sh"
