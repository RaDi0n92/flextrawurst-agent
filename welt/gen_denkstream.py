#!/usr/bin/env python3
"""Generiert migration_denkstream.sql und denkstream_api.py"""

migration = '''-- Denkstream: Live-Chunks während LLM-Generierung
-- Jeder Chunk kommt als PostgreSQL NOTIFY rein → SSE weiterleiten

CREATE TABLE IF NOT EXISTS entity_denkstream (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id   VARCHAR REFERENCES entity_slots(entity_id),
    stream_id   UUID DEFAULT gen_random_uuid(),
    chunk       TEXT NOT NULL,
    seq         INTEGER DEFAULT 0,
    done        BOOLEAN DEFAULT false,
    url         TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_denkstream_entity_at
    ON entity_denkstream(entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_denkstream_stream
    ON entity_denkstream(stream_id, seq);

-- Trigger: bei jedem INSERT NOTIFY senden
CREATE OR REPLACE FUNCTION notify_denkstream() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'entity_denkstream',
        json_build_object(
            'entity_id', NEW.entity_id,
            'stream_id', NEW.stream_id,
            'chunk',     NEW.chunk,
            'seq',       NEW.seq,
            'done',      NEW.done,
            'url',       NEW.url
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_denkstream ON entity_denkstream;
CREATE TRIGGER trg_notify_denkstream
    AFTER INSERT ON entity_denkstream
    FOR EACH ROW EXECUTE FUNCTION notify_denkstream();

-- Screenshot-Tabelle: aktueller Screenshot pro Wesen
CREATE TABLE IF NOT EXISTS entity_screenshots (
    entity_id   VARCHAR PRIMARY KEY REFERENCES entity_slots(entity_id),
    screenshot  BYTEA,
    url         TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
'''

denkstream_api = r'''#!/usr/bin/env python3
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


def _pg_listen_sse(channel: str, entity_filter: str | None) -> AsyncGenerator:
    """Generator: PostgreSQL LISTEN → SSE-Chunks."""
    conn = psycopg2.connect(DB_URI)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"LISTEN {channel}")

    async def gen():
        try:
            while True:
                if sel.select([conn], [], [], 30.0)[0]:
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
                else:
                    # Heartbeat alle 30s damit Connection offen bleibt
                    yield f": heartbeat\n\n"
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
'''

with open('/root/werkraum/welt/migration_denkstream.sql', 'w') as f:
    f.write(migration)

with open('/root/werkraum/welt/denkstream_api.py', 'w') as f:
    f.write(denkstream_api)

print("Fertig:")
print(f"  migration_denkstream.sql ({len(migration)} Zeichen)")
print(f"  denkstream_api.py ({len(denkstream_api)} Zeichen)")
