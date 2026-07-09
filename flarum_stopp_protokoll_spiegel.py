#!/usr/bin/env python3
"""
flarum_stopp_protokoll_spiegel.py — Postgres-Spiegel über die Protokolldateien
von flarum_stopp_protokoll.py (docs/2026-07-09_flarum_stopp_bericht.md,
Baustein 5).

Grundgesetz 1 (flextrawurst): meta JSONB, immer erweiterbar.
Grundgesetz 2: durchsuchbar/filterbar/paginierbar (GIN-Index auf meta + Volltext).
Grundgesetz 4: Events sind heilig — append-only, kein UPDATE, kein DELETE.

Die JSONL-Dateien bleiben die Wahrheit (menschenlesbar, funktioniert auch ohne
DB). Dieser Spiegel macht sie für flarumstyler live/interaktiv abfragbar, ohne
Dateien parsen zu müssen. Jeder Eintrag hat eine feste UUID (vergeben von
flarum_stopp_protokoll.schreibe()) — das macht das Spiegeln idempotent, kein
separater Sync-Cursor nötig: ON CONFLICT (id) DO NOTHING.
"""

import json
import logging
import os
from typing import Optional

import psycopg2
import psycopg2.extras

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:dakpass@localhost:5432/flextrawurst",
)

log = logging.getLogger("flarum-stopp-protokoll-spiegel")

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS flarum_stopp_protokoll (
    id UUID PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    typ TEXT NOT NULL,
    wesen TEXT,
    text TEXT NOT NULL,
    dauer_sekunden REAL,
    meta JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_fsp_ts ON flarum_stopp_protokoll (ts DESC);
CREATE INDEX IF NOT EXISTS idx_fsp_wesen ON flarum_stopp_protokoll (wesen);
CREATE INDEX IF NOT EXISTS idx_fsp_typ ON flarum_stopp_protokoll (typ);
CREATE INDEX IF NOT EXISTS idx_fsp_meta ON flarum_stopp_protokoll USING GIN (meta);
CREATE INDEX IF NOT EXISTS idx_fsp_text_fts ON flarum_stopp_protokoll
    USING GIN (to_tsvector('german', text));
"""

_UPSERT_SQL = """
INSERT INTO flarum_stopp_protokoll (id, ts, typ, wesen, text, dauer_sekunden, meta)
VALUES (%(id)s, %(ts)s, %(typ)s, %(wesen)s, %(text)s, %(dauer_sekunden)s, %(meta)s)
ON CONFLICT (id) DO NOTHING;
"""


def _verbindung():
    return psycopg2.connect(DB_URI, connect_timeout=3)


def stelle_schema_sicher() -> bool:
    try:
        conn = _verbindung()
        try:
            with conn.cursor() as cur:
                cur.execute(_SCHEMA_SQL)
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        log.warning(f"Schema-Sicherstellung fehlgeschlagen: {e}")
        return False


def spiegle(eintrag: dict) -> bool:
    """Schreibt einen einzelnen Protokolleintrag idempotent in Postgres.
    Fehlschlag (DB nicht erreichbar) wird nur geloggt — die JSONL-Datei bleibt
    in jedem Fall die Wahrheit, kein Aufrufer soll deswegen scheitern."""
    if "id" not in eintrag:
        log.warning("spiegle(): Eintrag ohne 'id' übersprungen (alt/vor-Migration?)")
        return False
    try:
        conn = _verbindung()
        try:
            with conn.cursor() as cur:
                cur.execute(_UPSERT_SQL, {
                    "id": eintrag["id"],
                    "ts": eintrag["ts"],
                    "typ": eintrag["typ"],
                    "wesen": eintrag.get("wesen"),
                    "text": eintrag["text"],
                    "dauer_sekunden": eintrag.get("dauer_sekunden"),
                    "meta": json.dumps(eintrag.get("meta") or {}, ensure_ascii=False),
                })
            conn.commit()
            return True
        finally:
            conn.close()
    except Exception as e:
        log.warning(f"Spiegeln fehlgeschlagen ({eintrag.get('typ')}/{eintrag.get('id')}): {e}")
        return False


def suche(wesen: Optional[str] = None, typ: Optional[str] = None,
          suchtext: Optional[str] = None, limit: int = 100, offset: int = 0) -> list[dict]:
    """Durchsuchbar/filterbar/paginierbar, wie von Grundgesetz 2 verlangt."""
    bedingungen = []
    parameter = {}
    if wesen:
        bedingungen.append("wesen = %(wesen)s")
        parameter["wesen"] = wesen
    if typ:
        bedingungen.append("typ = %(typ)s")
        parameter["typ"] = typ
    if suchtext:
        bedingungen.append("to_tsvector('german', text) @@ plainto_tsquery('german', %(suchtext)s)")
        parameter["suchtext"] = suchtext
    where = f"WHERE {' AND '.join(bedingungen)}" if bedingungen else ""
    parameter["limit"] = limit
    parameter["offset"] = offset

    conn = _verbindung()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"SELECT id, ts, typ, wesen, text, dauer_sekunden, meta "
                f"FROM flarum_stopp_protokoll {where} "
                f"ORDER BY ts DESC LIMIT %(limit)s OFFSET %(offset)s",
                parameter,
            )
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
