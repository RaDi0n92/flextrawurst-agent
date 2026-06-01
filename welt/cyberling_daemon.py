#!/usr/bin/env python3
"""
Cyberling-Daemon: Verwaltet Bedürfnisse, Tod und Wiedergeburt aller Cyberlinge.

Kaskade:
  Durst    → fällt schnell (pausiert während Entität schläft)
  Hunger   → fällt langsamer
  ↓ (beide niedrig)
  Energie  → sinkt (normal + kaskade)
  Stimmung → sinkt parallel
  ↓ (immer noch unbehandelt)
  Gesundheit → schwindet → Tod → nach 24h Wiedergeburt

Profile: leicht / mittel / hart — pro Cyberling in DB konfigurierbar.
Zustände: gesund → hungrig/durstig → müde → erschöpft → krank → kritisch → tot
"""

import time
import logging
import math
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

# ─── Profil-Parameter (0-1 Skala, pro Stunde) ─────────────────────────────────

PROFILE = {
    "leicht": {
        "durst_pro_h": 0.05,          # leer in ~20h
        "hunger_pro_h": 0.03,         # leer in ~33h
        "energie_abfall_normal": 0.005,
        "energie_abfall_kaskade": 0.04,
        "stimmung_abfall_kaskade": 0.03,
        "gesundheit_abfall": 0.02,
        "kaskade_schwelle": 0.35,
        "gesundheit_schwelle": 0.25,
        "energie_regen_h": 0.02,
        "gesundheit_regen_h": 0.015,
        "stimmung_regen_h": 0.015,
        "energie_basisrauschen": 0.01,
        "recovery_schwelle_hunger": 0.70,
        "recovery_schwelle_durst": 0.70,
        "recovery_energie_fuer_stimmung": 0.40,
        "tod_moeglich": False,
    },
    "mittel": {
        "durst_pro_h": 0.18,          # leer in ~5.5h
        "hunger_pro_h": 0.12,         # leer in ~8h
        "energie_abfall_normal": 0.01,
        "energie_abfall_kaskade": 0.08,
        "stimmung_abfall_kaskade": 0.06,
        "gesundheit_abfall": 0.04,
        "kaskade_schwelle": 0.40,
        "gesundheit_schwelle": 0.30,
        "energie_regen_h": 0.015,
        "gesundheit_regen_h": 0.008,
        "stimmung_regen_h": 0.01,
        "energie_basisrauschen": 0.02,
        "recovery_schwelle_hunger": 0.75,
        "recovery_schwelle_durst": 0.75,
        "recovery_energie_fuer_stimmung": 0.50,
        "tod_moeglich": True,
    },
    "hart": {
        "durst_pro_h": 0.18,
        "hunger_pro_h": 0.12,
        "energie_abfall_normal": 0.02,
        "energie_abfall_kaskade": 0.12,
        "stimmung_abfall_kaskade": 0.08,
        "gesundheit_abfall": 0.03,
        "kaskade_schwelle": 0.40,
        "gesundheit_schwelle": 0.35,
        "energie_regen_h": 0.005,
        "gesundheit_regen_h": 0.003,
        "stimmung_regen_h": 0.004,
        "energie_basisrauschen": 0.03,
        "recovery_schwelle_hunger": 0.80,
        "recovery_schwelle_durst": 0.80,
        "recovery_energie_fuer_stimmung": 0.60,
        "tod_moeglich": True,
    },
}

REVIVAL_NACH_H = 24

# Zustands-Schwellen (0-1 Skala)
ZUSTAND_THRESHOLDS = [
    ("kritisch", lambda h, d, e, s, g: g < 0.20),
    ("krank",    lambda h, d, e, s, g: g < 0.50),
    ("erschöpft", lambda h, d, e, s, g: e < 0.20),
    ("muede",    lambda h, d, e, s, g: e < 0.50),
    ("hungrig",  lambda h, d, e, s, g: h < 0.20),
    ("durstig",  lambda h, d, e, s, g: d < 0.20),
    ("gesund",   lambda h, d, e, s, g: True),
]


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def entity_schlaeft(cur, entity_id: str) -> bool:
    cur.execute(
        "SELECT status FROM entity_slots WHERE entity_id = %s",
        (entity_id,),
    )
    row = cur.fetchone()
    return row["status"] == "schläft" if row else False


def berechne_zustand(hunger, durst, energie, stimmung, gesundheit) -> str:
    for name, check in ZUSTAND_THRESHOLDS:
        if check(hunger, durst, energie, stimmung, gesundheit):
            return name
    return "gesund"


def get_profile_params(profil: str) -> dict:
    return PROFILE.get(profil, PROFILE["mittel"])


