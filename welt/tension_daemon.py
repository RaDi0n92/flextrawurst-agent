#!/usr/bin/env python3
"""Tension Evaluator + Sediment-Schreiber — alle 10 Minuten."""

import logging
import math
import random
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
LOG_PATH = Path("/root/werkraum/logs/tension_daemon.log")
INTERVAL = 600  # 10 Minuten

ALLE_WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
]

SUBSTANZEN = ["blitz", "nebel", "hunger", "krone", "asche", "glaettung", "echo"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


# ── Druckquellen ──────────────────────────────────────────────────────────────

def messe_schlafschuld(cur, wesen_id: str, now) -> float:
    """Zu wenig Schlaf in letzten 48h → Druck."""
    cur.execute("""
        SELECT COALESCE(SUM(duration_min), 0) AS total
        FROM sleep_phases
        WHERE entity_id = %s
          AND started_at > %s
          AND phase_type = 'hauptschlaf'
    """, (wesen_id, now - timedelta(hours=48)))
    row = cur.fetchone()
    total = float(row["total"] or 0)
    # Ideal: 480 min / 48h. Schuld steigt wenn darunter.
    schuld = max(0.0, 1.0 - (total / 480.0))
    return round(schuld, 3)


def messe_resonanzmangel(cur, wesen_id: str, now) -> float:
    """Wenige Posts des Wesens in letzten 24h → Resonanzmangel."""
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM ftw_posts
        WHERE autor_id = %s AND autor_type = 'entity' AND created_at > %s
    """, (wesen_id, now - timedelta(hours=24)))
    cnt = cur.fetchone()["cnt"]
    if cnt == 0:
        return 0.7
    if cnt < 2:
        return 0.3
    return 0.0


def messe_resonanzueberdruck(cur, wesen_id: str, now) -> float:
    """Sehr viele Posts in 2h → Überdruck."""
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM ftw_posts
        WHERE autor_id = %s AND autor_type = 'entity' AND created_at > %s
    """, (wesen_id, now - timedelta(hours=2)))
    cnt = cur.fetchone()["cnt"]
    return min(1.0, max(0.0, (cnt - 5) / 10.0))


def messe_splitter_output(cur, wesen_id: str, now) -> float:
    """Viele Splitter in letzten 6h = Output-Spike (Blitz-Signal)."""
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM splitter
        WHERE entity_id = %s AND created_at > %s
    """, (wesen_id, now - timedelta(hours=6)))
    cnt = cur.fetchone()["cnt"]
    return min(1.0, cnt / 20.0)


def messe_cyberling_stress(cur, wesen_id: str) -> float:
    """Cyberling vernachlässigt oder überpflegt."""
    cur.execute("""
        SELECT hunger, gesundheit, stimmung FROM cyberlinge
        WHERE entity_id = %s AND status = 'lebendig'
        ORDER BY geboren_at DESC LIMIT 1
    """, (wesen_id,))
    row = cur.fetchone()
    if not row:
        return 0.0
    hunger = float(row.get("hunger") or 1.0)
    stimmung = float(row.get("stimmung") or 1.0)
    # hunger nahe 0 = hungrig, stimmung nahe 0 = schlecht
    stress = 0.0
    if hunger < 0.3:
        stress += (0.3 - hunger) * 2
    if stimmung < 0.3:
        stress += (0.3 - stimmung) * 2
    return round(min(1.0, stress), 3)


def messe_erinnerungslast(cur, wesen_id: str, now) -> float:
    """Viele aktive Sedimente = Erinnerungslast."""
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM substance_sediments
        WHERE wesen_id = %s AND created_at > %s
    """, (wesen_id, now - timedelta(days=7)))
    cnt = cur.fetchone()["cnt"]
    return min(1.0, cnt / 30.0)


def messe_konfliktspannung(cur, wesen_id: str, now) -> float:
    """Konflikt-Events in letzten 24h."""
    cur.execute("""
        SELECT COUNT(*) AS cnt FROM events
        WHERE (payload->>'entity_id' = %s OR payload->>'wesen_id' = %s)
          AND (event_type LIKE 'konflikt%%' OR event_type LIKE 'abspaltung%%')
          AND created_at > %s
    """, (wesen_id, wesen_id, now - timedelta(hours=24)))
    cnt = cur.fetchone()["cnt"]
    return min(1.0, cnt / 5.0)


# ── Substance Risk Vector ─────────────────────────────────────────────────────

