#!/usr/bin/env python3
"""
DOM-Events-API: rrweb-Live-Spiegel fuer die Menschen-Auge-Ebene (Grundgesetz 1 /
dreiergespann_dom_theorie.md — "der Live-Mirror-Teil, rrweb-Idee").
Wird von api.py importiert via: from dom_events_api import dom_events_router

browser_agent.py schreibt DOM-Mutations-Events direkt in entity_dom_events (gleiche
Direktschreib-Konvention wie bei entity_denkstream — kein HTTP-Umweg, beide Prozesse
teilen sich dieselbe DB). Dieser Endpunkt reicht sie live als SSE weiter, damit ein
rrweb-Player im Browser eines Menschen die Seite pixelgenau nachbaut, ohne
Screenshots.

Endpunkte:
  GET /dom-events/stream/{entity_id} — SSE-Stream der DOM-Events eines Wesens (oeffentlich)
"""

import asyncio
import json
import select as sel

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Path
from fastapi.responses import StreamingResponse

import os as _os
DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")

dom_events_router = APIRouter(prefix="/dom-events", tags=["dom_events"])


def _pg_listen_dom_events_sse(entity_id: str):
    # 2026-07-21 gefunden: Verbindungsaufbau (psycopg2.connect) lief vorher in der
    # SYNCHRONEN Routen-Funktion, die FastAPI ueber einen anyio-Worker-Thread ausfuehrt --
    # das gesamte LISTEN/poll()/notifies-Handling danach lief aber auf dem Event-Loop-
    # Thread der async gen()-Funktion. Reale NOTIFYs von browser_agent.py (separater
    # Prozess) kamen dadurch nie an, obwohl ein unabhaengiges Test-Script mit exakt
    # derselben LISTEN/poll-Logik auf EINEM durchgehenden Thread sie zuverlaessig
    # empfangen hat -- per Selbsttest (pg_notify direkt aus dem gleichen Prozess)
    # bestaetigt funktionierte NUR die unmittelbare Eigen-Benachrichtigung, nie eine von
    # aussen. Fix: Verbindungsaufbau UND das gesamte Polling passieren jetzt konsequent
    # innerhalb der async gen()-Funktion selbst, auf dem Event-Loop-Thread.
    async def gen():
        conn = psycopg2.connect(DB_URI)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("LISTEN entity_dom_events")
        read_conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)

        def _poll_once():
            readable, _, _ = sel.select([conn], [], [], 0.5)
            return bool(readable)

        def _hole_event(event_id: str):
            with read_conn.cursor() as c:
                c.execute("SELECT event_json FROM entity_dom_events WHERE id = %s", (event_id,))
                row = c.fetchone()
                return row["event_json"] if row else None

        def _hole_backlog():
            # 2026-07-22 (zweiter Anlauf, jetzt zusammen mit dem eigentlichen Grid-CSS-Fix
            # verifiziert): ein neu verbundener/reconnecteter Client bekam bisher NUR
            # zukuenftige Events -- den einmaligen Meta+FullSnapshot-Bootstrap, den
            # rrweb.Replayer zwingend braucht, gab es nur beim letzten page.goto() des
            # Wesens, oft Minuten her. Fix: beim Connect erst den letzten Meta(type 4)+
            # FullSnapshot(type 2)-Block plus alle Inkremente seither nachliefern.
            with read_conn.cursor() as c:
                c.execute("""
                    WITH letzter_snapshot AS (
                        SELECT created_at FROM entity_dom_events
                        WHERE entity_id = %s AND event_json->>'type' = '2'
                        ORDER BY created_at DESC LIMIT 1
                    ), meta_davor AS (
                        SELECT created_at FROM entity_dom_events
                        WHERE entity_id = %s AND event_json->>'type' = '4'
                            AND created_at <= (SELECT created_at FROM letzter_snapshot)
                        ORDER BY created_at DESC LIMIT 1
                    )
                    SELECT event_json FROM entity_dom_events
                    WHERE entity_id = %s
                        AND created_at >= COALESCE(
                            (SELECT created_at FROM meta_davor),
                            (SELECT created_at FROM letzter_snapshot)
                        )
                    ORDER BY created_at ASC
                """, (entity_id, entity_id, entity_id))
                return [r["event_json"] for r in c.fetchall()]

        loop = asyncio.get_running_loop()
        try:
            backlog = await loop.run_in_executor(None, _hole_backlog)
            for event in backlog:
                yield f"data: {json.dumps(event)}\n\n"

            heartbeat = 0
            while True:
                ready = await loop.run_in_executor(None, _poll_once)
                if ready:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        try:
                            meta = json.loads(notify.payload)
                        except Exception:
                            continue
                        if meta.get("entity_id") != entity_id:
                            continue
                        event = await loop.run_in_executor(None, _hole_event, meta["id"])
                        if event is None:
                            continue
                        yield f"data: {json.dumps(event)}\n\n"
                        heartbeat = 0
                else:
                    heartbeat += 1
                    if heartbeat >= 60:
                        yield f": heartbeat\n\n"
                        heartbeat = 0
        finally:
            cur.close()
            conn.close()
            read_conn.close()

    return gen()


@dom_events_router.get("/stream/{entity_id}")
async def dom_events_sse(entity_id: str = Path(..., max_length=64)):
    """Live-SSE-Stream der rrweb-DOM-Events eines Wesens — oeffentlich, kein Auth
    (dieselbe Sichtbarkeit wie der bestehende Denkstream: kein privater Inhalt,
    nur die oeffentliche Browser-Aktivitaet eines Wesens).
    2026-07-21: async statt sync def -- vermeidet den anyio-Worker-Thread-Sprung,
    siehe Kommentar in _pg_listen_dom_events_sse."""
    return StreamingResponse(
        _pg_listen_dom_events_sse(entity_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )
