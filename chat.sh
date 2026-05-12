#!/usr/bin/env bash
set -euo pipefail
cd /root/werkraum

: "${BRIDGE_API_KEY:?BRIDGE_API_KEY ist nicht gesetzt}"
URL="http://127.0.0.1:8001"

mkdir -p state
touch state/journal.log

echo "Agent Chat gestartet. exit zum Beenden."
echo "Beispiele: status | list | read app/main.py | exec ls -la | exec git status"

while true; do
  read -rp "Du> " CMD
  [ "$CMD" = "exit" ] && break
  [ "$CMD" = "quit" ] && break
  [ -z "$CMD" ] && continue

  /root/werkraum/scripts/journal.sh "PLAN: $CMD" >/dev/null || true
  python3 /root/werkraum/vps_agent_werkbank.py "$CMD" \
    --vps-url "$URL" \
    --api-key "$BRIDGE_API_KEY" \
    --api-style workspace
  /root/werkraum/scripts/journal.sh "VERIFY: $CMD fertig" >/dev/null || true
done
