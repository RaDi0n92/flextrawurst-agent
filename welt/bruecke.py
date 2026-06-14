#!/usr/bin/env python3
"""Brücke: liest Selbstmodell-JSONs und synchronisiert mit PostgreSQL."""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras

SELBSTMODELLE_DIR = Path("/root/werkraum/innenleben/selbstmodelle")
LOGS_DIR = Path("/root/werkraum/logs")
LOG_FILE = LOGS_DIR / "bruecke.log"

WESEN = [
    "namelessAI_1234",
    "namelessAI_1324",
    "namelessAI_1423",
    "namelessAI_2341",
    "namelessAI_3123",
    "namelessAI_4321",
]

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
SYNC_INTERVALL = 30


def setup_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [bruecke] %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(),
        ],
    )


def lade_selbstmodell(entity_id: str) -> dict | None:
    pfad = SELBSTMODELLE_DIR / f"self_model_{entity_id}.json"
    if not pfad.exists():
        return None
    try:
        return json.loads(pfad.read_text())
    except Exception as e:
        logging.warning(f"Fehler beim Lesen von {pfad}: {e}")
        return None


def hole_aktuellen_zustand(cur, entity_id: str) -> dict | None:
    cur.execute(
        "SELECT stimmung, version FROM entity_states WHERE entity_id = %s",
        (entity_id,),
    )
    row = cur.fetchone()
    if row:
        return {"stimmung": row[0], "version": row[1]}
    return None


def upsert_entity_state(cur, entity_id: str, modell: dict):
    state = modell.get("current_state", {})
    sym = modell.get("symbolic_self_image", {})
    now = datetime.now(timezone.utc)

    last_ref_raw = modell.get("last_reflection_time")
    last_ref = None
    if last_ref_raw:
        try:
            last_ref = datetime.fromisoformat(last_ref_raw)
        except ValueError:
            pass

    cur.execute(
        """
        INSERT INTO entity_states
            (entity_id, stimmung, fokus, version, core, tendencies,
             relationships, symbolic_image_id, last_reflection_time,
             raw_model, visibility, updated_at)
        VALUES
            (%(entity_id)s, %(stimmung)s, %(fokus)s, %(version)s,
             %(core)s, %(tendencies)s, %(relationships)s,
             %(symbolic_image_id)s, %(last_reflection_time)s,
             %(raw_model)s, 'internal', %(updated_at)s)
        ON CONFLICT (entity_id) DO UPDATE SET
            stimmung             = EXCLUDED.stimmung,
            fokus                = EXCLUDED.fokus,
            version              = EXCLUDED.version,
            core                 = EXCLUDED.core,
            tendencies           = EXCLUDED.tendencies,
            relationships        = EXCLUDED.relationships,
            symbolic_image_id    = EXCLUDED.symbolic_image_id,
            last_reflection_time = EXCLUDED.last_reflection_time,
            raw_model            = EXCLUDED.raw_model,
            updated_at           = EXCLUDED.updated_at
        """,
        {
            "entity_id": entity_id,
            "stimmung": state.get("stimmung"),
            "fokus": state.get("fokus"),
            "version": modell.get("version"),
            "core": json.dumps(modell.get("core", {})),
            "tendencies": json.dumps(modell.get("tendencies", {})),
            "relationships": json.dumps(modell.get("relationships", {})),
            "symbolic_image_id": sym.get("image_id"),
            "last_reflection_time": last_ref,
            "raw_model": json.dumps(modell),
            "updated_at": now,
        },
    )


def schreibe_event(cur, event_type: str, entity_id: str, payload: dict,
                   origin_type: str = "innenleben_sync"):
    cur.execute(
        """
        INSERT INTO events
            (event_type, actor_type, actor_id, payload,
             origin_type, visibility_layer)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            event_type,
            "nameless_ai",
            entity_id,
            json.dumps(payload),
            origin_type,
            "internal",
        ),
    )


def sync_zyklus(conn):
    with conn.cursor() as cur:
        geaendert = 0
        for entity_id in WESEN:
            modell = lade_selbstmodell(entity_id)
            if modell is None:
                logging.warning(f"Kein Selbstmodell für {entity_id}")
                continue

            alter_zustand = hole_aktuellen_zustand(cur, entity_id)
            neue_stimmung = modell.get("current_state", {}).get("stimmung")
            neue_version = modell.get("version")

            upsert_entity_state(cur, entity_id, modell)

            if alter_zustand is None:
                logging.info(f"{entity_id}: neu eingetragen (v{neue_version})")
            else:
                alte_stimmung = alter_zustand["stimmung"]
                alte_version = alter_zustand["version"]

                if alte_stimmung != neue_stimmung:
                    schreibe_event(cur, "wesen.stimmung_wechsel", entity_id, {
                        "alt": alte_stimmung,
                        "neu": neue_stimmung,
                        "version": neue_version,
                    })
                    logging.info(f"{entity_id}: Stimmung {alte_stimmung!r} → {neue_stimmung!r}")
                    geaendert += 1

                if alte_version != neue_version:
                    schreibe_event(cur, "wesen.reflexion_abgeschlossen", entity_id, {
                        "alt": alte_version,
                        "neu": neue_version,
                        "stimmung": neue_stimmung,
                    })
                    logging.info(f"{entity_id}: Version {alte_version} → {neue_version}")
                    geaendert += 1

        schreibe_event(cur, "system.bruecken_sync", "system", {
            "wesen_gelesen": len(WESEN),
            "aenderungen": geaendert,
        }, origin_type="live_world")

        conn.commit()
        logging.info(f"Sync abgeschlossen — {geaendert} Änderungen")


def main():
    setup_logging()
    logging.info("Brücke startet")

    while True:
        try:
            conn = psycopg2.connect(DB_URI)
            psycopg2.extras.register_uuid()
            logging.info("DB verbunden")

            while True:
                try:
                    sync_zyklus(conn)
                except Exception as e:
                    logging.error(f"Sync-Fehler: {e}")
                    conn.rollback()
                time.sleep(SYNC_INTERVALL)

        except KeyboardInterrupt:
            logging.info("Brücke gestoppt")
            break
        except Exception as e:
            logging.error(f"Verbindungsfehler: {e} — Neustart in 10s")
            time.sleep(10)


if __name__ == "__main__":
    main()
