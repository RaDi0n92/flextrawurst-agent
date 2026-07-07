#!/usr/bin/env python3
"""
wesen_eigene_dienste.py — Lese-/Schreib-Helfer fuer die Tabelle wesen_eigene_dienste
(Postgres, DB=flextrawurst). Anders als dienst_konfiguration.py (Override eines
bestehenden Dienstes) verwaltet dieses Modul komplett NEUE, von Daniel erfundene
Wesen-Rhythmen -- jede Zeile wird von wesen_dienst_generator.py zu einem echten
eigenstaendigen Skript + systemd-Unit.

lade_alle()/lade_fuer_wesen() geben bei DB-Fehler eine leere Liste zurueck.
"""

import os

import psycopg2
import psycopg2.extras

DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:dakpass@localhost:5432/flextrawurst",
)

_FELDER = (
    "id, dienst_name, wesen, anzeige_name, takt_sekunden, start_offset_sekunden, "
    "verhalten_prompt, ziel_typ, ziel_discussion_id, ziel_tag_ids, status, "
    "script_pfad, unit_name, meta, created_at, updated_at"
)


def _verbinden():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor, connect_timeout=5)


def lade(dienst_name: str) -> dict:
    try:
        conn = _verbinden()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {_FELDER} FROM wesen_eigene_dienste WHERE dienst_name = %s", (dienst_name,))
                row = cur.fetchone()
                return dict(row) if row else {}
        finally:
            conn.close()
    except Exception:
        return {}


def lade_alle(nur_aktive: bool = False) -> list:
    try:
        conn = _verbinden()
        try:
            with conn.cursor() as cur:
                sql = f"SELECT {_FELDER} FROM wesen_eigene_dienste"
                if nur_aktive:
                    sql += " WHERE status = 'aktiv'"
                sql += " ORDER BY wesen, created_at"
                cur.execute(sql)
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()
    except Exception:
        return []


def lade_fuer_wesen(wesen: str, nur_aktive: bool = True) -> list:
    try:
        conn = _verbinden()
        try:
            with conn.cursor() as cur:
                sql = f"SELECT {_FELDER} FROM wesen_eigene_dienste WHERE wesen = %s"
                params = [wesen]
                if nur_aktive:
                    sql += " AND status = 'aktiv'"
                sql += " ORDER BY created_at"
                cur.execute(sql, params)
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()
    except Exception:
        return []


def anlegen(
    dienst_name: str,
    wesen: str,
    anzeige_name: str,
    takt_sekunden: int,
    verhalten_prompt: str,
    ziel_typ: str = "neue_diskussion",
    ziel_discussion_id: int = None,
    ziel_tag_ids: list = None,
    start_offset_sekunden: int = 0,
    meta: dict = None,
) -> dict:
    """Legt eine neue Wesen-Dienst-Definition an (INSERT, kein Upsert -- dienst_name
    ist eindeutig und wird vom Aufrufer/Generator einmalig vergeben)."""
    conn = _verbinden()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO wesen_eigene_dienste
                    (dienst_name, wesen, anzeige_name, takt_sekunden, start_offset_sekunden,
                     verhalten_prompt, ziel_typ, ziel_discussion_id, ziel_tag_ids, meta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING {felder}
                """.format(felder=_FELDER),
                (
                    dienst_name, wesen, anzeige_name, takt_sekunden, start_offset_sekunden,
                    verhalten_prompt, ziel_typ, ziel_discussion_id, ziel_tag_ids,
                    psycopg2.extras.Json(meta or {}),
                ),
            )
            conn.commit()
            return dict(cur.fetchone())
    finally:
        conn.close()


def setze_skript_und_unit(dienst_name: str, script_pfad: str, unit_name: str) -> None:
    conn = _verbinden()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE wesen_eigene_dienste SET script_pfad = %s, unit_name = %s, updated_at = NOW() "
                "WHERE dienst_name = %s",
                (script_pfad, unit_name, dienst_name),
            )
            conn.commit()
    finally:
        conn.close()


def setze_status(dienst_name: str, status: str) -> None:
    """status in ('aktiv', 'deaktiviert') -- Grundgesetz 4: nie hart loeschen, nur deaktivieren."""
    if status not in ("aktiv", "deaktiviert"):
        raise ValueError(f"Ungueltiger Status: {status}")
    conn = _verbinden()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE wesen_eigene_dienste SET status = %s, updated_at = NOW() WHERE dienst_name = %s",
                (status, dienst_name),
            )
            conn.commit()
    finally:
        conn.close()
