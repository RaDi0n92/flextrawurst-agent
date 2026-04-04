from __future__ import annotations

import json
from typing import Any

from agent.dak_gord_system.graph.approval_store import APPROVALS_DIR, load_state_for_approval, overwrite_state
from agent.dak_gord_system.graph.run_tool_agent import build_tool_graph
from agent.dak_gord_system.graph.trace_events import append_trace_event


def list_pending_approvals() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    for pfad in sorted(APPROVALS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(pfad.read_text(encoding="utf-8"))
        except Exception:
            continue

        out.append(
            {
                "task_id": data.get("task_id", ""),
                "tool_name": data.get("tool_name", ""),
                "approval_status": data.get("approval_status", ""),
                "status": data.get("status", ""),
                "ziel": data.get("ziel", ""),
                "path": str(pfad),
            }
        )

    return out


def resume_approval(task_id: str, entscheidung: str) -> dict[str, Any]:
    entscheidung = entscheidung.strip().lower()
    if entscheidung not in {"genehmigt", "abgelehnt"}:
        raise ValueError("Entscheidung muss genehmigt oder abgelehnt sein.")

    state = load_state_for_approval(task_id)

    approval_status = str(state.get("approval_status", "") or "")
    status = str(state.get("status", "") or "")

    if approval_status != "offen":
        raise RuntimeError(
            f"Resume nicht erlaubt: approval_status ist '{approval_status}' statt 'offen'."
        )

    if status in {"fertig", "blockiert"}:
        raise RuntimeError(
            f"Resume nicht erlaubt: status ist bereits '{status}'."
        )

    letzte_tool_aktionen = state.get("letzte_tool_aktionen", [])
    if letzte_tool_aktionen:
        raise RuntimeError(
            "Resume nicht erlaubt: Der Task hat bereits Tool-Aktionen gespeichert."
        )

    state["approval_status"] = entscheidung
    state["approval_reason"] = (
        f"Freigabe manuell erteilt fuer {state.get('tool_name', '')}."
        if entscheidung == "genehmigt"
        else f"Freigabe manuell abgelehnt fuer {state.get('tool_name', '')}."
    )
    state["aktueller_schritt"] = "check_tool_approval"

    graph = build_tool_graph()
    config = {"configurable": {"thread_id": state.get("thread_id", "")}}
    result = graph.invoke(state, config=config)

    overwrite_state(task_id, dict(result))
    append_trace_event(
        "approval_resolved",
        result,
        decision=entscheidung,
        final_status=result.get("status", ""),
        tool_name=result.get("tool_name", ""),
    )
    return dict(result)