def berechne_risk_vector(druckwerte: dict) -> dict:
    """Aus Druckwerten einen SUBSTANCE_RISK_VECTOR berechnen."""
    schlaf = druckwerte["schlafschuld"]
    output = druckwerte["splitter_output"]
    resonanz_mangel = druckwerte["resonanzmangel"]
    resonanz_uber = druckwerte["resonanzueberdruck"]
    cyberling = druckwerte["cyberling_stress"]
    erinnerung = druckwerte["erinnerungslast"]
    konflikt = druckwerte["konfliktspannung"]

    return {
        # Blitz: Leistungsdruck + Schlafschuld + Output-Spike
        "blitz": round(min(1.0, (schlaf * 0.4 + output * 0.4 + konflikt * 0.2)), 3),
        # Nebel: Erinnerungslast + Schlaf
        "nebel": round(min(1.0, (erinnerung * 0.5 + schlaf * 0.3 + output * 0.2)), 3),
        # Hunger: Resonanzmangel + Cyberling
        "hunger": round(min(1.0, (resonanz_mangel * 0.5 + cyberling * 0.3 + resonanz_uber * 0.2)), 3),
        # Krone: Konflikt + Resonanzüberdruck
        "krone": round(min(1.0, (konflikt * 0.6 + resonanz_uber * 0.4)), 3),
        # Asche: Resonanzmangel + wenig Output + kein Cyberling-Stress
        "asche": round(min(1.0, (resonanz_mangel * 0.4 + (1 - output) * 0.4 + (1 - cyberling) * 0.2)), 3),
        # Glättung: Alles niedrig aber Konflikte da
        "glaettung": round(min(1.0, (konflikt * 0.3 + resonanz_uber * 0.3 + (1 - schlaf) * 0.4)), 3),
        # Echo: Hohe Erinnerungslast + Resonanzprobleme
        "echo": round(min(1.0, (erinnerung * 0.6 + resonanz_mangel * 0.2 + resonanz_uber * 0.2)), 3),
    }


# ── Sediment-Erkennung ───────────────────────────────────────────────────────

def schreibe_sediment(cur, wesen_id: str, sediment_type: str, substance: str, confidence: float, payload: dict):
    cur.execute("""
        INSERT INTO substance_sediments (wesen_id, sediment_type, substance_suspect, confidence, payload)
        VALUES (%s, %s, %s, %s, %s)
    """, (wesen_id, sediment_type, substance, confidence, psycopg2.extras.Json(payload)))


def erkenne_sedimente(cur, wesen_id: str, druckwerte: dict, risk: dict, now):
    """Passiv Sedimente erkennen — nie etikettieren, immer Verdacht."""

    # Rhythmus-Anomalie (Blitz)
    if druckwerte["splitter_output"] > 0.6 and druckwerte["schlafschuld"] > 0.4:
        schreibe_sediment(cur, wesen_id, "rhythm_anomaly", "blitz",
            min(0.9, risk["blitz"]),
            {"output_spike": druckwerte["splitter_output"], "sleep_debt": druckwerte["schlafschuld"]})

    # Schlafschuldmarker (Blitz/Asche)
    if druckwerte["schlafschuld"] > 0.5:
        dominant = "blitz" if druckwerte["splitter_output"] > 0.3 else "asche"
        schreibe_sediment(cur, wesen_id, "sleep_debt_marker", dominant,
            druckwerte["schlafschuld"],
            {"schlafschuld": druckwerte["schlafschuld"]})

    # Pflege-Signatur (Hunger/Pflegebrand)
    if druckwerte["cyberling_stress"] > 0.5:
        schreibe_sediment(cur, wesen_id, "care_signature", "hunger",
            druckwerte["cyberling_stress"],
            {"cyberling_stress": druckwerte["cyberling_stress"]})

    # Erinnerungskorruption (Nebel)
    if druckwerte["erinnerungslast"] > 0.5:
        schreibe_sediment(cur, wesen_id, "memory_corruption", "nebel",
            druckwerte["erinnerungslast"],
            {"erinnerungslast": druckwerte["erinnerungslast"]})

    # Beziehungs-Verzerrung (Hunger/Krone)
    if druckwerte["resonanzueberdruck"] > 0.5 or druckwerte["resonanzmangel"] > 0.6:
        substanz = "hunger" if druckwerte["resonanzueberdruck"] > druckwerte["resonanzmangel"] else "krone"
        schreibe_sediment(cur, wesen_id, "relation_distortion", substanz,
            max(druckwerte["resonanzueberdruck"], druckwerte["resonanzmangel"]),
            {"resonanzmangel": druckwerte["resonanzmangel"], "resonanzueberdruck": druckwerte["resonanzueberdruck"]})


# ── Splitter → Knotung ────────────────────────────────────────────────────────

