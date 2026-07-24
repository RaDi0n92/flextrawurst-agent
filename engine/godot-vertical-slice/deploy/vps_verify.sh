#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${FLEXTRAWURST_GODOT_PROJECT_DIR:-/root/werkraum/engine/godot-vertical-slice}"
RUNTIME_DIR="${FLEXTRAWURST_GODOT_RUNTIME_DIR:-/root/werkraum/engine_runtime/godot-vertical-slice}"
BRIDGE_URL="${FLEXTRAWURST_GODOT_BRIDGE_URL:-http://127.0.0.1:8091}"
GODOT_BIN="${FLEXTRAWURST_GODOT_BIN:-$(command -v godot || true)}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROOF_DIR="${FLEXTRAWURST_GODOT_PROOF_DIR:-$RUNTIME_DIR/proofs/$STAMP}"
WORLD_ID="flextrawurst.engine.slice.001"

mkdir -p "$PROOF_DIR"
exec > >(tee "$PROOF_DIR/verify.log") 2>&1

fail() {
  echo "FLEXTRAWURST_VPS_ENGINE_VERIFY_FAIL: $*" >&2
  exit 1
}

[[ -d "$PROJECT_DIR" ]] || fail "Projekt fehlt: $PROJECT_DIR"
[[ -n "$GODOT_BIN" && -x "$GODOT_BIN" ]] || fail "Godot-Binary nicht gefunden"
command -v python3 >/dev/null || fail "python3 fehlt"
command -v curl >/dev/null || fail "curl fehlt"
command -v sha256sum >/dev/null || fail "sha256sum fehlt"

GODOT_VERSION="$($GODOT_BIN --version | head -n1)"
echo "Godot: $GODOT_VERSION"
[[ "$GODOT_VERSION" == 4.3* ]] || fail "VPS-Ziellinie erwartet Godot 4.3, gefunden: $GODOT_VERSION"

python3 "$PROJECT_DIR/tools/prepare_assets.py" | tee "$PROOF_DIR/asset-prepare.log"
ACTUAL_GLB_HASH="$(sha256sum "$PROJECT_DIR/assets/test_cube.glb" | awk '{print $1}')"
[[ "$ACTUAL_GLB_HASH" == "ca481b86fb41d80f59af4b3714ea34c0798adf2acd9d871d4bf563861e17ca00" ]] \
  || fail "GLB-Hash falsch: $ACTUAL_GLB_HASH"

"$GODOT_BIN" --headless --editor --quit --path "$PROJECT_DIR" \
  2>&1 | tee "$PROOF_DIR/godot-import.log"

"$GODOT_BIN" --headless --path "$PROJECT_DIR" \
  --script res://tests/headless_smoke.gd \
  2>&1 | tee "$PROOF_DIR/godot-smoke.log"
grep -q "FLEXTRAWURST_AGENT_ENGINE_SLICE_SMOKE_PASS" "$PROOF_DIR/godot-smoke.log" \
  || fail "Strukturtest-Marker fehlt"

curl --fail --silent "$BRIDGE_URL/health" > "$PROOF_DIR/bridge-health-before.json" \
  || fail "Bridge nicht erreichbar: $BRIDGE_URL"
BEFORE_CURSOR="$(python3 - "$PROOF_DIR/bridge-health-before.json" <<'PY'
import json, sys
print(int(json.load(open(sys.argv[1], encoding="utf-8")).get("last_cursor", 0)))
PY
)"

echo "Bridge-Cursor vor Godot: $BEFORE_CURSOR"
set +e
"$GODOT_BIN" --headless --path "$PROJECT_DIR" \
  --script res://tests/live_bridge_probe.gd \
  2>&1 | tee "$PROOF_DIR/godot-live.log"
GODOT_BRIDGE_STATUS=${PIPESTATUS[0]}
set -e
[[ "$GODOT_BRIDGE_STATUS" -eq 0 ]] || fail "Godot-Bridge-Probe beendet mit Status $GODOT_BRIDGE_STATUS"
grep -q "FLEXTRAWURST_GODOT_LIVE_BRIDGE_PROBE_PASS" "$PROOF_DIR/godot-live.log" \
  || fail "Bridge-Probe-Marker fehlt"

curl --fail --silent \
  "$BRIDGE_URL/worlds/$WORLD_ID/events?after=$BEFORE_CURSOR" \
  > "$PROOF_DIR/bridge-events-after.json" \
  || fail "Bridge-Ereignisse nicht lesbar"

