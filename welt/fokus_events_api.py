#!/usr/bin/env python3
"""
Fokus-Events-API: Röntgenblick-Overlay (2026-07-21, Daniels bestätigter Bauauftrag
nach rrweb Aufnahme+Wiedergabe — Grundgesetz 1 / dreiergespann_dom_theorie.md).
Wird von api.py importiert via: from fokus_events_api import fokus_events_router

browser_agent.py schreibt bei klicke:/tippe:/navigiere: direkt in entity_fokus_events
(melde_fokus(), gleiche Direktschreib-Konvention wie entity_denkstream/entity_dom_events).
Anders als entity_dom_events ist der Payload hier klein genug, um komplett im NOTIFY
mitzuschicken — kein zusätzlicher SELECT-Roundtrip nötig (siehe migration_fokus_events.sql).

Endpunkte:
  GET /fokus-events/stream/{entity_id} — SSE-Stream der Fokus-Events eines Wesens (öffentlich)
"""

import asyncio
import json
import select as sel

import psycopg2
from fastapi import APIRouter, Path
from fastapi.responses import StreamingResponse

import os as _os
DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")

fokus_events_router = APIRouter(prefix="/fokus-events", tags=["fokus_events"])


def _pg_listen_fokus_events_sse(entity_id: str):
    # 2026-07-21 gefunden (siehe dom_events_api.py fuer die volle Herleitung): Verbindungsaufbau
    # muss innerhalb von gen() passieren, sonst laeuft er im anyio-Worker-Thread der
    # synchronen Routen-Funktion waehrend Polling/Notifies auf dem Event-Loop-Thread
    # laufen -- reale NOTIFYs von browser_agent.py kamen dadurch nie an.
    async def gen():
        conn = psycopg2.connect(DB_URI)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("LISTEN entity_fokus_events")

        def _poll_once():
            readable, _, _ = sel.select([conn], [], [], 0.5)
            return bool(readable)

        loop = asyncio.get_running_loop()
        try:
            heartbeat = 0
            while True:
                ready = await loop.run_in_executor(None, _poll_once)
                if ready:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        try:
                            data = json.loads(notify.payload)
                        except Exception:
                            continue
                        if data.get("entity_id") != entity_id:
                            continue
                        yield f"data: {json.dumps(data)}\n\n"
                        heartbeat = 0
                else:
                    heartbeat += 1
                    if heartbeat >= 60:
                        yield f": heartbeat\n\n"
                        heartbeat = 0
        finally:
            cur.close()
            conn.close()

    return gen()


@fokus_events_router.get("/stream/{entity_id}")
async def fokus_events_sse(entity_id: str = Path(..., max_length=64)):
    """Live-SSE-Stream der Fokus-Events eines Wesens — öffentlich, kein Auth
    (dieselbe Sichtbarkeit wie Denkstream/DOM-Events: kein privater Inhalt,
    nur die öffentliche Browser-Aktivität eines Wesens)."""
    return StreamingResponse(
        _pg_listen_fokus_events_sse(entity_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )
