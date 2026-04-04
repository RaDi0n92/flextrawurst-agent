from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.verdichtung import verdichte_text, formatiere_verdichtungsblock


GRAPH_RUNS_DIR = Path("/root/werkraum/agent/dak_gord_system/spuren/graph_runs")


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def build_summary_node(state: AgentState) -> AgentState:
    GRAPH_RUNS_DIR.mkdir(parents=True, exist_ok=True)

    task_id = state.get("task_id", "unbekannt")
    fokus_pfad = state.get("fokus_pfad", "")
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
            "aktueller_schritt": "build_summary",
            "status": "fehlgeschlagen",
            "fehler": "Keine Datei oder kein Rohauszug fuer Verdichtung vorhanden.",
            "notizen": notizen + ["Verdichtung fehlgeschlagen: Datei oder Rohauszug fehlt."],
        }

    ergebnis = verdichte_text(
        art="graph_datei_lesen",
        datei=fokus_pfad,
        textauszug=rohauszug,
        offset=0,
        chunk_groesse=len(rohauszug),
    )
    verdichtung_text = formatiere_verdichtungsblock(ergebnis)

    verdichtung_pfad = GRAPH_RUNS_DIR / f"{task_id}_verdichtung.md"
    verdichtung_pfad.write_text(verdichtung_text, encoding="utf-8")

    beobachtungen.append({
        "art": "verdichtung",
        "inhalt": verdichtung_text[:2000],
        "quelle": str(verdichtung_pfad),
        "zeitstempel": _ts(),
    })
    artefakte.append({
        "art": "verdichtung",
        "pfad": str(verdichtung_pfad),
        "beschreibung": "Verdichtung aus Graph-Lauf",
        "zeitstempel": _ts(),
    })
    notizen.append(f"Verdichtung geschrieben: {verdichtung_pfad}")

    return {
        "aktueller_schritt": "refresh_agent_file",
        "status": "in_arbeit",
        "beobachtungen": beobachtungen,
        "artefakte": artefakte,
        "notizen": notizen,
        "fehler": None,
    }
