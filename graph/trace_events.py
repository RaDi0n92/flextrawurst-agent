from __future__ import annotations

import json
import os
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


TRACE_FILE = Path("/root/werkraum/agent/dak_gord_system/spuren/traces/events.jsonl")


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _append_jsonl_line(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            size = os.lseek(fd, 0, os.SEEK_END)
            prefix = b""
            if size > 0:
                os.lseek(fd, -1, os.SEEK_END)
                last = os.read(fd, 1)
                if last != b"\n":
                    prefix = b"\n"
                os.lseek(fd, 0, os.SEEK_END)

            payload = json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n"
            os.write(fd, prefix + payload)
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def append_trace_event(event_type: str, state: Mapping[str, Any] | None = None, **payload: Any) -> str:
    state = state or {}

    event = {
        "timestamp": _ts(),
        "event_type": event_type,
        "task_id": state.get("task_id", ""),
        "thread_id": state.get("thread_id", ""),
        "run_type": state.get("run_type", ""),
        "status": state.get("status", ""),
        "step": state.get("aktueller_schritt", ""),
        "approval_status": state.get("approval_status", ""),
        "tool_name": state.get("tool_name", ""),
        "fokus_pfad": state.get("fokus_pfad", ""),
        "payload": payload,
    }

    _append_jsonl_line(TRACE_FILE, event)
    return str(TRACE_FILE)
