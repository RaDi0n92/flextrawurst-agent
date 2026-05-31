#!/usr/bin/env python3
"""
Traumprozess-Skeleton v0.1 — regelbasierte Vorauswahl

Scope: NUR auswählen, nicht deuten.
- Findet Wesen die gerade schlafen
- Wählt Events aus der letzten Wachphase als Traumrohstoff
- Schreibt traumkandidaten_log + traumkandidaten_events
- Kein LLM, kein Integrator, kein Selbstmodell, keine entities.meta-Änderung
"""

import psycopg2
import psycopg2.extras
from datetime import datetime, timezone, timedelta

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"

SELEKTIONSREGEL = "v0.1_interaktionsnah"

# Event-Typen die als Traumrohstoff betrachtet werden (alle außer sleep/system)
BETRACHTBARE_TYPEN = {
    "gedanke.gepostet",
    "post.erstellt",
    "resonanz.gesendet",
    "resonanz.empfangen",
    "schattenkommentar.geschrieben",
    "schatten.antwort",
    "schlafbrief.gelesen",
    "schlafbrief.geschrieben",
}

# Diese haben höhere Auswahlpriorität (Interaktionsnähe)
PRIORITAET_HOCH = {
    "resonanz.gesendet",
    "resonanz.empfangen",
    "schattenkommentar.geschrieben",
    "schatten.antwort",
    "schlafbrief.gelesen",
    "post.erstellt",
}

MAX_BETRACHTET = 20   # wie viele Events maximal betrachtet werden
MAX_AUSGEWAEHLT = 7   # wie viele davon ausgewählt werden


def hole_schlafende_wesen(cur):
    cur.execute("""
        SELECT phase_id, entity_id, started_at
        FROM sleep_phases
        WHERE ended_at IS NULL
        ORDER BY started_at DESC
    """)
    return cur.fetchall()


def hole_wachphase_start(cur, entity_id, schlaf_beginn):
    """Wann endete die letzte abgeschlossene Schlafphase (= Beginn der aktuellen Wachphase)."""
    cur.execute("""
        SELECT ended_at
        FROM sleep_phases
        WHERE entity_id = %s
          AND ended_at IS NOT NULL
          AND ended_at < %s
        ORDER BY ended_at DESC
        LIMIT 1
    """, (entity_id, schlaf_beginn))
    row = cur.fetchone()
    if row and row["ended_at"]:
        return row["ended_at"]
    # Fallback: 24h vor Schlafbeginn
    return schlaf_beginn - timedelta(hours=24)


def hole_events_wachphase(cur, entity_id, von, bis):
    """Alle Entity-Events aus dem Wachzeitraum, gefiltert auf betrachtbare Typen."""
    cur.execute("""
        SELECT event_id, event_type, created_at
        FROM events
        WHERE actor_id = %s
          AND actor_type = 'entity'
          AND event_type = ANY(%s)
          AND created_at >= %s
          AND created_at < %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (entity_id, list(BETRACHTBARE_TYPEN), von, bis, MAX_BETRACHTET))
    return cur.fetchall()


def waehle_aus(events):
    """
    Teilt Events in 'betrachtet' und 'ausgewaehlt'.
    Priorität: hohe Interaktionsnähe zuerst, dann Recency.
    """
    hoch = [e for e in events if e["event_type"] in PRIORITAET_HOCH]
    niedrig = [e for e in events if e["event_type"] not in PRIORITAET_HOCH]

    # Hoch-Priorität zuerst, Rest auffüllen bis MAX_AUSGEWAEHLT
    ausgewaehlt_ids = set()
    for e in hoch[:MAX_AUSGEWAEHLT]:
        ausgewaehlt_ids.add(e["event_id"])
    verbleibend = MAX_AUSGEWAEHLT - len(ausgewaehlt_ids)
    for e in niedrig[:verbleibend]:
        ausgewaehlt_ids.add(e["event_id"])

    return ausgewaehlt_ids


def verarbeite_wesen(cur, phase_id, entity_id, schlaf_beginn):
    wach_von = hole_wachphase_start(cur, entity_id, schlaf_beginn)
    events = hole_events_wachphase(cur, entity_id, wach_von, schlaf_beginn)

    if not events:
        print(f"[TRAUM-SKELETON] entity_id={entity_id} | keine Events in Wachphase — übersprungen")
        return

    ausgewaehlt_ids = waehle_aus(events)

    begruendung = (
        f"Wachphase {wach_von.isoformat()} – {schlaf_beginn.isoformat()} | "
        f"{len(events)} Events betrachtet | "
        f"Priorität: Interaktionsnähe"
    )

    # traumkandidaten_log schreiben
    cur.execute("""
        INSERT INTO traumkandidaten_log
            (entity_id, sleep_phase_id, selektionsregel, begruendung)
        VALUES (%s, %s, %s, %s)
        RETURNING log_id
    """, (entity_id, phase_id, SELEKTIONSREGEL, begruendung))
    log_id = cur.fetchone()["log_id"]

    # traumkandidaten_events schreiben
    for event in events:
        status = "ausgewaehlt" if event["event_id"] in ausgewaehlt_ids else "betrachtet"
        cur.execute("""
            INSERT INTO traumkandidaten_events
                (log_id, event_id, status, begruendung)
            VALUES (%s, %s, %s, %s)
        """, (
            log_id,
            event["event_id"],
            status,
            f"event_type={event['event_type']}, prioritaet={'hoch' if event['event_type'] in PRIORITAET_HOCH else 'normal'}"
        ))

    print(
        f"[TRAUM-SKELETON] entity_id={entity_id} | "
        f"betrachtet={len(events)} | "
        f"ausgewaehlt={len(ausgewaehlt_ids)} | "
        f"regel={SELEKTIONSREGEL} | "
        f"log_id={log_id}"
    )


def main():
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    cur = conn.cursor()

    wesen = hole_schlafende_wesen(cur)
    if not wesen:
        print("[TRAUM-SKELETON] Kein Wesen schläft gerade.")
        return

    print(f"[TRAUM-SKELETON] {len(wesen)} schlafende Wesen gefunden.")

    for w in wesen:
        # Nur verarbeiten wenn noch kein Log für diese Schlafphase existiert
        cur.execute("""
            SELECT log_id FROM traumkandidaten_log
            WHERE sleep_phase_id = %s
            LIMIT 1
        """, (w["phase_id"],))
        if cur.fetchone():
            print(f"[TRAUM-SKELETON] entity_id={w['entity_id']} | bereits verarbeitet — übersprungen")
            continue

        verarbeite_wesen(cur, w["phase_id"], w["entity_id"], w["started_at"])

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
