#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${BACKEND_DIR:-$ROOT_DIR/backend}"
BACKEND_APP_DIR="${BACKEND_APP_DIR:-$BACKEND_DIR/app}"
FRONTEND_DIR="${FRONTEND_DIR:-$ROOT_DIR/frontend}"
UVICORN_CMD="${UVICORN_CMD:-uvicorn}"
UVICORN_APP="${UVICORN_APP:-app.main:app}"
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
NPM_CMD="${NPM_CMD:-npm}"

if [[ ! -f "$BACKEND_APP_DIR/main.py" ]]; then
  echo "Cannot find main.py in $BACKEND_APP_DIR" >&2
  exit 1
fi

if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  echo "Cannot find package.json in $FRONTEND_DIR" >&2
  exit 1
fi

cleanup() {
  local code=${1:-$?}
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
  wait "$BACKEND_PID" 2>/dev/null || true
  wait "$FRONTEND_PID" 2>/dev/null || true
  return $code
}

on_exit() {
  local status=$?
  cleanup "$status"
}

trap on_exit EXIT
trap 'trap - EXIT; cleanup 130; exit 130' INT
trap 'trap - EXIT; cleanup 143; exit 143' TERM

cd "$BACKEND_DIR"
echo "Starting backend: $UVICORN_CMD $UVICORN_APP --reload --host $BACKEND_HOST --port $BACKEND_PORT"
$UVICORN_CMD "$UVICORN_APP" --reload --host "$BACKEND_HOST" --port "$BACKEND_PORT" &
BACKEND_PID=$!

cd "$FRONTEND_DIR"
echo "Starting frontend: $NPM_CMD start"
$NPM_CMD start &
FRONTEND_PID=$!

wait "$BACKEND_PID" || BACKEND_EXIT=$?
wait "$FRONTEND_PID" || FRONTEND_EXIT=$?

exit ${BACKEND_EXIT:-${FRONTEND_EXIT:-0}}
