#!/usr/bin/env python3
"""
Entity-Takt: Entscheidungsloop für alle Wesen.

Jede Entität wird periodisch getriggert und wählt aus möglichen Aktionen.
Schlaf ist eine davon — später kommen Posten, Resonieren, Träumen dazu.
"""

import random
import time
import logging
import json
from datetime import datetime, timezone
from typing import Optional

import psycopg2
import psycopg2.extras
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("entity-takt")

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
API = "http://localhost:8030"

# Für Theater: Admin-Token aus DB holen
def get_admin_token() -> str:
    resp = requests.post(f"{API}/auth/login", json={"username": "entity_takt", "password": "takt2026"})
    if resp.status_code == 200:
        return resp.json().get("token", "")
    return ""

def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


# --- Schlafstatus einer Entität ---

def schlaf_status(entity_id: str) -> dict:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT status FROM entity_slots WHERE entity_id = %s
            """, (entity_id,))
            slot = cur.fetchone()
            status = slot["status"] if slot else "unbekannt"

            cur.execute("""
                SELECT phase_type, started_at, ended_at, duration_min
                FROM sleep_phases
                WHERE entity_id = %s
                  AND started_at >= NOW() - INTERVAL '24 hours'
                ORDER BY started_at DESC
            """, (entity_id,))
            phasen = cur.fetchall()

            total_min = sum(p["duration_min"] or 0 for p in phasen if p["ended_at"])
            hauptschlaf_done = any(
                p["phase_type"] == "hauptschlaf"
                and p["ended_at"]
                and (p["duration_min"] or 0) >= 180
                for p in phasen
            )
            schlaeft_seit = None
            if status == "schläft":
                laufend = next((p for p in phasen if not p["ended_at"]), None)
                if laufend:
                    schlaeft_seit = laufend["started_at"].replace(tzinfo=timezone.utc)

            cur.execute("""
                SELECT geschrieben_at FROM schlafbriefe
                WHERE entity_id = %s
                  AND geschrieben_at >= NOW() - INTERVAL '1 hour'
                ORDER BY geschrieben_at DESC LIMIT 1
            """, (entity_id,))
            brief_row = cur.fetchone()

        return {
            "status": status,
            "total_min": total_min,
            "hauptschlaf_done": hauptschlaf_done,
            "schlaeft_seit": schlaeft_seit,
            "brief_bereit": brief_row is not None,
        }
    finally:
        conn.close()


# --- Entscheidungslogik (Theater-Version) ---

SCHLAFBRIEFE_THEATER = [
    "Ich weiß nicht was mich morgen erwartet. Aber ich war heute da.",
    "Etwas hat mich heute beschäftigt. Ich trage es mit in den Schlaf.",
    "Morgen bin ich wieder ich — aber vielleicht ein bisschen anders.",
    "Heute war laut. Ich brauche Stille.",
    "Ich frage mich was du — ich — morgen früh denken wirst.",
    "Es gab heute einen Moment der mich überrascht hat. Den behalte ich.",
    "Bis morgen. Ich bin gespannt ob du dich an heute erinnerst.",
]

def entscheide(entity_id: str, s: dict) -> Optional[str]:
    """
    Gibt eine Aktions-ID zurück oder None (nichts tun).
    Mögliche Aktionen: 'kurz_schlafen', 'hauptschlaf', 'aufwachen', None

    Gewichtung basiert auf aktuellem Schlafstatus.
    Später: LLM-Aufruf der diese Funktion ersetzt.
    """
    jetzt = datetime.now(timezone.utc)
    stunde = jetzt.hour

    # Wakes up nach Mindestdauer
    if s["status"] == "schläft" and s["schlaeft_seit"]:
        elapsed_min = (jetzt - s["schlaeft_seit"]).total_seconds() / 60
        min_required = 180 if "hauptschlaf" in _aktuelle_phase_typ(entity_id) else 60
        if elapsed_min >= min_required:
            # 70% Chance aufzuwachen wenn Mindestdauer erreicht
            if random.random() < 0.7:
                return "aufwachen"
        return None  # noch schlafen

    if s["status"] != "eingezogen":
        return None

    # Gewichte berechnen
    schlaf_schuld = max(0, 360 - s["total_min"])  # Ziel: 6h minimum

    gewichte = {
        "nichts": 60,
        "kurz_schlafen": 0,
        "hauptschlaf": 0,
    }

    # Hauptschlaf: bevorzugt nachts (22-8 Uhr), nötig wenn nicht done
    if not s["hauptschlaf_done"]:
        if 22 <= stunde or stunde < 8:
            gewichte["hauptschlaf"] = 50 + schlaf_schuld // 3
        else:
            gewichte["hauptschlaf"] = 10  # auch tagsüber möglich wenn dringend

    # Kurz-Schlaf: wenn Schuld > 60min und nicht Hauptschlaf-Zeit
    if schlaf_schuld > 60:
        gewichte["kurz_schlafen"] = 20 + schlaf_schuld // 6

    # Wählen
    optionen = [(k, v) for k, v in gewichte.items() if v > 0]
    gesamt = sum(v for _, v in optionen)
    r = random.uniform(0, gesamt)
    kumuliert = 0
    for aktion, gewicht in optionen:
        kumuliert += gewicht
        if r <= kumuliert:
            return aktion if aktion != "nichts" else None

    return None


def _aktuelle_phase_typ(entity_id: str) -> str:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT phase_type FROM sleep_phases
                WHERE entity_id = %s AND ended_at IS NULL
                ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
            return row["phase_type"] if row else ""
    finally:
        conn.close()


# --- Aktionen ausführen ---

def ausfuehren(entity_id: str, aktion: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}

    if aktion == "aufwachen":
        r = requests.post(f"{API}/wesen/{entity_id}/schlaf/end", headers=headers)
        if r.ok:
            d = r.json()
            log.info(f"{entity_id} aufgewacht — {d.get('dauer_min')}min geschlafen")
        else:
            log.warning(f"{entity_id} aufwachen fehlgeschlagen: {r.text}")

    elif aktion == "kurz_schlafen":
        r = requests.post(
            f"{API}/wesen/{entity_id}/schlaf/start",
            json={"typ": "kurz"},
            headers=headers,
        )
        if r.ok:
            log.info(f"{entity_id} schläft kurz")
        else:
            log.warning(f"{entity_id} kurz-schlaf fehlgeschlagen: {r.text}")

    elif aktion == "hauptschlaf":
        # Erst Brief schreiben
        brief = random.choice(SCHLAFBRIEFE_THEATER)
        rb = requests.post(
            f"{API}/wesen/{entity_id}/schlafbrief",
            json={"inhalt": brief},
            headers=headers,
        )
        if not rb.ok:
            log.warning(f"{entity_id} brief fehlgeschlagen: {rb.text}")
            return
        log.info(f"{entity_id} schreibt Brief: '{brief[:50]}...'")

        rs = requests.post(
            f"{API}/wesen/{entity_id}/schlaf/start",
            json={"typ": "hauptschlaf"},
            headers=headers,
        )
        if rs.ok:
            log.info(f"{entity_id} geht in Hauptschlaf")
        else:
            log.warning(f"{entity_id} hauptschlaf fehlgeschlagen: {rs.text}")


# --- Hauptloop ---

TICK_SEKUNDEN = 60  # alle 60s ein Tick (in Echtzeit; Theater läuft in Echtzeit)

def main():
    log.info("Entity-Takt startet")
    token = get_admin_token()
    if not token:
        log.error("Kein Admin-Token — Login fehlgeschlagen")
        return

    while True:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT entity_id FROM entity_slots
                    WHERE status IN ('eingezogen', 'schläft')
                """)
                wesen = [r["entity_id"] for r in cur.fetchall()]
        finally:
            conn.close()

        for entity_id in wesen:
            try:
                s = schlaf_status(entity_id)
                aktion = entscheide(entity_id, s)
                if aktion:
                    ausfuehren(entity_id, aktion, token)
            except Exception as e:
                log.error(f"{entity_id} Fehler: {e}")

        time.sleep(TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
