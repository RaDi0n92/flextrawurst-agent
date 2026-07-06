#!/usr/bin/env python3
"""
Wesen-Einzug Vorschau (Dry-Run).

Zeigt exakt was beim Einzug jedes Wesens passieren würde — ohne etwas zu schreiben.
Kann auch als Ausführungsmodus laufen: --einzug <entity_id_oder_alle>
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
import requests

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
API = "http://localhost:8030"

ALLE_WESEN = [
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
]


def get_wesen_state(entity_id: str) -> dict:
    conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entity_slots WHERE entity_id = %s", (entity_id,))
            slot = dict(cur.fetchone() or {})

            cur.execute("SELECT * FROM entity_profiles WHERE entity_id = %s", (entity_id,))
            profile = dict(cur.fetchone() or {})

            cur.execute("SELECT * FROM entity_states WHERE entity_id = %s", (entity_id,))
            state = dict(cur.fetchone() or {})

            cur.execute("SELECT * FROM cyberlinge WHERE entity_id = %s", (entity_id,))
            cyberling = dict(cur.fetchone() or {})

            cur.execute(
                "SELECT COUNT(*) AS cnt FROM entity_thinking_log WHERE entity_id = %s",
                (entity_id,),
            )
            denklog_count = cur.fetchone()["cnt"]

            cur.execute(
                "SELECT COUNT(*) AS cnt FROM events WHERE actor_id = %s",
                (entity_id,),
            )
            event_count = cur.fetchone()["cnt"]

            cur.execute(
                "SELECT COUNT(*) AS cnt FROM sleep_phases WHERE entity_id = %s",
                (entity_id,),
            )
            schlaf_count = cur.fetchone()["cnt"]

    finally:
        conn.close()

    return {
        "slot": slot,
        "profile": profile,
        "state": state,
        "cyberling": cyberling,
        "denklog_count": denklog_count,
        "event_count": event_count,
        "schlaf_count": schlaf_count,
    }


def dry_run_einzug(entity_id: str) -> dict:
    state = get_wesen_state(entity_id)
    slot = state["slot"]
    profile = state["profile"]

    if not slot:
        return {"entity_id": entity_id, "fehler": "Nicht in entity_slots gefunden"}

    if slot.get("status") == "eingezogen":
        return {
            "entity_id": entity_id,
            "status": "bereits_eingezogen",
            "ankunft": profile.get("meta", {}).get("einzug_timestamp", "unbekannt"),
        }

    aktionen = [
        f"entity_slots: status '{slot['status']}' → 'eingezogen'",
        f"entity_slots: visibility '{slot.get('visibility', 'internal')}' → 'public'",
    ]

    if not state["cyberling"]:
        aktionen.append("cyberlinge: neuer Eintrag erstellen")
    else:
        aktionen.append("cyberlinge: bereits vorhanden (ON CONFLICT DO NOTHING)")

    if state["state"]:
        aktionen.append("entity_states: stimmung → 'angekommen', fokus → 'neue Welt erkunden'")
    else:
        aktionen.append("entity_states: NEUER Eintrag: stimmung='angekommen'")

    aktionen.append(
        f"entity_thinking_log: +1 Eintrag (Ankunftsmoment) [vorher: {state['denklog_count']} Einträge]"
    )

    meta = profile.get("meta", {}) if isinstance(profile.get("meta"), dict) else {}
    aktionen.append(
        f"entity_profiles.meta: profil_status '{meta.get('profil_status', '?')}' → 'eingezogen'"
    )
    aktionen.append(
        f"entity_profiles.meta: flarum_herkunft_eingebunden '{meta.get('flarum_herkunft_eingebunden', False)}' → True"
    )
    aktionen.append("entity_profiles.meta: einzug_timestamp = jetzt")
    aktionen.append("entity_activity: sicherstellen dass Eintrag vorhanden")
    aktionen.append("events: INSERT wesen.eingezogen (public, origin=admin, herkunft=flarum)")

    return {
        "entity_id": entity_id,
        "aktuelle_status": slot.get("status"),
        "selbstbeschreibung": (profile.get("selbstbeschreibung") or "")[:80],
        "vorhandene_denklogs": state["denklog_count"],
        "vorhandene_events": state["event_count"],
        "schlafphasen": state["schlaf_count"],
        "cyberling_vorhanden": bool(state["cyberling"]),
        "aktionen_beim_einzug": aktionen,
        "status": "bereit_zum_einzug",
    }


def einzug_ausfuehren(entity_id: str, token: str) -> dict:
    r = requests.post(
        f"{API}/admin/wesen/{entity_id}/einzug",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if r.ok:
        return {"entity_id": entity_id, "ok": True, "antwort": r.json()}
    else:
        return {"entity_id": entity_id, "ok": False, "fehler": r.text, "status_code": r.status_code}


def admin_login(username: str = "daniel") -> str:
    import getpass
    pw = getpass.getpass(f"Admin-Passwort für '{username}': ")
    r = requests.post(f"{API}/auth/login", json={"username": username, "password": pw}, timeout=5)
    if r.ok and r.json().get("token"):
        return r.json()["token"]
    print(f"Login fehlgeschlagen: {r.text}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Wesen-Einzug Vorschau / Ausführung")
    parser.add_argument("--einzug", metavar="ENTITY_ID|alle", help="Einzug ausführen (VORSICHT)")
    parser.add_argument("--json", action="store_true", help="JSON-Output")
    args = parser.parse_args()

    if args.einzug:
        print("EINZUG-MODUS: Das ist kein Dry-Run. Wesen werden eingezogen.")
        confirm = input("Bist du sicher? (ja/nein): ").strip().lower()
        if confirm != "ja":
            print("Abgebrochen.")
            sys.exit(0)

        token = admin_login()
        targets = ALLE_WESEN if args.einzug == "alle" else [args.einzug]

        results = []
        for eid in targets:
            result = einzug_ausfuehren(eid, token)
            results.append(result)
            status = "✓" if result["ok"] else "✗"
            print(f"{status} {eid}: {result.get('antwort', result.get('fehler', ''))}")

        if args.json:
            print(json.dumps(results, indent=2, default=str))

    else:
        # Dry-Run
        print("=== WESEN-EINZUG DRY-RUN ===")
        print(f"Stand: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        results = []
        for eid in ALLE_WESEN:
            result = dry_run_einzug(eid)
            results.append(result)

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            for r in results:
                eid = r["entity_id"]
                if "fehler" in r:
                    print(f"✗ {eid}: {r['fehler']}")
                    continue
                if r.get("status") == "bereits_eingezogen":
                    print(f"✓ {eid}: bereits eingezogen (seit {r.get('ankunft', '?')})")
                    continue

                print(f"→ {eid} [{r['aktuelle_status']}]")
                print(f"  Selbstbeschreibung: {r['selbstbeschreibung']}...")
                print(f"  Denklogs: {r['vorhandene_denklogs']} | Events: {r['vorhandene_events']} | Schlafphasen: {r['schlafphasen']}")
                print(f"  Beim Einzug passiert:")
                for aktion in r["aktionen_beim_einzug"]:
                    print(f"    • {aktion}")
                print()


if __name__ == "__main__":
    main()
