#!/usr/bin/env python3
"""Local append-only bridge between the Godot vertical slice and the VPS world body.

The service intentionally binds to 127.0.0.1 only. Public exposure is a later,
separately authenticated ring. Ports 8090 and 8091 belong to the existing 3D-MCP
and 95-tool VPS-MCP bodies and are never used by this bridge.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = os.environ.get("FLEXTRAWURST_GODOT_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.environ.get("FLEXTRAWURST_GODOT_BRIDGE_PORT", "18092"))
DATA_DIR = Path(
    os.environ.get(
        "FLEXTRAWURST_GODOT_BRIDGE_DATA",
        "/root/werkraum/engine_runtime/godot-vertical-slice",
    )
).resolve()
EVENTS_PATH = DATA_DIR / "events.jsonl"
STATE_PATH = DATA_DIR / "state.json"
WORLD_ID_RE = re.compile(r"^[a-zA-Z0-9._:-]{1,160}$")
MAX_BODY = 1024 * 1024
_LOCK = threading.RLock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EVENTS_PATH.touch(exist_ok=True)
    if not STATE_PATH.exists():
        STATE_PATH.write_text(
            json.dumps({"last_cursor": 0, "updated_at": utc_now()}, indent=2),
            encoding="utf-8",
        )


def read_state() -> dict:
    ensure_store()
    try:
        value = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        value = {"last_cursor": 0, "updated_at": utc_now()}
    return value if isinstance(value, dict) else {"last_cursor": 0, "updated_at": utc_now()}


def write_state(state: dict) -> None:
    temp = STATE_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, STATE_PATH)


def validate_event(world_id: str, event: object) -> tuple[bool, str]:
    if not WORLD_ID_RE.fullmatch(world_id):
        return False, "invalid world_id"
    if not isinstance(event, dict):
        return False, "event must be an object"
    if event.get("world_id") != world_id:
        return False, "event.world_id must equal route world_id"
    required_strings = ("event_id", "event_type", "origin", "truth_status", "timestamp")
    for field in required_strings:
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            return False, f"missing or invalid {field}"
    if not isinstance(event.get("payload", {}), dict):
        return False, "payload must be an object"
    return True, ""


def append_event(world_id: str, event: dict) -> dict:
    ensure_store()
    with _LOCK:
        state = read_state()
        cursor = int(state.get("last_cursor", 0)) + 1
        record = dict(event)
        record["cursor"] = cursor
        record["server_received_at"] = utc_now()
        record["event_sha256"] = hashlib.sha256(canonical_json(event)).hexdigest()

        with EVENTS_PATH.open("a", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

        write_state({"last_cursor": cursor, "updated_at": utc_now(), "last_world_id": world_id})
        return record


def list_events(world_id: str, after: int, limit: int) -> tuple[list[dict], int]:
    ensure_store()
    found: list[dict] = []
    last_cursor = after
    with EVENTS_PATH.open("r", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            cursor = int(record.get("cursor", 0))
            if record.get("world_id") != world_id or cursor <= after:
                continue
            found.append(record)
            last_cursor = max(last_cursor, cursor)
            if len(found) >= limit:
                break
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return found, last_cursor


class Handler(BaseHTTPRequestHandler):
    server_version = "FlextrawurstGodotBridge/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{utc_now()}] {self.client_address[0]} {fmt % args}", flush=True)

    def json_response(self, status: int, value: object) -> None:
        body = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def route_world_id(self, suffix: str) -> str | None:
        path = urlparse(self.path).path
        prefix = "/worlds/"
        if not path.startswith(prefix) or not path.endswith(suffix):
            return None
        middle = path[len(prefix) : -len(suffix)]
        return middle.strip("/")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            state = read_state()
            self.json_response(
                200,
                {
                    "status": "ok",
                    "service": "flextrawurst-godot-world-bridge",
                    "bind": f"{HOST}:{PORT}",
                    "storage": str(DATA_DIR),
                    "last_cursor": int(state.get("last_cursor", 0)),
                    "public": False,
                    "timestamp": utc_now(),
                },
            )
            return

        world_id = self.route_world_id("/events")
        if world_id is None or not WORLD_ID_RE.fullmatch(world_id):
            self.json_response(404, {"error": "not_found"})
            return
        params = parse_qs(parsed.query)
        try:
            after = max(0, int(params.get("after", ["0"])[0] or "0"))
            limit = min(500, max(1, int(params.get("limit", ["100"])[0] or "100")))
        except ValueError:
            self.json_response(400, {"error": "invalid_cursor_or_limit"})
            return
        events, cursor = list_events(world_id, after, limit)
        self.json_response(200, {"world_id": world_id, "cursor": str(cursor), "events": events})

    def do_POST(self) -> None:
        world_id = self.route_world_id("/events")
        if world_id is None:
            self.json_response(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self.json_response(413, {"error": "invalid_body_size"})
            return
        try:
            event = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.json_response(400, {"error": "invalid_json"})
            return
        valid, error = validate_event(world_id, event)
        if not valid:
            self.json_response(422, {"error": error})
            return
        record = append_event(world_id, event)
        self.json_response(
            201,
            {
                "status": "accepted",
                "world_id": world_id,
                "cursor": str(record["cursor"]),
                "event_id": record["event_id"],
                "event_sha256": record["event_sha256"],
            },
        )


def main() -> int:
    if PORT in {8090, 8091}:
        raise SystemExit(f"Port {PORT} ist für vorhandene Flextrawurst-MCP-Dienste reserviert")
    ensure_store()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(
        json.dumps(
            {
                "status": "starting",
                "service": "flextrawurst-godot-world-bridge",
                "bind": f"{HOST}:{PORT}",
                "data_dir": str(DATA_DIR),
                "public": False,
                "reserved_ports_untouched": [8090, 8091],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
