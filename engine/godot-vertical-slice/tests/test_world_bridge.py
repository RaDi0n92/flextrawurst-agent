#!/usr/bin/env python3
"""E2E test for the localhost-only append-only Godot bridge."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
SERVER = PROJECT_DIR / "deploy" / "world_bridge_server.py"
WORLD_ID = "flextrawurst.engine.slice.001"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def request_json(url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def main() -> int:
    port = free_port()
    with tempfile.TemporaryDirectory(prefix="flextrawurst-bridge-test-") as temp_dir:
        env = os.environ.copy()
        env.update(
            {
                "FLEXTRAWURST_GODOT_BRIDGE_HOST": "127.0.0.1",
                "FLEXTRAWURST_GODOT_BRIDGE_PORT": str(port),
                "FLEXTRAWURST_GODOT_BRIDGE_DATA": temp_dir,
                "PYTHONUNBUFFERED": "1",
            }
        )
        process = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=PROJECT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(50):
                try:
                    status, health = request_json(f"{base}/health")
                    if status == 200 and health.get("status") == "ok":
                        break
                except OSError:
                    pass
                time.sleep(0.1)
            else:
                raise AssertionError("bridge did not become healthy")

            event = {
                "world_id": WORLD_ID,
                "event_id": "bridge-test-001",
                "event_type": "GODOT_BRIDGE_CONTRACT_TEST",
                "origin": "RaDi0n92/flextrawurst-agent",
                "truth_status": "REAL_AUTOMATED_TEST",
                "timestamp": "2026-07-24T00:00:00+00:00",
                "payload": {"asset_id": "alleswisser.asset.3d.test-cube.001"},
            }
            status, accepted = request_json(f"{base}/worlds/{WORLD_ID}/events", event)
            assert status == 201, accepted
            assert accepted["status"] == "accepted"
            assert accepted["event_id"] == event["event_id"]
            assert len(accepted["event_sha256"]) == 64

            status, listing = request_json(f"{base}/worlds/{WORLD_ID}/events?after=0")
            assert status == 200, listing
            assert listing["world_id"] == WORLD_ID
            assert len(listing["events"]) == 1
            assert listing["events"][0]["event_type"] == event["event_type"]
            assert listing["events"][0]["cursor"] == 1

            wrong = dict(event)
            wrong["event_id"] = "wrong-world"
            wrong["world_id"] = "different.world"
            status, rejected = request_json(f"{base}/worlds/{WORLD_ID}/events", wrong)
            assert status == 422, rejected

            events_path = Path(temp_dir) / "events.jsonl"
            assert events_path.exists()
            assert events_path.read_text(encoding="utf-8").count("\n") == 1
            print("FLEXTRAWURST_GODOT_WORLD_BRIDGE_TEST_PASS")
            return 0
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            if process.returncode not in (0, -15):
                output = process.stdout.read() if process.stdout else ""
                print(output, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
