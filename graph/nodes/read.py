from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.graph.state import AgentState
from agent.dak_gord_system.graph.tools.runtime import run_registered_tool


WERKRAUM_ROOT = Path("/root/werkraum")


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def resolve_file_node(state: AgentState) -> AgentState:
    fokus_datei = (state.get("fokus_datei") or "").strip()
    fokus_pfad = (state.get("fokus_pfad") or "").strip()

    resolved = ""
    if fokus_pfad and Path(fokus_pfad).exists():
        resolved = fokus_pfad
    elif fokus_datei:
        matches = list(WERKRAUM_ROOT.rglob(fokus_datei))
        if matches:
            resolved = str(matches[0])

    beobachtungen = list(state.get("beobachtungen", []))
    notizen = list(state.get("notizen", []))

    if resolved:
        beobachtungen.append({
            "art": "datei_aufgeloest",
            "inhalt": resolved,
            "quelle": "resolve_file_node",
            "zeitstempel": _ts(),
        })
        notizen.append(f"Datei aufgeloest: {resolved}")
        return {
            "fokus_pfad": resolved,
            "aktueller_schritt": "read_file",
            "status": "in_arbeit",
            "beobachtungen": beobachtungen,
            "notizen": notizen,
            "fehler": None,
        }

    notizen.append(f"Datei konnte nicht aufgeloest werden: {fokus_datei or fokus_pfad}")
    return {
        "aktueller_schritt": "resolve_file",
        "status": "fehlgeschlagen",
        "fehler": f"Datei nicht gefunden: {fokus_datei or fokus_pfad}",
        "notizen": notizen,
    }


def read_file_node(state: AgentState) -> AgentState:
    fokus_pfad = (state.get("fokus_pfad") or "").strip()
    beobachtungen = list(state.get("beobachtungen", []))
    notizen = list(state.get("notizen", []))
    letzte_tool_aktionen = list(state.get("letzte_tool_aktionen", []))
    chunk_groesse = int(state.get("chunk_groesse", 1600) or 1600)

    if not fokus_pfad:
        return {
            "status": "fehlgeschlagen",
            "fehler": "Kein fokus_pfad zum Lesen vorhanden.",
            "aktueller_schritt": "read_file",
        }

    result, tool_aktion = run_registered_tool(
        state,
        "read_text_file",
        {"path": fokus_pfad, "max_chars": chunk_groesse},
        aktion="datei_lesen",
    )
    letzte_tool_aktionen.append(tool_aktion)

    if not result.ok:
        return {
            "status": "fehlgeschlagen",
            "fehler": result.error or "Tool-Lauf read_text_file fehlgeschlagen.",
            "aktueller_schritt": "read_file",
            "letzte_tool_aktionen": letzte_tool_aktionen,
        }

    output = result.output or {}
    auszug = str(output.get("text", ""))

    beobachtungen.append({
        "art": "rohauszug",
        "inhalt": auszug,
        "quelle": fokus_pfad,
        "zeitstempel": _ts(),
    })
    notizen.append(f"Datei ueber Tool gelesen: {fokus_pfad}")

    return {
        "aktueller_schritt": "refresh_focus",
        "status": "in_arbeit",
        "beobachtungen": beobachtungen,
        "notizen": notizen,
        "letzte_tool_aktionen": letzte_tool_aktionen,
        "fehler": None,
    }
