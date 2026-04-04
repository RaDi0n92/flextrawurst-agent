from __future__ import annotations

from datetime import datetime

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.graph.tools.runtime import run_registered_tool
from agent.dak_gord_system.graph.trace_events import append_trace_event


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_tool_node(state: AgentState) -> AgentState:
    beobachtungen = list(state.get("beobachtungen", []))
    notizen = list(state.get("notizen", []))
    letzte_tool_aktionen = list(state.get("letzte_tool_aktionen", []))

    tool_name = str(state.get("tool_name", "") or "").strip()
    tool_args = state.get("tool_args", {})
    tool_aktion = str(state.get("tool_aktion", "tool_lauf") or "tool_lauf")

    if not tool_name:
        append_trace_event("tool_run_invalid", state, reason="tool_name fehlt")
        return {
            "status": "fehlgeschlagen",
            "fehler": "Kein tool_name im State vorhanden.",
            "aktueller_schritt": "run_tool",
        }

    if not isinstance(tool_args, dict):
        append_trace_event("tool_run_invalid", state, reason="tool_args ist kein dict")
        return {
            "status": "fehlgeschlagen",
            "fehler": "tool_args muss ein Dict sein.",
            "aktueller_schritt": "run_tool",
        }

    result, tool_aktion_obj = run_registered_tool(
        state,
        tool_name,
        tool_args,
        aktion=tool_aktion,
    )
    letzte_tool_aktionen.append(tool_aktion_obj)

    if not result.ok:
        trace_path = append_trace_event(
            "tool_run_failed",
            state,
            tool_name=tool_name,
            tool_action=tool_aktion,
            tool_args=tool_args,
            error=result.error or "",
        )
        notizen.append(f"Tool fehlgeschlagen: {tool_name}")
        notizen.append(f"Trace-Ereignis geschrieben: {trace_path}")
        return {
            "status": "fehlgeschlagen",
            "fehler": result.error or f"Tool fehlgeschlagen: {tool_name}",
            "aktueller_schritt": "run_tool",
            "letzte_tool_aktionen": letzte_tool_aktionen,
            "notizen": notizen,
        }

    output_preview = str(result.output)[:2000] if result.output is not None else ""
    beobachtungen.append({
        "art": "tool_result",
        "inhalt": output_preview,
        "quelle": tool_name,
        "zeitstempel": _ts(),
    })

    final_event_state = dict(state)
    final_event_state["status"] = "fertig"
    final_event_state["aktueller_schritt"] = "done"

    trace_path = append_trace_event(
        "tool_run_completed",
        final_event_state,
        tool_name=tool_name,
        tool_action=tool_aktion,
        tool_args=tool_args,
        result_preview=output_preview[:500],
    )

    notizen.append(f"Tool erfolgreich: {tool_name}")
    notizen.append(f"Trace-Ereignis geschrieben: {trace_path}")

    return {
        "aktueller_schritt": "done",
        "status": "fertig",
        "beobachtungen": beobachtungen,
        "letzte_tool_aktionen": letzte_tool_aktionen,
        "notizen": notizen,
        "fehler": None,
    }
