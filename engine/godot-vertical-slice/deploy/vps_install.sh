#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="${FLEXTRAWURST_AGENT_REPO_URL:-https://github.com/RaDi0n92/flextrawurst-agent.git}"
BRANCH="${FLEXTRAWURST_ENGINE_BRANCH:-engine/godot-vertical-slice-001}"
WERKRAUM="${FLEXTRAWURST_WERKRAUM:-/root/werkraum}"
TARGET="$WERKRAUM/engine/godot-vertical-slice"
RUNTIME="$WERKRAUM/engine_runtime/godot-vertical-slice"
BACKUP_ROOT="$WERKRAUM/backups/godot-vertical-slice"
UNIT_NAME="flextrawurst-godot-world-bridge.service"
UNIT_PATH="/etc/systemd/system/$UNIT_NAME"
BRIDGE_PORT="${FLEXTRAWURST_GODOT_BRIDGE_PORT:-18092}"
BRIDGE_URL="http://127.0.0.1:$BRIDGE_PORT"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$BACKUP_ROOT/$STAMP"
STAGE="$(mktemp -d /tmp/flextrawurst-godot-install.XXXXXX)"
LOG_DIR="$RUNTIME/installations/$STAMP"

mkdir -p "$LOG_DIR" "$BACKUP_DIR"
exec > >(tee "$LOG_DIR/install.log") 2>&1

[[ "$(id -u)" -eq 0 ]] || { echo "Muss als root laufen" >&2; exit 1; }
[[ "$BRIDGE_PORT" =~ ^[0-9]+$ ]] || { echo "Bridge-Port ist keine Zahl: $BRIDGE_PORT" >&2; exit 1; }
[[ "$BRIDGE_PORT" -ge 1024 && "$BRIDGE_PORT" -le 65535 ]] || { echo "Bridge-Port außerhalb 1024-65535: $BRIDGE_PORT" >&2; exit 1; }
[[ "$BRIDGE_PORT" -ne 8090 ]] || { echo "Port 8090 gehört der bestehenden 3D-MCP-Schicht" >&2; exit 1; }
[[ "$BRIDGE_PORT" -ne 8091 ]] || { echo "Port 8091 gehört dem bestehenden 95-Tool-VPS-MCP" >&2; exit 1; }

require_command() {
  command -v "$1" >/dev/null || { echo "Pflichtkommando fehlt: $1" >&2; exit 1; }
}

for command_name in git rsync curl python3 systemctl sha256sum; do
  require_command "$command_name"
done

if ! command -v xvfb-run >/dev/null; then
  echo "xvfb-run fehlt; installiere ausschließlich das Screenshot-Paket xvfb"
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq xvfb
fi

GODOT_BIN="${FLEXTRAWURST_GODOT_BIN:-$(command -v godot || true)}"
[[ -n "$GODOT_BIN" && -x "$GODOT_BIN" ]] || {
  echo "Bestehendes Godot-Binary fehlt. Die verifizierte VPS-Pipeline behauptete Godot 4.3; Abbruch statt stiller Fremdinstallation." >&2
  exit 1
}
GODOT_VERSION="$($GODOT_BIN --version | head -n1)"
[[ "$GODOT_VERSION" == 4.3* ]] || {
  echo "Erwartet Godot 4.3 aus der bestehenden VPS-Pipeline, gefunden: $GODOT_VERSION" >&2
  exit 1
}

echo "[1/9] Snapshot"
TARGET_EXISTED=0
UNIT_EXISTED=0
UNIT_WAS_ACTIVE=0
UNIT_WAS_ENABLED=0
if [[ -d "$TARGET" ]]; then
  TARGET_EXISTED=1
  mkdir -p "$BACKUP_DIR/project"
  rsync -a "$TARGET/" "$BACKUP_DIR/project/"
fi
if [[ -f "$UNIT_PATH" ]]; then
  UNIT_EXISTED=1
  cp -a "$UNIT_PATH" "$BACKUP_DIR/$UNIT_NAME"
