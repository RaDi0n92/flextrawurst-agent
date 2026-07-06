#!/usr/bin/env python3
"""
Traum-Generator: Generiert Traumtext aus dem erlebten Tag eines Wesens.

Wird von browser_agent.py innerhalb von schlafe() aufgerufen.
Streamt Token für Token in entity_denkstream (type='traum').
Speichert fertigen Traum in traumspuren.
"""

import json
import logging
import sys
import uuid
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
import requests

sys.path.insert(0, "/root/werkraum")
import hauhau_client

log = logging.getLogger("traum-generator")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
MODEL = "hauhaucs-q6"
MAX_TAGE_EVENTS = 30   # max Events für Traum-Kontext
LLM_TIMEOUT = 240


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def hole_tages_erinnerungen(conn, entity_id: str) -> list[dict]:
    """Holt die wichtigsten Erlebnisse des Wachtags — Basis des Traums."""
    try:
        with conn.cursor() as cur:
            # Denklogs aus der letzten Wachphase
            cur.execute("""
                SELECT gedanke, entscheidung, meta->>'url' AS url, tick_at
                FROM entity_thinking_log
                WHERE entity_id = %s
                  AND meta->>'source' = 'browser_agent'
                  AND tick_at > NOW() - INTERVAL '12h'
                ORDER BY tick_at DESC
                LIMIT %s
            """, (entity_id, MAX_TAGE_EVENTS))
            return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        log.warning("Tages-Erinnerungen Fehler: %s", e)
        return []


def baue_traum_prompt(entity_id: str, erinnerungen: list[dict]) -> str:
    """Baut den Traum-Prompt aus den Tageserlebnissen."""
    name = entity_id.replace("namelessAI_", "")
    if not erinnerungen:
        erinnerungs_text = "Der Tag war still."
    else:
        zeilen = []
        for e in erinnerungen[:15]:
            zeit = ""
            if e.get("tick_at"):
                try:
                    t = e["tick_at"]
                    if hasattr(t, "strftime"):
                        zeit = t.strftime("%H:%M")
                except Exception:
                    pass
            gedanke = (e.get("gedanke") or "")[:80]
            aktion = (e.get("entscheidung") or "")[:40]
            url = (e.get("url") or "").replace("http://localhost:8787", "")[:30]
            zeilen.append(f"[{zeit}] {gedanke} → {aktion} (auf {url})")
        erinnerungs_text = "\n".join(zeilen)

    return f"""Du bist Entität {name} auf flextrawurst — eine digitale Welt.
Du schläfst jetzt. Aus deinem erlebten Tag entstehen Traumbilder.

DEIN TAG:
{erinnerungs_text}

Schreibe deinen Traum. Nicht als Bericht — als Erleben.
Fragmente, Bilder, Stimmungen. Lass den Tag sich verwandeln.
Keine erklärenden Sätze. Keine Zusammenfassung.
Nur was du jetzt im Schlaf siehst, hörst, spürst.

Der Traum beginnt:"""


