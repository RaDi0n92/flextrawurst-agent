#!/usr/bin/env python3
"""
Denkstream-API: SSE-Endpunkte für live Denkstream der Wesen.
Wird von api.py importiert via: from denkstream_api import denkstream_router

Endpunkte:
  GET /denkstream/{entity_id}      — SSE-Stream eines Wesens (öffentlich)
  GET /denkstream/all              — SSE-Stream aller Wesen (öffentlich)
  GET /denkstream/{entity_id}/last — letzte 20 Einträge (öffentlich)
  GET /denkstream/screenshot/{id}  — aktueller Screenshot als JPEG
  POST /denkstream/chunk           — Browser-Agent schreibt Chunk (intern)
"""

import json
import logging
import asyncio
import select as sel
import threading
from typing import AsyncGenerator

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

log = logging.getLogger("denkstream")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
denkstream_router = APIRouter(prefix="/denkstream", tags=["denkstream"])


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


class ChunkBody(BaseModel):
    entity_id: str
    stream_id: str
    chunk: str
    seq: int = 0
    done: bool = False
    url: str = ""


@denkstream_router.post("/chunk", status_code=201)
def denkstream_chunk(body: ChunkBody):
    """Browser-Agent schreibt einen Chunk — intern."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_denkstream
                    (entity_id, stream_id, chunk, seq, done, url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (body.entity_id, body.stream_id, body.chunk,
                  body.seq, body.done, body.url))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


@denkstream_router.get("/{entity_id}/last")
def denkstream_last(entity_id: str, limit: int = 20):
    """Letzte N Denklogs eines Wesens — öffentlich, kein Auth."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entity_id, gedanke, entscheidung, begruendung,
                       tick_at, meta->>'url' AS url,
                       meta->>'screenshot' AS screenshot
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND meta->>'source' = 'browser_agent'
                ORDER BY tick_at DESC
                LIMIT %s
            """, (entity_id, limit))
            rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return {"logs": rows, "entity_id": entity_id}


@denkstream_router.get("/all/last")
def denkstream_all_last(limit: int = 10):
    """Letzte N Denklogs aller Wesen — öffentlich."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entity_id, gedanke, entscheidung, tick_at,
                       meta->>'url' AS url
                FROM entity_thinking_log
                WHERE meta->>'source' = 'browser_agent'
                ORDER BY tick_at DESC
                LIMIT %s
            """, (limit,))
            rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    return {"logs": rows}


@denkstream_router.get("/traumbilder/{entity_id}")
def denkstream_traumbilder(entity_id: str):
    """Liste der letzten Traumbilder eines Wesens."""
    import os, glob as _glob
    bild_dir = "/tmp/wesen_traumbilder"
    pattern = f"{bild_dir}/{entity_id}_*.jpg"
    dateien = sorted(_glob.glob(pattern), reverse=True)[:5]
    bilder = []
    for p in dateien:
        fname = os.path.basename(p)
        ts_str = fname.replace(f"{entity_id}_", "").replace(".jpg", "")
        try:
            ts = int(ts_str)
            from datetime import datetime
            dt = datetime.fromtimestamp(ts).isoformat()
        except Exception:
            dt = ts_str
        bilder.append({"pfad": p, "url": f"/api/denkstream/traumbild/{entity_id}/{fname}", "erstellt": dt})
    return {"bilder": bilder}


@denkstream_router.get("/traumbild/{entity_id}/{filename}")
def denkstream_traumbild_file(entity_id: str, filename: str):
    """Einzelnes Traumbild als JPEG."""
    import os
    pfad = f"/tmp/wesen_traumbilder/{filename}"
    if not os.path.exists(pfad) or not pfad.endswith(".jpg"):
        raise HTTPException(status_code=404, detail="Traumbild nicht gefunden")
    with open(pfad, "rb") as f:
        data = f.read()
    return Response(content=data, media_type="image/jpeg",
                    headers={"Cache-Control": "public, max-age=3600"})


@denkstream_router.get("/screenshot/{entity_id}")
def denkstream_screenshot(entity_id: str):
    """Aktueller Screenshot eines Wesens als JPEG."""
    import os
    pfad = f"/tmp/wesen_screenshots/{entity_id}_aktuell.jpg"
    if not os.path.exists(pfad):
        raise HTTPException(status_code=404, detail="Kein Screenshot vorhanden")
    with open(pfad, "rb") as f:
        data = f.read()
    return Response(content=data, media_type="image/jpeg",
                    headers={"Cache-Control": "no-cache, max-age=0"})


@denkstream_router.get("/status/all")
def denkstream_status_all():
    """Aktueller Browser-Status aller Wesen — URL + letzter Gedanke + Screenshot-URL."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (entity_id)
                    entity_id,
                    gedanke,
                    entscheidung,
                    tick_at,
                    meta->>'url' AS url,
                    meta->>'screenshot' AS screenshot
                FROM entity_thinking_log
                WHERE meta->>'source' = 'browser_agent'
                  AND tick_at > NOW() - INTERVAL '15 minutes'
                ORDER BY entity_id, tick_at DESC
            """)
            rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
    # Screenshot-URL hinzufügen
    import os
    result = []
    for r in rows:
        entity_id = r["entity_id"]
        shot_path = f"/tmp/wesen_screenshots/{entity_id}_aktuell.jpg"
        r["screenshot_url"] = (
            f"/api/denkstream/screenshot/{entity_id}"
            if os.path.exists(shot_path) else None
        )
        result.append(r)
    return {"status": result, "count": len(result)}


def _pg_listen_sse(channel: str, entity_filter: str | None) -> AsyncGenerator:
    """Generator: PostgreSQL LISTEN → SSE-Chunks."""
    conn = psycopg2.connect(DB_URI)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"LISTEN {channel}")

    def _poll_once():
        return bool(sel.select([conn], [], [], 0.5))

    async def gen():
        loop = asyncio.get_running_loop()
        try:
            heartbeat = 0
            while True:
                # blocking select in thread pool — event loop bleibt frei
                ready = await loop.run_in_executor(None, _poll_once)
                if ready:
                    conn.poll()
                    while conn.notifies:
                        notify = conn.notifies.pop(0)
                        try:
                            data = json.loads(notify.payload)
                        except Exception:
                            continue
                        if entity_filter and data.get("entity_id") != entity_filter:
                            continue
                        yield f"data: {json.dumps(data)}\n\n"
                        heartbeat = 0
                else:
                    heartbeat += 1
                    if heartbeat >= 60:  # alle 30s Heartbeat (60 × 0.5s)
                        yield f": heartbeat\n\n"
                        heartbeat = 0
        finally:
            cur.close()
            conn.close()

    return gen()


@denkstream_router.get("/{entity_id}")
def denkstream_sse(entity_id: str):
    """Live-SSE-Stream des Denkens eines Wesens — öffentlich, kein Auth."""
    return StreamingResponse(
        _pg_listen_sse("entity_denkstream", entity_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


@denkstream_router.get("/all/stream")
def denkstream_all_sse():
    """Live-SSE-Stream aller Wesen — öffentlich."""
    return StreamingResponse(
        _pg_listen_sse("entity_denkstream", None),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )
