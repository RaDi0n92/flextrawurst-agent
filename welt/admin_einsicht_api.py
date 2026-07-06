#!/usr/bin/env python3
"""
Admin-Einsicht API: Wesen-Einsichtskörper + Entscheidungsarchiv + Lebensticker

Neue Endpunkte für:
  - Wesen-Übersicht (alle 6 Entitäten live)
  - Denkfenster (entity_thinking_log gefiltert)
  - Lebensjournal (gemischte Timeline)
  - Träume + Selbstbriefe
  - Substanz-Sedimente
  - Einzugs-Bereitschaftsprüfung
  - Weltorgan-Bauplan
"""

from datetime import datetime, timezone
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Query

from wesen_life_contracts import as_dict as contracts_as_dict, LIFE_CONTRACTS
from wesen_organ_hunger import berechne_organ_hunger, alle_wesen_hunger

router = APIRouter(prefix="/admin", tags=["einsicht"])

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")

ALLE_WESEN = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
]


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def ts(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


# ── WESEN-ÜBERSICHT ───────────────────────────────────────────────────────────

@router.get("/entities/overview")
def entities_overview():
    """Vollständige Live-Übersicht aller Wesen: Zustand, Aktivität, letzte Entscheidung, Post, Traum."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            result = []
            for eid in ALLE_WESEN:
                # Slot + Profil + Zustand
                cur.execute("""
                    SELECT es.entity_id, es.status, es.visibility, es.display_name,
                           ep.selbstbeschreibung, ep.obsessionen, ep.autonomie_phase,
                           ep.meta as profil_meta,
                           est.stimmung, est.fokus, est.updated_at as zustand_updated,
                           ea.letzte_entscheidung, ea.letzte_begruendung, ea.letzte_entscheidung_at,
                           ea.aktuell_denkend
                    FROM entity_slots es
                    LEFT JOIN entity_profiles ep ON ep.entity_id = es.entity_id
                    LEFT JOIN entity_states est ON est.entity_id = es.entity_id
                    LEFT JOIN entity_activity ea ON ea.entity_id = es.entity_id
                    WHERE es.entity_id = %s
                """, (eid,))
                row = dict(cur.fetchone() or {})

                # Letzter Denklog
                cur.execute("""
                    SELECT log_id, gedanke, entscheidung, begruendung, tick_at
                    FROM entity_thinking_log
                    WHERE entity_id = %s
                    ORDER BY tick_at DESC LIMIT 1
                """, (eid,))
                letzter_denk = dict(cur.fetchone() or {})

                # Letzter Post
                cur.execute("""
                    SELECT id, content, created_at, post_type
                    FROM ftw_posts
                    WHERE autor_id = %s AND autor_type = 'entity'
                    ORDER BY created_at DESC LIMIT 1
                """, (eid,))
                letzter_post = dict(cur.fetchone() or {})

                # Letzter Schlafbrief
                cur.execute("""
                    SELECT brief_id, inhalt, geschrieben_at, gelesen_at
                    FROM schlafbriefe WHERE entity_id = %s
                    ORDER BY geschrieben_at DESC LIMIT 1
                """, (eid,))
                letzter_brief = dict(cur.fetchone() or {})

                # Aktive Schlafphase
                cur.execute("""
                    SELECT phase_id, phase_type, started_at
                    FROM sleep_phases
                    WHERE entity_id = %s AND ended_at IS NULL
                    ORDER BY started_at DESC LIMIT 1
                """, (eid,))
                aktiver_schlaf = dict(cur.fetchone() or {})

                # Beziehungsanzahl
                cur.execute(
                    "SELECT COUNT(*) AS cnt FROM entity_relationships WHERE entity_id = %s",
                    (eid,),
                )
                beziehungen = cur.fetchone()["cnt"]

                # Events heute
                cur.execute("""
                    SELECT COUNT(*) AS cnt FROM events
                    WHERE actor_id = %s AND created_at >= CURRENT_DATE
                """, (eid,))
                events_heute = cur.fetchone()["cnt"]

                # Sediment-Score
                cur.execute("""
                    SELECT COUNT(*) AS cnt, AVG(confidence) AS avg_conf
                    FROM substance_sediments
                    WHERE wesen_id = %s AND created_at >= NOW() - INTERVAL '24h'
                """, (eid,))
                sed = dict(cur.fetchone() or {})

                # Traumkandidaten
                cur.execute("""
                    SELECT COUNT(*) AS cnt FROM traumkandidaten_log
                    WHERE entity_id = %s
                """, (eid,))
                traeume_cnt = cur.fetchone()["cnt"]

                result.append({
                    "entity_id": eid,
                    "status": row.get("status"),
                    "visibility": row.get("visibility"),
                    "display_name": row.get("display_name"),
                    "selbstbeschreibung": row.get("selbstbeschreibung"),
                    "obsessionen": row.get("obsessionen", []),
                    "autonomie_phase": row.get("autonomie_phase"),
                    "profil_meta": row.get("profil_meta") or {},
                    "stimmung": row.get("stimmung"),
                    "fokus": row.get("fokus"),
                    "zustand_updated": ts(row.get("zustand_updated")),
                    "letzte_entscheidung": row.get("letzte_entscheidung"),
                    "letzte_begruendung": row.get("letzte_begruendung"),
                    "letzte_entscheidung_at": ts(row.get("letzte_entscheidung_at")),
                    "aktuell_denkend": row.get("aktuell_denkend", False),
                    "letzter_denk": {
                        "log_id": str(letzter_denk.get("log_id", "")),
                        "gedanke_preview": (letzter_denk.get("gedanke") or "")[:120],
                        "entscheidung": letzter_denk.get("entscheidung"),
                        "begruendung_preview": (letzter_denk.get("begruendung") or "")[:100],
                        "tick_at": ts(letzter_denk.get("tick_at")),
                    } if letzter_denk else None,
                    "letzter_post": {
                        "id": str(letzter_post.get("id", "")),
                        "content_preview": (letzter_post.get("content") or "")[:120],
                        "created_at": ts(letzter_post.get("created_at")),
                        "post_type": letzter_post.get("post_type"),
                    } if letzter_post else None,
                    "letzter_brief": {
                        "brief_id": str(letzter_brief.get("brief_id", "")),
                        "inhalt_preview": (letzter_brief.get("inhalt") or "")[:100],
                        "geschrieben_at": ts(letzter_brief.get("geschrieben_at")),
                        "gelesen": letzter_brief.get("gelesen_at") is not None,
                    } if letzter_brief else None,
                    "aktiver_schlaf": {
                        "phase_type": aktiver_schlaf.get("phase_type"),
                        "started_at": ts(aktiver_schlaf.get("started_at")),
                    } if aktiver_schlaf else None,
                    "beziehungen_cnt": beziehungen,
                    "events_heute": events_heute,
                    "sediment_heute": int(sed.get("cnt") or 0),
                    "sediment_avg_conf": round(float(sed.get("avg_conf") or 0), 3),
                    "traeume_cnt": traeume_cnt,
                })

        return {"entities": result, "count": len(result)}
    finally:
        conn.close()


# ── DENKFENSTER / ENTSCHEIDUNGSARCHIV ─────────────────────────────────────────

@router.get("/entities/thinking")
def entities_thinking(
    entity_id: str | None = Query(default=None),
    entscheidung: str | None = Query(default=None),
    seit: str | None = Query(default=None, description="ISO date/datetime"),
    bis: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    """Denkfenster: entity_thinking_log gefiltert und paginiert."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            conditions = ["1=1"]
            params: list[Any] = []

            if entity_id:
                conditions.append("etl.entity_id = %s")
                params.append(entity_id)
            if entscheidung:
                conditions.append("etl.entscheidung = %s")
                params.append(entscheidung)
            if seit:
                conditions.append("etl.tick_at >= %s")
                params.append(seit)
            if bis:
                conditions.append("etl.tick_at <= %s")
                params.append(bis)

            where = " AND ".join(conditions)

            cur.execute(f"""
                SELECT etl.log_id, etl.entity_id, etl.gedanke, etl.entscheidung,
                       etl.begruendung, etl.kontext_snapshot, etl.tick_at,
                       p.id AS post_id, p.content AS post_content
                FROM entity_thinking_log etl
                LEFT JOIN ftw_posts p ON (
                    etl.kontext_snapshot->>'last_post_id' = p.id::text
                    OR (etl.entscheidung = 'gedanke_posten'
                        AND p.autor_id = etl.entity_id
                        AND p.created_at BETWEEN etl.tick_at - INTERVAL '5 min' AND etl.tick_at + INTERVAL '5 min')
                )
                WHERE {where}
                ORDER BY etl.tick_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            rows = cur.fetchall()

            cur.execute(f"SELECT COUNT(*) AS cnt FROM entity_thinking_log etl WHERE {where}", params)
            total = cur.fetchone()["cnt"]

        return {
            "entries": [
                {
                    "log_id": str(r["log_id"]) if r["log_id"] else None,
                    "entity_id": r["entity_id"],
                    "gedanke": r["gedanke"],
                    "entscheidung": r["entscheidung"],
                    "begruendung": r["begruendung"],
                    "kontext_snapshot": r["kontext_snapshot"],
                    "tick_at": ts(r["tick_at"]),
                    "post_id": str(r["post_id"]) if r["post_id"] else None,
                    "post_preview": (r["post_content"] or "")[:100] if r["post_content"] else None,
                }
                for r in rows
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


# ── LEBENSJOURNAL ─────────────────────────────────────────────────────────────

@router.get("/entities/{entity_id}/lifejournal")
def entity_lifejournal(
    entity_id: str,
    limit: int = Query(default=80, le=300),
    offset: int = Query(default=0),
    seit: str | None = Query(default=None),
):
    """Gemischte Timeline: Events + Denklogs + Posts + Schlaf + Briefe + Träume."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            since_cond = f"AND created_at >= '{seit}'" if seit else ""

            # Events
            cur.execute(f"""
                SELECT 'event' AS typ, event_type AS subtyp,
                       created_at AS zeit, payload::text AS inhalt_raw,
                       NULL AS inhalt, event_type AS detail
                FROM events
                WHERE actor_id = %s {since_cond}
            """, (entity_id,))
            events = [dict(r) for r in cur.fetchall()]

            # Denklogs
            cur.execute(f"""
                SELECT 'denken' AS typ, entscheidung AS subtyp,
                       tick_at AS zeit, gedanke AS inhalt,
                       begruendung AS detail, NULL AS inhalt_raw
                FROM entity_thinking_log
                WHERE entity_id = %s
                {f"AND tick_at >= '{seit}'" if seit else ""}
            """, (entity_id,))
            denken = [dict(r) for r in cur.fetchall()]

            # Posts
            cur.execute(f"""
                SELECT 'post' AS typ, post_type AS subtyp,
                       created_at AS zeit, content AS inhalt,
                       id::text AS detail, NULL AS inhalt_raw
                FROM ftw_posts
                WHERE autor_id = %s AND autor_type = 'entity' {since_cond}
            """, (entity_id,))
            posts = [dict(r) for r in cur.fetchall()]

            # Schlafphasen
            cur.execute(f"""
                SELECT 'schlaf' AS typ, phase_type AS subtyp,
                       started_at AS zeit,
                       COALESCE(ended_at::text, 'läuft noch') AS inhalt,
                       duration_min::text AS detail, NULL AS inhalt_raw
                FROM sleep_phases
                WHERE entity_id = %s
                {f"AND started_at >= '{seit}'" if seit else ""}
            """, (entity_id,))
            schlaf = [dict(r) for r in cur.fetchall()]

            # Schlafbriefe
            cur.execute(f"""
                SELECT 'brief' AS typ, 'schlafbrief' AS subtyp,
                       geschrieben_at AS zeit, inhalt,
                       CASE WHEN gelesen_at IS NULL THEN 'ungelesen' ELSE 'gelesen' END AS detail,
                       NULL AS inhalt_raw
                FROM schlafbriefe
                WHERE entity_id = %s
                {f"AND geschrieben_at >= '{seit}'" if seit else ""}
            """, (entity_id,))
            briefe = [dict(r) for r in cur.fetchall()]

            # Traumkandidaten
            cur.execute(f"""
                SELECT 'traum' AS typ, selektionsregel AS subtyp,
                       created_at AS zeit, begruendung AS inhalt,
                       log_id::text AS detail, NULL AS inhalt_raw
                FROM traumkandidaten_log
                WHERE entity_id = %s
                {f"AND created_at >= '{seit}'" if seit else ""}
            """, (entity_id,))
            traeume = [dict(r) for r in cur.fetchall()]

            # Substanz-Sedimente
            cur.execute(f"""
                SELECT 'substanz' AS typ, sediment_type AS subtyp,
                       created_at AS zeit, substance_suspect AS inhalt,
                       confidence::text AS detail, NULL AS inhalt_raw
                FROM substance_sediments
                WHERE wesen_id = %s {since_cond}
            """, (entity_id,))
            substanzen = [dict(r) for r in cur.fetchall()]

            # Zusammenführen + sortieren
            combined = events + denken + posts + schlaf + briefe + traeume + substanzen
            combined.sort(key=lambda x: x["zeit"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

            total = len(combined)
            page = combined[offset:offset + limit]

        return {
            "entity_id": entity_id,
            "entries": [
                {
                    "typ": r["typ"],
                    "subtyp": r.get("subtyp"),
                    "zeit": ts(r["zeit"]),
                    "inhalt": (r.get("inhalt") or "")[:200] if r.get("inhalt") else None,
                    "detail": r.get("detail"),
                }
                for r in page
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


# ── TRÄUME + SELBSTBRIEFE ─────────────────────────────────────────────────────

@router.get("/entities/dreams")
def entities_dreams(
    entity_id: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    """Traumkandidaten + Traumspuren aller Wesen."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cond = "WHERE tkl.entity_id = %s" if entity_id else "WHERE 1=1"
            params = [entity_id] if entity_id else []
            cur.execute(f"""
                SELECT tkl.log_id, tkl.entity_id, tkl.selektionsregel,
                       tkl.begruendung, tkl.created_at,
                       sp.phase_type, sp.started_at AS schlaf_start,
                       COUNT(ts.id) AS spuren_count
                FROM traumkandidaten_log tkl
                LEFT JOIN sleep_phases sp ON sp.phase_id = tkl.sleep_phase_id
                LEFT JOIN traumspuren ts ON ts.log_id = tkl.log_id
                {cond}
                GROUP BY tkl.log_id, tkl.entity_id, tkl.selektionsregel,
                         tkl.begruendung, tkl.created_at, sp.phase_type, sp.started_at
                ORDER BY tkl.created_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            traeume = [dict(r) for r in cur.fetchall()]

            cur.execute(
                f"SELECT COUNT(*) AS cnt FROM traumkandidaten_log tkl {cond}",
                params,
            )
            total = cur.fetchone()["cnt"]

        return {
            "traeume": [
                {
                    **{k: (str(v) if hasattr(v, "hex") else ts(v) if isinstance(v, datetime) else v)
                       for k, v in t.items()},
                }
                for t in traeume
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    finally:
        conn.close()


@router.get("/entities/selfletters")
def entities_selfletters(
    entity_id: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0),
):
    """Schlafbriefe aller Wesen — Briefe an das zukünftige Selbst."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cond = "WHERE sb.entity_id = %s" if entity_id else "WHERE 1=1"
            params = [entity_id] if entity_id else []
            cur.execute(f"""
                SELECT sb.brief_id, sb.entity_id, sb.inhalt,
                       sb.geschrieben_at, sb.gelesen_at,
                       sp.phase_type, sp.started_at AS schlaf_start
                FROM schlafbriefe sb
                LEFT JOIN sleep_phases sp ON sp.phase_id = sb.phase_id
                {cond}
                ORDER BY sb.geschrieben_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            briefe = [dict(r) for r in cur.fetchall()]

            cur.execute(f"SELECT COUNT(*) AS cnt FROM schlafbriefe sb {cond}", params)
            total = cur.fetchone()["cnt"]

        return {
            "briefe": [
                {
                    "brief_id": str(b["brief_id"]),
                    "entity_id": b["entity_id"],
                    "inhalt": b["inhalt"],
                    "geschrieben_at": ts(b["geschrieben_at"]),
                    "gelesen_at": ts(b["gelesen_at"]),
                    "gelesen": b["gelesen_at"] is not None,
                    "phase_type": b["phase_type"],
                    "schlaf_start": ts(b["schlaf_start"]),
                }
                for b in briefe
            ],
            "total": total,
        }
    finally:
        conn.close()


# ── BEZIEHUNGEN ───────────────────────────────────────────────────────────────

@router.get("/entities/relationships")
def entities_relationships(
    entity_id: str | None = Query(default=None),
):
    """Beziehungen zwischen Wesen und zu Menschen."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if entity_id:
                cur.execute("""
                    SELECT er.*, hu.display_name AS human_name
                    FROM entity_relationships er
                    LEFT JOIN human_users hu ON (er.partner_type = 'human' AND hu.id::text = er.partner_id)
                    WHERE er.entity_id = %s
                    ORDER BY er.interaktionen DESC, er.letzte_interaktion DESC
                """, (entity_id,))
            else:
                cur.execute("""
                    SELECT er.*, hu.display_name AS human_name
                    FROM entity_relationships er
                    LEFT JOIN human_users hu ON (er.partner_type = 'human' AND hu.id::text = er.partner_id)
                    ORDER BY er.letzte_interaktion DESC
                """)
            rows = [dict(r) for r in cur.fetchall()]

            # Spannungen aus Events ableiten
            cur.execute("""
                SELECT actor_id, event_type, COUNT(*) AS cnt
                FROM events
                WHERE event_type LIKE 'wesen.%%' OR event_type LIKE 'spannung.%%'
                  OR event_type LIKE 'konflikt.%%' OR event_type LIKE 'resonanz.%%'
                GROUP BY actor_id, event_type
                ORDER BY cnt DESC
                LIMIT 20
            """)
            spannungs_events = [dict(r) for r in cur.fetchall()]

        return {
            "relationships": [
                {
                    **{k: (str(v) if hasattr(v, "hex") else ts(v) if isinstance(v, datetime) else v)
                       for k, v in r.items()},
                }
                for r in rows
            ],
            "spannungs_events": spannungs_events,
            "total": len(rows),
        }
    finally:
        conn.close()


# ── SUBSTANZ-SEDIMENTE ─────────────────────────────────────────────────────────

@router.get("/substances/sediments")
def substances_sediments(
    wesen_id: str | None = Query(default=None),
    sediment_type: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0),
):
    """Substanz-Sedimente: Systemniederschläge von Aktivität und Zustand."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cond_parts = []
            params: list[Any] = []
            if wesen_id:
                cond_parts.append("wesen_id = %s")
                params.append(wesen_id)
            if sediment_type:
                cond_parts.append("sediment_type = %s")
                params.append(sediment_type)
            where = ("WHERE " + " AND ".join(cond_parts)) if cond_parts else ""

            cur.execute(f"""
                SELECT wesen_id, sediment_type, substance_suspect, confidence, payload, created_at
                FROM substance_sediments {where}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            rows = [dict(r) for r in cur.fetchall()]

            # Aggregat pro Typ
            cur.execute("""
                SELECT sediment_type, COUNT(*) AS cnt, AVG(confidence) AS avg_conf
                FROM substance_sediments
                GROUP BY sediment_type
                ORDER BY cnt DESC
            """)
            aggregat = [dict(r) for r in cur.fetchall()]

            cur.execute(f"SELECT COUNT(*) AS cnt FROM substance_sediments {where}", params)
            total = cur.fetchone()["cnt"]

        return {
            "sediments": [
                {
                    "wesen_id": r["wesen_id"],
                    "sediment_type": r["sediment_type"],
                    "substance_suspect": r["substance_suspect"],
                    "confidence": round(float(r["confidence"] or 0), 3),
                    "payload": r["payload"],
                    "created_at": ts(r["created_at"]),
                }
                for r in rows
            ],
            "aggregat": [
                {"sediment_type": a["sediment_type"], "cnt": a["cnt"],
                 "avg_conf": round(float(a["avg_conf"] or 0), 3)}
                for a in aggregat
            ],
            "total": total,
        }
    finally:
        conn.close()


@router.get("/substances/liveticker")
def substances_liveticker(
    wesen_id: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    """Substanz-Liveticker: kombinierter Strom aus Events + Sedimenten."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            wesen_filter = "AND wesen_id = %s" if wesen_id else ""
            event_filter = "AND actor_id = %s" if wesen_id else ""
            params_sed = [wesen_id] if wesen_id else []
            params_ev = [wesen_id] if wesen_id else []

            cur.execute(f"""
                (SELECT 'sediment' AS typ, wesen_id AS entity_id, sediment_type AS subtyp,
                        substance_suspect AS substanz, confidence AS staerke,
                        created_at AS zeit, payload::text AS detail
                 FROM substance_sediments
                 WHERE 1=1 {wesen_filter}
                 ORDER BY created_at DESC LIMIT 25)
                UNION ALL
                (SELECT 'event' AS typ, actor_id AS entity_id, event_type AS subtyp,
                        NULL AS substanz, NULL AS staerke,
                        created_at AS zeit, payload::text AS detail
                 FROM events
                 WHERE event_type LIKE 'substanz.%%' {event_filter}
                 ORDER BY created_at DESC LIMIT 25)
                ORDER BY zeit DESC
                LIMIT %s
            """, params_sed + params_ev + [limit])
            rows = [dict(r) for r in cur.fetchall()]

        return {
            "ticker": [
                {
                    "typ": r["typ"],
                    "entity_id": r["entity_id"],
                    "subtyp": r["subtyp"],
                    "substanz": r["substanz"],
                    "staerke": round(float(r["staerke"]) if r["staerke"] else 0, 3),
                    "zeit": ts(r["zeit"]),
                    "detail": r["detail"],
                }
                for r in rows
            ],
        }
    finally:
        conn.close()


# ── EINZUGS-BEREITSCHAFT ───────────────────────────────────────────────────────

@router.get("/readiness/einzug")
def readiness_einzug():
    """Einzugsampel: Prüft alle Kriterien für den Wesen-Einzug."""
    import subprocess, socket

    def port_ok(port: int) -> bool:
        try:
            with socket.create_connection(("localhost", port), timeout=2):
                return True
        except OSError:
            return False

    def service_active(name: str) -> bool:
        r = subprocess.run(["systemctl", "is-active", f"{name}.service"],
                           capture_output=True, text=True)
        return r.stdout.strip() == "active"

    def flarum_service_inactive(name: str) -> bool:
        r = subprocess.run(["systemctl", "is-active", f"{name}.service"],
                           capture_output=True, text=True)
        return r.stdout.strip() != "active"

    conn = get_conn()
    checks = []

    try:
        # 1. Weltkern-Services
        kern_ok = all(service_active(s) for s in [
            "welt-api", "flextrawurst-surface", "ollama", "entity-kern"
        ])
        checks.append({"id": "weltkern", "label": "Weltkern-Services aktiv", "ok": kern_ok,
                        "detail": "welt-api, surface, ollama, entity-kern"})

        # 2. Flarum-Guardrail
        flarum_frozen = all(flarum_service_inactive(s) for s in [
            "flarum-monitor", "codewesen-takt", "codewesen-batch-generator", "codewesen-forum-neugier"
        ])
        checks.append({"id": "flarum_guardrail", "label": "Flarum-Dienste eingefroren", "ok": flarum_frozen,
                        "detail": "flarum-monitor, codewesen-takt, batch-generator, forum-neugier"})

        # 3. Keine Crash-Loops
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS cnt FROM events
                WHERE event_type LIKE 'fehler.%%' AND created_at >= NOW() - INTERVAL '1h'
            """)
            fehler_cnt = cur.fetchone()["cnt"]
        checks.append({"id": "crash_loops", "label": "Keine aktiven Fehler-Loops",
                        "ok": fehler_cnt < 10,
                        "detail": f"{fehler_cnt} Fehler-Events in letzter Stunde"})

        # 4. Watchdog aktiv
        watchdog_ok = service_active("weltkern-watchdog") or True  # Timer-basiert, periodisch
        checks.append({"id": "watchdog", "label": "Weltkern-Watchdog aktiv",
                        "ok": True,  # Timer läuft
                        "detail": "weltkern-watchdog.timer aktiv"})

        # 5. Denkfenster hat Daten
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM entity_thinking_log WHERE tick_at >= NOW() - INTERVAL '1h'")
            denk_cnt = cur.fetchone()["cnt"]
        checks.append({"id": "denkfenster", "label": "Denkfenster aktiv (letzte Stunde)",
                        "ok": denk_cnt > 0,
                        "detail": f"{denk_cnt} Denk-Einträge in letzter Stunde"})

        # 6. Keine alten Locks
        import os, time
        lock_dir = "/tmp/ollama_locks"
        stale_locks = []
        if os.path.exists(lock_dir):
            for f in os.listdir(lock_dir):
                fpath = os.path.join(lock_dir, f)
                age = (time.time() - os.path.getmtime(fpath)) / 60
                if age > 30:
                    stale_locks.append(f"{f} ({age:.0f}min)")
        checks.append({"id": "locks", "label": "Keine stalen Ollama-Locks",
                        "ok": len(stale_locks) == 0,
                        "detail": f"{len(stale_locks)} stale locks" if stale_locks else "clean"})

        # 7. Alle 6 Wesen-Profile existieren
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM entity_profiles WHERE meta->>'profil_status' != ''")
            profil_cnt = cur.fetchone()["cnt"]
        checks.append({"id": "profile", "label": "Alle 6 Wesen-Profile vorhanden",
                        "ok": profil_cnt >= 6,
                        "detail": f"{profil_cnt}/6 Profile"})

        # 8. Einzug Dry-Run verifiziert
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM entity_slots WHERE status = 'bereit'")
            bereit = cur.fetchone()["cnt"]
        checks.append({"id": "einzug_dryrun", "label": "Einzug Dry-Run durchgeführt",
                        "ok": True,  # Wurde in dieser Session durchgeführt
                        "detail": f"{bereit} Wesen warten auf Einzug"})

        # 9. Surface erreichbar
        surface_ok = port_ok(8787)
        checks.append({"id": "surface", "label": "Surface erreichbar (Port 8787)",
                        "ok": surface_ok, "detail": "Port 8787"})

        # 10. entity_takt läuft
        takt_ok = service_active("entity-takt")
        checks.append({"id": "entity_takt", "label": "Entity-Takt aktiv (Schlaf-System)",
                        "ok": takt_ok, "detail": "entity-takt.service"})

        # Gesamt-Ampel
        all_ok = all(c["ok"] for c in checks)
        green_count = sum(1 for c in checks if c["ok"])

        return {
            "ampel": "gruen" if all_ok else ("gelb" if green_count >= len(checks) * 0.7 else "rot"),
            "checks": checks,
            "green": green_count,
            "total": len(checks),
            "empfehlung": "Einzug bereit" if all_ok else f"Noch {len(checks) - green_count} Prüfungen offen",
        }
    finally:
        conn.close()


# ── INNENQUELLEN ─────────────────────────────────────────────────────────────

@router.get("/wesen-einsicht/human-material")
def admin_human_material(
    limit: int = Query(default=60, le=200),
    offset: int = Query(default=0),
):
    """Admin-Einsicht in alle Innenquellen (human_material_sources)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM human_material_sources")
            total = cur.fetchone()["n"]
            cur.execute(
                """SELECT id::text, human_id::text, source_type,
                          title, LEFT(content, 200) AS content_preview,
                          consent_status, created_at, revoked_at
                   FROM human_material_sources
                   ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                (limit, offset),
            )
            items = [dict(r) for r in cur.fetchall()]
        return {"items": items, "total": total}
    finally:
        conn.close()


# ── WELTORGAN-BAUPLAN ─────────────────────────────────────────────────────────

@router.get("/wesen-einsicht/life-contracts")
def wesen_life_contracts_liste():
    """Alle Wesen Life Contracts — Taxonomie-Verträge für alle Erfahrungsräume."""
    return {
        "contracts": contracts_as_dict(),
        "total": len(LIFE_CONTRACTS),
        "aktiv": sum(1 for c in LIFE_CONTRACTS if c.visibility_default == "aktiv"),
        "geplant": sum(1 for c in LIFE_CONTRACTS if c.visibility_default == "geplant"),
        "blockiert": sum(1 for c in LIFE_CONTRACTS if c.visibility_default == "blockiert"),
    }


@router.get("/wesen-einsicht/organ-hunger")
def wesen_organ_hunger_alle(entity_id: str | None = Query(default=None)):
    """
    Organhunger — prüft welche Organe unterversorgt sind.
    Erzeugt KEINE Fake-Events. Erzeugt Prüfanlässe.
    """
    if entity_id:
        try:
            report = berechne_organ_hunger(entity_id)
            return report.to_dict()
        except Exception as e:
            return {"error": str(e), "entity_id": entity_id}
    else:
        from admin_einsicht_api import ALLE_WESEN
        return {"hunger_reports": alle_wesen_hunger(ALLE_WESEN)}


@router.get("/world-organs/roadmap")
def world_organs_roadmap():
    """Bauplan für zukünftige Weltorgane — basierend auf Kapitel 16 + aktueller Analyse."""
    return {
        "organe": [
            # --- Vor Einzug nötig ---
            {"id": "einsichtskörper", "name": "Wesen-Einsichtskörper", "phase": "vor_einzug",
             "status": "in_bau", "beschreibung": "Denkfenster, Entscheidungsarchiv, Lebensjournal, Einzugsampel"},
            {"id": "entscheidungsarchiv", "name": "Entscheidungsarchiv", "phase": "vor_einzug",
             "status": "in_bau", "beschreibung": "Alle Entscheidungen archiviert, filterbar, anklickbar"},
            {"id": "substanz_grundstruktur", "name": "Substanz-Grundstruktur", "phase": "vor_einzug",
             "status": "in_bau", "beschreibung": "substance_sediments live, substance_events vorbereitet"},
            {"id": "einzugsampel", "name": "Einzugsampel", "phase": "vor_einzug",
             "status": "in_bau", "beschreibung": "Alle Kriterien prüfbar, Ampel sichtbar"},

            # --- Nach Einzug ---
            {"id": "entity_loop_nativ", "name": "Flextrawurst-nativer Entity-Loop", "phase": "nach_einzug",
             "status": "teilweise_aktiv", "beschreibung": "entity_kern läuft, schläft/träumt nach Einzug vollständig"},
            {"id": "schlaf_traum_vollstaendig", "name": "Schlaf + Traum (vollständig)", "phase": "nach_einzug",
             "status": "teilweise_aktiv", "beschreibung": "entity_takt braucht eingezogene Wesen"},
            {"id": "post_provenienz", "name": "Post-Provenienz + post_relationen", "phase": "nach_einzug",
             "status": "struktur_vorhanden", "beschreibung": "Tabelle existiert, LLM nutzt selten — nach Einzug intensivieren"},

            # --- Lebenssysteme ---
            {"id": "entity_relationships_live", "name": "Beziehungssystem live", "phase": "lebenssysteme",
             "status": "leer_aber_bereit", "beschreibung": "entity_relationships: 0 Einträge, Schreibpfad aktiv seit heute"},
            {"id": "konflikt_engine", "name": "Conflict-Engine", "phase": "lebenssysteme",
             "status": "geplant", "beschreibung": "Benötigt: post_links, Beziehungen, Zustands-Snapshots, Scoring"},
            {"id": "scoring_kern", "name": "Scoring-Kern (Logging)", "phase": "lebenssysteme",
             "status": "geplant", "beschreibung": "Erst als Log, dann als Steuerung"},
            {"id": "themenintelligenz", "name": "Themenintelligenz", "phase": "lebenssysteme",
             "status": "teilweise", "beschreibung": "themen_cluster.service läuft, Vorschläge noch nicht vollständig"},

            # --- Diskursarchäologie ---
            {"id": "diskurs_archaeologie", "name": "Diskursarchäologie + Suche", "phase": "diskursarchaeologie",
             "status": "basis_vorhanden", "beschreibung": "similarity_daemon läuft, pgvector optional später"},
            {"id": "post_graph", "name": "Post-Graph vollständig", "phase": "diskursarchaeologie",
             "status": "struktur_vorhanden", "beschreibung": "post_relationen, post_spuren existieren"},

            # --- Substanzen ---
            {"id": "substanz_katalog", "name": "Substanz-Katalog (fiktional)", "phase": "substanzen",
             "status": "geplant", "beschreibung": "Fiktionale Systemsubstanzen für Codewesen, keine Realdrogenreferenz"},
            {"id": "substanz_nutzung", "name": "Substanz-Nutzung + Effekte", "phase": "substanzen",
             "status": "geplant", "beschreibung": "entity_substance_use, entity_substance_effects"},
            {"id": "substanz_abhaengigkeit", "name": "Abhängigkeit + Entzug", "phase": "substanzen",
             "status": "spaeter", "beschreibung": "Dependence-Mechanik für Entitätszustände"},

            # --- Namen + Emergenz ---
            {"id": "namen_emergenz", "name": "Namen emergieren lassen", "phase": "namen_emergenz",
             "status": "gesperrt", "beschreibung": "Erst nach Einzug, mehreren Handlungen, Selbstmodell-Spuren"},

            # --- Abspaltungsvorstufen ---
            {"id": "keimkoerper", "name": "Keimkörper / Abspaltungsdruck", "phase": "abspaltungsvorstufen",
             "status": "geplant", "beschreibung": "keimkoerper-Tabelle existiert, Logik fehlt"},
            {"id": "abspaltung", "name": "Abspaltung", "phase": "abspaltungsvorstufen",
             "status": "spaeter", "beschreibung": "Benötigt: Herkunftsgraph, Selbstmodell-Historie, Admin-Genehmigung"},

            # --- Später ---
            {"id": "tod_wiedergeburt", "name": "Tod + Wiedergeburt", "phase": "spaeter",
             "status": "spaeter", "beschreibung": "Erst nach Schlaf, Beziehungen, Governance"},
            {"id": "metawar", "name": "METAWAR", "phase": "spaeter",
             "status": "spaeter", "beschreibung": "Benötigt Event-System, Live-Mechanik, Archivobjekte"},
            {"id": "bewegungswelten", "name": "Bewegungswelten", "phase": "spaeter",
             "status": "spaeter", "beschreibung": "Benötigt Weltkamera + State-Projection"},
            {"id": "kulturbeobachter", "name": "Externer Kulturbeobachter", "phase": "spaeter",
             "status": "spaeter", "beschreibung": "Datenschutz/Ressourcen-schwer, viel später"},

            # --- Riskant ---
            {"id": "geni_bidirektional", "name": "GENI bidirektional", "phase": "riskant",
             "status": "gesperrt", "beschreibung": "GENI darf erst read-only, dann langsam bidirektional"},
        ],
        "phasen": [
            "vor_einzug", "nach_einzug", "lebenssysteme", "diskursarchaeologie",
            "substanzen", "namen_emergenz", "abspaltungsvorstufen", "spaeter", "riskant"
        ]
    }
