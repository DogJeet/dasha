#!/usr/bin/env sh
set -eu

MODE="${APP_MODE:-api}"

if [ "$MODE" = "bot" ]; then
  exec python -m bot.main
fi

exec uvicorn api.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
