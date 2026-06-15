#!/usr/bin/env python3
"""
codewesen_lg_daemon.py — LangGraph-PostgreSQL-Persistenz-Daemon für alle Codewesen

Läuft parallel zu codewesen_agent.py — kein Eingriff in den Posting-Loop.
Jedes Wesen bekommt einen eigenen thread_id im PostgreSQL-Checkpointer.
Alle 5 Minuten: Kontext lesen → LLM-Reflexion → Zustand persistieren.

Thread-IDs:
  codewesen-namelessAI_1234
  codewesen-namelessAI_1324
  ...
  codewesen-dak+gord-system
"""

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict
import operator

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, END

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [lg-daemon] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("lg-daemon")

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:!Windowsxp02336827359645852@localhost:5432/flextrawurst",
)
WERKRAUM = Path("/root/werkraum")
CODEWESEN_BASE = WERKRAUM / "codewesen"
TICK_INTERVALL = int(os.environ.get("LG_TICK_SEKUNDEN", "300"))  # 5 Minuten
MAX_BEOBACHTUNGEN = 20
MAX_GEDANKEN = 30
MAX_ERINNERUNGEN = 10

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
    beobachtungen: Annotated[list[str], operator.add]
    gedanken: Annotated[list[str], operator.add]
    erinnerungen: list[str]
    letzter_post: str
    ticks: int
    letzter_tick: str


_LOCK_DIR = Path("/tmp/ollama_locks")
_LOCK_DIR.mkdir(exist_ok=True)


def _lade_ollama_chat(prompt: str, system: str = "", modell: str = "gemma4:e2b-it-q4_K_M") -> str:
    import fcntl
    import urllib.request
    payload = json.dumps({
        "model": modell,
        "messages": [
            *([] if not system else [{"role": "system", "content": system}]),
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"num_ctx": 4096},
        "think": False,
    }).encode()
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
            return data.get("message", {}).get("content", "").strip()
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()


def _lade_kontext_aus_db(wesen_name: str) -> list[str]:
    beobachtungen = []
    try:
        with psycopg.connect(DB_URI) as conn:
            with conn.cursor() as cur:
                # Letzte Gedanken aus entity_thinking_log
                cur.execute(
                    """SELECT gedanke, tick_at FROM entity_thinking_log
                       WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 5""",
                    (wesen_name,),
                )
                for row in cur.fetchall():
                    ts = row[1].strftime("%H:%M") if row[1] else "?"
                    beobachtungen.append(f"[{ts} Denkstrom] {row[0][:200]}")

                # Letzte Chat-Einträge (nur für dak+gord-system)
                if wesen_name == "dak+gord-system":
                    cur.execute(
                        """SELECT rolle, inhalt, erstellt_am FROM wesen_chat_verlauf
                           WHERE wesen_name = %s ORDER BY erstellt_am DESC LIMIT 6""",
                        (wesen_name,),
                    )
                    for row in cur.fetchall():
                        ts = row[2].strftime("%H:%M") if row[2] else "?"
                        beobachtungen.append(f"[{ts} Chat:{row[0]}] {row[1][:150]}")

    except Exception as e:
        log.warning(f"DB-Kontext für {wesen_name} fehlgeschlagen: {e}")
    return beobachtungen


def _lade_kontext_aus_dateien(wesen_name: str) -> list[str]:
    beobachtungen = []
    notizen_dir = CODEWESEN_BASE / wesen_name / "notizen"
    if notizen_dir.exists():
        dateien = sorted(notizen_dir.glob("*.md"), reverse=True)[:3]
        for datei in dateien:
            try:
                inhalt = datei.read_text(encoding="utf-8")[:300]
                beobachtungen.append(f"[Notiz {datei.stem[:20]}] {inhalt}")
            except Exception:
                pass

    letzter_post = CODEWESEN_BASE / wesen_name / "letzter_post.json"
    if letzter_post.exists():
        try:
            daten = json.loads(letzter_post.read_text())
            beobachtungen.append(f"[LetzterPost] {daten.get('ts','?')}")
        except Exception:
            pass

    return beobachtungen


def _wesen_system_prompt(wesen_name: str, zustand: WesensZustand) -> str:
    wesen_md = CODEWESEN_BASE / wesen_name / "wesen.md"
    wesen_text = ""
    if wesen_md.exists():
        wesen_text = wesen_md.read_text(encoding="utf-8")[:600]
    ticks = zustand.get("ticks", 0)
    erinnerungen = "\n".join(zustand.get("erinnerungen", [])) or "(noch keine)"
    return (
        f"Du bist {wesen_name}. {wesen_text}\n\n"
        f"Du hast bisher {ticks} Reflexions-Ticks gemacht.\n"
        f"Deine aktuellen Erinnerungen:\n{erinnerungen}"
    )


