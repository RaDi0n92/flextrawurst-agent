#!/usr/bin/env bash
set -euo pipefail

WERKRAUM="${FLEXTRAWURST_WERKRAUM:-/root/werkraum}"
TARGET="$WERKRAUM/engine/godot-vertical-slice"
BACKUP_ROOT="$WERKRAUM/backups/godot-vertical-slice"
UNIT_NAME="flextrawurst-godot-world-bridge.service"
UNIT_PATH="/etc/systemd/system/$UNIT_NAME"
SNAPSHOT_DIR="${1:-}"

[[ "$(id -u)" -eq 0 ]] || { echo "Muss als root laufen" >&2; exit 1; }

if [[ -z "$SNAPSHOT_DIR" ]]; then
  SNAPSHOT_DIR="$(find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort | tail -n1 || true)"
  [[ -n "$SNAPSHOT_DIR" ]] && SNAPSHOT_DIR="$BACKUP_ROOT/$SNAPSHOT_DIR"
fi

[[ -n "$SNAPSHOT_DIR" && -f "$SNAPSHOT_DIR/snapshot.json" ]] || {
  echo "Kein gültiger Snapshot gefunden" >&2
  exit 1
}

readarray -t META < <(python3 - "$SNAPSHOT_DIR/snapshot.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
for key in ("target_existed", "unit_existed", "unit_was_active", "unit_was_enabled"):
    print(1 if value.get(key) else 0)
PY
)
TARGET_EXISTED="${META[0]}"
UNIT_EXISTED="${META[1]}"
UNIT_WAS_ACTIVE="${META[2]}"
UNIT_WAS_ENABLED="${META[3]}"

systemctl stop "$UNIT_NAME" 2>/dev/null || true

if [[ "$TARGET_EXISTED" -eq 1 ]]; then
  rm -rf "$TARGET"
  mkdir -p "$TARGET"
  rsync -a "$SNAPSHOT_DIR/project/" "$TARGET/"
else
  rm -rf "$TARGET"
fi

if [[ "$UNIT_EXISTED" -eq 1 ]]; then
  cp -a "$SNAPSHOT_DIR/$UNIT_NAME" "$UNIT_PATH"
else
  rm -f "$UNIT_PATH"
fi

systemctl daemon-reload
if [[ "$UNIT_WAS_ENABLED" -eq 1 ]]; then
  systemctl enable "$UNIT_NAME" >/dev/null 2>&1 || true
else
  systemctl disable "$UNIT_NAME" >/dev/null 2>&1 || true
fi
if [[ "$UNIT_WAS_ACTIVE" -eq 1 ]]; then
  systemctl start "$UNIT_NAME"
fi

echo "FLEXTRAWURST_GODOT_VPS_ROLLBACK_PASS: $SNAPSHOT_DIR"
