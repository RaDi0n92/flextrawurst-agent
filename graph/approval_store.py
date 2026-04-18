from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APPROVALS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/approvals")
APPROVALS_DIR.mkdir(parents=True, exist_ok=True)


def approval_path(task_id: str) -> Path:
    return APPROVALS_DIR / f"{task_id}.json"


def save_state_for_approval(state: dict[str, Any]) -> str:
    task_id = str(state.get("task_id", "") or "").strip()
    if not task_id:
        raise ValueError("task_id fehlt fuer approval save")
    pfad = approval_path(task_id)
    pfad.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(pfad)


def load_state_for_approval(task_id: str) -> dict[str, Any]:
    pfad = approval_path(task_id)
    if not pfad.exists():
        raise FileNotFoundError(f"Keine Approval-Datei gefunden: {pfad}")
    return json.loads(pfad.read_text(encoding="utf-8"))


def overwrite_state(task_id: str, state: dict[str, Any]) -> str:
    pfad = approval_path(task_id)
    pfad.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(pfad)
