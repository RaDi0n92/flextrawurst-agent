#!/usr/bin/env python3
"""
Traum-Integrator v0.1 — Einzel-Freigabe

Scope: NUR eine explizit freigegebene spur_id verarbeiten.
- Kein Batch. Kein Auto-Write. Kein Generalschlüssel.
- Schreibt genau einen append-only Eintrag in entity_selfmodel_entries.
- Setzt integrator_status='angenommen' auf der Traumspur.
- Verändert NICHT entities.meta, entity_states, oder andere Spuren.

Verwendung:
  python3 traum_integrator.py --spur-id UUID --spur-text "Bei ... verdichtet sich ..."

Sicherheitsregel: Ohne --spur-id läuft gar nichts.
"""

import argparse
import json
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"

BEGRUENDUNG_DEFAULT = (
    "Dry-Run bestätigt: Traumtext direkt aus Wachereignissen ableitbar. "
    "Keine Halluzination, keine Rollenvergabe, keine Identitätskrone. "
    "Manuell freigegeben durch Daniel nach 4-Punkte-Prüfung."
)


def hole_spur(cur, spur_id):
    cur.execute("""
        SELECT ts.spur_id, ts.entity_id, ts.log_id,
               ts.integrator_status, ts.llm_traumtext
        FROM traumspuren ts
        WHERE ts.spur_id = %s
    """, (spur_id,))
    return cur.fetchone()


def schreibe_integrator(conn, cur, spur, spur_text):
    spur_id    = spur["spur_id"]
    entity_id  = spur["entity_id"]

    # 1. Traumspur aktualisieren
    cur.execute("""
        UPDATE traumspuren
        SET integrator_status      = 'angenommen',
            integrator_spur        = %s,
            integrator_begruendung = %s
        WHERE spur_id = %s
          AND integrator_status = 'offen'
    """, (spur_text, BEGRUENDUNG_DEFAULT, spur_id))

    if cur.rowcount == 0:
        print(f"[INTEGRATOR] ABBRUCH — spur_id={spur_id} ist nicht mehr 'offen' oder existiert nicht.")
        conn.rollback()
        return None

    # 2. Selbstmodell-Eintrag schreiben (append-only)
    kontext = json.dumps({
        "integrator_version": "v0.1",
        "freigabe": "manuell",
        "dry_run_version": "v0.3",
        "log_id": str(spur["log_id"]) if spur["log_id"] else None
    })

    cur.execute("""
        INSERT INTO entity_selfmodel_entries
            (entity_id, quelle, spur_id, inhalt, ist_vorgeschichte, kontext)
        VALUES (%s, 'traum', %s, %s, false, %s)
        RETURNING entry_id
    """, (entity_id, spur_id, spur_text, kontext))

    entry_id = cur.fetchone()["entry_id"]
    conn.commit()
    return entry_id


def main():
    parser = argparse.ArgumentParser(description="Traum-Integrator v0.1 — Einzel-Freigabe")
    parser.add_argument("--spur-id",   required=True, help="UUID der freigegebenen Traumspur")
    parser.add_argument("--spur-text", required=True, help="Freigegebene Integrator-Spur (Pflichtform)")
    args = parser.parse_args()

    spur_id   = args.spur_id.strip()
    spur_text = args.spur_text.strip()

    if not spur_text.startswith("Bei "):
        print(f"[INTEGRATOR] ABBRUCH — Spur-Text muss mit 'Bei ' beginnen (Pflichtform).")
        print(f"  Erhaltener Text: {spur_text[:80]}")
        return

    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    cur = conn.cursor()

    spur = hole_spur(cur, spur_id)
    if not spur:
        print(f"[INTEGRATOR] ABBRUCH — spur_id={spur_id} nicht in DB gefunden.")
        conn.close()
        return

    print(f"[INTEGRATOR] Verarbeite:")
    print(f"  spur_id   : {spur['spur_id']}")
    print(f"  entity_id : {spur['entity_id']}")
    print(f"  status    : {spur['integrator_status']} → angenommen")
    print(f"  spur-text : {spur_text}")
    print()

    entry_id = schreibe_integrator(conn, cur, spur, spur_text)

    if entry_id is None:
        cur.close()
        conn.close()
        return

    # Verifikation
    cur.execute("SELECT COUNT(*) AS n FROM entity_selfmodel_entries WHERE entity_id = %s", (spur["entity_id"],))
    gesamt = cur.fetchone()["n"]

    cur.execute("SELECT stimmung, version FROM entity_states WHERE entity_id = %s", (spur["entity_id"],))
    state = cur.fetchone()

    print(f"[INTEGRATOR] Fertig.")
    print(f"  entry_id                          : {entry_id}")
    print(f"  inhalt                            : {spur_text}")
    print(f"  quelle                            : traum")
    print(f"  ist_vorgeschichte                 : false")
    print(f"  entity_selfmodel_entries gesamt   : {gesamt} (nur dieser eine neu)")
    if state:
        print(f"  entity_states.stimmung            : {state['stimmung']} (unverändert)")
        print(f"  entity_states.version             : {state['version']} (unverändert)")
    print(f"  entities.meta                     : nicht angefasst")
    print(f"  weitere Traumspuren verarbeitet   : 0")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
