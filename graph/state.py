from __future__ import annotations

from datetime import datetime
from typing import Literal, TypedDict


AgentStatus = Literal[
    "neu",
    "in_arbeit",
    "wartet_auf_freigabe",
    "blockiert",
    "fertig",
    "fehlgeschlagen",
]

ApprovalStatus = Literal[
    "nicht_noetig",
    "offen",
    "genehmigt",
    "abgelehnt",
]


class Beobachtung(TypedDict, total=False):
    art: str
    inhalt: str
    quelle: str
    zeitstempel: str


class Artefakt(TypedDict, total=False):
    art: str
    pfad: str
    beschreibung: str
    zeitstempel: str


class ToolAktion(TypedDict, total=False):
    tool: str
    aktion: str
    eingabe: str
    ergebnis: str
    erfolgreich: bool
    zeitstempel: str


class AgentState(TypedDict, total=False):
    task_id: str
    thread_id: str
    run_type: str
    ziel: str
    modus: str
    fokus_datei: str
    fokus_pfad: str
    textstueck: str
    offset: int
    chunk_groesse: int
    nachfrage_tiefe: int
    shell_argv: list[str]
    shell_cwd: str
    shell_timeout_sec: int
    tool_name: str
    tool_args: dict[str, object]
    tool_aktion: str
    approval_reason: str
    approval_request_path: str
    aktueller_schritt: str
    status: AgentStatus
    beobachtungen: list[Beobachtung]
    artefakte: list[Artefakt]
    letzte_tool_aktionen: list[ToolAktion]
    approval_status: ApprovalStatus
    fehler: str | None
    notizen: list[str]


def _zeitstempel() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def new_agent_state(
    *,
    task_id: str,
    thread_id: str,
    run_type: str,
    ziel: str,
    modus: str,
    fokus_datei: str = "",
    fokus_pfad: str = "",
    textstueck: str = "",
    offset: int = 0,
    chunk_groesse: int = 1600,
    nachfrage_tiefe: int = 0,
    aktueller_schritt: str = "start",
) -> AgentState:
    return {
        "task_id": task_id,
        "thread_id": thread_id,
        "run_type": run_type,
        "ziel": ziel,
        "modus": modus,
        "fokus_datei": fokus_datei,
        "fokus_pfad": fokus_pfad,
        "textstueck": textstueck,
        "offset": offset,
        "chunk_groesse": chunk_groesse,
        "nachfrage_tiefe": nachfrage_tiefe,
        "aktueller_schritt": aktueller_schritt,
        "status": "neu",
        "beobachtungen": [],
        "artefakte": [],
        "letzte_tool_aktionen": [],
        "approval_status": "nicht_noetig",
        "approval_reason": "",
        "approval_request_path": "",
        "fehler": None,
        "notizen": [f"state erstellt: {_zeitstempel()}"],
    }
