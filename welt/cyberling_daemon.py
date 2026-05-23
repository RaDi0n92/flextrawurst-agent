#!/usr/bin/env python3
"""
Cyberling-Daemon: Verwaltet Bedürfnisse, Tod und Wiedergeburt aller Cyberlinge.

Kaskade:
  Durst    → fällt schnell (pausiert während Entität schläft)
  Hunger   → fällt langsamer
  ↓ (beide niedrig)
  Energie  → sinkt
  Stimmung → sinkt parallel
  ↓ (immer noch unbehandelt)
  Gesundheit → schwindet → Tod → nach 24h Wiedergeburt
"""

import time
import logging
from datetime import datetime, timezone, timedelta

import psycopg2
import psycopg2.extras

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("cyberling")

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
TICK_SEKUNDEN = 300  # alle 5 Minuten

# Verfallsraten pro Stunde (1.0 = voll, 0.0 = leer)
DURST_PRO_H    = 0.10   # leer in ~10h aktiver Zeit
HUNGER_PRO_H   = 0.05   # leer in ~20h aktiver Zeit

# Kaskaden-Schwellen
KASKADE_SCHWELLE  = 0.4   # unter dieser Schwelle bei hunger+durst → energie+stimmung sinken
STIMMUNG_SCHWELLE = 0.5   # unter dieser Schwelle bei hunger ODER durst → stimmung sinkt
GESUNDHEIT_SCHWELLE = 0.3  # unter dieser energie → gesundheit sinkt

ENERGIE_PRO_H_KASKADE    = 0.08
STIMMUNG_PRO_H_KASKADE   = 0.06
GESUNDHEIT_PRO_H_KASKADE = 0.04

REVIVAL_NACH_H = 24


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def entity_schlaeft(cur, entity_id: str) -> bool:
    cur.execute(
        "SELECT status FROM entity_slots WHERE entity_id = %s",
        (entity_id,),
    )
    row = cur.fetchone()
    return row["status"] == "schläft" if row else False


def tick_cyberling(cur, c: dict, stunden: float):
    """Berechnet neue Zustände für einen Cyberling. Gibt dict mit Updates zurück."""
    hunger     = c["hunger"]
    durst      = c["durst"]
    energie    = c["energie"]
    stimmung   = c["stimmung"]
    gesundheit = c["gesundheit"]

    # Grundverfall
    durst  = max(0.0, durst  - DURST_PRO_H  * stunden)
    hunger = max(0.0, hunger - HUNGER_PRO_H * stunden)

    # Energie-Kaskade
    if hunger < KASKADE_SCHWELLE and durst < KASKADE_SCHWELLE:
        energie = max(0.0, energie - ENERGIE_PRO_H_KASKADE * stunden)

    # Stimmungs-Kaskade
    if hunger < STIMMUNG_SCHWELLE or durst < STIMMUNG_SCHWELLE:
        stimmung = max(0.0, stimmung - STIMMUNG_PRO_H_KASKADE * stunden)

    # Gesundheits-Kaskade
    if energie < GESUNDHEIT_SCHWELLE:
        gesundheit = max(0.0, gesundheit - GESUNDHEIT_PRO_H_KASKADE * stunden)

    return {
        "hunger": round(hunger, 4),
        "durst": round(durst, 4),
        "energie": round(energie, 4),
        "stimmung": round(stimmung, 4),
        "gesundheit": round(gesundheit, 4),
    }


def cyberling_stirbt(cur, c: dict):
    jetzt = datetime.now(timezone.utc)
    lebensbeginn = c["lebensbeginn_at"].replace(tzinfo=timezone.utc)
    lebensdauer_min = int((jetzt - lebensbeginn).total_seconds() / 60)
    neuer_rekord = max(c["rekord_min"], lebensdauer_min)

    cur.execute("""
        UPDATE cyberlinge SET
            status = 'tot',
            tod_at = NOW(),
            tode = tode + 1,
            rekord_min = %s,
            gesundheit = 0,
            hunger = 0, durst = 0, energie = 0, stimmung = 0
        WHERE id = %s
    """, (neuer_rekord, c["id"]))

    cur.execute("""
        INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
        VALUES ('cyberling.gestorben', 'entity', %s, %s, 'system', 'internal')
    """, (c["entity_id"], psycopg2.extras.Json({
        "cyberling_id": str(c["id"]),
        "lebensdauer_min": lebensdauer_min,
        "tode_gesamt": c["tode"] + 1,
        "neuer_rekord": neuer_rekord > c["rekord_min"],
    })))
    log.info(f"Cyberling von {c['entity_id']} gestorben — Leben: {lebensdauer_min}min, Rekord: {neuer_rekord}min")


def cyberling_erwacht(cur, c: dict):
    cur.execute("""
        UPDATE cyberlinge SET
            status = 'lebendig',
            tod_at = NULL,
            lebensbeginn_at = NOW(),
            zuletzt_belebt = NOW(),
            hunger = 1.0, durst = 1.0, energie = 1.0,
            stimmung = 0.7, gesundheit = 1.0,
            letzte_interaktion = NOW()
        WHERE id = %s
    """, (c["id"],))

    cur.execute("""
        INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
        VALUES ('cyberling.erwacht', 'entity', %s, %s, 'system', 'internal')
    """, (c["entity_id"], psycopg2.extras.Json({
        "cyberling_id": str(c["id"]),
        "tode_bisher": c["tode"],
    })))
    log.info(f"Cyberling von {c['entity_id']} erwacht nach Tod #{c['tode']}")


def main():
    log.info("Cyberling-Daemon startet")
    letzter_tick: dict[str, datetime] = {}

    while True:
        jetzt = datetime.now(timezone.utc)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cyberlinge")
                alle = cur.fetchall()

            for c in alle:
                cid = str(c["id"])

                with conn.cursor() as cur:
                    # Toter Cyberling: Wiedergeburt nach 24h prüfen
                    if c["status"] == "tot":
                        if c["tod_at"]:
                            tod_at = c["tod_at"].replace(tzinfo=timezone.utc)
                            if (jetzt - tod_at).total_seconds() >= REVIVAL_NACH_H * 3600:
                                cyberling_erwacht(cur, c)
                                conn.commit()
                        continue

                    # Schläft die Entität? → kein Verfall
                    if entity_schlaeft(cur, c["entity_id"]):
                        letzter_tick[cid] = jetzt
                        continue

                    # Stunden seit letztem Tick
                    seit = letzter_tick.get(cid)
                    if seit is None:
                        letzter_tick[cid] = jetzt
                        continue
                    stunden = (jetzt - seit).total_seconds() / 3600
                    letzter_tick[cid] = jetzt

                    if stunden <= 0:
                        continue

                    neue = tick_cyberling(cur, c, stunden)
                    cur.execute("""
                        UPDATE cyberlinge SET
                            hunger = %s, durst = %s, energie = %s,
                            stimmung = %s, gesundheit = %s
                        WHERE id = %s
                    """, (
                        neue["hunger"], neue["durst"], neue["energie"],
                        neue["stimmung"], neue["gesundheit"], c["id"],
                    ))

                    # Tod einleiten wenn Gesundheit 0
                    if neue["gesundheit"] <= 0:
                        cyberling_stirbt(cur, c)

                    conn.commit()

        except Exception as e:
            log.error(f"Tick-Fehler: {e}")
        finally:
            conn.close()

        time.sleep(TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
