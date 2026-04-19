#!/usr/bin/env bash
# Startet den Claude Code Remote-Control-Server.
#
# Umgebungsvariablen:
#   REMOTE_TOKEN  — Zugriffstoken für den Browser (Standard: "changeme")
#   REMOTE_PORT   — Port (Standard: 8765)
#   REMOTE_HOST   — Bind-Adresse (Standard: 0.0.0.0)
#
# Beispiel:
#   REMOTE_TOKEN=geheimesPasswort ./start_remote.sh

set -euo pipefail

REMOTE_TOKEN="${REMOTE_TOKEN:-changeme}"
REMOTE_PORT="${REMOTE_PORT:-8765}"
REMOTE_HOST="${REMOTE_HOST:-0.0.0.0}"

if [ "$REMOTE_TOKEN" = "changeme" ]; then
  echo "⚠  WARNUNG: Standard-Token 'changeme' wird verwendet."
  echo "   Setze REMOTE_TOKEN=<deinPasswort> für Produktion."
  echo ""
fi

echo "Claude Code Remote-Control startet…"
echo "  URL:   http://<VPS-IP>:${REMOTE_PORT}"
echo "  Token: ${REMOTE_TOKEN}"
echo ""

export REMOTE_TOKEN

exec uvicorn remote_control.server:app \
  --host "$REMOTE_HOST" \
  --port "$REMOTE_PORT" \
  --log-level info
