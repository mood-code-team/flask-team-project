#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PY="${PY:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python
fi

echo
echo " Mood Code Server"
echo " http://127.0.0.1:5000/"
echo " Stop: Ctrl+C"
echo

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "[setup] .env created from .env.example"
fi

"$PY" -m pip install -r requirements.txt -q

if [ ! -f database/shop.db ]; then
  echo "[setup] First run: creating database and sample data..."
  "$PY" scripts/seed_db.py
fi

exec "$PY" hspace_server.py