fi
if systemctl is-active --quiet "$UNIT_NAME"; then UNIT_WAS_ACTIVE=1; fi
if systemctl is-enabled --quiet "$UNIT_NAME" 2>/dev/null; then UNIT_WAS_ENABLED=1; fi
cat > "$BACKUP_DIR/snapshot.json" <<JSON
{
  "timestamp": "$STAMP",
  "target": "$TARGET",
  "target_existed": $TARGET_EXISTED,
  "unit_path": "$UNIT_PATH",
  "unit_existed": $UNIT_EXISTED,
  "unit_was_active": $UNIT_WAS_ACTIVE,
  "unit_was_enabled": $UNIT_WAS_ENABLED,
  "bridge_port": $BRIDGE_PORT,
  "branch": "$BRANCH"
}
JSON

rollback_on_error() {
  status=$?
  echo "INSTALLATION FEHLGESCHLAGEN; stelle Snapshot $BACKUP_DIR wieder her" >&2
  systemctl stop "$UNIT_NAME" 2>/dev/null || true
  if [[ "$TARGET_EXISTED" -eq 1 ]]; then
    rm -rf "$TARGET"
    mkdir -p "$TARGET"
    rsync -a "$BACKUP_DIR/project/" "$TARGET/"
  else
    rm -rf "$TARGET"
  fi
  if [[ "$UNIT_EXISTED" -eq 1 ]]; then
    cp -a "$BACKUP_DIR/$UNIT_NAME" "$UNIT_PATH"
  else
    rm -f "$UNIT_PATH"
  fi
  systemctl daemon-reload || true
  if [[ "$UNIT_WAS_ENABLED" -eq 1 ]]; then systemctl enable "$UNIT_NAME" >/dev/null 2>&1 || true; fi
  if [[ "$UNIT_WAS_ACTIVE" -eq 1 ]]; then systemctl start "$UNIT_NAME" || true; fi
  rm -rf "$STAGE"
  exit "$status"
}
trap rollback_on_error ERR INT TERM

echo "[2/9] Isolierter Sparse-Checkout aus $BRANCH"
git clone --depth 1 --filter=blob:none --sparse --branch "$BRANCH" "$REPO_URL" "$STAGE/repo"
git -C "$STAGE/repo" sparse-checkout set engine/godot-vertical-slice
DEPLOYED_COMMIT="$(git -C "$STAGE/repo" rev-parse HEAD)"
SOURCE="$STAGE/repo/engine/godot-vertical-slice"
[[ -f "$SOURCE/project.godot" ]] || { echo "project.godot fehlt im Branch" >&2; false; }

echo "[3/9] Atomarer Projektkörper"
rm -rf "$STAGE/new-project"
mkdir -p "$STAGE/new-project"
rsync -a --delete "$SOURCE/" "$STAGE/new-project/"
python3 "$STAGE/new-project/tools/prepare_assets.py"
echo "$DEPLOYED_COMMIT" > "$STAGE/new-project/.deployed_commit"

rm -rf "$TARGET.next"
mkdir -p "$(dirname "$TARGET")"
mv "$STAGE/new-project" "$TARGET.next"
rm -rf "$TARGET"
mv "$TARGET.next" "$TARGET"
chmod +x "$TARGET/tools/prepare_assets.py" \
  "$TARGET/deploy/world_bridge_server.py" \
  "$TARGET/deploy/vps_verify.sh" \
  "$TARGET/deploy/vps_install.sh" \
  "$TARGET/deploy/vps_rollback.sh" 2>/dev/null || true

echo "[4/9] Runtime-Override ohne Veränderung des sicheren Grundseeds"
mkdir -p "$RUNTIME"
cat > "$TARGET/data/world_seed.runtime.json" <<JSON
{
  "truth_status": "REAL_VPS_RUNTIME",
  "deployment": {
    "repository": "RaDi0n92/flextrawurst-agent",
    "branch": "$BRANCH",
    "commit": "$DEPLOYED_COMMIT",
    "installed_at": "$STAMP",
    "project_dir": "$TARGET"
  },
  "bridge": {
    "enabled": true,
    "base_url": "$BRIDGE_URL",
    "sync_interval_seconds": 1.0,
    "proof_event_on_start": true,
    "status": "REAL_LOCAL_VPS_BRIDGE_ACTIVE"
  }
}
JSON

