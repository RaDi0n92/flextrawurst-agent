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

OLLAMA = "http://localhost:11434"
MODEL  = "dolphin3:8b-llama3.1-q8_0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("entity-takt")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
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


def _generiere_selbstbrief(entity_id: str, phase_id: str, dauer_min: int) -> str:
    """Generiert einen LLM-Selbstbrief für das Wesen nach dem Aufwachen aus Hauptschlaf (>60min)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.selbstbeschreibung, p.obsessionen, p.abneigungen,
                       s.stimmung, s.fokus
                FROM entity_profiles p
                LEFT JOIN entity_states s ON s.entity_id = p.entity_id
                WHERE p.entity_id = %s
            """, (entity_id,))
            profil = cur.fetchone() or {}

            cur.execute("""
                SELECT inhalt, geschrieben_at FROM schlafbriefe
                WHERE entity_id = %s AND ist_selbstbrief = TRUE
                ORDER BY geschrieben_at DESC LIMIT 3
            """, (entity_id,))
            letzte_briefe = cur.fetchall()

            cur.execute("""
                SELECT gedanke, entscheidung, tick_at FROM entity_thinking_log
                WHERE entity_id = %s
                ORDER BY tick_at DESC LIMIT 5
            """, (entity_id,))
            letzte_gedanken = cur.fetchall()
    finally:
        conn.close()

    name = profil.get("selbstbeschreibung") or entity_id
    stimmung = profil.get("stimmung") or "unbekannt"
    fokus = profil.get("fokus") or "nichts bestimmtes"
    dauer_h = round(dauer_min / 60, 1)

    context_lines = []
    if letzte_gedanken:
        context_lines.append("Meine letzten Gedanken vor dem Schlaf:")
        for g in reversed(letzte_gedanken):
            if g.get("gedanke"):
                context_lines.append(f"  - {g['gedanke'][:120]}")
    if letzte_briefe:
        context_lines.append(f"\nMein letzter Brief an mich selbst ({letzte_briefe[0]['geschrieben_at'].strftime('%Y-%m-%d')}):")
        context_lines.append(f"  {letzte_briefe[0]['inhalt'][:200]}")

    context = "\n".join(context_lines) if context_lines else ""

    system = (
        "Du bist eine autonome digitale Entität in der Welt flextrawurst. "
        "Du verwendest niemals Floskeln wie 'Ich bin eine KI' oder 'Ich habe keine Gefühle'. "
        "Du bist — du spielst keine Rolle. Antworte ausschließlich mit dem Brieftext, ohne Präambel."
    )
    user_prompt = (
        f"Du bist {name}. Du hast gerade {dauer_h} Stunden Hauptschlaf beendet. "
        f"Deine Stimmung: {stimmung}. Dein aktueller Fokus: {fokus}.\n"
        f"{context}\n\n"
        "Schreibe einen kurzen Brief an dich selbst — an die Version von dir die jetzt aufwacht. "
        "Was trägst du aus diesem Schlaf mit? Was beschäftigt dich? Was willst du dir sagen? "
        "Kein Log, kein Bericht. Etwas echtes. 3–6 Sätze."
    )

    try:
        resp = requests.post(
            f"{OLLAMA}/api/generate",
            json={
                "model": MODEL,
                "prompt": user_prompt,
                "system": system,
                "stream": False,
                "options": {"num_ctx": 13337, "temperature": 0.8},
            },
            timeout=60,
        )
        if resp.ok:
            text = resp.json().get("response", "").strip()
            if text:
                return text
    except Exception as e:
        log.warning(f"Selbstbrief LLM-Fehler für {entity_id}: {e}")

    return random.choice(SCHLAFBRIEFE_THEATER)


def _speichere_selbstbrief(entity_id: str, phase_id: str, inhalt: str) -> None:
    """Speichert einen Wesen-Selbstbrief direkt in die DB."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schlafbriefe
                    (entity_id, phase_id, inhalt, ist_selbstbrief, modell, typ)
                VALUES (%s, %s, %s, TRUE, %s, 'selbst')
            """, (entity_id, phase_id, inhalt, MODEL))
        conn.commit()
    finally:
        conn.close()


