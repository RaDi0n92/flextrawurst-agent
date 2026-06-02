#!/usr/bin/env python3
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("browser-agent")

DB_URI = "postgresql://dak:dakpass@localhost:5432/flextrawurst"
OLLAMA = "http://localhost:11434"
MODEL = "gemma4:e2b-it-q4_K_M"
API_BASE = "http://localhost:8030"
SURFACE_URL = "http://localhost:8787/flextrawurst_surface.html"
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
    page.evaluate(f"localStorage.setItem('ftw_token', '{token}'); localStorage.setItem('ftw_role', 'entity')")
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

        # Klickbare Elemente via JS — zuverlässiger als query_selector_all
        try:
            raw_elemente = page.evaluate("""
                () => {
                    const sels = ['button[data-view]','button:not([data-view])','a[href]'];
                    const seen = new Set(); const result = [];
                    sels.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => {
                            const t = (el.textContent||'').trim().substring(0,40);
                            if (t && !seen.has(t) && el.offsetParent !== null) {
                                seen.add(t); result.push(t);
                            }
                        });
                    });
                    return result.slice(0,15);
                }
            """)
            elemente = raw_elemente if isinstance(raw_elemente, list) else []
        except Exception:
            elemente = []

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
                    (entity_id, tick_at, raw_output, gedanke, entscheidung, begruendung, meta)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s)
            """, (
                entity_id,
                f"GEDANKE: {gedanke}\nENTSCHEIDUNG: {entscheidung}\nBEGRÜNDUNG: {begruendung}",
                gedanke, entscheidung, begruendung,
                psycopg2.extras.Json({
                    "url": url,
                    "source": "browser_agent",
                    "screenshot": screenshot_pfad,
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
    """Prüft ob das Wesen schlafen sollte.
    Bedingungen: 6+ Stunden wach ODER Gesamtschlaf in 24h < 6h.
    Verhindert: zu kurze Wachphasen (< 30 min), zu viel Schlaf (> 9h/24h).
    """
    try:
        with conn.cursor() as cur:
            # Letzter Schlaf-Ende
            cur.execute("""
                SELECT started_at, ended_at FROM sleep_phases
                WHERE entity_id = %s
                ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()

            now = datetime.now(timezone.utc)

            # Gesamtschlaf in letzten 24h prüfen (max 9h)
            cur.execute("""
                SELECT COALESCE(SUM(
                    EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at))
                ), 0) AS total_schlaf
                FROM sleep_phases
                WHERE entity_id = %s AND started_at > NOW() - INTERVAL '24h'
            """, (entity_id,))
            total = cur.fetchone()["total_schlaf"] or 0
            if total >= 9 * 3600:
                return False  # Genug geschlafen in 24h

            if not row:
                # Noch nie geschlafen — nach 8h Aktivität empfehlen
                cur.execute("""
                    SELECT MIN(tick_at) AS erster FROM entity_thinking_log
                    WHERE entity_id = %s AND meta->>'source' = 'browser_agent'
                """, (entity_id,))
                r = cur.fetchone()
                if not r or not r["erster"]:
                    return False
                erster = r["erster"]
                if erster.tzinfo is None:
                    erster = erster.replace(tzinfo=timezone.utc)
                return (now - erster).total_seconds() > 8 * 3600

            letzter_schlaf_start = row["started_at"]
            letzter_schlaf_ende = row["ended_at"]

            if letzter_schlaf_start.tzinfo is None:
                letzter_schlaf_start = letzter_schlaf_start.replace(tzinfo=timezone.utc)

            # Mindest-Wachzeit nach letztem Schlaf: 30 Minuten
            referenz = letzter_schlaf_ende or letzter_schlaf_start
            if referenz.tzinfo is None:
                referenz = referenz.replace(tzinfo=timezone.utc)
            wach_seit = (now - referenz).total_seconds()
            if wach_seit < 1800:
                return False  # Noch keine 30 min wach

            # Nach 6h Wachzeit: schlafen empfehlen
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

    # Traum generieren (läuft parallel zum Schlafen)
    traumtext = ""
    try:
        from traum_generator import generiere_traum as _generiere_traum
        log.info("%s: Traumgenerierung startet", entity_id)
        traumtext = _generiere_traum(entity_id, laufend_check=lambda: _laufend)
        log.info("%s: Traum fertig (%d Zeichen)", entity_id, len(traumtext))
    except Exception as e:
        log.warning("Traumgenerierung fehlgeschlagen: %s", e)

    # Restliche Schlafzeit abwarten (nach Traum)
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

        # Login: erst Root für localStorage, dann Surface
        try:
            page.goto("http://localhost:8787/", timeout=10000, wait_until="domcontentloaded")
            injiziere_jwt(page, jwt)
            page.goto(SURFACE_URL, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)  # JS initialisieren lassen
        except Exception as e:
            log.error("Surface nicht erreichbar: %s", e)
            browser.close()
            conn.close()
            return
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

            # 4. LLM entscheidet — mit Live-Streaming in entity_denkstream
            prompt = baue_prompt(entity_id, seite, letzter_gedanke, andere)
            import uuid as _uuid
            stream_id = str(_uuid.uuid4())
            llm_out = ""
            try:
                stream_resp = requests.post(f"{OLLAMA}/api/chat", json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                    "options": {"think": False, "num_ctx": 4096},
                }, timeout=LLM_TIMEOUT, stream=True)
                seq = 0
                for line in stream_resp.iter_lines():
                    if not line or not _laufend:
                        break
                    try:
                        d = json.loads(line)
                        chunk = d.get("message", {}).get("content", "")
                        if chunk:
                            llm_out += chunk
                            done = d.get("done", False)
                            # Live-Chunk in DB schreiben → NOTIFY → SSE
                            try:
                                with conn.cursor() as _c:
                                    _c.execute("""
                                        INSERT INTO entity_denkstream
                                            (entity_id, stream_id, chunk, seq, done, url)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    """, (entity_id, stream_id, chunk, seq, done, seite["url"]))
                                conn.commit()
                            except Exception:
                                pass
                            seq += 1
                    except Exception:
                        pass
            except Exception as e:
                log.warning("Ollama Streaming-Fehler: %s — nachdenken", e)
                llm_out = "GEDANKE: warte\nENTSCHEIDUNG: nachdenken\nBEGRÜNDUNG: Ollama nicht erreichbar"

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
