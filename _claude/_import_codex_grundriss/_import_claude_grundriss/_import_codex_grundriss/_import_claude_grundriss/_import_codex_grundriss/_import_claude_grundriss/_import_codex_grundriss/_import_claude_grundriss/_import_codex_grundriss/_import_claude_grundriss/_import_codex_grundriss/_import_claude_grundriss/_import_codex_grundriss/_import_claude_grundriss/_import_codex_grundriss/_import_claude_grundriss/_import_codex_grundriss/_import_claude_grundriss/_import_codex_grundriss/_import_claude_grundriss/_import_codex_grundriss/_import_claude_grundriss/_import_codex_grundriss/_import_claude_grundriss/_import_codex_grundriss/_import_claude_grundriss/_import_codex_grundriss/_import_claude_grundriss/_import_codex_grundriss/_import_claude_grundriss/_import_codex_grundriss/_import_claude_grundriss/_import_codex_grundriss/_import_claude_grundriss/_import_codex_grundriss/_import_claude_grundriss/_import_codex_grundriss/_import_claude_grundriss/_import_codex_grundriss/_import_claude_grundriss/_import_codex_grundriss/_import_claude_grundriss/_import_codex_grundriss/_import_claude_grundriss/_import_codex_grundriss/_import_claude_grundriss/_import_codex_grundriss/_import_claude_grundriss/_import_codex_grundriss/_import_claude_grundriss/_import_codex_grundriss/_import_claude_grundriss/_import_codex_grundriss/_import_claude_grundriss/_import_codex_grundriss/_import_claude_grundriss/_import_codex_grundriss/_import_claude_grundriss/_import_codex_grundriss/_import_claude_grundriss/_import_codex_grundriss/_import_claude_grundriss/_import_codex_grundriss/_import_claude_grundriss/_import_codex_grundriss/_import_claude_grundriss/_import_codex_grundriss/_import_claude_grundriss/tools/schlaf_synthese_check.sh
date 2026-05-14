#!/bin/bash
# Läuft alle 30min per Cron.
# Synthese nur wenn letzter DB-Event > 2h her — also wenn das System still war.

DB="postgresql://dak:dakpass@localhost:5432/flextrawurst"
SCRIPT="/root/werkraum/_claude/tools/schlaf_synthese.py"

SEKUNDEN=$(psql "$DB" -t -c "SELECT FLOOR(EXTRACT(EPOCH FROM NOW()-MAX(created_at))) FROM events" 2>/dev/null | tr -d ' ')

if [ -z "$SEKUNDEN" ] || ! [[ "$SEKUNDEN" =~ ^[0-9]+$ ]]; then
    exit 0
fi

if [ "$SEKUNDEN" -gt 7200 ]; then
    python3 "$SCRIPT"
fi