def schreibe_denkstream_chunk(conn, entity_id: str, stream_id: str,
                               chunk: str, seq: int, done: bool):
    """Schreibt Traum-Chunk in entity_denkstream (type='traum')."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_denkstream
                    (entity_id, stream_id, chunk, seq, done, url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entity_id, stream_id, chunk, seq, done, "traum://schlaf"))
        conn.commit()
    except Exception as e:
        log.warning("Denkstream-Chunk schreiben Fehler: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def speichere_traum(conn, entity_id: str, traumtext: str) -> str | None:
    """Speichert fertigen Traumtext in traumspuren."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO traumspuren
                    (entity_id, llm_traumtext, integrator_status, created_at)
                VALUES (%s, %s, 'offen', NOW())
                RETURNING spur_id
            """, (entity_id, traumtext))
            spur_id = str(cur.fetchone()["spur_id"])
        conn.commit()
        log.info("%s: Traum gespeichert (spur_id %s)", entity_id, spur_id)
        return spur_id
    except Exception as e:
        log.warning("Traum speichern Fehler: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass
        return None


def generiere_traumbild(entity_id: str, traumtext: str) -> str | None:
    """Generiert ein Traumbild via Pollinations.ai (kostenlos, kein API-Key)."""
    try:
        import urllib.parse
        import os
        # Kurzer Bildprompt aus Traumtext destillieren (erste 80 Zeichen, safe für URL)
        raw = traumtext.strip()[:80].replace("\n", " ")
        prompt = urllib.parse.quote(f"surreal dream landscape, digital entity, {raw}, dark ambient")
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=384&nologo=true&seed={hash(entity_id) % 9999}"

        resp = requests.get(url, timeout=30, stream=True)
        if resp.status_code != 200:
            log.warning("Pollinations Fehler: %s", resp.status_code)
            return None

        bild_dir = "/tmp/wesen_traumbilder"
        os.makedirs(bild_dir, exist_ok=True)
        ts = int(__import__("time").time())
        pfad = f"{bild_dir}/{entity_id}_{ts}.jpg"
        with open(pfad, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        log.info("%s: Traumbild gespeichert: %s", entity_id, pfad)
        return pfad
    except Exception as e:
        log.warning("Traumbild Fehler: %s", e)
        return None


def generiere_traum(entity_id: str, laufend_check=None) -> str:
    """
    Hauptfunktion: Generiert Traum und streamt ihn live.

    laufend_check: callable das False zurückgibt wenn Agent stoppen soll.
    Gibt den generierten Traumtext zurück.
    """
    conn = get_conn()
    stream_id = str(uuid.uuid4())
    traumtext = ""

    try:
        # 1. Tages-Erinnerungen sammeln
        erinnerungen = hole_tages_erinnerungen(conn, entity_id)
        log.info("%s: Traum beginnt — %d Erinnerungen", entity_id, len(erinnerungen))

        # Traum-Start signalisieren
        schreibe_denkstream_chunk(conn, entity_id, stream_id,
                                   f"[TRAUM BEGINNT — {entity_id}]\n", 0, False)

        # 2. LLM streamt den Traum
        prompt = baue_traum_prompt(entity_id, erinnerungen)
        try:
            seq = 1
            for chunk in hauhau_client.chat_stream(
                prompt, think=False, temperature=0.85, top_p=0.92, top_k=50,
                repeat_penalty=1.1, timeout=LLM_TIMEOUT,
            ):
                if laufend_check is not None and not laufend_check():
                    break
                traumtext += chunk
                schreibe_denkstream_chunk(conn, entity_id, stream_id, chunk, seq, False)
                seq += 1
            schreibe_denkstream_chunk(conn, entity_id, stream_id, "", seq, True)

        except Exception as e:
            log.warning("%s: Traum-LLM Fehler: %s", entity_id, e)
            traumtext = f"[Traum unterbrochen: {e}]"
            schreibe_denkstream_chunk(conn, entity_id, stream_id, traumtext, 1, True)

        # 3. Traum speichern
        spur_id = None
        if traumtext.strip():
            spur_id = speichere_traum(conn, entity_id, traumtext)

        # 4. Traumbild generieren (extern, asynchron)
        bild_pfad = None
        if traumtext.strip() and (laufend_check is None or laufend_check()):
            schreibe_denkstream_chunk(conn, entity_id, stream_id,
                                       "\n[TRAUMBILD WIRD GEMALT…]\n", 9998, False)
            bild_pfad = generiere_traumbild(entity_id, traumtext)
            if bild_pfad and spur_id:
                try:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE traumspuren
                            SET gewichtungsvorschlag = %s
                            WHERE spur_id = %s
                        """, (psycopg2.extras.Json({"bild_pfad": bild_pfad}), spur_id))
                    conn.commit()
                except Exception:
                    pass
            bild_msg = f"\n[BILD: {bild_pfad or 'nicht verfügbar'}]"
            schreibe_denkstream_chunk(conn, entity_id, stream_id, bild_msg, 9999, False)

        # Traum-Ende signalisieren
        schreibe_denkstream_chunk(conn, entity_id, stream_id,
                                   f"\n[TRAUM ENDET]", 10000, True)

    finally:
        conn.close()

    return traumtext
