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
        # 2026-07-22 gefunden (per pg_stat_activity verifiziert): ohne Autocommit blieb
        # jede einzelne SELECT-Query dieser lang lebenden SSE-Verbindung in EINER nie
        # committeten Transaktion haengen (bei einer Kachel schon 6+ Minuten offen) --
        # Snapshot-Alter wächst mit der Verbindungsdauer, was Autovacuum blockiert und
        # die Tabelle ueber Stunden zunehmend traege macht. Gleicher Fix wie bei der
        # LISTEN-Verbindung oben.
        read_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

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
                    SELECT id, event_json FROM entity_dom_events
                    WHERE entity_id = %s
                        AND created_at >= COALESCE(
                            (SELECT created_at FROM meta_davor),
                            (SELECT created_at FROM letzter_snapshot)
                        )
                    ORDER BY created_at ASC
                """, (entity_id, entity_id, entity_id))
                # 2026-07-22 (Daniel live gefunden per Konsolen-Log: wiederholte rrweb-
                # Warnungen "[replayer] Node with id 'X' not found"): das LISTEN lief schon
                # VOR dieser Backlog-Query, Notifies fuer Zeilen, die WAEHREND der Query
                # eingefuegt wurden, landen dadurch in BEIDEM -- im Backlog-Ergebnis UND
                # nochmal live ueber die Notify-Queue. rrweb bekommt dieselbe Mutation
                # dadurch zweimal, verwirft die zweite lautlos als "Node nicht gefunden"
                # (der Knoten wurde ja schon beim ersten Mal hinzugefuegt/entfernt) --
                # nachfolgende, WIRKLICH neue Mutationen koennen dadurch kaskadierend
                # falsch aufgesetzt werden. Fix: die IDs aller Backlog-Zeilen zurueckgeben,
                # damit der Aufrufer identische Notifies aus der Live-Queue verwerfen kann.
                rows = c.fetchall()
                return [str(r["id"]) for r in rows], [r["event_json"] for r in rows]

        loop = asyncio.get_running_loop()
        # 2026-07-22 gefunden (nach ausfuehrlicher Playwright-Reproduktion des Live-Delivery-
        # Problems, siehe erlebnisschicht-Ideendatei "zweiter Nachtrag"): die bisherige Schleife
        # belegte JEDE offene SSE-Verbindung alle 0.5s aufs Neue einen Slot im geteilten
        # Default-Threadpool (loop.run_in_executor(None, _poll_once)) -- nur fuer die reine
        # Pruefung "ist etwas da". Bei mehreren gleichzeitig offenen Verbindungen (7 Kacheln +
        # Modal + Testverbindungen) konkurrierten diese Dauerpoll-Tasks um den Threadpool,
        # echte Event-Zustellung wurde dadurch verzoegert/unregelmaessig -- reproduziert: gleicher
        # Code lieferte auf einer isolierten Testseite zuverlaessig, in der vollen Produktions-
        # seite mit paralleler Verbindung nicht. Fix: die Postgres-LISTEN-Verbindung wird direkt
        # per loop.add_reader() an die Event-Loop gehaengt (psycopg2-Standardmuster fuer async
        # Notifications) -- die Loop selbst weckt den Callback, sobald am Socket wirklich Daten
        # anliegen, kein Dauerpolling-Thread mehr noetig. Threadpool wird nur noch fuer die
        # eigentlichen (selteneren) Event-Fetches gebraucht.
        notify_queue: asyncio.Queue = asyncio.Queue()

        def _bei_lesbar():
            try:
                conn.poll()
            except Exception:
                return
            while conn.notifies:
                notify_queue.put_nowait(conn.notifies.pop(0))

        loop.add_reader(conn.fileno(), _bei_lesbar)
        try:
            bekannte_ids, backlog = await loop.run_in_executor(None, _hole_backlog)
            bekannte_ids = set(bekannte_ids)
            for event in backlog:
                yield f"data: {json.dumps(event)}\n\n"
            # 2026-07-22 (per Playwright-Repro verifiziert, siehe build_surface.ts-Kommentar
            # bei _scvVerarbeiteGridEvent): der Client darf den Backlog NICHT durch denselben
            # liveMode-Scheduler jagen wie echte Live-Events -- rrweb plant jedes addEvent()
            # nach seinem *echten* Zeitstempel relativ zur Baseline ein. Liegt der letzte
            # Snapshot Minuten/Stunden zurueck, muesste der Client buchstaeblich so lange
            # warten, bis die juengsten Backlog-Events "dran" waeren -- die Kachel blieb
            # ein Standbild. Dieser Marker sagt dem Client: Backlog fertig, jetzt per
            # replayer.pause(totalTime) synchron ans Ende vorspulen und danach erst live schalten.
            yield f"data: {json.dumps({'backlog_done': True})}\n\n"

            while True:
                try:
                    notify = await asyncio.wait_for(notify_queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield f": heartbeat\n\n"
                    continue
                try:
                    meta = json.loads(notify.payload)
                except Exception:
                    continue
                if meta.get("entity_id") != entity_id:
                    continue
                if meta["id"] in bekannte_ids:
                    continue  # bereits im Backlog enthalten -- siehe Kommentar bei _hole_backlog
                bekannte_ids.add(meta["id"])
                event = await loop.run_in_executor(None, _hole_event, meta["id"])
                if event is None:
                    continue
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            loop.remove_reader(conn.fileno())
            cur.close()
            conn.close()
            read_conn.close()

    return gen()


def _pg_listen_dom_events_alle_sse():
    # 2026-07-22 (Daniel live gefunden, per Browser-EventSource-Tracing bestaetigt):
    # Browser begrenzen gleichzeitige HTTP-Verbindungen pro Origin auf ~6 (klassisches
    # HTTP/1.1-Limit). Die SCREENS-Seite brauchte bisher 7 einzelne dom-events-Streams
    # (eine pro Wesen-Kachel) PLUS events/stream PLUS denkstream/all/stream -- weit ueber
    # dem Limit. Ueberzaehlige Verbindungen haengen dann einfach im Browser fest, ohne
    # Fehler, ohne je Daten zu bekommen -- welche Kachel das trifft ist praktisch
    # zufaellig. Fix, analog zum schon bestehenden denkstream_api.py::/all/stream-Muster:
    # EINE gemeinsame Verbindung fuer alle Wesen, jedes Event mit entity_id markiert,
    # das Frontend sortiert client-seitig zum richtigen Kachel-Replayer. Jedes Wesen
    # behaelt seinen eigenen individuellen Spiegel -- nur die Leitung ist gemeinsam.
    async def gen():
        conn = psycopg2.connect(DB_URI)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("LISTEN entity_dom_events")
        read_conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
        # 2026-07-22 gefunden (per pg_stat_activity verifiziert): ohne Autocommit blieb
        # jede einzelne SELECT-Query dieser lang lebenden SSE-Verbindung in EINER nie
        # committeten Transaktion haengen (bei einer Kachel schon 6+ Minuten offen) --
        # Snapshot-Alter wächst mit der Verbindungsdauer, was Autovacuum blockiert und
        # die Tabelle ueber Stunden zunehmend traege macht. Gleicher Fix wie bei der
        # LISTEN-Verbindung oben.
        read_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        def _hole_event(event_id: str):
            with read_conn.cursor() as c:
                c.execute("SELECT event_json FROM entity_dom_events WHERE id = %s", (event_id,))
                row = c.fetchone()
                return row["event_json"] if row else None

        def _hole_backlog_alle():
            with read_conn.cursor() as c:
                c.execute("""
                    SELECT DISTINCT entity_id FROM entity_dom_events
                    WHERE event_json->>'type' = '2'
                """)
                entity_ids = [r["entity_id"] for r in c.fetchall()]
            ergebnis = []
            bekannte_ids = set()
            for eid in entity_ids:
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
                        SELECT id, event_json FROM entity_dom_events
                        WHERE entity_id = %s
                            AND created_at >= COALESCE(
                                (SELECT created_at FROM meta_davor),
                                (SELECT created_at FROM letzter_snapshot)
                            )
                        ORDER BY created_at ASC
                    """, (eid, eid, eid))
                    for r in c.fetchall():
                        ergebnis.append({"entity_id": eid, "event": r["event_json"]})
                        bekannte_ids.add(str(r["id"]))
                # Marker direkt nach dem Backlog-Block DIESES Wesens (siehe Kommentar in
                # _pg_listen_dom_events_sse oben -- gleicher Grund, hier pro Wesen einzeln,
                # da alle 7 sich diese eine Verbindung teilen). In dieselbe {entity_id,event}-
                # Huelle gepackt wie jede andere Nachricht dieses Endpunkts, sonst liest der
                # Client (der immer data.event auswertet) den Marker als event=undefined.
                ergebnis.append({"entity_id": eid, "event": {"backlog_done": True}})
            return bekannte_ids, ergebnis

        loop = asyncio.get_running_loop()
        # Gleicher Fix wie in _pg_listen_dom_events_sse oben (dort ausfuehrlich begruendet):
        # kein Dauerpolling-Thread mehr, die LISTEN-Verbindung haengt direkt an der Event-Loop.
        notify_queue: asyncio.Queue = asyncio.Queue()

        def _bei_lesbar():
            try:
                conn.poll()
            except Exception:
                return
            while conn.notifies:
                notify_queue.put_nowait(conn.notifies.pop(0))

        loop.add_reader(conn.fileno(), _bei_lesbar)
        try:
            bekannte_ids, backlog = await loop.run_in_executor(None, _hole_backlog_alle)
            for item in backlog:
                yield f"data: {json.dumps(item)}\n\n"

            while True:
                try:
                    notify = await asyncio.wait_for(notify_queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield f": heartbeat\n\n"
                    continue
                try:
                    meta = json.loads(notify.payload)
                except Exception:
                    continue
                if meta["id"] in bekannte_ids:
                    continue  # bereits im Backlog enthalten -- siehe Kommentar bei _hole_backlog_alle
                bekannte_ids.add(meta["id"])
                event = await loop.run_in_executor(None, _hole_event, meta["id"])
                if event is None:
                    continue
                yield f"data: {json.dumps({'entity_id': meta.get('entity_id'), 'event': event})}\n\n"
        finally:
            loop.remove_reader(conn.fileno())
            cur.close()
            conn.close()
            read_conn.close()

    return gen()


@dom_events_router.get("/stream/all")
async def dom_events_alle_sse():
    """Live-SSE-Stream der rrweb-DOM-Events ALLER Wesen in EINER Verbindung — oeffentlich.
    Payload je Event: {"entity_id": "...", "event": {...rrweb-Event...}}. Muss VOR der
    dynamischen /stream/{entity_id}-Route registriert sein, sonst wuerde 'all' faelschlich
    als entity_id gematcht."""
    return StreamingResponse(
        _pg_listen_dom_events_alle_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


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
