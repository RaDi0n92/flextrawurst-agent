#!/usr/bin/env python3
"""
geni_lg.py — LangGraph PostgreSQL Persistenz für GENI-Sessions.

Ersetzt _sessions (in-memory dict) durch PostgreSQL-Checkpoint.
Thread-IDs: geni-{session_id}
Erinnerungen werden alle DESTILLATIONS_INTERVALL Turns destilliert.
"""
import json
import logging
import os
import urllib.request
from typing import TypedDict

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END

log = logging.getLogger("geni-lg")

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:!Windowsxp02336827359645852@localhost:5432/flextrawurst",
)
OLLAMA = "http://localhost:11434"
MODEL = "gemma4:e2b-it-q4_K_M"
MAX_VERLAUF = 20
MAX_ERINNERUNGEN = 8
DESTILLATIONS_INTERVALL = 10


class GeniZustand(TypedDict):
    session_id: str
    verlauf: list
    erinnerungen: list
    turn_count: int


_pg_conn: psycopg.Connection | None = None
_checkpointer: PostgresSaver | None = None
_graph = None


def _init() -> None:
    global _pg_conn, _checkpointer, _graph
    if _graph is not None:
        return
    _pg_conn = psycopg.connect(DB_URI, autocommit=True)
    _checkpointer = PostgresSaver(_pg_conn)
    _checkpointer.setup()

    def _passthrough(state: GeniZustand) -> dict:
        return {}

    g = StateGraph(GeniZustand)
    g.add_node("tick", _passthrough)
    g.set_entry_point("tick")
    g.add_edge("tick", END)
    _graph = g.compile(checkpointer=_checkpointer)
    log.info("GENI LangGraph bereit — PostgresSaver eingerichtet")


def _thread(session_id: str) -> dict:
    return {"configurable": {"thread_id": f"geni-{session_id}"}}


def lade_session(session_id: str) -> dict:
    """Lädt Session-Zustand aus PostgreSQL. Neu → leerer Zustand."""
    _init()
    try:
        snap = _graph.get_state(_thread(session_id))
        if snap and snap.values:
            return dict(snap.values)
    except Exception as e:
        log.warning(f"lade_session({session_id}) fehlgeschlagen: {e}")
    return {"session_id": session_id, "verlauf": [], "erinnerungen": [], "turn_count": 0}


def speichere_session(session_id: str, verlauf: list, turn_count: int, erinnerungen: list) -> None:
    """Schreibt Session-Zustand in PostgreSQL."""
    _init()
    try:
        _graph.invoke(
            {
                "session_id": session_id,
                "verlauf": verlauf[-MAX_VERLAUF:],
                "erinnerungen": (erinnerungen or [])[:MAX_ERINNERUNGEN],
                "turn_count": turn_count,
            },
            config=_thread(session_id),
        )
    except Exception as e:
        log.warning(f"speichere_session({session_id}) fehlgeschlagen: {e}")


def destilliere_erinnerungen(verlauf: list, existing: list) -> list:
    """
    Destilliert die letzten Turns → max. MAX_ERINNERUNGEN Stichpunkte.
    Kein fcntl-Lock — GENI hat eigenes Ollama-Management.
    """
    if len(verlauf) < 4:
        return existing or []

    dialog_text = "\n".join(
        f"{m['role'].upper()}: {m.get('content', '')[:200]}"
        for m in verlauf[-MAX_VERLAUF:]
        if isinstance(m, dict)
    )
    bestehende = "\n".join(f"- {e}" for e in (existing or [])) or "(keine)"

    prompt = (
        f"Das sind unsere letzten Gespräche:\n{dialog_text}\n\n"
        f"Bestehende Erinnerungen:\n{bestehende}\n\n"
        f"Destilliere in maximal {MAX_ERINNERUNGEN} kurzen Stichpunkten "
        "was GENI sich für zukünftige Gespräche mit Daniel merken soll. "
        "Jeder Punkt eine Zeile, kein Präfix, keine Nummerierung."
    )

    try:
        payload = json.dumps({
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Du bist GENI — ein neuronales Gedächtnis-Wesen. Destilliere das Gespräch präzise.",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"num_ctx": 4096, "num_predict": 300},
            "think": False,
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            text = data.get("message", {}).get("content", "").strip()
        result = [z.strip() for z in text.splitlines() if z.strip()][:MAX_ERINNERUNGEN]
        log.info(f"Erinnerungen destilliert: {len(result)} Punkte")
        return result
    except Exception as e:
        log.warning(f"destilliere_erinnerungen fehlgeschlagen: {e}")
        return existing or []
