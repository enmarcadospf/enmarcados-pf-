#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [ -f ".env.backend" ]; then
  set -a
  source .env.backend
  set +a
fi

exec .venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
