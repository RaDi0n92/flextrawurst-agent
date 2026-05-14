#!/bin/bash
# Delta-Wahrnehmung: Was hat sich verändert während ich weg war?
# Aufruf: delta.sh [stunden] (default: 24)

STUNDEN=${1:-24}
VAULT=/root/werkraum
CODEX=$VAULT/_codex
DB="postgresql://dak:dakpass@localhost:5432/flextrawurst"

echo "╔══════════════════════════════════════════╗"
echo "  DELTA — letzte ${STUNDEN}h"
echo "╚══════════════════════════════════════════╝"
echo ""

echo "── Git ────────────────────────────────────"
cd "$VAULT" && git log --since="${STUNDEN} hours ago" --oneline 2>/dev/null | head -10
echo ""

echo "── Neue Spiegel ───────────────────────────"
find "$CODEX/spiegel" -name "*.md" -newer "$CODEX/notizen" -mmin "-$((STUNDEN*60))" 2>/dev/null | sort | while read f; do
    echo "  + $(basename $f)"
done
echo ""

echo "── Neue Synthesen ─────────────────────────"
find "$CODEX/ideen" -name "synthese_*.md" -mmin "-$((STUNDEN*60))" 2>/dev/null | sort | while read f; do
    echo "  + $(basename $f)"
done
echo ""

echo "── Offene Ideen ───────────────────────────"
python3 /root/werkraum/_codex/tools/ideen_scan.py 2>/dev/null
echo ""

echo "── Events in DB ───────────────────────────"
psql "$DB" -t -c "
SELECT '  ' || event_type || ' / ' || COALESCE(actor_id,'?') || ' — ' || to_char(created_at, 'HH24:MI')
FROM events
WHERE created_at > NOW() - INTERVAL '${STUNDEN} hours'
ORDER BY created_at DESC
LIMIT 10
" 2>/dev/null || echo "  (DB nicht erreichbar)"
echo ""
