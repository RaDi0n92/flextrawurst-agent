from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.agentdateien import _split_verlauf_bloecke, _schreibe_datei_mit_dossier


WERKRAUM_ROOT = Path("/root/werkraum")
AGENTDATEIEN_ROOT = WERKRAUM_ROOT / "agent" / "dak_gord_system" / "spuren" / "agentdateien"


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _agentdatei_pfad(quellpfad: str) -> Path:
    quelle = Path(quellpfad)
    rel = quelle.relative_to(WERKRAUM_ROOT)
    ziel = AGENTDATEIEN_ROOT / rel
    return ziel.with_suffix(".agent.md")


def refresh_agent_file_node(state: AgentState) -> AgentState:
    task_id = state.get("task_id", "unbekannt")
    fokus_pfad = state.get("fokus_pfad", "")
    ziel = state.get("ziel", "")
    beobachtungen = list(state.get("beobachtungen", []))
    artefakte = list(state.get("artefakte", []))
    notizen = list(state.get("notizen", []))

    if not fokus_pfad:
        return {
            "aktueller_schritt": "refresh_agent_file",
            "status": "fehlgeschlagen",
            "fehler": "Kein fokus_pfad fuer Agentdatei vorhanden.",
            "notizen": notizen + ["Agentdatei-Refresh fehlgeschlagen: fokus_pfad fehlt."],
        }

    rohauszug = ""
    verdichtung_text = ""

    for eintrag in reversed(beobachtungen):
        if not rohauszug and eintrag.get("art") == "rohauszug":
            rohauszug = eintrag.get("inhalt", "")
        if not verdichtung_text and eintrag.get("art") == "verdichtung":
            verdichtung_text = eintrag.get("inhalt", "")

    agent_pfad = _agentdatei_pfad(fokus_pfad)
    agent_pfad.parent.mkdir(parents=True, exist_ok=True)

    if agent_pfad.exists():
        alt = agent_pfad.read_text(encoding="utf-8")
        _, bloecke = _split_verlauf_bloecke(alt)
    else:
        bloecke = []

    neuer_block = "\n".join([
        f"[{_ts()}] dak+gord-system",
        "ART: graph_run_dossier",
        "HERKUNFT: graph_run",
        f"QUELLE: {fokus_pfad}",
        f"TASK_ID: {task_id}",
        f"ZIEL: {ziel}",
        "ROHAUSZUG:",
        rohauszug,
        "VERDICHTUNG:",
        verdichtung_text,
    ]).strip()

    bloecke.append(neuer_block)
    _schreibe_datei_mit_dossier(agent_pfad, fokus_pfad, bloecke)

    artefakte.append({
        "art": "agentdatei",
        "pfad": str(agent_pfad),
        "beschreibung": "Agentdatei nach Graph-Lauf aktualisiert",
        "zeitstempel": _ts(),
    })
    notizen.append(f"Agentdatei aktualisiert: {agent_pfad}")

    return {
        "aktueller_schritt": "write_trace",
        "status": "in_arbeit",
        "artefakte": artefakte,
        "notizen": notizen,
        "fehler": None,
    }
