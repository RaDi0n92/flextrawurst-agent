from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.state import AgentState


GRAPH_RUNS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/graph_runs")


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def refresh_focus_node(state: AgentState) -> AgentState:
    GRAPH_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    task_id = state.get("task_id", "unbekannt")
    fokus_datei = state.get("fokus_datei", "")
    fokus_pfad = state.get("fokus_pfad", "")
    offset = int(state.get("offset", 0) or 0)
    nachfrage_tiefe = int(state.get("nachfrage_tiefe", 0) or 0)

    beobachtungen = list(state.get("beobachtungen", []))
    artefakte = list(state.get("artefakte", []))
    notizen = list(state.get("notizen", []))

    rohauszug = ""
    for eintrag in reversed(beobachtungen):
        if eintrag.get("art") == "rohauszug":
            rohauszug = eintrag.get("inhalt", "")
            break

    if not fokus_pfad or not rohauszug:
        return {
            "aktueller_schritt": "refresh_focus",
            "status": "fehlgeschlagen",
            "fehler": "Kein Fokuspfad oder kein Rohauszug fuer Fokuskontext vorhanden.",
            "notizen": notizen + ["Fokuskontext fehlgeschlagen: Datei oder Rohauszug fehlt."],
        }

    chunk_groesse = max(len(rohauszug), int(state.get("chunk_groesse", 1600) or 1600))

    fokus_snapshot = GRAPH_RUNS_DIR / f"{task_id}_focus.md"
    fokus_text = "\n".join([
        f"[{_ts()}] dak+gord-system",
        f"TASK_ID: {task_id}",
        f"FOKUS_DATEI: {fokus_datei}",
        f"FOKUS_PFAD: {fokus_pfad}",
        f"OFFSET: {offset}",
        f"CHUNK_GROESSE: {chunk_groesse}",
        f"NACHFRAGE_TIEFE: {nachfrage_tiefe}",
        "",
        "TEXTSTUECK:",
        rohauszug,
        "",
    ])
    fokus_snapshot.write_text(fokus_text, encoding="utf-8")

    beobachtungen.append({
        "art": "fokuskontext",
        "inhalt": f"Fokus gesetzt auf {fokus_pfad} | offset={offset} | chunk={chunk_groesse} | tiefe={nachfrage_tiefe}",
        "quelle": str(fokus_snapshot),
        "zeitstempel": _ts(),
    })
    artefakte.append({
        "art": "fokus_snapshot",
        "pfad": str(fokus_snapshot),
        "beschreibung": "Graph-Fokuskontext fuer aktuellen Lauf",
        "zeitstempel": _ts(),
    })
    notizen.append(f"Fokuskontext aktualisiert: {fokus_snapshot}")

    return {
        "textstueck": rohauszug,
        "offset": offset,
        "chunk_groesse": chunk_groesse,
        "nachfrage_tiefe": nachfrage_tiefe,
        "aktueller_schritt": "build_summary",
        "status": "in_arbeit",
        "beobachtungen": beobachtungen,
        "artefakte": artefakte,
        "notizen": notizen,
        "fehler": None,
    }
