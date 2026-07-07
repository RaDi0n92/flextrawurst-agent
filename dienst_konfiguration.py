#!/usr/bin/env python3
"""
dienst_konfiguration.py — gemeinsamer Lese-/Schreib-Helfer fuer die Tabelle
dienst_konfiguration (Postgres, DB=flextrawurst). Ermoeglicht Daemons, ihren
Takt/Intervall und einen Verhaltenstext (der direkt in den System-Prompt
einfliesst) aus der DB statt aus hartcodierten Konstanten zu lesen — editierbar
ueber flarumstyler.

lade() gibt bei jedem Fehler (DB nicht erreichbar, kein Eintrag) ein leeres
Dict zurueck — Aufrufer behalten dann einfach ihre eigenen Default-Werte.
"""

import os

import psycopg2
import psycopg2.extras

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:dakpass@localhost:5432/flextrawurst",
)


def lade(dienst_name: str) -> dict:
    try:
        conn = psycopg2.connect(
            DB_URI, cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=3
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT takt_sekunden, verhalten_text, beschreibung_override, meta "
                    "FROM dienst_konfiguration WHERE dienst_name = %s",
                    (dienst_name,),
                )
                row = cur.fetchone()
                return dict(row) if row else {}
        finally:
            conn.close()
    except Exception:
        return {}


def speichere(dienst_name: str, takt_sekunden=None, verhalten_text=None, meta=None, beschreibung_override=None) -> dict:
    """Upsert. takt_sekunden/verhalten_text/beschreibung_override werden 1:1 uebernommen —
    None bedeutet hier bewusst 'kein Override, Standard gilt' (so kann ein Feld im
    UI-Formular geleert werden, um zum Standard zurueckzukehren). meta hat noch kein
    eigenes UI-Feld, bleibt deshalb erhalten wenn hier nicht explizit etwas uebergeben wird."""
    if meta is None:
        bestehend = lade(dienst_name)
        meta = bestehend.get("meta") or {}

    conn = psycopg2.connect(
        DB_URI, cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=5
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dienst_konfiguration (dienst_name, takt_sekunden, verhalten_text, beschreibung_override, meta)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (dienst_name) DO UPDATE SET
                    takt_sekunden  = EXCLUDED.takt_sekunden,
                    verhalten_text = EXCLUDED.verhalten_text,
                    beschreibung_override = EXCLUDED.beschreibung_override,
                    meta           = EXCLUDED.meta,
                    updated_at     = NOW()
                RETURNING dienst_name, takt_sekunden, verhalten_text, beschreibung_override, meta, updated_at
                """,
                (dienst_name, takt_sekunden, verhalten_text, beschreibung_override, psycopg2.extras.Json(meta)),
            )
            conn.commit()
            return dict(cur.fetchone())
    finally:
        conn.close()


def alle() -> dict:
    """Laedt die Konfiguration ALLER Dienste auf einmal — fuer den Watchdog,
    der sie pro Lauf einmal einliest statt pro Dienst einzeln zu verbinden."""
    try:
        conn = psycopg2.connect(
            DB_URI, cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=3
        )
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT dienst_name, takt_sekunden, verhalten_text, beschreibung_override, meta, updated_at "
                    "FROM dienst_konfiguration"
                )
                return {r["dienst_name"]: dict(r) for r in cur.fetchall()}
        finally:
            conn.close()
    except Exception:
        return {}