def tick_cyberling(c: dict, stunden: float):
    """Berechnet neue Zustände für einen Cyberling. Gibt dict mit Updates zurück."""
    p = get_profile_params(c.get("profil", "mittel"))

    hunger     = c["hunger"]
    durst      = c["durst"]
    energie    = c["energie"]
    stimmung   = c["stimmung"]
    gesundheit = c["gesundheit"]

    # Grundverfall
    durst  = max(0.0, durst  - p["durst_pro_h"]  * stunden)
    hunger = max(0.0, hunger - p["hunger_pro_h"] * stunden)

    kaskade_aktiv = hunger < p["kaskade_schwelle"] and durst < p["kaskade_schwelle"]
    recovery_aktiv = (
        hunger >= p["recovery_schwelle_hunger"]
        and durst >= p["recovery_schwelle_durst"]
    )

    # ── Energie ──
    if kaskade_aktiv:
        energie = max(0.0, energie - p["energie_abfall_kaskade"] * stunden)
    else:
        # Normaler Abfall + Rauschen
        energie = max(0.0, energie - p["energie_abfall_normal"] * stunden)
        rauschen = p["energie_basisrauschen"] * math.sin(time.time() * 0.1) * stunden
        energie = max(0.0, min(1.0, energie + rauschen))
        # Recovery
        if recovery_aktiv and energie < 1.0:
            energie = min(1.0, energie + p["energie_regen_h"] * stunden)

    # ── Stimmung ──
    if hunger < p["kaskade_schwelle"] or durst < p["kaskade_schwelle"]:
        stimmung = max(0.0, stimmung - p["stimmung_abfall_kaskade"] * stunden)
    elif recovery_aktiv and energie >= p["recovery_energie_fuer_stimmung"] and stimmung < 1.0:
        stimmung = min(1.0, stimmung + p["stimmung_regen_h"] * stunden)

    # ── Gesundheit ──
    if energie < p["gesundheit_schwelle"]:
        gesundheit = max(0.0, gesundheit - p["gesundheit_abfall"] * stunden)
    elif recovery_aktiv and gesundheit < 1.0:
        gesundheit = min(1.0, gesundheit + p["gesundheit_regen_h"] * stunden)

    # Zustand berechnen
    zustand = berechne_zustand(hunger, durst, energie, stimmung, gesundheit)

    return {
        "hunger": round(hunger, 4),
        "durst": round(durst, 4),
        "energie": round(energie, 4),
        "stimmung": round(stimmung, 4),
        "gesundheit": round(gesundheit, 4),
        "zustand": zustand,
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
            hunger = 0, durst = 0, energie = 0, stimmung = 0,
            zustand = 'tot'
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
        "profil": c.get("profil", "mittel"),
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
            zustand = 'gesund',
            letzte_interaktion = NOW()
        WHERE id = %s
    """, (c["id"],))

    cur.execute("""
        INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
        VALUES ('cyberling.erwacht', 'entity', %s, %s, 'system', 'internal')
    """, (c["entity_id"], psycopg2.extras.Json({
        "cyberling_id": str(c["id"]),
        "tode_bisher": c["tode"],
        "profil": c.get("profil", "mittel"),
    })))
    log.info(f"Cyberling von {c['entity_id']} erwacht nach Tod #{c['tode']}")


def event_zustandswechsel(cur, c: dict, alter_zustand: str, neuer_zustand: str):
    if alter_zustand == neuer_zustand:
        return
    cur.execute("""
        INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
        VALUES ('cyberling.zustand_geaendert', 'entity', %s, %s, 'system', 'internal')
    """, (c["entity_id"], psycopg2.extras.Json({
        "cyberling_id": str(c["id"]),
        "von": alter_zustand,
        "nach": neuer_zustand,
        "profil": c.get("profil", "mittel"),
        "werte": {
            "hunger": c["hunger"],
            "durst": c["durst"],
            "energie": c["energie"],
            "stimmung": c["stimmung"],
            "gesundheit": c["gesundheit"],
        },
    })))
    log.info(f"Cyberling von {c['entity_id']}: {alter_zustand} → {neuer_zustand}")


def main():
    log.info("Cyberling-Daemon startet")
    letzter_tick: dict[str, datetime] = {}

    # letzter_tick aus DB laden (Provenienz-Sicherung)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, letzter_tick FROM cyberlinge WHERE letzter_tick IS NOT NULL")
            for row in cur.fetchall():
                letzter_tick[str(row["id"])] = row["letzter_tick"].replace(tzinfo=timezone.utc)
        log.info(f"letzter_tick geladen für {len(letzter_tick)} Cyberlinge")
    except Exception as e:
        log.warning(f"Konnte letzter_tick nicht laden: {e}")
    finally:
        conn.close()

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

                    alter_zustand = c.get("zustand", "gesund")
                    neue = tick_cyberling(c, stunden)

                    cur.execute("""
                        UPDATE cyberlinge SET
                            hunger = %s, durst = %s, energie = %s,
                            stimmung = %s, gesundheit = %s, zustand = %s
                        WHERE id = %s
                    """, (
                        neue["hunger"], neue["durst"], neue["energie"],
                        neue["stimmung"], neue["gesundheit"], neue["zustand"], c["id"],
                    ))

                    # Zustandswechsel-Event
                    event_zustandswechsel(cur, c, alter_zustand, neue["zustand"])

                    # Tod einleiten wenn Gesundheit 0
                    p = get_profile_params(c.get("profil", "mittel"))
                    if neue["gesundheit"] <= 0 and p["tod_moeglich"]:
                        cyberling_stirbt(cur, c)

                    conn.commit()

                # letzter_tick persistieren (unabhängig vom Zustand)
                if cid in letzter_tick:
                    with conn.cursor() as cur2:
                        cur2.execute(
                            "UPDATE cyberlinge SET letzter_tick = %s WHERE id = %s",
                            (letzter_tick[cid], c["id"]),
                        )
                        conn.commit()

        except Exception as e:
            log.error(f"Tick-Fehler: {e}")
        finally:
            conn.close()

        time.sleep(TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
