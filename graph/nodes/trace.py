from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.state import AgentState


GRAPH_RUNS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/graph_runs")
TRACE_LOG = GRAPH_RUNS_DIR / "graph_run.log"


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_trace_node(state: AgentState) -> AgentState:
    GRAPH_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    final_status = "fertig" if not state.get("fehler") else "fehlgeschlagen"
    final_step = "done"

    lines = [
        f"[{_ts()}] dak+gord-system",
        f"TASK_ID: {state.get('task_id', '')}",
        f"THREAD_ID: {state.get('thread_id', '')}",
        f"RUN_TYPE: {state.get('run_type', '')}",
        f"ZIEL: {state.get('ziel', '')}",
        f"FOKUS_DATEI: {state.get('fokus_datei', '')}",
        f"FOKUS_PFAD: {state.get('fokus_pfad', '')}",
        f"STATUS: {final_status}",
        f"SCHRITT: {final_step}",
        f"FEHLER: {state.get('fehler', None)}",
        "---",
    ]

    alt = TRACE_LOG.read_text(encoding="utf-8") if TRACE_LOG.exists() else ""
    TRACE_LOG.write_text("\n".join(lines) + "\n" + alt, encoding="utf-8")

    notizen = list(state.get("notizen", []))
    notizen.append(f"Trace geschrieben: {TRACE_LOG}")

    return {
        "aktueller_schritt": final_step,
        "status": final_status,
        "notizen": notizen,
    }
