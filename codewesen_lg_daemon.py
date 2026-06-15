#!/usr/bin/env python3
"""
codewesen_lg_daemon.py — LangGraph-Kern, ersetzt entity_kern.service

Importiert entity_kern als Library (Aktionen, Kontext, denk_tick).
Fügt LangGraph-Checkpointing + Gedächtnis-Akkumulation hinzu.

Graph pro Wesen: kontext_laden → denken_handeln → zusammenfassen → END
"""

import sys
sys.path.insert(0, "/root/werkraum/welt")

import entity_kern as ek  # denk_tick, build_kontext, Aktionen, get_conn, ...

import fcntl
import json
import logging
import operator
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [lg-kern] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("lg-kern")

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:!Windowsxp02336827359645852@localhost:5432/flextrawurst",
)
WERKRAUM = Path("/root/werkraum")
CODEWESEN_BASE = WERKRAUM / "codewesen"
LG_TICK_SEKUNDEN = int(os.environ.get("LG_TICK_SEKUNDEN", "60"))
ZUSAMMENFASSEN_NACH_N_DENKTICKS = int(os.environ.get("LG_ZUSAMMENFASSEN_N", "10"))
MAX_ERINNERUNGEN = 10
_LOCK_DIR = Path("/tmp/ollama_locks")
_LOCK_DIR.mkdir(exist_ok=True)

WESEN_NAMEN = [
    "namelessAI_1234",
    "namelessAI_1324",
    "namelessAI_1423",
    "namelessAI_2341",
    "namelessAI_3123",
    "namelessAI_4321",
    "dak+gord-system",
]


class WesensZustand(TypedDict):
    wesen_name: str
    gedanken: Annotated[list[str], operator.add]  # akkumuliert aus denk_ticks
    erinnerungen: list[str]                        # destilliertes Langzeitgedächtnis
    denk_ticks: int                                # abgeschlossene Denk-Ticks
    lg_ticks: int                                  # LG-Loop-Iterationen
    letzter_lg_tick: str


