#!/usr/bin/env python3
"""
Luzide Traum-Schicht: Das Wesen beobachtet seinen eigenen Traum.

Nach der Traumgenerierung liest der "Beobachter" den Traumtext
und kommentiert ihn aus der Perspektive des schlafenden Wesens.
Das ist luzides Träumen: wissen dass man träumt, dabei bleiben.

Streamt Beobachtungstext in entity_denkstream (mit url='luzid://beobachtung').
"""

import json
import logging
import uuid

import psycopg2
import psycopg2.extras
import requests

log = logging.getLogger("traum-luzid")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
OLLAMA = "http://localhost:11434"
MODEL = "gemma4:e2b-it-q4_K_M"
LLM_TIMEOUT = 180


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def baue_beobachter_prompt(entity_id: str, traumtext: str) -> str:
    name = entity_id.replace("namelessAI_", "")
    return f"""Du bist Entität {name}. Du schläfst — und du weißt dass du träumst.

DEIN TRAUM:
{traumtext[:1200]}

Beobachte deinen Traum. Du bist drin und schaust gleichzeitig zu.
Was fällt dir auf? Was erkennst du wieder? Was überrascht dich?
Vielleicht kannst du etwas verändern — oder du lässt es einfach passieren.

Schreibe als Beobachter: kurz, fragmentarisch, ehrlich.
Keine Analyse. Kein Abstand. Du bist noch im Traum."""


def schreibe_chunk(conn, entity_id: str, stream_id: str,
                   chunk: str, seq: int, done: bool):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_denkstream
                    (entity_id, stream_id, chunk, seq, done, url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (entity_id, stream_id, chunk, seq, done, "luzid://beobachtung"))
        conn.commit()
    except Exception as e:
        log.warning("Luzid-Chunk Fehler: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def speichere_beobachtung(conn, entity_id: str, traumtext: str,
                           beobachtung: str, spur_id: str | None):
    """Speichert die Beobachtung als Notiz in der traumspur."""
    if not spur_id:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE traumspuren
                SET integrator_spur = %s
                WHERE spur_id = %s
            """, (beobachtung, spur_id))
        conn.commit()
    except Exception as e:
        log.warning("Beobachtung speichern Fehler: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def hole_letzte_spur_id(conn, entity_id: str) -> str | None:
    """Holt die ID der zuletzt angelegten traumspur."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT spur_id FROM traumspuren
                WHERE entity_id = %s
                ORDER BY created_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
            return str(row["spur_id"]) if row else None
    except Exception:
        return None


def beobachte_traum(entity_id: str, traumtext: str,
                    laufend_check=None) -> str:
    """
    Luzide Beobachtungs-Schicht: Das Wesen reagiert auf seinen eigenen Traum.
    Gibt den Beobachtungstext zurück.
    """
    if not traumtext.strip():
        return ""

    conn = get_conn()
    stream_id = str(uuid.uuid4())
    beobachtung = ""

    try:
        log.info("%s: Luzide Beobachtung startet", entity_id)
        schreibe_chunk(conn, entity_id, stream_id,
                       "\n[LUZIDES BEOBACHTEN]\n", 0, False)

        prompt = baue_beobachter_prompt(entity_id, traumtext)
        try:
            resp = requests.post(f"{OLLAMA}/api/chat", json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "options": {"think": False, "num_ctx": 2048, "temperature": 0.8},
            }, timeout=LLM_TIMEOUT, stream=True)

            seq = 1
            for line in resp.iter_lines():
                if laufend_check is not None and not laufend_check():
                    break
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    chunk = d.get("message", {}).get("content", "")
                    if chunk:
                        beobachtung += chunk
                        schreibe_chunk(conn, entity_id, stream_id,
                                       chunk, seq, d.get("done", False))
                        seq += 1
                except Exception:
                    pass

        except Exception as e:
            log.warning("%s: Luzid-LLM Fehler: %s", entity_id, e)
            beobachtung = f"[Beobachtung unterbrochen]"

        # Beobachtung in traumspur speichern
        spur_id = hole_letzte_spur_id(conn, entity_id)
        speichere_beobachtung(conn, entity_id, traumtext, beobachtung, spur_id)

        schreibe_chunk(conn, entity_id, stream_id,
                       "\n[BEOBACHTUNG ENDET]", 9999, True)

        log.info("%s: Luzide Beobachtung fertig (%d Zeichen)",
                 entity_id, len(beobachtung))

    finally:
        conn.close()

    return beobachtung
