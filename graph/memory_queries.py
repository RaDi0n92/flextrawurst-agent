from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TRACE_FILE = Path("/root/werkraum/agent/dak_gord_system/spuren/traces/events.jsonl")


def load_trace_events(limit: int | None = None) -> list[dict[str, Any]]:
    if not TRACE_FILE.exists():
        return []

    events: list[dict[str, Any]] = []
    for line in TRACE_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue

    if limit is not None and limit >= 0:
        return events[-limit:]
    return events


def latest_events(limit: int = 20) -> list[dict[str, Any]]:
    return load_trace_events(limit=limit)


def filter_events_by_type(prefix: str, limit: int = 20) -> list[dict[str, Any]]:
    prefix = prefix.strip().lower()
    events = load_trace_events()
    filtered = [e for e in events if str(e.get("event_type", "")).lower().startswith(prefix)]
    return filtered[-limit:]


def filter_events_by_task(task_id: str, limit: int = 20) -> list[dict[str, Any]]:
    task_id = task_id.strip()
    events = load_trace_events()
    filtered = [e for e in events if str(e.get("task_id", "")) == task_id]
    return filtered[-limit:]


def format_event_lines(events: list[dict[str, Any]]) -> list[str]:
    if not events:
        return ["[System] Keine passenden Events gefunden."]

    lines: list[str] = []
    for e in events:
        payload = e.get("payload", {}) or {}
        payload_preview = str(payload)
        if len(payload_preview) > 220:
            payload_preview = payload_preview[:220] + "..."

        lines.append(
            " | ".join(
                [
                    str(e.get("timestamp", "")),
                    str(e.get("event_type", "")),
                    f"task={e.get('task_id', '')}",
                    f"status={e.get('status', '')}",
                    f"approval={e.get('approval_status', '')}",
                    f"tool={e.get('tool_name', '')}",
                    f"payload={payload_preview}",
                ]
            )
        )
    return lines