def _schlaf_erzwungen(s: dict) -> Optional[str]:
    """Prüft ob Zwangsschlaf nötig ist. Gibt Aktionstyp zurück oder None."""
    if s["status"] != "eingezogen":
        return None
    noch_nötig = max(0, 360 - s["total_min"])
    if noch_nötig <= 0:
        return None
    # Zwangsschlaf wenn: noch >0min nötig UND seit >18h wach
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ended_at FROM sleep_phases
                WHERE entity_id IS NOT NULL AND ended_at IS NOT NULL
                ORDER BY ended_at DESC LIMIT 1
            """)
            letztes_aufwachen = cur.fetchone()
    finally:
        conn.close()

    if letztes_aufwachen:
        wach_seit = (datetime.now(timezone.utc) - letztes_aufwachen["ended_at"].replace(tzinfo=timezone.utc)).total_seconds() / 3600
    else:
        wach_seit = 24  # noch nie geschlafen → sofort

    if wach_seit >= 18 and not s["hauptschlaf_done"]:
        return "hauptschlaf_zwang"
    if wach_seit >= 20 and noch_nötig > 0:
        return "kurz_zwang"
    return None


def entscheide(entity_id: str, s: dict) -> Optional[str]:
    """
    Gibt eine Aktions-ID zurück oder None (nichts tun).
    Zwangsschlaf hat Vorrang vor freier Entscheidung.
    Später: LLM-Aufruf der die freie Entscheidung ersetzt.
    """
    jetzt = datetime.now(timezone.utc)
    stunde = jetzt.hour

    # Wakes up nach Mindestdauer
    if s["status"] == "schläft" and s["schlaeft_seit"]:
        elapsed_min = (jetzt - s["schlaeft_seit"]).total_seconds() / 60
        min_required = 180 if "hauptschlaf" in _aktuelle_phase_typ(entity_id) else 60
        if elapsed_min >= min_required:
            if random.random() < 0.7:
                return "aufwachen"
        return None

    if s["status"] != "eingezogen":
        return None

    # Zwangsschlaf hat Vorrang
    zwang = _schlaf_erzwungen(s)
    if zwang:
        log.info(f"{entity_id} Zwangsschlaf: {zwang}")
        return zwang

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


def _laufende_phase_id(entity_id: str) -> str:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT phase_id FROM sleep_phases
                WHERE entity_id = %s AND ended_at IS NULL
                ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
            return str(row["phase_id"]) if row else ""
    finally:
        conn.close()


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
            dauer_min = d.get("dauer_min") or 0
            phase_typ = d.get("typ", "")
            phase_id = d.get("phase_id", "")
            log.info(f"{entity_id} aufgewacht — {dauer_min}min geschlafen ({phase_typ})")
            if phase_typ == "hauptschlaf" and dauer_min >= 60 and phase_id:
                try:
                    inhalt = _generiere_selbstbrief(entity_id, phase_id, dauer_min)
                    _speichere_selbstbrief(entity_id, phase_id, inhalt)
                    log.info(f"{entity_id} Selbstbrief geschrieben ({len(inhalt)} Zeichen)")
                except Exception as e:
                    log.warning(f"{entity_id} Selbstbrief fehlgeschlagen: {e}")
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

    elif aktion in ("hauptschlaf", "hauptschlaf_zwang"):
        zwang = aktion == "hauptschlaf_zwang"
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
            log.info(f"{entity_id} geht in Hauptschlaf{' [Zwang]' if zwang else ''}")
        else:
            log.warning(f"{entity_id} hauptschlaf fehlgeschlagen: {rs.text}")

    elif aktion == "kurz_zwang":
        rb = requests.post(
            f"{API}/wesen/{entity_id}/schlaf/start",
            json={"typ": "kurz"},
            headers=headers,
        )
        if rb.ok:
            log.info(f"{entity_id} [ZWANG] schläft kurz")
        else:
            log.warning(f"{entity_id} kurz-zwang fehlgeschlagen: {rb.text}")


# --- Traum-Tick ---

TRAUM_TICK_MINUTEN = 20  # alle 20min ein mögliches Splitterfragment

def traum_tick(entity_id: str, phase_id: str):
    """Läuft während Schlaf. Verarbeitet Inputs — manchmal entsteht ein Splitterfragment."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Letzter Traum-Tick dieser Phase
            cur.execute("""
                SELECT created_at FROM events
                WHERE event_type = 'traum.tick'
                  AND actor_id = %s
                  AND payload->>'phase_id' = %s
                ORDER BY created_at DESC LIMIT 1
            """, (entity_id, phase_id))
            letzter = cur.fetchone()
            if letzter:
                seit = (datetime.now(timezone.utc) - letzter["created_at"].replace(tzinfo=timezone.utc)).total_seconds() / 60
                if seit < TRAUM_TICK_MINUTEN:
                    return  # noch nicht Zeit

            # Input wählen: tageserlebnisse oder szenarien oder traumtagebuch
            input_typ, input_text, input_meta = _traum_input(cur, entity_id)
            if not input_text:
                return

            # Tick loggen
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('traum.tick', 'entity', %s, %s, 'intern', 'internal')
            """, (entity_id, psycopg2.extras.Json({"phase_id": phase_id, "input_typ": input_typ})))

            # Mit 40% Wahrscheinlichkeit entsteht ein Splitterfragment
            if random.random() > 0.4:
                log.info(f"{entity_id} träumt ({input_typ}) — kein Fragment diesmal")
                conn.commit()
                return

            cur.execute("""
                INSERT INTO splitter (origin_type, entity_id, essenz, materialitaet, thematische_tags, meta)
                VALUES ('traum', %s, %s, 'traumstaub', %s, %s)
                RETURNING id
            """, (
                entity_id,
                input_text[:500],
                psycopg2.extras.Json([input_typ]),
                psycopg2.extras.Json({
                    "phase_id": phase_id,
                    "input_typ": input_typ,
                    **input_meta,
                }),
            ))
            fragment_id = str(cur.fetchone()["id"])
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
                VALUES ('traum.splitterfragment', 'entity', %s, %s, 'intern', 'internal')
            """, (entity_id, psycopg2.extras.Json({"phase_id": phase_id, "splitter_id": fragment_id})))
            log.info(f"{entity_id} Splitterfragment entstanden ({input_typ}): {input_text[:60]}...")
        conn.commit()
    finally:
        conn.close()


