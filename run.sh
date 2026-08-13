#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo
echo " Mood Code Server"
echo " http://127.0.0.1:5000/"
echo " Stop: Ctrl+C"
echo

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "[setup] .env created from .env.example"
fi

PY_BOOT="${PY_BOOT:-python3}"
if ! command -v "$PY_BOOT" >/dev/null 2>&1; then
  PY_BOOT=python
fi

"$PY_BOOT" scripts/ensure_venv.py

PY="venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "venv python not found after setup"
  exit 1
fi

echo "Python: $PY"
"$PY" --version

if [ ! -f database/shop.db ]; then
  echo "[setup] First run: creating database and sample data..."
  "$PY" scripts/seed_db.py
fi

export MOODCODE_OPEN_URL="${MOODCODE_OPEN_URL:-/}"
exec "$PY" hspace_server.py
