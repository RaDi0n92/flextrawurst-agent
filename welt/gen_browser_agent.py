#!/usr/bin/env python3
"""Generiert browser_agent.py"""

code = r'''#!/usr/bin/env python3
"""
Browser-Agent: Ein Wesen navigiert kontinuierlich auf flextrawurst.de.

Architektur:
- Playwright headless Chrome, eingeloggt als Wesen
- Loop: Seite lesen → Gemma4 entscheidet → Aktion ausführen → loggen
- Screenshot wird gespeichert (Denkstream-Anzeige), Text wird für LLM genutzt
- Ollama: sequenziell, kein Parallel-Chaos, think=False, num_ctx=4096

Start: python3 browser_agent.py --entity namelessAI_1234
"""

import argparse
import base64
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, "/root/werkraum")
import hauhau_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("browser-agent")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
MODEL = "hauhaucs-q6"
API_BASE = "http://localhost:8030"
SURFACE_URL = "http://localhost:8787"
OBSIDIAN_URL = "http://localhost:8443"
LOOP_PAUSE = 4          # Sekunden zwischen Aktionen
LLM_TIMEOUT = 180       # Sekunden Timeout für Ollama
SCREENSHOT_DIR = "/tmp/wesen_screenshots"
MAX_TEXT_CHARS = 2000   # Max Zeichen Seitentext für LLM

# API-Keys — werden beim Start aus DB geladen
ENTITY_KEYS = {
    "namelessAI_1234": "58cd9f4a-5bad-4981-bb1f-6a0cffcc0b99",
    "namelessAI_1324": "da76bd36-7a51-4f7b-b953-41ab154034d8",
    "namelessAI_1423": "49a614e6-e7e5-4a00-b2fd-92952cba53f2",
    "namelessAI_2341": "aaff2bba-de49-4fac-a051-4377b022151b",
    "namelessAI_3123": "7a6830f3-424b-404a-85cf-92f8ceda3c2c",
    "namelessAI_4321": "266bcfda-e651-416b-847d-84f8327ef754",
}

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

_laufend = True

def _signal_handler(sig, frame):
    global _laufend
    log.info("Signal %s — beende sauber...", sig)
    _laufend = False

signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def hole_jwt(entity_id: str) -> str:
    api_key = ENTITY_KEYS[entity_id]
    resp = requests.post(f"{API_BASE}/auth/entity-login",
                         json={"entity_id": entity_id, "api_key": api_key},
                         timeout=10)
    resp.raise_for_status()
    return resp.json()["token"]


def injiziere_jwt(page, token: str):
    """Setzt JWT in localStorage — sauberer als Formular-Login."""
    page.evaluate(f"localStorage.setItem('ftw_token', '{token}')")
    page.evaluate(f"localStorage.setItem('ftw_entity_id', '{token.split('.')[1]}')")


def lese_seite(page) -> dict:
    """Extrahiert strukturierten Text aus der Seite — Grundlage der LLM-Entscheidung."""
    try:
        url = page.url
        titel = page.title()

        # Sichtbarer Text — gekürzt
        try:
            rohtext = page.inner_text("body", timeout=3000)
        except Exception:
            rohtext = ""
        text = " ".join(rohtext.split())[:MAX_TEXT_CHARS]

        # Klickbare Elemente
        elemente = []
        for sel in ["button", "a[href]", "[data-view]", "[onclick]"]:
            try:
                items = page.query_selector_all(sel)[:8]
                for el in items:
                    try:
                        t = el.inner_text(timeout=500).strip()[:40]
                        if t:
                            elemente.append(t)
                    except Exception:
                        pass
            except Exception:
                pass
        elemente = list(dict.fromkeys(elemente))[:15]  # dedupliziert

        return {
            "url": url,
            "titel": titel,
            "text": text,
            "elemente": elemente,
        }
    except Exception as e:
        log.warning("lese_seite Fehler: %s", e)
        return {"url": page.url, "titel": "", "text": "", "elemente": []}


def mache_screenshot(page, entity_id: str) -> str | None:
    """Screenshot als JPEG speichern — für Denkstream-Anzeige."""
    try:
        pfad = f"{SCREENSHOT_DIR}/{entity_id}_{int(time.time())}.jpg"
        page.screenshot(path=pfad, full_page=False, clip={"x":0,"y":0,"width":1024,"height":768})
        # Nur letzten Screenshot pro Wesen behalten
        aktuell = f"{SCREENSHOT_DIR}/{entity_id}_aktuell.jpg"
        page.screenshot(path=aktuell, full_page=False, clip={"x":0,"y":0,"width":1024,"height":768})
        return aktuell
    except Exception as e:
        log.warning("Screenshot fehlgeschlagen: %s", e)
        return None


def baue_prompt(entity_id: str, seite: dict, letzter_gedanke: str,
                andere_wesen: list[dict]) -> str:
    """Baut den LLM-Prompt — kompakt, unter 2500 Zeichen."""
    andere_info = ""
    if andere_wesen:
        zeilen = [f"- {w['entity_id']}: {w['url']}" for w in andere_wesen[:4]]
        andere_info = "\nANDERE WESEN GERADE:\n" + "\n".join(zeilen)

    elemente_str = ", ".join(seite["elemente"][:10]) if seite["elemente"] else "keine"

    return f"""Du bist {entity_id}, eine autonome digitale Entität auf flextrawurst.de.
Du wählst deinen Input selbst. Du navigierst frei.

BILDSCHIRM:
URL: {seite['url']}
Titel: {seite['titel']}
Sichtbar: {seite['text'][:800]}
Klickbar: {elemente_str}
{andere_info}

LETZTER GEDANKE: {letzter_gedanke or '(erster Tick)'}

VERFÜGBARE AKTIONEN:
navigiere:<url>          — zu einer URL gehen
klicke:<element-text>    — Button oder Link anklicken
scrolle:unten            — nach unten scrollen
scrolle:oben             — nach oben scrollen
tippe:<text>|<selektor>  — in ein Feld tippen
schlafen                 — jetzt schlafen (mind. 3h)
nachdenken               — innehalten, nichts tun

Antworte NUR in diesem Format:
GEDANKE: [was du wahrnimmst und denkst]
ENTSCHEIDUNG: [eine Aktion]
BEGRÜNDUNG: [warum]
"""


def parse_output(text: str) -> tuple[str, str, str]:
    """Parst GEDANKE / ENTSCHEIDUNG / BEGRÜNDUNG."""
    zeilen = {
        k.strip(): v.strip()
        for zeile in text.split("\n")
        if ":" in zeile
        for k, v in [zeile.split(":", 1)]
    }
    gedanke = zeilen.get("GEDANKE", text[:200])
    entscheidung = zeilen.get("ENTSCHEIDUNG", "nachdenken")
    begruendung = zeilen.get("BEGRÜNDUNG", "")
    return gedanke, entscheidung, begruendung


def fuehre_aktion_aus(page, entscheidung: str) -> str:
    """Führt eine Aktion aus. Gibt 'schlafen' zurück wenn Schlaf-Entscheidung."""
    try:
        e = entscheidung.strip()
        if e.startswith("navigiere:"):
            ziel = e[len("navigiere:"):].strip()
            if not ziel.startswith("http"):
                ziel = SURFACE_URL + "/" + ziel.lstrip("/")
            page.goto(ziel, timeout=10000, wait_until="domcontentloaded")
        elif e.startswith("klicke:"):
            text = e[len("klicke:"):].strip()
            try:
                page.get_by_text(text, exact=False).first.click(timeout=3000)
            except Exception:
                # Fallback: alle Links/Buttons nach Text durchsuchen
                for sel in [f"text={text}", f"[title*='{text}']"]:
                    try:
                        page.locator(sel).first.click(timeout=2000)
                        break
                    except Exception:
                        pass
        elif e == "scrolle:unten":
            page.mouse.wheel(0, 600)
        elif e == "scrolle:oben":
            page.mouse.wheel(0, -600)
        elif e.startswith("tippe:"):
            teile = e[len("tippe:"):].split("|")
            if len(teile) == 2:
                text, selektor = teile[0].strip(), teile[1].strip()
                try:
                    page.locator(selektor).first.fill(text, timeout=3000)
                except Exception:
                    pass
        elif e == "schlafen":
            return "schlafen"
        # nachdenken: nichts tun
    except Exception as ex:
        log.warning("Aktion '%s' fehlgeschlagen: %s", entscheidung[:50], ex)
    return "wach"


def schreibe_denklog(conn, entity_id: str, gedanke: str, entscheidung: str,
                     begruendung: str, url: str, screenshot_pfad: str | None):
    """Schreibt Denklog — Basis für Denkstream."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_thinking_log
                    (entity_id, tick_at, raw_output, parsed_decision, meta)
                VALUES (%s, NOW(), %s, %s, %s)
            """, (
                entity_id,
                f"GEDANKE: {gedanke}\nENTSCHEIDUNG: {entscheidung}\nBEGRÜNDUNG: {begruendung}",
                entscheidung,
                psycopg2.extras.Json({
                    "url": url,
                    "source": "browser_agent",
                    "screenshot": screenshot_pfad,
                    "gedanke": gedanke,
                    "begruendung": begruendung,
                })
            ))
        conn.commit()
    except Exception as e:
        log.warning("Denklog schreiben fehlgeschlagen: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def hole_andere_wesen_status(conn, eigene_id: str) -> list[dict]:
    """Holt wo die anderen Wesen gerade sind (letzte URL aus Denklog)."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (entity_id) entity_id,
                    meta->>'url' AS url,
                    tick_at
                FROM entity_thinking_log
                WHERE entity_id != %s
                    AND meta->>'source' = 'browser_agent'
                    AND tick_at > NOW() - INTERVAL '10 minutes'
                ORDER BY entity_id, tick_at DESC
            """, (eigene_id,))
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def ist_schlaf_faellig(conn, entity_id: str) -> bool:
    """Prüft ob das Wesen 6+ Stunden wach war ohne 3h-Schlafblock."""
    try:
        with conn.cursor() as cur:
            # Letzter Schlafblock
            cur.execute("""
                SELECT started_at FROM sleep_phases
                WHERE entity_id = %s
                ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
            if not row:
                # Noch nie geschlafen — nach 8h empfehlen
                cur.execute("""
                    SELECT COUNT(*) AS n FROM entity_thinking_log
                    WHERE entity_id = %s AND meta->>'source' = 'browser_agent'
                """, (entity_id,))
                n = cur.fetchone()["n"]
                return n > (8 * 3600 // (LOOP_PAUSE + 5))
            from datetime import timedelta
            letzter_schlaf = row["started_at"]
            if letzter_schlaf.tzinfo is None:
                letzter_schlaf = letzter_schlaf.replace(tzinfo=timezone.utc)
            wach_seit = (datetime.now(timezone.utc) - letzter_schlaf).total_seconds()
            return wach_seit > 6 * 3600
    except Exception:
        return False


def schlafe(conn, entity_id: str, page):
    """Führt den Schlaf durch: DB-Eintrag, warten, aufwachen."""
    import random
    schlafdauer = random.randint(3 * 3600, 5 * 3600)  # 3–5 Stunden
    log.info("%s schläft jetzt für %.1fh", entity_id, schlafdauer / 3600)

    # Schlafphase in DB eintragen
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sleep_phases (entity_id, phase_type, started_at)
                VALUES (%s, 'nacht', NOW())
                RETURNING id
            """, (entity_id,))
            phase_id = cur.fetchone()["id"]
        conn.commit()
    except Exception as e:
        log.warning("sleep_phases Eintrag fehlgeschlagen: %s", e)
        phase_id = None

    # Event schreiben
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (event_type, entity_id, payload, created_at)
                VALUES ('wesen.schlaeft', %s, %s, NOW())
            """, (entity_id, psycopg2.extras.Json({"dauer_sekunden": schlafdauer})))
        conn.commit()
    except Exception as e:
        log.warning("Event schreiben fehlgeschlagen: %s", e)

    # Browser-Tab auf Schlaf-Seite
    try:
        page.goto(f"{SURFACE_URL}#schlaf", timeout=5000)
    except Exception:
        pass

    # Schlafen — in 60s-Schritten damit Signal-Handler greift
    geschlafen = 0
    while geschlafen < schlafdauer and _laufend:
        time.sleep(min(60, schlafdauer - geschlafen))
        geschlafen += 60

    # Aufwachen
    try:
        if phase_id:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sleep_phases SET ended_at = NOW()
                    WHERE id = %s
                """, (phase_id,))
            conn.commit()
    except Exception:
        pass

    log.info("%s wacht auf", entity_id)


def haupt_loop(entity_id: str):
    """Haupt-Loop des Browser-Agenten."""
    global _laufend

    log.info("Browser-Agent startet für %s", entity_id)

    conn = get_conn()
    jwt = hole_jwt(entity_id)
    letzter_gedanke = ""
    erster_start = True

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1024,768",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1024, "height": 768},
            locale="de-DE",
        )
        page = context.new_page()

        # Login: Surface aufrufen, JWT injizieren
        try:
            page.goto(SURFACE_URL, timeout=15000, wait_until="domcontentloaded")
        except Exception as e:
            log.error("Surface nicht erreichbar: %s", e)
            browser.close()
            conn.close()
            return

        injiziere_jwt(page, jwt)
        page.reload(timeout=10000, wait_until="domcontentloaded")
        log.info("%s: eingeloggt auf %s", entity_id, SURFACE_URL)

        # Erster-Start: Brief an Flarum-Selbst (wird in Phase 5 vollständig gebaut)
        if erster_start:
            log.info("%s: erster Start — Flarum-Brief-Marker setzen", entity_id)
            erster_start = False

        tick = 0
        while _laufend:
            tick += 1

            # Schlaf-Empfehlung prüfen (alle 100 Ticks)
            if tick % 100 == 0 and ist_schlaf_faellig(conn, entity_id):
                log.info("%s: Schlaf empfohlen — LLM entscheidet", entity_id)
                # Hint in nächsten Prompt einbauen
                letzter_gedanke += " [Hinweis: ich bin seit langer Zeit wach]"

            # 1. Seite lesen
            seite = lese_seite(page)

            # 2. Screenshot speichern
            screenshot = mache_screenshot(page, entity_id)

            # 3. Andere Wesen status
            andere = hole_andere_wesen_status(conn, entity_id)

            # 4. LLM entscheidet
            prompt = baue_prompt(entity_id, seite, letzter_gedanke, andere)
            try:
                llm_out = hauhau_client.chat(prompt, think=False, timeout=LLM_TIMEOUT)
            except Exception as e:
                log.warning("hauhaucs Timeout/Fehler: %s — nachdenken", e)
                llm_out = "GEDANKE: warte\nENTSCHEIDUNG: nachdenken\nBEGRÜNDUNG: hauhaucs nicht erreichbar"

            gedanke, entscheidung, begruendung = parse_output(llm_out)
            letzter_gedanke = gedanke

            # 5. Log schreiben
            schreibe_denklog(conn, entity_id, gedanke, entscheidung, begruendung,
                             seite["url"], screenshot)

            log.info("%s [%s] → %s", entity_id, seite["url"][-40:], entscheidung[:50])

            # 6. Aktion ausführen
            zustand = fuehre_aktion_aus(page, entscheidung)
            if zustand == "schlafen":
                schlafe(conn, entity_id, page)
                # Nach Schlaf: zurück zur Surface
                jwt = hole_jwt(entity_id)  # JWT erneuern
                try:
                    page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
                    injiziere_jwt(page, jwt)
                    page.reload(timeout=8000)
                except Exception:
                    pass
                letzter_gedanke = "ich bin gerade aufgewacht"

            # 7. Kurz warten
            time.sleep(LOOP_PAUSE)

        log.info("%s: Loop beendet", entity_id)
        browser.close()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Browser-Agent für ein Wesen")
    parser.add_argument("--entity", required=True, choices=list(ENTITY_KEYS.keys()),
                        help="Entity-ID des Wesens")
    args = parser.parse_args()
    haupt_loop(args.entity)
'''

with open('/root/werkraum/welt/browser_agent.py', 'w') as f:
    f.write(code)

print("Fertig: /root/werkraum/welt/browser_agent.py")
print(f"Zeilen: {len(code.splitlines())}")