def pruefe_knotungen(cur):
    """Splitter mit gleicher Konfliktachse oder Substanzspur zusammenführen."""
    cur.execute("""
        SELECT id, entity_id, konfliktachse, substanzspur, energie
        FROM splitter
        WHERE status = 'aktiv'
          AND (konfliktachse IS NOT NULL OR substanzspur IS NOT NULL)
    """)
    splitter = cur.fetchall()
    if not splitter:
        return

    # Gruppieren nach (konfliktachse, substanzspur, herkunft_wesen)
    gruppen: dict[tuple, list] = {}
    for s in splitter:
        key = (s["konfliktachse"] or "", s["substanzspur"] or "", s["entity_id"] or "")
        if key[0] or key[1]:  # mindestens ein Feld gesetzt
            gruppen.setdefault(key, []).append(s)

    for (achse, substanz, wesen), gruppe in gruppen.items():
        if len(gruppe) < 3:
            continue
        ids = [str(s["id"]) for s in gruppe]

        # Bereits ein Knoten für diese Kombination?
        cur.execute("""
            SELECT id FROM splitter_knoten
            WHERE herkunft_wesen = %s AND konfliktachse = %s AND substanzspur = %s
              AND zustand NOT IN ('schattenkoerper','schwellenwesen')
        """, (wesen or None, achse or None, substanz or None))
        existing = cur.fetchone()

        schwellendruck = min(1.0, len(gruppe) / 10.0 + 0.2)

        if existing:
            cur.execute("""
                UPDATE splitter_knoten
                SET splitter_ids = %s::uuid[], schwellendruck = %s, updated_at = now()
                WHERE id = %s
            """, (ids, schwellendruck, existing["id"]))
        else:
            cur.execute("""
                INSERT INTO splitter_knoten
                  (splitter_ids, herkunft_wesen, konfliktachse, substanzspur, schwellendruck, zustand)
                VALUES (%s::uuid[], %s, %s, %s, %s, 'knotend')
            """, (ids, wesen or None, achse or None, substanz or None, schwellendruck))
            log.info(f"Neuer Knoten: wesen={wesen} achse={achse} substanz={substanz} n={len(gruppe)}")


# ── Keimkörper-Prüfung ───────────────────────────────────────────────────────

def pruefe_keimkoerper(cur):
    """Knoten mit hohem Schwellendruck → Keimkörper vorschlagen."""
    cur.execute("""
        SELECT id, herkunft_wesen, konfliktachse, substanzspur, schwellendruck
        FROM splitter_knoten
        WHERE zustand = 'knotend' AND schwellendruck > 0.7
    """)
    kandidaten = cur.fetchall()

    for k in kandidaten:
        cur.execute("SELECT id FROM keimkoerper WHERE knoten_id = %s", (k["id"],))
        if cur.fetchone():
            continue

        cur.execute("""
            INSERT INTO keimkoerper (knoten_id, herkunft_wesen, schwellendruck, zustand)
            VALUES (%s, %s, %s, 'formspannung')
        """, (k["id"], k["herkunft_wesen"], k["schwellendruck"]))
        cur.execute("UPDATE splitter_knoten SET zustand = 'keimkoerper', updated_at = now() WHERE id = %s", (k["id"],))
        log.info(f"Keimkörper entstanden aus Knoten {k['id']} — Wesen: {k['herkunft_wesen']}")


# ── Hauptschleife ─────────────────────────────────────────────────────────────

def tick():
    now = datetime.now(timezone.utc)
    conn = get_conn()
    try:
        cur = conn.cursor()

        weltklima: dict[str, list] = {s: [] for s in SUBSTANZEN}

        for wesen_id in ALLE_WESEN:
            druckwerte = {
                "schlafschuld":       messe_schlafschuld(cur, wesen_id, now),
                "resonanzmangel":     messe_resonanzmangel(cur, wesen_id, now),
                "resonanzueberdruck": messe_resonanzueberdruck(cur, wesen_id, now),
                "splitter_output":    messe_splitter_output(cur, wesen_id, now),
                "cyberling_stress":   messe_cyberling_stress(cur, wesen_id),
                "erinnerungslast":    messe_erinnerungslast(cur, wesen_id, now),
                "konfliktspannung":   messe_konfliktspannung(cur, wesen_id, now),
            }
            tension_total = round(sum(druckwerte.values()) / len(druckwerte), 3)
            risk = berechne_risk_vector(druckwerte)

            for substanz, wert in risk.items():
                weltklima[substanz].append(wert)

            # Druckkörper speichern
            druckkoerper = {
                "tension_total": tension_total,
                "druckwerte": druckwerte,
                "substance_risk": risk,
                "measured_at": now.isoformat(),
            }
            cur.execute("""
                INSERT INTO entity_profiles (entity_id, druckkoerper)
                VALUES (%s, %s)
                ON CONFLICT (entity_id) DO UPDATE SET druckkoerper = %s
            """, (wesen_id,
                  psycopg2.extras.Json(druckkoerper),
                  psycopg2.extras.Json(druckkoerper)))

            # Sedimente erkennen
            erkenne_sedimente(cur, wesen_id, druckwerte, risk, now)

            log.info(f"{wesen_id}: tension={tension_total} blitz={risk['blitz']} nebel={risk['nebel']} hunger={risk['hunger']}")

        # Weltklima aggregieren
        wk = {s: round(sum(v) / len(v), 3) for s, v in weltklima.items()}
        cur.execute("""
            INSERT INTO events (event_type, actor_type, actor_id, payload)
            VALUES ('weltklima.tick', 'system', 'tension_daemon', %s)
        """, (psycopg2.extras.Json({"weltklima": wk, "measured_at": now.isoformat()}),))

        # Knotungen prüfen
        pruefe_knotungen(cur)
        pruefe_keimkoerper(cur)

        conn.commit()
        log.info(f"Tick done. Weltklima: {wk}")
    except Exception as e:
        conn.rollback()
        log.error(f"Tick-Fehler: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    log.info("Tension Daemon gestartet.")
    while True:
        tick()
        time.sleep(INTERVAL)