echo "[5/9] Systemd-Bridge"
if command -v ss >/dev/null && ss -ltnH | awk '{print $4}' | grep -Eq "(^|:)$BRIDGE_PORT$"; then
  if ! systemctl is-active --quiet "$UNIT_NAME"; then
    echo "Port $BRIDGE_PORT ist durch einen unbekannten Dienst belegt; Abbruch statt Überfahren" >&2
    false
  fi
fi
sed "s/FLEXTRAWURST_GODOT_BRIDGE_PORT=18092/FLEXTRAWURST_GODOT_BRIDGE_PORT=$BRIDGE_PORT/" \
  "$TARGET/deploy/$UNIT_NAME" > "$STAGE/$UNIT_NAME"
install -m 0644 "$STAGE/$UNIT_NAME" "$UNIT_PATH"
systemctl daemon-reload
systemctl enable --now "$UNIT_NAME"

for _ in $(seq 1 50); do
  if curl --fail --silent "$BRIDGE_URL/health" > "$LOG_DIR/bridge-health.json"; then
    break
  fi
  sleep 0.2
done
curl --fail --silent "$BRIDGE_URL/health" > "$LOG_DIR/bridge-health.json"

echo "[6/9] Bestehende 3D-Pipeline bleibt unberührt"
[[ -f "$WERKRAUM/tools/3d_pipeline/godot_pipeline.py" ]] || {
  echo "Bestehende godot_pipeline.py fehlt; Abbruch" >&2
  false
}
[[ -f "$WERKRAUM/tools/3d_pipeline/flextrawurst_3d_mcp.py" ]] || {
  echo "Bestehender 3D-MCP-Server fehlt; Abbruch" >&2
  false
}

echo "[7/9] Vollständiger VPS-Beweis"
FLEXTRAWURST_GODOT_BIN="$GODOT_BIN" \
FLEXTRAWURST_GODOT_PROJECT_DIR="$TARGET" \
FLEXTRAWURST_GODOT_RUNTIME_DIR="$RUNTIME" \
FLEXTRAWURST_GODOT_BRIDGE_URL="$BRIDGE_URL" \
  "$TARGET/deploy/vps_verify.sh" | tee "$LOG_DIR/vps-verify-entry.log"

echo "[8/9] Installationsmanifest"
python3 - "$LOG_DIR/installation.json" "$DEPLOYED_COMMIT" "$GODOT_VERSION" "$BACKUP_DIR" "$BRIDGE_PORT" <<'PY'
import json, sys
from datetime import datetime, timezone
out, commit, godot, backup, bridge_port = sys.argv[1:]
value = {
    "schema_version": "1.1.0",
    "status": "PASS",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "repository": "RaDi0n92/flextrawurst-agent",
    "branch": "engine/godot-vertical-slice-001",
    "commit": commit,
    "target": "/root/werkraum/engine/godot-vertical-slice",
    "runtime": "/root/werkraum/engine_runtime/godot-vertical-slice",
    "godot_version": godot,
    "bridge_service": "flextrawurst-godot-world-bridge.service",
    "bridge_url": f"http://127.0.0.1:{int(bridge_port)}",
    "reserved_ports_untouched": [8090, 8091],
    "snapshot": backup,
    "single_html_changed": False,
    "existing_3d_pipeline_changed": False,
}
open(out, "w", encoding="utf-8").write(json.dumps(value, ensure_ascii=False, indent=2))
print(json.dumps(value, ensure_ascii=False, indent=2))
PY
sha256sum "$LOG_DIR"/* > "$LOG_DIR/SHA256SUMS.txt"

echo "[9/9] Abschluss"
trap - ERR INT TERM
rm -rf "$STAGE"
echo "FLEXTRAWURST_GODOT_VPS_INSTALL_PASS"
echo "Projekt: $TARGET"
echo "Runtime: $RUNTIME"
echo "Bridge: $BRIDGE_URL"
echo "Beweise: $LOG_DIR"
echo "Snapshot: $BACKUP_DIR"
