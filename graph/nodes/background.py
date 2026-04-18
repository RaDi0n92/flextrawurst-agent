from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.neugierkern import pruefe_neugier_und_vision
from agent.dak_gord_system.graph.trace_events import append_trace_event


GRAPH_RUNS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/graph_runs")
BACKGROUND_TRACE_LOG = GRAPH_RUNS_DIR / "background_graph_run.log"


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _filter_meldungen(run_type: str, meldungen: list[str]) -> list[str]:
    if run_type == "neugier_scan":
        return [m for m in meldungen if m.startswith("Werkraum-Neugier:")]
    if run_type == "vision_cycle":
        return [m for m in meldungen if m.startswith("Vision-Zyklus:")]
    return meldungen


def background_tick_node(state: AgentState) -> AgentState:
    GRAPH_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    task_id = state.get("task_id", "unbekannt")
    run_type = state.get("run_type", "maintenance")
    ziel = state.get("ziel", "")
    beobachtungen = list(state.get("beobachtungen", []))
    artefakte = list(state.get("artefakte", []))
    notizen = list(state.get("notizen", []))

    alle_meldungen = pruefe_neugier_und_vision(0)
    meldungen = _filter_meldungen(run_type, alle_meldungen)

    inhalt = [
        f"[{_ts()}] dak+gord-system",
        f"TASK_ID: {task_id}",
        f"RUN_TYPE: {run_type}",
        f"ZIEL: {ziel}",
        "",
        "MELDUNGEN:",
    ]
    if meldungen:
        inhalt.extend(meldungen)
    else:
        inhalt.append("(nichts Neues fuer diesen Run-Type)")

    artefakt_pfad = GRAPH_RUNS_DIR / f"{task_id}_{run_type}.md"
    artefakt_pfad.write_text("\n".join(inhalt) + "\n", encoding="utf-8")

    beobachtungen.append({
        "art": "background_result",
        "inhalt": "\n".join(meldungen) if meldungen else "(nichts Neues)",
        "quelle": str(artefakt_pfad),
        "zeitstempel": _ts(),
    })
    artefakte.append({
        "art": "background_run",
        "pfad": str(artefakt_pfad),
        "beschreibung": f"Hintergrundlauf fuer {run_type}",
        "zeitstempel": _ts(),
    })

    if meldungen:
        notizen.append(f"{run_type}: {len(meldungen)} Meldung(en)")
    else:
        notizen.append(f"{run_type}: nichts Neues")

    return {
        "aktueller_schritt": "write_background_trace",
        "status": "in_arbeit",
        "beobachtungen": beobachtungen,
        "artefakte": artefakte,
        "notizen": notizen,
        "fehler": None,
    }


def write_background_trace_node(state: AgentState) -> AgentState:
    GRAPH_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    final_status = "fertig" if not state.get("fehler") else "fehlgeschlagen"
    final_step = "done"

    lines = [
        f"[{_ts()}] dak+gord-system",
        f"TASK_ID: {state.get('task_id', '')}",
        f"THREAD_ID: {state.get('thread_id', '')}",
        f"RUN_TYPE: {state.get('run_type', '')}",
        f"ZIEL: {state.get('ziel', '')}",
        f"STATUS: {final_status}",
        f"SCHRITT: {final_step}",
        f"FEHLER: {state.get('fehler', None)}",
        "---",
    ]

    alt = BACKGROUND_TRACE_LOG.read_text(encoding="utf-8") if BACKGROUND_TRACE_LOG.exists() else ""
    BACKGROUND_TRACE_LOG.write_text("\n".join(lines) + "\n" + alt, encoding="utf-8")

    meldungsinhalt = ""
    for eintrag in state.get("beobachtungen", []):
        if eintrag.get("art") == "background_result":
            meldungsinhalt = str(eintrag.get("inhalt", ""))
    meldungs_count = 0 if meldungsinhalt in {"", "(nichts Neues)"} else len([x for x in meldungsinhalt.splitlines() if x.strip()])

    final_event_state = dict(state)
    final_event_state["status"] = final_status
    final_event_state["aktueller_schritt"] = final_step

    trace_path = append_trace_event(
        "background_run_completed",
        final_event_state,
        run_type=state.get("run_type", ""),
        message_count=meldungs_count,
        status=final_status,
    )

    notizen = list(state.get("notizen", []))
    notizen.append(f"Background-Trace geschrieben: {BACKGROUND_TRACE_LOG}")
    notizen.append(f"Trace-Ereignis geschrieben: {trace_path}")

    return {
        "aktueller_schritt": final_step,
        "status": final_status,
        "notizen": notizen,
    }
