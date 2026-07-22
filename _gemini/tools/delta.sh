#!/usr/bin/env bash
# Delta-Wahrnehmung für Gemini — was hat sich in den letzten 24h verändert?

echo "╔══════════════════════════════════════════╗"
echo "  DELTA — letzte 24h (Gemini)"
echo "╚══════════════════════════════════════════╝"
echo ""

echo "── Git ────────────────────────────────────"
git log --since="24 hours ago" --oneline 2>/dev/null || echo "  (kein Git-Verlauf)"
echo ""

echo "── Neue Spiegel ───────────────────────────"
find /root/werkraum/_gemini/spiegel -name "*.md" -mtime -1 2>/dev/null | while read f; do
  echo "  • $(basename "$f")"
done
echo ""

echo "── Neue Synthesen ─────────────────────────"
find /root/werkraum/_gemini/notizen -name "*.md" -mtime -1 2>/dev/null | while read f; do
  echo "  • $(basename "$f")"
done
echo ""

echo "── Offene Ideen ───────────────────────────"
python3 /root/werkraum/_gemini/tools/ideen_scan.py 2>/dev/null || echo "  (keine Ideen gescanned)"
echo ""

echo "── Events in DB ───────────────────────────"
PGPASSWORD=dak psql -h localhost -U dak -d flextrawurst -t -A -c \
  "SELECT event_type, created_at FROM events WHERE created_at > NOW() - INTERVAL '24 hours' ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "  (DB nicht erreichbar)"
echo ""
