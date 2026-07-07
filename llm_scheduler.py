#!/usr/bin/env python3
"""
llm_scheduler.py — Prioritaets-Warteschlange fuer die gemeinsam genutzten
llama-server-Instanzen (1 echter Slot je Server, --parallel 1 in den systemd-Units).

Ersetzt das alte /tmp/ollama_locks/slot_0.lock-Semaphor: dort teilten sich alle
~18 Hintergrund-Prozesse EIN Lock (nur 1 effektiver Slot statt 2), die meisten
warteten unbegrenzt lange, und ein 600s-Aufrufer konnte jeden anderen fuer bis
zu 10 Minuten einfrieren — unabhaengig von dessen eigener Dringlichkeit.
Analyse + Simulation dazu: 2026-07-07, siehe docs/systemdoku.

Neues Modell:
  - 1 echter Slot pro Server wird auch als 1 nutzbarer Slot behandelt.
  - Prioritaetsstufen (PRIO_HOCH/NORMAL/NIEDRIG) — hoehere Prioritaet UND
    frueherer Zeitpunkt gewinnt, nie umgekehrt.
  - JEDER Aufrufer wartet hoechstens max_wartezeit Sekunden, dann gibt er sauber
    auf (LLMSlotTimeout) statt endlos zu blockieren.
  - Koordination ueber eine Postgres-Tabelle (llm_warteschlange) + einen kurzen
    Advisory-Lock nur fuer den atomaren "bin ich dran"-Check — der eigentliche
    LLM-Aufruf laeuft danach ganz ohne DB-Verbindung.
  - Selbstheilend: eine Zeile zaehlt nur "aktiv" solange slot_bis in der Zukunft
    liegt. Stirbt ein Prozess mit gehaltenem Slot, faellt er automatisch frei.

Verwendung (ersetzt fcntl.flock(slot_0.lock, LOCK_EX)):

    import llm_scheduler as sched
    with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_HOCH,
                        rufer="codewesen_takt:ready_check", max_wartezeit=90,
                        max_haltezeit=90):
        antwort = hauhau_client.chat(...)
"""

import os
import time
import zlib

import psycopg2
import psycopg2.extras

def _load_db_uri() -> str:
    env = os.environ.get("FLEXTRAWURST_DB_URI")
    if env:
        return env

    env_path = "/root/werkraum/.agent/flextrawurst-db.env"
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("FLEXTRAWURST_DB_URI="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass

    raise RuntimeError(f"FLEXTRAWURST_DB_URI fehlt und {env_path} ist nicht lesbar")


DB_URI = _load_db_uri()

PRIO_HOCH, PRIO_NORMAL, PRIO_NIEDRIG = 0, 1, 2

N_SLOTS = {"hintergrund": 1, "chat": 1}

POLL_INTERVALL_SEK = 1.0
STALE_WARTER_SEK = 180


class LLMSlotTimeout(Exception):
    """Wird ausgeloest wenn max_wartezeit ueberschritten wurde, ohne einen Slot
    zu bekommen. Aufrufer sollen das abfangen und die Iteration ueberspringen —
    genau wie vorher bei OllamaSlotTimeout."""


def _conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=5)


def _advisory_key(server: str) -> int:
    # Stabiler kleiner Hash fuer pg_advisory_lock — Pythons eingebautes hash()
    # ist pro Prozess randomisiert und taugt hier nicht als gemeinsamer Lock-Key.
    return zlib.crc32(f"llm_warteschlange:{server}".encode("utf-8")) & 0x7fffffff


def _cleanup_stale_waiters(cur, server: str):
    cur.execute(
        """
        DELETE FROM llm_warteschlange
        WHERE server = %s
          AND slot_bis IS NULL
          AND angefragt_um < NOW() - (%s || ' seconds')::interval
        """,
        (server, STALE_WARTER_SEK),
    )


class LLMSlot:
    """Context-Manager: reiht sich in die Prioritaets-Warteschlange fuer `server`
    ein, wartet hoechstens `max_wartezeit` Sekunden auf einen freien Slot, haelt
    ihn danach hoechstens `max_haltezeit` Sekunden (Sicherheitsnetz falls der
    LLM-Aufruf selbst haengt und __exit__ nie erreicht wird)."""

    def __init__(self, server: str = "hintergrund", prioritaet: int = PRIO_NORMAL,
                 rufer: str = "unbekannt", max_wartezeit: float = 90.0,
                 max_haltezeit: float = 300.0):
        self.server = server
        self.prioritaet = prioritaet
        self.rufer = rufer
        self.max_wartezeit = max_wartezeit
        self.max_haltezeit = max_haltezeit
        self._id = None
        self._conn = None

    def __enter__(self):
        self._conn = _conn()
        self._conn.autocommit = True
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO llm_warteschlange (server, prioritaet, rufer) "
                "VALUES (%s, %s, %s) RETURNING id, angefragt_um",
                (self.server, self.prioritaet, self.rufer),
            )
            row = cur.fetchone()
            self._id = row["id"]
            start = row["angefragt_um"]

        n_slots = N_SLOTS.get(self.server, 2)
        key = _advisory_key(self.server)
        while True:
            with self._conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_lock(%s)", (key,))
                try:
                    _cleanup_stale_waiters(cur, self.server)
                    cur.execute(
                        """
                        UPDATE llm_warteschlange
                        SET slot_bis = NOW() + (%s || ' seconds')::interval
                        WHERE id = %s
                          AND slot_bis IS NULL
                          AND (
                              SELECT COUNT(*) FROM llm_warteschlange w2
                              WHERE w2.server = %s AND w2.slot_bis IS NOT NULL AND w2.slot_bis > NOW()
                          ) < %s
                          AND NOT EXISTS (
                              SELECT 1 FROM llm_warteschlange w3
                              WHERE w3.server = %s AND w3.slot_bis IS NULL
                                AND (w3.prioritaet, w3.angefragt_um) < (
                                    SELECT prioritaet, angefragt_um FROM llm_warteschlange WHERE id = %s
                                )
                          )
                        RETURNING id
                        """,
                        (self.max_haltezeit, self._id, self.server, n_slots, self.server, self._id),
                    )
                    gewonnen = cur.fetchone() is not None
                finally:
                    cur.execute("SELECT pg_advisory_unlock(%s)", (key,))

            if gewonnen:
                return self

            with self._conn.cursor() as cur:
                cur.execute("SELECT NOW() - %s AS gewartet", (start,))
                gewartet = cur.fetchone()["gewartet"].total_seconds()
            if gewartet > self.max_wartezeit:
                self._aufraeumen()
                raise LLMSlotTimeout(
                    f"LLM-Slot '{self.server}' blockiert nach {gewartet:.0f}s — {self.rufer} uebersprungen"
                )
            time.sleep(POLL_INTERVALL_SEK)

    def _aufraeumen(self):
        try:
            with self._conn.cursor() as cur:
                cur.execute("DELETE FROM llm_warteschlange WHERE id = %s", (self._id,))
        finally:
            self._conn.close()
            self._conn = None

    def __exit__(self, *_):
        self._aufraeumen()
        return False