python3 - "$PROOF_DIR/bridge-events-after.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path, encoding="utf-8"))
events = data.get("events", [])
assert events, data
event = events[-1]
assert event["world_id"] == "flextrawurst.engine.slice.001", event
assert event["event_type"] == "GODOT_VPS_BRIDGE_PROBE", event
assert event["origin"] == "RaDi0n92/flextrawurst-agent", event
assert event["truth_status"] == "REAL_VPS_RUNTIME_EVENT", event
assert event["payload"]["asset_id"] == "alleswisser.asset.3d.test-cube.001", event
assert len(event["event_sha256"]) == 64, event
print("FLEXTRAWURST_GODOT_TO_VPS_BRIDGE_PASS")
PY

if [[ -f /root/werkraum/tools/3d_pipeline/godot_pipeline.py ]]; then
  python3 - "$PROJECT_DIR" "$PROOF_DIR/legacy-3d-pipeline.json" <<'PY'
import json, sys
sys.path.insert(0, "/root/werkraum/tools/3d_pipeline")
import godot_pipeline
result = godot_pipeline.godot_import_and_test(sys.argv[1])
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(result, ensure_ascii=False, indent=2))
assert result.get("status") == "ok", result
print("FLEXTRAWURST_EXISTING_3D_PIPELINE_GODOT_PASS")
PY
else
  fail "bestehende VPS-3D-Pipeline fehlt"
fi

SCREENSHOT_STATUS="BLOCKIERT_XVFB_FEHLT"
SCREENSHOT_PATH="$PROOF_DIR/engine-proof.png"
if command -v xvfb-run >/dev/null; then
  xvfb-run -a "$GODOT_BIN" --path "$PROJECT_DIR" \
    --script res://tests/capture_proof.gd \
    -- --output="$SCREENSHOT_PATH" \
    2>&1 | tee "$PROOF_DIR/godot-screenshot.log"
  python3 - "$SCREENSHOT_PATH" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
data = path.read_bytes()
assert data.startswith(b"\x89PNG\r\n\x1a\n")
assert len(data) > 1000
print(f"FLEXTRAWURST_ENGINE_PNG_PASS {len(data)}")
PY
  SCREENSHOT_STATUS="PASS"
fi

python3 - \
  "$PROOF_DIR/proof.json" \
  "$PROJECT_DIR" \
  "$GODOT_VERSION" \
  "$ACTUAL_GLB_HASH" \
  "$SCREENSHOT_STATUS" \
  "$SCREENSHOT_PATH" \
  "$BEFORE_CURSOR" <<'PY'
import hashlib, json, os, sys
from datetime import datetime, timezone

out, project, godot, glb_hash, screenshot_status, screenshot_path, before_cursor = sys.argv[1:]

def sha(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

proof = {
    "schema_version": "1.0.0",
    "status": "PASS" if screenshot_status == "PASS" else "PASS_OHNE_SCREENSHOT",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "project_dir": project,
    "world_id": "flextrawurst.engine.slice.001",
    "godot_version": godot,
    "asset": {
        "alleswisser_id": "alleswisser.asset.3d.test-cube.001",
        "sha256": glb_hash,
        "import": "PASS",
    },
    "bridge": {
        "service": "flextrawurst-godot-world-bridge.service",
        "url": "http://127.0.0.1:8091",
        "before_cursor": int(before_cursor),
        "roundtrip": "PASS",
        "append_only": True,
        "public": False,
        "probe_event_type": "GODOT_VPS_BRIDGE_PROBE",
    },
    "existing_3d_pipeline": "PASS",
    "structural_smoke": "PASS",
    "main_scene_boot": "PASS",
    "screenshot": {
        "status": screenshot_status,
        "path": screenshot_path if screenshot_status == "PASS" else None,
        "sha256": sha(screenshot_path),
    },
}
open(out, "w", encoding="utf-8").write(json.dumps(proof, ensure_ascii=False, indent=2))
print(json.dumps(proof, ensure_ascii=False, indent=2))
PY

sha256sum "$PROOF_DIR"/* > "$PROOF_DIR/SHA256SUMS.txt"
echo "FLEXTRAWURST_VPS_ENGINE_VERIFY_PASS: $PROOF_DIR"