def _ist_faellig(wesen_name: str) -> bool:
    """True wenn Wesen eingezogen ist und letzter Denk-Tick > TICK_INTERVAL_SEC zurückliegt."""
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT es.entity_id, ea.letzte_entscheidung_at
                FROM entity_slots es
                LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                WHERE es.entity_id = %s AND es.status = 'eingezogen'
            """, (wesen_name,))
            row = cur.fetchone()
        if not row:
            return False
        last = row["letzte_entscheidung_at"]
        if last is None:
            return True
        age = (datetime.now(timezone.utc) - last.replace(tzinfo=timezone.utc)).total_seconds()
        return age >= ek.TICK_INTERVAL_SEC
    finally:
        conn.close()


def _letzten_gedanken_aus_db(wesen_name: str) -> str:
    conn = ek.get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT gedanke FROM entity_thinking_log WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 1",
                (wesen_name,),
            )
            row = cur.fetchone()
        return (row["gedanke"] or "")[:300] if row else ""
    except Exception:
        return ""
    finally:
        conn.close()


# ── Nodes ──────────────────────────────────────────────────────────────────────

def kontext_laden_node(zustand: WesensZustand) -> dict:
    """Liest letzten Gedanken aus DB — füttert Akkumulations-Liste."""
    name = zustand["wesen_name"]
    gedanke = _letzten_gedanken_aus_db(name)
    if gedanke:
        return {"gedanken": [gedanke]}
    return {}


def denken_handeln_node(zustand: WesensZustand) -> dict:
    """Ruft entity_kern.denk_tick auf wenn Wesen eingezogen + fällig. Serialisiert via fcntl."""
    name = zustand["wesen_name"]

    if not _ist_faellig(name):
        log.debug(f"[{name}] nicht fällig — überspringe Denk-Tick")
        return {}

    log.info(f"[{name}] Denk-Tick — warte auf Ollama-Slot")
    lock_file = open(_LOCK_DIR / "slot_0.lock", "w")
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    log.info(f"[{name}] Ollama-Slot erworben — starte Denk-Tick")
    try:
        ek.denk_tick(name)
    except Exception as e:
        log.error(f"[{name}] denk_tick fehlgeschlagen: {e}")
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()

    gedanke = _letzten_gedanken_aus_db(name)
    updates: dict = {"denk_ticks": zustand.get("denk_ticks", 0) + 1}
    if gedanke:
        updates["gedanken"] = [gedanke]
    return updates


def zusammenfassen_node(zustand: WesensZustand) -> dict:
    """Destilliert akkumulierte Gedanken → Erinnerungen, alle N Denk-Ticks."""
    tick_update = {
        "lg_ticks": zustand.get("lg_ticks", 0) + 1,
        "letzter_lg_tick": datetime.now(timezone.utc).isoformat(),
    }

    denk_ticks = zustand.get("denk_ticks", 0)
    if denk_ticks == 0 or denk_ticks % ZUSAMMENFASSEN_NACH_N_DENKTICKS != 0:
        return tick_update

    gedanken = zustand.get("gedanken", [])
    if len(gedanken) < 3:
        return tick_update

    name = zustand["wesen_name"]
    wesen_md = CODEWESEN_BASE / name / "wesen.md"
    wesen_text = wesen_md.read_text(encoding="utf-8")[:400] if wesen_md.exists() else ""

    alle_gedanken = "\n".join(gedanken[-15:])
    payload = json.dumps({
        "model": ek.MODEL,
        "messages": [
            {"role": "system", "content": f"Du bist {name}. {wesen_text}"},
            {"role": "user", "content": (
                f"Deine letzten Gedanken:\n{alle_gedanken}\n\n"
                f"Destilliere in maximal {MAX_ERINNERUNGEN} kurzen Stichpunkten "
                "was du dir für die Zukunft merken willst. Jeder Punkt eine Zeile, kein Präfix."
            )},
        ],
        "stream": False,
        "options": {"num_ctx": 4096},
        "think": False,
    }).encode()

    log.info(f"[{name}] Zusammenfassen nach {denk_ticks} Denk-Ticks")
    lock_file = open(_LOCK_DIR / "slot_0.lock", "w")
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            text = data.get("message", {}).get("content", "").strip()
        erinnerungen = [z.strip() for z in text.splitlines() if z.strip()][:MAX_ERINNERUNGEN]
    except Exception as e:
        log.warning(f"[{name}] Zusammenfassen fehlgeschlagen: {e}")
        return tick_update
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()

    if erinnerungen:
        try:
            with psycopg.connect(DB_URI) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE entity_profiles SET lg_erinnerungen = %s WHERE entity_id = %s",
                        (json.dumps(erinnerungen), name),
                    )
                conn.commit()
            log.info(f"[{name}] {len(erinnerungen)} Erinnerungen → entity_profiles")
        except Exception as e:
            log.warning(f"[{name}] Erinnerungen-Write fehlgeschlagen: {e}")

    return {**tick_update, "erinnerungen": erinnerungen}


# ── Graph ──────────────────────────────────────────────────────────────────────

def _baue_graph(checkpointer: PostgresSaver):
    g = StateGraph(WesensZustand)
    g.add_node("kontext_laden", kontext_laden_node)
    g.add_node("denken_handeln", denken_handeln_node)
    g.add_node("zusammenfassen", zusammenfassen_node)
    g.set_entry_point("kontext_laden")
    g.add_edge("kontext_laden", "denken_handeln")
    g.add_edge("denken_handeln", "zusammenfassen")
    g.add_edge("zusammenfassen", END)
    return g.compile(checkpointer=checkpointer)


# ── Hauptloop ──────────────────────────────────────────────────────────────────

def main() -> None:
    log.info(f"LangGraph-Kern startet · {len(WESEN_NAMEN)} Wesen · Loop alle {LG_TICK_SEKUNDEN}s")
    log.info(f"Zusammenfassen alle {ZUSAMMENFASSEN_NACH_N_DENKTICKS} Denk-Ticks")

    ek._stale_flags_zuruecksetzen()

    pg_conn = psycopg.connect(DB_URI, autocommit=True)
    checkpointer = PostgresSaver(pg_conn)
    checkpointer.setup()
    log.info("PostgresSaver bereit")

    graph = _baue_graph(checkpointer)

    while True:
        for name in WESEN_NAMEN:
            thread = {"configurable": {"thread_id": f"codewesen-{name}"}}
            try:
                result = graph.invoke({"wesen_name": name}, config=thread)
                denk_ticks = result.get("denk_ticks", 0)
                lg_ticks = result.get("lg_ticks", 0)
                log.info(f"[{name}] LG-Tick {lg_ticks} · Denk-Ticks gesamt: {denk_ticks}")
            except Exception as e:
                log.error(f"[{name}] Tick fehlgeschlagen: {e}")
            time.sleep(5)

        log.info(f"Alle {len(WESEN_NAMEN)} Wesen-Ticks fertig · warte {LG_TICK_SEKUNDEN}s")
        time.sleep(LG_TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