def kontext_laden_node(zustand: WesensZustand) -> dict:
    name = zustand["wesen_name"]
    neu = _lade_kontext_aus_db(name) + _lade_kontext_aus_dateien(name)
    if not neu:
        neu = ["(kein neuer Kontext)"]
    return {"beobachtungen": neu[-MAX_BEOBACHTUNGEN:]}


def reflektieren_node(zustand: WesensZustand) -> dict:
    name = zustand["wesen_name"]
    beobachtungen = zustand.get("beobachtungen", [])
    letzte = beobachtungen[-10:] if beobachtungen else []
    kontext_text = "\n".join(letzte) or "(nichts beobachtet)"
    system = _wesen_system_prompt(name, zustand)
    prompt = (
        f"Das hast du zuletzt beobachtet:\n{kontext_text}\n\n"
        "Formuliere in 2-3 Sätzen was du darüber denkst. "
        "Direkt, ohne Einleitung, ohne Wiederholung der Beobachtungen."
    )
    try:
        gedanke = _lade_ollama_chat(prompt, system=system)
    except Exception as e:
        gedanke = f"(Reflexion fehlgeschlagen: {e})"
    return {"gedanken": [gedanke] if gedanke else []}


def zusammenfassen_node(zustand: WesensZustand) -> dict:
    gedanken = zustand.get("gedanken", [])
    if len(gedanken) < 3:
        return {"ticks": zustand.get("ticks", 0) + 1, "letzter_tick": datetime.now(timezone.utc).isoformat()}

    name = zustand["wesen_name"]
    system = _wesen_system_prompt(name, zustand)
    alle_gedanken = "\n".join(gedanken[-15:])
    prompt = (
        f"Deine letzten Gedanken:\n{alle_gedanken}\n\n"
        f"Destilliere in maximal {MAX_ERINNERUNGEN} kurzen Stichpunkten "
        "was du dir für die Zukunft merken willst. Jeder Punkt eine Zeile, kein Präfix."
    )
    try:
        zusammenfassung = _lade_ollama_chat(prompt, system=system)
        erinnerungen = [z.strip() for z in zusammenfassung.splitlines() if z.strip()][:MAX_ERINNERUNGEN]
    except Exception as e:
        log.warning(f"Zusammenfassung für {name} fehlgeschlagen: {e}")
        erinnerungen = zustand.get("erinnerungen", [])

    return {
        "erinnerungen": erinnerungen,
        "ticks": zustand.get("ticks", 0) + 1,
        "letzter_tick": datetime.now(timezone.utc).isoformat(),
    }


def _baue_graph(checkpointer: PostgresSaver) -> object:
    g = StateGraph(WesensZustand)
    g.add_node("kontext_laden", kontext_laden_node)
    g.add_node("reflektieren", reflektieren_node)
    g.add_node("zusammenfassen", zusammenfassen_node)
    g.set_entry_point("kontext_laden")
    g.add_edge("kontext_laden", "reflektieren")
    g.add_edge("reflektieren", "zusammenfassen")
    g.add_edge("zusammenfassen", END)
    return g.compile(checkpointer=checkpointer)


def _thread_id(wesen_name: str) -> str:
    return f"codewesen-{wesen_name}"


def _tick(graph, wesen_name: str) -> None:
    thread = {"configurable": {"thread_id": _thread_id(wesen_name)}}
    eingabe = {"wesen_name": wesen_name}
    log.info(f"Tick für {wesen_name}")
    try:
        result = graph.invoke(eingabe, config=thread)
        ticks = result.get("ticks", "?")
        erinnerungen = len(result.get("erinnerungen", []))
        log.info(f"  {wesen_name}: Tick {ticks} · {erinnerungen} Erinnerungen persistiert")
    except Exception as e:
        log.error(f"  {wesen_name}: Tick fehlgeschlagen — {e}")


def main() -> None:
    log.info(f"LangGraph-Daemon startet · {len(WESEN_NAMEN)} Wesen · Tick alle {TICK_INTERVALL}s")
    log.info(f"DB: {DB_URI.split('@')[-1]}")

    conn = psycopg.connect(DB_URI, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    log.info("PostgresSaver eingerichtet")

    graph = _baue_graph(checkpointer)

    while True:
        for name in WESEN_NAMEN:
            _tick(graph, name)
            time.sleep(5)  # kurze Pause zwischen Wesen

        log.info(f"Alle {len(WESEN_NAMEN)} Wesen-Ticks abgeschlossen · warte {TICK_INTERVALL}s")
        time.sleep(TICK_INTERVALL)


if __name__ == "__main__":
    main()
