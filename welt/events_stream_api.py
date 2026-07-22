#!/usr/bin/env python3
"""
Events-Stream-API: generischer Live-Update-Kanal fuer ganz flextrawurst.
Wird von api.py importiert via: from events_stream_api import events_stream_router

Daniels Grundgesetz "Live statt F5" (2026-07-21): jedes INSERT in die heilige
events-Tabelle (Grundgesetz 5) loest per DB-Trigger (migration_events_stream.sql)
ein PostgreSQL NOTIFY aus, das hier als SSE-Chunk weitergereicht wird. Der Stream
traegt bewusst nur ein minimales, unsensibles Signal (event_type + Routing-Hinweise) --
niemals den vollen payload. Das Frontend entscheidet pro Event-Praefix, ob und was
es ueber den normalen, auth-geprueften REST-Weg neu laedt.

Endpunkte:
  GET /events/stream                 — SSE-Stream aller Events (oeffentlich)
  GET /events/stream?praefix=xyz     — nur Events deren event_type mit xyz beginnt
"""

import asyncio
import json
import select as sel
from typing import AsyncGenerator

import psycopg2
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

import os as _os
DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")

events_stream_router = APIRouter(prefix="/events", tags=["events_stream"])


def _pg_listen_events_sse(praefix: str | None) -> AsyncGenerator:
    """Generator: PostgreSQL LISTEN auf 'events_stream' -> SSE-Chunks.
    Analog zu denkstream_api._pg_listen_sse, hier generisch fuer alle Event-Typen.
    2026-07-21 gefunden (siehe dom_events_api.py fuer die volle Herleitung): Verbindungsaufbau
    muss innerhalb von gen() passieren, sonst laeuft er im anyio-Worker-Thread der
    synchronen Routen-Funktion waehrend Polling/Notifies auf dem Event-Loop-Thread laufen --
    reale NOTIFYs aus anderen Prozessen kamen dadurch nie zuverlaessig an. Betraf damit
    potenziell Grundgesetz 8 ("Live statt F5") systemweit, nicht nur einen einzelnen Tab."""
    async def gen():
        conn = psycopg2.connect(DB_URI)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("LISTEN events_stream")

        def _poll_once():
            # 2026-07-21 gefunden: bool(select.select(...)) ist IMMER True, da select()
            # immer ein 3-Tupel zurueckgibt -- der Heartbeat-Zweig unten war toter Code.
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
                        if praefix and not str(data.get("event_type", "")).startswith(praefix):
                            continue
                        yield f"data: {json.dumps(data)}\n\n"
                        heartbeat = 0
                else:
                    heartbeat += 1
                    if heartbeat >= 60:  # alle 30s Heartbeat (60 x 0.5s)
                        yield f": heartbeat\n\n"
                        heartbeat = 0
        finally:
            cur.close()
            conn.close()

    return gen()


@events_stream_router.get("/stream")
async def events_sse(praefix: str | None = Query(default=None, max_length=64)):
    """Live-SSE-Stream aller Events (optional gefiltert nach event_type-Praefix) — oeffentlich, kein Auth.
    Traegt niemals sensible Inhalte, nur ein Neulade-Signal (siehe Moduldoku)."""
    return StreamingResponse(
        _pg_listen_events_sse(praefix),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )
