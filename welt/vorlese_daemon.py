#!/usr/bin/env python3
"""
Billiges Vorlesen — Phase 1 (2026-07-22, Daniels Auftrag, siehe
_claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md).

Ein Wesen soll nicht nur auf explizite rag_erkunden:-Anfragen reagieren, sondern neue
Inhalte, die auf flextrawurst entstehen, automatisch und GUENSTIG (Embedding-Vergleich,
kein LLM-Call) gegen sein eigenes Interessensprofil pruefen. Nur bei ausreichender
Naehe wird ein echter, teurer LLM-Tick mit diesem Fund gefuettert.

Architektur: hoert auf den bestehenden Events-Stream-Kanal (Grundgesetz 8,
migration_events_stream.sql), genau wie das Frontend per SSE -- nur hier direkt per
psycopg2 LISTEN, kein HTTP-Umweg. Bei einem neuen 'ankuendigung.*'-Event: Inhalt holen,
mit bge-m3 embedden (gleiches Modell/gleiche Dimension wie rag_retrieve.py), gegen
jedes vorhandene entity_interessensprofil per Kosinus-Aehnlichkeit vergleichen. Ueber
der Schwelle: Fund in entity_vorlese_funde ablegen, browser_agent.py liest das beim
naechsten Tick.

Eigener, leichter Prozess statt Teil des Haupt-Tick-Loops -- die Wesen sollen guenstig
UND gleichzeitig scannen koennen, nicht sequenziell im geteilten LLM-Slot-Takt.

Phase 1 bewusst eng: nur EINE Quelle (Ankuendigungen). Erweiterung auf Surface-Inhalte,
Menschenprofile, Traumanalysen, Notizen, Gedankenblasenfeld, KompOase folgt schrittweise
nach Verifikation (Skalpell-Prinzip, siehe Ideen-Datei).

AEHNLICHKEITS-SCHWELLE: 0.55, NICHT empirisch kalibriert (anders als z.B. die
Memory-Dedupe-Schwelle vom 2026-07-09, die gegen echte Beispiele kalibriert wurde) --
es gibt noch keine Beispieldaten fuer "Charakterbeschreibung vs. Ankuendigungsinhalt".
Muss nach echten Beobachtungen nachjustiert werden.
"""

import json
import logging
import os
import select as sel
import signal
import time

import psycopg2
import psycopg2.extras
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("vorlese-daemon")

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODELL = "bge-m3"
AEHNLICHKEITS_SCHWELLE = 0.55  # siehe Modul-Docstring -- nicht kalibriert

_laufend = True


def _signal_handler(sig, frame):
    global _laufend
    log.info("Signal %s — beende sauber...", sig)
    _laufend = False


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def embed(text: str) -> list[float]:
    resp = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODELL, "input": text}, timeout=60)
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def seede_charakterprofil_falls_fehlend(conn, entity_id: str, wesen_md_pfad: str):
    """Startpunkt des Interessensprofils: die Charakterbeschreibung (wesen.md).
    Die anderen beiden Zutaten (RAG-Anfrage-Historie, tatsaechliche Reaktionen) gibt
    es bei einem frischen Profil noch nicht -- sie fliessen organisch dazu, sobald
    Historie existiert (Phase 2, hier noch nicht umgesetzt)."""
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM entity_interessensprofil WHERE entity_id = %s", (entity_id,))
        if cur.fetchone():
            return
    if not os.path.exists(wesen_md_pfad):
        log.warning("%s: wesen.md nicht gefunden unter %s, kein Profil-Seed", entity_id, wesen_md_pfad)
        return
    with open(wesen_md_pfad, encoding="utf-8") as f:
        charakter_text = f.read()
    vektor = embed(charakter_text)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO entity_interessensprofil (entity_id, profil_vektor, quellen)
            VALUES (%s, %s, %s)
            ON CONFLICT (entity_id) DO NOTHING
        """, (entity_id, str(vektor), psycopg2.extras.Json({
            "charakter": {"quelle": wesen_md_pfad, "aktualisiert_am": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
            "rag_anfragen": [],
            "reaktionen": [],
        })))
    conn.commit()
    log.info("%s: Interessensprofil aus %s geseedet", entity_id, wesen_md_pfad)


def hole_ankuendigung(conn, ankuendigung_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute("SELECT id, titel, inhalt FROM ankuendigungen WHERE id = %s::uuid", (ankuendigung_id,))
        return cur.fetchone()


def pruefe_gegen_profile(conn, quelle: str, quelle_ref: str, titel: str, inhalt: str):
    """Embedded den neuen Inhalt einmal, vergleicht ihn gegen alle vorhandenen
    Interessensprofile (SQL macht die Kosinus-Rechnung, kein Python-seitiges Neuladen
    der Vektoren noetig), legt Treffer ueber der Schwelle in entity_vorlese_funde ab."""
    vektor = embed(f"{titel}\n\n{inhalt}")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT entity_id, 1 - (profil_vektor <=> %(vektor)s) AS aehnlichkeit
            FROM entity_interessensprofil
            WHERE 1 - (profil_vektor <=> %(vektor)s) >= %(schwelle)s
        """, {"vektor": str(vektor), "schwelle": AEHNLICHKEITS_SCHWELLE})
        treffer = cur.fetchall()
        for t in treffer:
            cur.execute("""
                INSERT INTO entity_vorlese_funde (entity_id, quelle, quelle_ref, titel, aehnlichkeit)
                VALUES (%s, %s, %s, %s, %s)
            """, (t["entity_id"], quelle, quelle_ref, titel, t["aehnlichkeit"]))
            log.info("%s: Fund '%s' (Aehnlichkeit %.3f) -> entity_vorlese_funde", t["entity_id"], titel, t["aehnlichkeit"])
    conn.commit()


def haupt_loop():
    log.info("Vorlese-Daemon startet (Phase 1: Quelle=Ankuendigungen)")

    conn = get_conn()

    def hole_conn():
        nonlocal conn
        if conn.closed:
            log.warning("DB-Verbindung geschlossen — baue neu auf")
            conn = get_conn()
        return conn

    # Phase 1: nur Schorschel, wie mit Daniel abgestimmt
    seede_charakterprofil_falls_fehlend(
        hole_conn(), "Schorschel", "/root/werkraum/codewesen/Schorschel/wesen.md"
    )

    listen_conn = psycopg2.connect(DB_URI)
    listen_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    listen_cur = listen_conn.cursor()
    listen_cur.execute("LISTEN events_stream")

    while _laufend:
        readable, _, _ = sel.select([listen_conn], [], [], 1.0)
        if not readable:
            continue
        listen_conn.poll()
        while listen_conn.notifies:
            notify = listen_conn.notifies.pop(0)
            try:
                meta = json.loads(notify.payload)
            except Exception:
                continue
            event_type = meta.get("event_type", "")
            if not event_type.startswith("ankuendigung."):
                continue
            ankuendigung_id = meta.get("ankuendigung_id")
            if not ankuendigung_id:
                continue
            try:
                conn = hole_conn()
                ank = hole_ankuendigung(conn, ankuendigung_id)
                if not ank:
                    continue
                pruefe_gegen_profile(conn, "ankuendigung", ankuendigung_id, ank["titel"], ank["inhalt"])
            except Exception as e:
                log.warning("Verarbeitung von %s fehlgeschlagen: %s", ankuendigung_id, e)
                try:
                    hole_conn().rollback()
                except Exception:
                    pass

    log.info("Vorlese-Daemon beendet")
    listen_cur.close()
    listen_conn.close()
    conn.close()


if __name__ == "__main__":
    haupt_loop()
