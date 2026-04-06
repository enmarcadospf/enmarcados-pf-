#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [ -f ".env.backend" ]; then
  set -a
  source .env.backend
  set +a
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

exec .venv/bin/uvicorn backend.main:app --host "$HOST" --port "$PORT"
