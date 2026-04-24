#!/usr/bin/env bash
# Запускает API и Web параллельно. Ctrl+C останавливает оба.

set -euo pipefail

cd "$(dirname "$0")/.."

# Поднимаем API в фоне
uv run uvicorn docuview.main:app \
    --host "${API_HOST:-127.0.0.1}" \
    --port "${API_PORT:-8000}" \
    --reload \
    --env-file .env &
API_PID=$!

# Поднимаем Web в фоне
(cd web && npm run dev -- --port "${WEB_PORT:-3000}") &
WEB_PID=$!

# Корректное завершение обоих при Ctrl+C
trap 'echo ""; echo "[dev] stopping..."; kill $API_PID $WEB_PID 2>/dev/null; wait; exit 0' INT TERM

echo "[dev] API pid=$API_PID on :${API_PORT:-8000}"
echo "[dev] Web pid=$WEB_PID on :${WEB_PORT:-3000}"
echo "[dev] Ctrl+C to stop"

wait