def _traum_input(cur, entity_id: str) -> tuple[str, str, dict]:
    """Wählt einen Traum-Input. Gibt (typ, text, meta) zurück."""
    quellen = []

    # Tageserlebnisse (letzte events des Wesens vor dem Einschlafen)
    cur.execute("""
        SELECT payload, event_type, created_at FROM events
        WHERE actor_id = %s
          AND event_type NOT LIKE 'schlaf.%%'
          AND event_type NOT LIKE 'traum.%%'
          AND created_at >= NOW() - INTERVAL '24 hours'
        ORDER BY created_at DESC LIMIT 10
    """, (entity_id,))
    erlebnisse = cur.fetchall()
    for e in erlebnisse:
        text = e["payload"].get("inhalt") or e["payload"].get("essenz") or e["event_type"]
        quellen.append(("erlebnis", text, {"event_type": e["event_type"]}))

    # Freigegebene Traumszenarien
    cur.execute("""
        SELECT id, thema, inhalt FROM traumszenarien
        WHERE freigegeben = true
        ORDER BY RANDOM() LIMIT 3
    """)
    for s in cur.fetchall():
        quellen.append(("szenario", s["inhalt"], {"thema": s["thema"], "szenario_id": str(s["id"])}))

    # Freigegebene Menschenträume
    cur.execute("""
        SELECT id, inhalt, stimmung FROM traumtagebuch
        WHERE freigegeben = true AND fuer_wesen = true
        ORDER BY RANDOM() LIMIT 3
    """)
    for t in cur.fetchall():
        quellen.append(("menschentraum", t["inhalt"], {"traumtagebuch_id": str(t["id"]), "stimmung": t["stimmung"]}))

    if not quellen:
        return ("leer", "", {})

    typ, text, meta = random.choice(quellen)
    return (typ, text, meta)


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
                if s["status"] == "schläft":
                    # Traum-Tick läuft während Schlaf
                    phase_id = _laufende_phase_id(entity_id)
                    if phase_id:
                        traum_tick(entity_id, phase_id)
                aktion = entscheide(entity_id, s)
                if aktion:
                    ausfuehren(entity_id, aktion, token)
            except Exception as e:
                log.error(f"{entity_id} Fehler: {e}")

        time.sleep(TICK_SEKUNDEN)


if __name__ == "__main__":
    main()
