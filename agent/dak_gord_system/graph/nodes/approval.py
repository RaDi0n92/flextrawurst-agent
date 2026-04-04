from __future__ import annotations

from agent.dak_gord_system.graph.approval_store import save_state_for_approval
from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.graph.tools.runtime import ensure_default_tools_registered
from agent.dak_gord_system.graph.tools.registry import registry
from agent.dak_gord_system.graph.trace_events import append_trace_event


def check_tool_approval_node(state: AgentState) -> AgentState:
    ensure_default_tools_registered()

    tool_name = str(state.get("tool_name", "") or "").strip()
    notizen = list(state.get("notizen", []))

    if not tool_name:
        append_trace_event("approval_invalid", state, reason="tool_name fehlt")
        return {
            "status": "fehlgeschlagen",
            "fehler": "Kein tool_name im State vorhanden.",
            "aktueller_schritt": "check_tool_approval",
        }

    try:
        tool = registry.get(tool_name)
    except KeyError as exc:
        append_trace_event("approval_invalid", state, reason=str(exc))
        return {
            "status": "fehlgeschlagen",
            "fehler": str(exc),
            "aktueller_schritt": "check_tool_approval",
        }

    approval_status = state.get("approval_status", "nicht_noetig")

    if approval_status == "genehmigt":
        trace_path = append_trace_event(
            "approval_pregranted",
            state,
            tool_name=tool_name,
            reason="approval_status bereits genehmigt",
        )
        notizen.append(f"Freigabe bereits erteilt fuer Tool {tool_name}.")
        notizen.append(f"Trace-Ereignis geschrieben: {trace_path}")
        return {
            "approval_status": "genehmigt",
            "status": "in_arbeit",
            "aktueller_schritt": "run_tool",
            "notizen": notizen,
            "fehler": None,
        }

    if approval_status == "abgelehnt":
        reason = state.get("approval_reason", "") or f"Tool {tool_name} wurde abgelehnt."
        trace_path = append_trace_event(
            "approval_rejected_state",
            state,
            tool_name=tool_name,
            reason=reason,
        )
        notizen.append(reason)
        notizen.append(f"Trace-Ereignis geschrieben: {trace_path}")
        return {
            "approval_status": "abgelehnt",
            "status": "blockiert",
            "aktueller_schritt": "approval_rejected",
            "approval_reason": reason,
            "notizen": notizen,
            "fehler": None,
        }

    risk = tool.risk
    if risk == "low":
        trace_path = append_trace_event(
            "approval_not_needed",
            state,
            tool_name=tool_name,
            risk=risk,
        )
        notizen.append(f"Freigabe nicht noetig fuer Tool {tool_name} (risk={risk})")
        notizen.append(f"Trace-Ereignis geschrieben: {trace_path}")
        return {
            "approval_status": "nicht_noetig",
            "approval_reason": "",
            "approval_request_path": "",
            "status": "in_arbeit",
            "aktueller_schritt": "run_tool",
            "notizen": notizen,
            "fehler": None,
        }

    reason = f"Tool {tool_name} erfordert Freigabe (risk={risk})."
    pending_state = dict(state)
    pending_state.update(
        {
            "approval_status": "offen",
            "approval_reason": reason,
            "status": "wartet_auf_freigabe",
            "aktueller_schritt": "approval_required",
            "notizen": notizen + [reason],
            "fehler": None,
        }
    )
    pfad = save_state_for_approval(pending_state)
    trace_path = append_trace_event(
        "approval_requested",
        pending_state,
        tool_name=tool_name,
        risk=risk,
        approval_request_path=pfad,
    )

    return {
        "approval_status": "offen",
        "approval_reason": reason,
        "approval_request_path": pfad,
        "status": "wartet_auf_freigabe",
        "aktueller_schritt": "approval_required",
        "notizen": notizen + [reason, f"Approval gespeichert: {pfad}", f"Trace-Ereignis geschrieben: {trace_path}"],
        "fehler": None,
    }
