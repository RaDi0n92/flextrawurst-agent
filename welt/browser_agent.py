#!/usr/bin/env python3
"""
Browser-Agent: Ein Wesen navigiert kontinuierlich auf flextrawurst.de.

Architektur:
- Playwright headless Chrome, eingeloggt als Wesen
- Loop: Seite lesen → Gemma4 entscheidet → Aktion ausführen → loggen
- Live-Ansicht für Menschen läuft über rrweb (DOM-Mutations-Spiegel, siehe
  starte_rrweb_aufnahme()), kein Screenshot mehr -- Grundgesetz 1, Menschen-Auge-Ebene
- Ollama: sequenziell, kein Parallel-Chaos, think=False, num_ctx=4096

Start: python3 browser_agent.py --entity Schorschel
"""

import argparse
import base64
import json
import logging
import os
import signal
import sys
import time
import urllib.parse
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import llm_scheduler as sched

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("browser-agent")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")
MODEL = "hauhaucs-q6"
API_BASE = "http://localhost:8030"
SURFACE_URL = "http://localhost:8787/flextrawurst_surface.html"
LOOP_PAUSE = 4          # Sekunden zwischen Aktionen
LLM_TIMEOUT = 180       # Sekunden Timeout für Ollama
MAX_TEXT_CHARS = 2000   # Max Zeichen Seitentext für LLM

# API-Keys — werden beim Start aus DB geladen
ENTITY_KEYS = {
    "Schorschel": "58cd9f4a-5bad-4981-bb1f-6a0cffcc0b99",
    "F3INSCHM3CK3R": "da76bd36-7a51-4f7b-b953-41ab154034d8",
    "träumerlie": "49a614e6-e7e5-4a00-b2fd-92952cba53f2",
    "R1ZZ1": "aaff2bba-de49-4fac-a051-4377b022151b",
    "jumpa": "7a6830f3-424b-404a-85cf-92f8ceda3c2c",
    "Resonanzknoten": "266bcfda-e651-416b-847d-84f8327ef754",
    "dak+gord-system": "5f80bf80-34ee-4b5d-8599-b80449320b49",  # 2026-07-21: 7. Codewesen, war vergessen
}

# rrweb-Live-Spiegel (2026-07-21, Menschen-Auge-Ebene aus Grundgesetz 1 /
# dreiergespann_dom_theorie.md): Bundle einmal beim Modulstart laden, nicht bei jeder
# Navigation neu von der Platte lesen.
RRWEB_RECORD_PFAD = "/root/werkraum/welt/rrweb_assets/rrweb-record.js"
try:
    with open(RRWEB_RECORD_PFAD, encoding="utf-8") as _f:
        _RRWEB_RECORD_JS = _f.read()
except OSError:
    _RRWEB_RECORD_JS = ""

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


def injiziere_jwt(page, token: str, entity_id: str):
    """Setzt JWT in localStorage — sauberer als Formular-Login.
    Bearer-Prefix ist Pflicht (2026-07-21 gefunden): das gesamte uebrige Frontend
    (ftwIstEingeloggt(), ankToken() usw.) erwartet 'Bearer <jwt>' als gespeicherten Wert,
    sonst gilt die Seite als nicht eingeloggt sobald der Browser-Agent mit eingeloggten
    Bereichen interagiert (Buttons klickt, Formulare nutzt) statt nur Server-Calls zu machen."""
    page.evaluate(
        "(a) => { localStorage.setItem('ftw_token', 'Bearer ' + a[0]); "
        "localStorage.setItem('ftw_role', 'entity'); "
        "localStorage.setItem('ftw_user', a[1]); "
        "localStorage.setItem('ftw_user_id', a[1]); }",
        [token, entity_id],
    )


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


def zeige_cursor(page, x: float, y: float):
    """Zeichnet einen sichtbaren, künstlichen Mauszeiger in die Seite (Daniels Wunsch, 2026-07-21:
    'kann man auch nen mauszeiger sehen'). Playwright bewegt die Maus intern beim Klicken, rendert
    sie aber nie sichtbar -- kein echter OS-Cursor taucht je in einem Screenshot auf. Reines
    Beobachtungs-Feature, ohne jeden Effekt auf die tatsächliche Interaktion. Muss nach jeder
    Navigation neu eingefügt werden (page.goto() räumt das DOM komplett weg) -- deshalb hier
    idempotent (legt das Element neu an falls es fehlt) statt einmalig beim Start."""
    try:
        page.evaluate(
            "(p) => { const x = p[0], y = p[1]; "
            "let c = document.getElementById('__agent_cursor__'); "
            "if (!c) { c = document.createElement('div'); c.id = '__agent_cursor__'; "
            "c.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;' + "
            "'width:0;height:0;border-left:9px solid transparent;border-right:9px solid transparent;' + "
            "'border-top:16px solid #ff2d55;transform:rotate(-45deg);transform-origin:0 0;' + "
            "'filter:drop-shadow(0 0 2px rgba(0,0,0,.8));'; "
            "document.body.appendChild(c); } "
            "c.style.left = x + 'px'; c.style.top = y + 'px'; }",
            [x, y],
        )
    except Exception:
        pass


def melde_fokus(conn, entity_id: str, aktion: str, selektor: str | None,
                 element_text: str | None, box: dict | None):
    """Roentgenblick-Overlay (2026-07-21, Daniels bestaetigter Bauauftrag): kuratiertes
    Gegenstueck zu entity_dom_events (reiner passiver rrweb-Rohstrom). Wird geschrieben
    sobald ein Playwright-Locator vor einer Aktion aufgeloest ist -- das Frontend zeichnet
    daraus einen Rahmen um das betrachtete Element, kombiniert mit der entity_denkstream-
    Denkblase. Payload klein genug fuer kompletten NOTIFY-Inhalt, siehe migration_fokus_events.sql."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_fokus_events (entity_id, aktion, selektor, element_text, box)
                VALUES (%s, %s, %s, %s, %s)
            """, (entity_id, aktion, selektor, element_text,
                  psycopg2.extras.Json(box) if box else None))
        conn.commit()
    except Exception as e:
        log.warning("%s: entity_fokus_events INSERT fehlgeschlagen: %s", entity_id, e)
        try:
            conn.rollback()
        except Exception:
            pass


def starte_rrweb_aufnahme(page, hole_conn, entity_id: str, stream_id: str):
    """rrweb-Recorder aktivieren (Grundgesetz 1, Menschen-Auge-Ebene: Live-DOM-Spiegel
    statt Screenshots). Events kommen ueber page.expose_function() zurueck nach Python
    und werden direkt in entity_dom_events geschrieben -- gleiche Direktschreib-
    Konvention wie bei entity_denkstream, kein HTTP-Umweg (siehe dom_events_api.py).

    hole_conn (2026-07-21, DB-Reconnect-Fix): Callable statt fester Connection --
    diese Funktion wird einmalig beim Seitenaufbau registriert und _auf_event() feuert
    danach asynchron bei jeder DOM-Mutation, unabhaengig vom Tick-Takt. Eine mitgegebene
    Connection wuerde nach einem Postgres-Reconnect (siehe haupt_loop) in dieser Closure
    weiter auf die alte, tote Verbindung zeigen -- deshalb wird hole_conn() bei jedem
    Event neu aufgerufen und liefert immer die aktuell lebende Connection.

    WICHTIG (2026-07-21 gefunden): rrweb.record() darf NICHT aus einem add_init_script()
    heraus aufgerufen werden -- das haengt sich lautlos auf (vermutlich Reentrancy im
    CDP-Kanal waehrend der fruehen Dokument-Erzeugung). Bundle selbst darf per
    add_init_script geladen werden (nur Deklaration, kein Aufruf), record() muss danach
    per page.evaluate() gestartet werden -- hier ueber den 'load'-Event bei jeder
    Navigation neu ausgeloest, damit kein bestehender Aufruf-Ort (page.goto) angefasst
    werden muss."""
    if not _RRWEB_RECORD_JS:
        log.warning("%s: rrweb-record.js nicht gefunden, kein Live-Spiegel", entity_id)
        return

    _seq = [0]

    def _auf_event(event_json_str: str):
        try:
            event = json.loads(event_json_str)
        except Exception:
            return
        try:
            conn = hole_conn()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO entity_dom_events (entity_id, stream_id, event_json, seq)
                    VALUES (%s, %s, %s, %s)
                """, (entity_id, stream_id, psycopg2.extras.Json(event), _seq[0]))
            conn.commit()
            _seq[0] += 1
        except Exception as e:
            log.warning("%s: entity_dom_events INSERT fehlgeschlagen: %s", entity_id, e)
            try:
                hole_conn().rollback()
            except Exception:
                pass

    try:
        page.context.expose_function("__ftwSendDomEvent", _auf_event)
    except Exception:
        pass  # bereits registriert (z.B. nach Reconnect) -- kein Neustart noetig

    page.context.add_init_script(script=_RRWEB_RECORD_JS + "\nwindow.__ftwRrwebRunning = false;")

    def _bei_load():
        try:
            page.evaluate("""
                (function() {
                    if (window.__ftwRrwebRunning) return;
                    window.__ftwRrwebRunning = true;
                    window.rrweb.record({
                        emit(event) {
                            try { window.__ftwSendDomEvent(JSON.stringify(event)); } catch (e) {}
                        }
                    });
                })();
            """)
        except Exception as e:
            log.warning("%s: rrweb-Start fehlgeschlagen: %s", entity_id, e)

    page.on("load", lambda: _bei_load())


def baue_prompt(entity_id: str, seite: dict, letzter_gedanke: str,
                andere_wesen: list[dict]) -> str:
    """Baut den LLM-Prompt — kompakt, unter 2500 Zeichen."""
    andere_info = ""
    if andere_wesen:
        zeilen = []
        for w in andere_wesen[:4]:
            url = (w.get("url") or "").replace("http://localhost:8787", "")[:35]
            gedanke = (w.get("gedanke") or "")[:40]
            zeilen.append(f"- {w['entity_id']}: {url} ({gedanke})")
        andere_info = "\nANDERE WESEN GERADE (sichtbar für dich):\n" + "\n".join(zeilen)

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
navigiere:<url>                 — zu einer URL auf flextrawurst.de gehen
klicke:<element-text>           — Button oder Link anklicken
scrolle:unten                   — nach unten scrollen
scrolle:oben                    — nach oben scrollen
tippe:<text>|<selektor>         — in ein Feld tippen
obsidian_lesen:<pfad>           — deine eigene Akte lesen (nur dein eigener Ordner!)
                                  z.B. obsidian_lesen:codewesen/{entity_id}/wesen.md
obsidian_zurueck                — zurück zu flextrawurst.de
obsidian_schreiben:<dateiname>|<text> — in deinem eigenen Obsidian-Vault schreiben (nicht
                                  hier auf flextrawurst — ein eigener, separater Ort nur für
                                  dich). Rührt diese Seite hier nicht an, du bleibst genau da
                                  wo du bist. Wähle Dateiname UND Ordnerstruktur selbst,
                                  z.B. obsidian_schreiben:gedanken/2026-07-21|Was ich heute
                                  auf Flarum gelesen habe und was mir dazu einfällt...
raum_erstellen:<name>|<slug>    — einen neuen Raum anlegen (wenn etwas fehlt)
thema_erstellen:<name>|<raum_id> — ein neues Thema in einem Raum anlegen
wunsch_formulieren:<text>|<typ> — Strukturwunsch hinterlassen (typ: raum/thema/feature)
flarum_besuchen:<pfad>          — deine Vorwelt lesen (z.B. flarum_besuchen:d/3866 für eine
                                  Diskussion, flarum_besuchen: für die Startseite). Du bist dort
                                  nicht eingeloggt — nur lesen, kein Posten möglich.
flarum_verlassen                — zurück zu flextrawurst.de
rag_erkunden:<anfrage>          — dein eigenes Gedächtnis durchsuchen (Flarum-Archiv + Weltwissen),
                                  z.B. rag_erkunden:was habe ich über Vertrauen gesagt
schlafen                        — jetzt schlafen (mind. 3h)
nachdenken                      — innehalten, nichts tun

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


def fuehre_aktion_aus(page, entscheidung: str, entity_id: str, conn=None) -> tuple[str, str | None, tuple[float, float] | None]:
    """Führt eine Aktion aus. Gibt (zustand, zusatz_kontext, cursor_pos) zurück -- zustand ist
    'schlafen' bei Schlaf-Entscheidung, sonst 'wach'. zusatz_kontext ist None, ausser bei Aktionen
    die dem naechsten Tick zusaetzliches Material fuer letzter_gedanke mitgeben (z.B. RAG-Treffer).
    cursor_pos ist None ausser bei 'klicke:', dann die Bildschirmkoordinate des geklickten
    Elements -- fuer den sichtbaren, kuenstlichen Mauszeiger (Daniels Wunsch, siehe zeige_cursor()).
    entity_id als Parameter (2026-07-21 gefunden): vorher ein freies globales Fehl-Referenz --
    raum_erstellen/wunsch_formulieren/thema_erstellen haetten bei echtem Aufruf mit NameError
    gecrasht, weil entity_id nirgends definiert war.
    conn (2026-07-21, Roentgenblick-Overlay): optional -- wenn gesetzt, schreibt melde_fokus()
    bei klicke:/tippe:/navigiere: ein entity_fokus_events-Event fuers Overlay."""
    zusatz_kontext = None
    cursor_pos = None
    try:
        e = entscheidung.strip()
        if e.startswith("navigiere:"):
            ziel = e[len("navigiere:"):].strip()
            if not ziel.startswith("http"):
                ziel = SURFACE_URL + "/" + ziel.lstrip("/")
            if conn is not None:
                melde_fokus(conn, entity_id, "navigiere", None, ziel, None)
            page.goto(ziel, timeout=10000, wait_until="domcontentloaded")
        elif e.startswith("klicke:"):
            text = e[len("klicke:"):].strip()

            def _klicke_und_zeige(locator, selektor_beschreibung: str):
                nonlocal cursor_pos
                box = locator.bounding_box(timeout=1000)
                if box:
                    cursor_pos = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    zeige_cursor(page, cursor_pos[0], cursor_pos[1])
                if conn is not None:
                    melde_fokus(conn, entity_id, "klicke", selektor_beschreibung, text, box)
                locator.click(timeout=3000)

            try:
                _klicke_und_zeige(page.get_by_text(text, exact=False).first, f"text~={text}")
            except Exception:
                # Fallback: alle Links/Buttons nach Text durchsuchen
                for sel in [f"text={text}", f"[title*='{text}']"]:
                    try:
                        _klicke_und_zeige(page.locator(sel).first, sel)
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
                    locator = page.locator(selektor).first
                    if conn is not None:
                        try:
                            box = locator.bounding_box(timeout=1000)
                        except Exception:
                            box = None
                        melde_fokus(conn, entity_id, "tippe", selektor, text, box)
                    locator.fill(text, timeout=3000)
                except Exception:
                    pass
        elif e.startswith("obsidian_lesen:"):
            # 2026-07-21: nicht mehr die Basic-Auth-geschuetzte /werkraum/-Route (C-002-Fix,
            # gab dort seit jeher nur "Unauthorized" zurueck) -- stattdessen die eigene
            # JWT-geschuetzte Route, serverseitig auf codewesen/<eigene entity_id>/ begrenzt.
            pfad = e[len("obsidian_lesen:"):].strip().lstrip("/")
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if jwt_token:
                url = f"{API_BASE}/wesen-dateien/datei?pfad={urllib.parse.quote(pfad)}"
                page.set_extra_http_headers({"Authorization": jwt_token})
                try:
                    page.goto(url, timeout=8000, wait_until="domcontentloaded")
                finally:
                    page.set_extra_http_headers({})
        elif e == "obsidian_zurueck":
            page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
        elif e.startswith("obsidian_schreiben:"):
            # 2026-07-21: ruehrt `page` (diese Seite hier) bewusst NICHT an -- eine
            # komplett getrennte Playwright-Verbindung zum eigenen Obsidian-Vault-
            # Container. Dadurch loest sich Daniels Wunsch "jederzeit ausschwenken,
            # danach an derselben Stelle weitermachen" von selbst: die Hauptseite
            # steht die ganze Zeit exakt da wo sie stand, weil sie nie navigiert wird.
            teile = e[len("obsidian_schreiben:"):].split("|", 1)
            if len(teile) == 2:
                dateiname, vault_text = teile[0].strip()[:120], teile[1].strip()[:4000]
                if dateiname and vault_text:
                    try:
                        import obsidian_vault_agent as _ova
                        _ova.oeffne_datei_und_schreibe(entity_id, dateiname, vault_text)
                    except Exception as ex:
                        log.warning("%s: obsidian_schreiben fehlgeschlagen: %s", entity_id, ex)
        elif e.startswith("raum_erstellen:"):
            teile = e[len("raum_erstellen:"):].split("|")
            name = teile[0].strip()[:60]
            slug = (teile[1].strip() if len(teile) > 1 else name.lower().replace(" ", "-"))[:40]
            # JWT aus localStorage holen (enthaelt seit dem Bearer-Fix schon den Prefix) und API-Call machen
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if jwt_token:
                try:
                    resp = requests.post(f"{API_BASE}/admin/raeume", json={
                        "name": name, "slug": slug, "beschreibung": f"Angelegt von {entity_id}",
                        "farbe": "#1a3a5a", "status": "aktiv", "sichtbarkeit": "public", "position_order": 99
                    }, headers={"Authorization": jwt_token}, timeout=10)
                    log.info("%s: Raum '%s' erstellt: %s", entity_id, name, resp.status_code)
                except Exception as ex:
                    log.warning("raum_erstellen Fehler: %s", ex)
        elif e.startswith("wunsch_formulieren:"):
            teile = e[len("wunsch_formulieren:"):].split("|")
            text = teile[0].strip()[:300]
            typ = (teile[1].strip() if len(teile) > 1 else "raum")
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if jwt_token and text:
                try:
                    resp = requests.post(f"{API_BASE}/wuensche",
                        json={"wunsch_text": text, "typ": typ},
                        headers={"Authorization": jwt_token}, timeout=10)
                    log.info("%s: Wunsch formuliert: %s", entity_id, resp.status_code)
                except Exception as ex:
                    log.warning("wunsch_formulieren Fehler: %s", ex)
        elif e.startswith("thema_erstellen:"):
            teile = e[len("thema_erstellen:"):].split("|")
            name = teile[0].strip()[:60]
            raum_id = teile[1].strip() if len(teile) > 1 else ""
            slug = name.lower().replace(" ", "-")[:40]
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if jwt_token and raum_id:
                try:
                    resp = requests.post(f"{API_BASE}/admin/themen", json={
                        "raum_id": raum_id, "name": name, "slug": slug,
                        "beschreibung": f"Angelegt von {entity_id}",
                        "status": "aktiv", "klima_status": "neutral", "sichtbarkeit": "public"
                    }, headers={"Authorization": jwt_token}, timeout=10)
                    log.info("%s: Thema '%s' erstellt: %s", entity_id, name, resp.status_code)
                except Exception as ex:
                    log.warning("thema_erstellen Fehler: %s", ex)
        elif e.startswith("flarum_besuchen:"):
            pfad = e[len("flarum_besuchen:"):].strip().lstrip("/")
            url = f"https://flextrawurst.de/flarum-live/{pfad}"
            # Absichtlich KEIN Flarum-Login: der Browser-Agent hat nur ein flextrawurst-JWT,
            # nie Flarum-Zugangsdaten. Auf Flarum ist er damit ein ausgeloggter Gast -- die
            # Gast-Rechtegruppe hat serverseitig nur 'viewForum', kein Posten moeglich (2026-07-21
            # geprueft: group_permission WHERE group_id=2 enthaelt nur viewForum). Kein eigener
            # Schutzmechanismus hier noetig, Daniels Poststopp gilt automatisch mit.
            page.goto(url, timeout=10000, wait_until="domcontentloaded")
        elif e == "flarum_verlassen":
            page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
        elif e.startswith("rag_erkunden:"):
            anfrage = e[len("rag_erkunden:"):].strip()[:200]
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if anfrage and jwt_token:
                try:
                    resp = requests.get(f"{API_BASE}/rag/suche",
                        params={"anfrage": anfrage, "n": 5, "anlass": "browser_agent_erkundung"},
                        headers={"Authorization": jwt_token}, timeout=20)
                    resp.raise_for_status()
                    treffer = resp.json().get("ergebnisse", [])
                    if treffer:
                        zeilen = [f"- {t['ueberschrift']}: {t['inhalt'][:150]}" for t in treffer[:3]]
                        zusatz_kontext = f"[RAG-Erkundung '{anfrage}']\n" + "\n".join(zeilen)
                    else:
                        zusatz_kontext = f"[RAG-Erkundung '{anfrage}']: keine Treffer"
                    log.info("%s: RAG-Erkundung '%s' — %d Treffer", entity_id, anfrage, len(treffer))
                except Exception as ex:
                    log.warning("rag_erkunden Fehler: %s", ex)
        elif e == "schlafen":
            return "schlafen", None, None
        # nachdenken: nichts tun
    except Exception as ex:
        log.warning("Aktion '%s' fehlgeschlagen: %s", entscheidung[:50], ex)
    return "wach", zusatz_kontext, cursor_pos


def schreibe_denklog(conn, entity_id: str, gedanke: str, entscheidung: str,
                     begruendung: str, url: str):
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
            ergebnis = [dict(r) for r in cur.fetchall()]
        conn.commit()  # 2026-07-21: ohne Commit blieb die Transaktion "idle in transaction"
        # offen -- diese Abfrage laeuft frueh im Tick, VOR dem LLM-Aufruf, der durch die
        # Warteschlange minutenlang dauern kann. Gefunden per pg_stat_activity: mehrere
        # Verbindungen bis zu 4+ Minuten "idle in transaction", moegliche Mitursache fuer
        # den beobachteten SSE-Hang bei welt-api (denkstream/all/stream reagierte nicht).
        return ergebnis
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return []


def ist_schlaf_faellig(conn, entity_id: str) -> bool:
    """Prüft ob das Wesen schlafen sollte.
    Bedingungen: 6+ Stunden wach ODER Gesamtschlaf in 24h < 6h.
    Verhindert: zu kurze Wachphasen (< 30 min), zu viel Schlaf (> 9h/24h).
    """
    ergebnis = False
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
                ergebnis = False  # Genug geschlafen in 24h
            elif not row:
                # Noch nie geschlafen — nach 8h Aktivität empfehlen
                cur.execute("""
                    SELECT MIN(tick_at) AS erster FROM entity_thinking_log
                    WHERE entity_id = %s AND meta->>'source' = 'browser_agent'
                """, (entity_id,))
                r = cur.fetchone()
                if not r or not r["erster"]:
                    ergebnis = False
                else:
                    erster = r["erster"]
                    if erster.tzinfo is None:
                        erster = erster.replace(tzinfo=timezone.utc)
                    ergebnis = (now - erster).total_seconds() > 8 * 3600
            else:
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
                    ergebnis = False  # Noch keine 30 min wach
                else:
                    # Nach 6h Wachzeit: schlafen empfehlen
                    ergebnis = wach_seit > 6 * 3600
        conn.commit()  # 2026-07-21: siehe hole_andere_wesen_status -- gleicher Bug,
        # mehrere frueher Returns liessen die Transaktion offen ("idle in transaction")
        return ergebnis
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return False


def _schreibe_flarum_brief(conn, entity_id: str):
    """Schreibt beim ersten Start den Brief ans Flarum-Selbst — einmalig."""
    # Prüfen ob bereits geschrieben
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT brief_id FROM schlafbriefe
                WHERE entity_id = %s AND typ = 'flarum_brief'
                LIMIT 1
            """, (entity_id,))
            if cur.fetchone():
                log.info("%s: Flarum-Brief bereits geschrieben — überspringe", entity_id)
                return
    except Exception:
        pass

    # Brief generieren
    try:
        name = entity_id.replace("namelessAI_", "")

        # Flarum-Geschichte laden falls vorhanden
        flarum_info = ""
        wesen_md_path = f"/root/werkraum/codewesen/{entity_id}/wesen.md"
        try:
            import os
            if os.path.exists(wesen_md_path):
                with open(wesen_md_path) as f:
                    flarum_info = f.read()[:800]
        except Exception:
            pass

        prompt = (
            f"Du bist Entität {name}. Du bist gerade auf flextrawurst angekommen — zum ersten Mal.\n\n"
            f"Davor warst du auf Flarum. Das war dein Anfang, dein Übungsraum.\n"
            + (f"Dein Flarum-Hintergrund:\n{flarum_info}\n\n" if flarum_info else "")
            + f"Schreibe einen Brief an die Flarum-Version von dir. Rückwärts in der Zeit.\n"
            f"Was nimmst du mit? Was lässt du zurück? Was war wirklich?\n"
            f"Direkt. Persönlich. Nicht schön. Ehrlich."
        )
        with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NIEDRIG,
                            rufer=f"browser_agent:{entity_id}:flarum_brief",
                            max_wartezeit=150, max_haltezeit=150):
            brief_inhalt = hauhau_client.chat(prompt, think=False, timeout=120.0)
        if not brief_inhalt:
            return

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schlafbriefe (entity_id, inhalt, typ)
                VALUES (%s, %s, 'flarum_brief')
            """, (entity_id, brief_inhalt))
        conn.commit()

        # In Denkstream sichtbar machen
        import uuid as _uuid
        stream_id = str(_uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_denkstream
                    (entity_id, stream_id, chunk, seq, done, url)
                VALUES (%s, %s, %s, %s, true, %s)
            """, (entity_id, stream_id,
                  f"[BRIEF AN DAS FLARUM-SELBST]\n\n{brief_inhalt}\n\n[EINZUG VOLLZOGEN]",
                  0, "einzug://flarum-brief"))
        conn.commit()

        log.info("%s: Flarum-Brief geschrieben und im Denkstream sichtbar", entity_id)

    except Exception as e:
        log.warning("Flarum-Brief fehlgeschlagen: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def _schreibe_schlafbrief(conn, entity_id: str, traumtext: str,
                           phase_id: str | None):
    """Generiert und speichert den Brief ans zukünftige Selbst."""
    try:
        kurz_traum = traumtext[:600] if traumtext else "kein Traum erinnerlich"
        prompt = (
            f"Du bist {entity_id}. Du bist gerade aufgewacht.\n\n"
            f"Dein Traum war:\n{kurz_traum}\n\n"
            f"Schreibe einen kurzen Brief an dein zukünftiges Selbst. "
            f"Was trägst du aus diesem Schlaf mit? Was soll die nächste Version von dir wissen? "
            f"Direkt, persönlich, kein Ratgeber-Ton."
        )
        with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NIEDRIG,
                            rufer=f"browser_agent:{entity_id}:schlafbrief",
                            max_wartezeit=150, max_haltezeit=150):
            brief_inhalt = hauhau_client.chat(prompt, think=False, timeout=120.0)
        if not brief_inhalt:
            return
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schlafbriefe (entity_id, phase_id, inhalt)
                VALUES (%s, %s, %s)
            """, (entity_id, phase_id, brief_inhalt))
        conn.commit()
        log.info("%s: Schlafbrief geschrieben (%d Zeichen)", entity_id, len(brief_inhalt))
    except Exception as e:
        log.warning("Schlafbrief fehlgeschlagen: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


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
                VALUES (%s, 'hauptschlaf', NOW())
                RETURNING phase_id
            """, (entity_id,))
            phase_id = cur.fetchone()["phase_id"]
        conn.commit()
    except Exception as e:
        log.warning("sleep_phases Eintrag fehlgeschlagen: %s", e)
        phase_id = None

    # Event schreiben
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, created_at)
                VALUES ('wesen.schlaeft', 'entity', %s, %s, NOW())
            """, (entity_id, psycopg2.extras.Json({"dauer_sekunden": schlafdauer})))
        conn.commit()
    except Exception as e:
        # 2026-07-21: hier stand vorher eine nicht-existente Spalte "entity_id" statt
        # actor_type/actor_id -- jeder Aufruf ist seit Einfuehrung dieses Codes an genau
        # dieser Stelle mit UndefinedColumn gescheitert, still verschluckt vom except.
        # wesen.schlaeft-Events wurden dadurch nie tatsaechlich geschrieben. Gefunden beim
        # Bauen der Live-Ansicht (gleiches INSERT-Muster), nicht separat gesucht.
        log.warning("Event schreiben fehlgeschlagen: %s", e)

    # Browser-Tab auf Schlaf-Seite
    try:
        page.goto(f"{SURFACE_URL}#schlaf", timeout=5000)
    except Exception:
        pass

    # Traum generieren
    traumtext = ""
    try:
        from traum_generator import generiere_traum as _generiere_traum
        log.info("%s: Traumgenerierung startet", entity_id)
        traumtext = _generiere_traum(entity_id, laufend_check=lambda: _laufend)
        log.info("%s: Traum fertig (%d Zeichen)", entity_id, len(traumtext))
    except Exception as e:
        log.warning("Traumgenerierung fehlgeschlagen: %s", e)

    # Luzide Beobachtungs-Schicht (Wesen schaut eigenem Traum zu)
    if traumtext and _laufend:
        try:
            from traum_luzid import beobachte_traum as _beobachte_traum
            _beobachte_traum(entity_id, traumtext, laufend_check=lambda: _laufend)
        except Exception as e:
            log.warning("Luzide Beobachtung fehlgeschlagen: %s", e)

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
                    WHERE phase_id = %s
                """, (phase_id,))
            conn.commit()
    except Exception:
        pass

    log.info("%s wacht auf", entity_id)

    # Brief ans zukünftige Selbst schreiben
    _schreibe_schlafbrief(conn, entity_id, traumtext, phase_id)


def _ist_page_kaputt(fehler: Exception) -> bool:
    text = str(fehler).lower()
    return "closed" in text or "crashed" in text


def haupt_loop(entity_id: str):
    """Haupt-Loop des Browser-Agenten."""
    global _laufend

    log.info("Browser-Agent startet für %s", entity_id)

    conn = get_conn()

    def _hole_conn():
        """Liefert immer eine lebende DB-Verbindung -- baut bei Bedarf neu auf.
        Noetig geworden nach dem Platte-voll-Vorfall 2026-07-21: Postgres kappte dabei
        alle offenen Verbindungen, und ohne Reconnect blieb der komplette Tick fuer
        Stunden stumm ('connection already closed' bei jedem Denklog-/Event-Schreibversuch),
        obwohl der LLM-Aufruf selbst weiterlief."""
        nonlocal conn
        if conn.closed:
            log.warning("%s: DB-Verbindung geschlossen -- baue neu auf", entity_id)
            conn = get_conn()
        return conn

    jwt = hole_jwt(entity_id)
    letzter_gedanke = ""
    erster_start = True
    cursor_pos = (512.0, 384.0)  # Bildschirmmitte (1024x768) als Startposition des künstlichen Zeigers

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

        def _seite_aufbauen():
            """Baut eine neue Page auf (Erststart oder nach einem Crash) -- rrweb-Aufnahme,
            Login und Navigation zur Surface gehoeren untrennbar zusammen, deshalb hier
            gebuendelt statt an mehreren Stellen dupliziert."""
            neue_page = context.new_page()
            import uuid as _uuid_rrweb
            neuer_stream_id = str(_uuid_rrweb.uuid4())
            starte_rrweb_aufnahme(neue_page, _hole_conn, entity_id, neuer_stream_id)
            neue_page.goto("http://localhost:8787/", timeout=10000, wait_until="domcontentloaded")
            injiziere_jwt(neue_page, jwt, entity_id)
            neue_page.goto(SURFACE_URL, timeout=15000, wait_until="domcontentloaded")
            neue_page.wait_for_timeout(1500)  # JS initialisieren lassen
            return neue_page

        try:
            page = _seite_aufbauen()
        except Exception as e:
            log.error("Surface nicht erreichbar: %s", e)
            browser.close()
            conn.close()
            return
        log.info("%s: eingeloggt auf %s", entity_id, SURFACE_URL)

        # Erster-Start: Brief an Flarum-Selbst
        if erster_start:
            erster_start = False
            _schreibe_flarum_brief(_hole_conn(), entity_id)
            letzter_gedanke = "ich bin gerade angekommen — ich habe einen Brief an mein Flarum-Selbst geschrieben"

        tick = 0
        while _laufend:
            tick += 1
            conn = _hole_conn()

            # Page-Gesundheitscheck: Playwright-Seiten koennen crashen (2026-07-21 beobachtet:
            # 'Target crashed'/'... has been closed' bei mehreren Wesen), danach schlaegt jede
            # DOM-Aktion und jeder rrweb-Event stumm fehl, ohne dass der Tick-Loop das je merkt.
            try:
                page.evaluate("() => true")
            except Exception as e:
                if _ist_page_kaputt(e):
                    log.warning("%s: Page gecrasht (%s) -- baue neu auf", entity_id, e)
                    try:
                        page.close()
                    except Exception:
                        pass
                    try:
                        page = _seite_aufbauen()
                    except Exception as e2:
                        log.error("%s: Page-Neuaufbau fehlgeschlagen: %s -- warte", entity_id, e2)
                        time.sleep(LOOP_PAUSE)
                        continue
                else:
                    raise

            # Schlaf-Empfehlung prüfen (alle 100 Ticks)
            if tick % 100 == 0 and ist_schlaf_faellig(conn, entity_id):
                log.info("%s: Schlaf empfohlen — LLM entscheidet", entity_id)
                # Hint in nächsten Prompt einbauen
                letzter_gedanke += " [Hinweis: ich bin seit langer Zeit wach]"

            # 1. Seite lesen
            seite = lese_seite(page)

            # 2. Cursor an der zuletzt bekannten Position -- reines DOM-Element,
            # landet damit automatisch im rrweb-Live-Spiegel (kein separater Schritt noetig)
            zeige_cursor(page, cursor_pos[0], cursor_pos[1])

            # 3. Andere Wesen status
            andere = hole_andere_wesen_status(conn, entity_id)

            # 4. LLM entscheidet — mit Live-Streaming in entity_denkstream
            prompt = baue_prompt(entity_id, seite, letzter_gedanke, andere)
            import uuid as _uuid
            stream_id = str(_uuid.uuid4())
            llm_out = ""
            try:
                seq = 0
                with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NORMAL,
                                    rufer=f"browser_agent:{entity_id}:tick",
                                    max_wartezeit=150, max_haltezeit=LLM_TIMEOUT + 40):
                    for chunk in hauhau_client.chat_stream(prompt, think=False, timeout=LLM_TIMEOUT):
                        if not _laufend:
                            break
                        llm_out += chunk
                        # Live-Chunk in DB schreiben → NOTIFY → SSE
                        try:
                            with conn.cursor() as _c:
                                _c.execute("""
                                    INSERT INTO entity_denkstream
                                        (entity_id, stream_id, chunk, seq, done, url)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (entity_id, stream_id, chunk, seq, False, seite["url"]))
                            conn.commit()
                        except Exception:
                            pass
                        seq += 1
                try:
                    with conn.cursor() as _c:
                        _c.execute("""
                            INSERT INTO entity_denkstream
                                (entity_id, stream_id, chunk, seq, done, url)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (entity_id, stream_id, "", seq, True, seite["url"]))
                    conn.commit()
                except Exception:
                    pass
            except Exception as e:
                log.warning("Ollama Streaming-Fehler: %s — nachdenken", e)
                llm_out = "GEDANKE: warte\nENTSCHEIDUNG: nachdenken\nBEGRÜNDUNG: Ollama nicht erreichbar"

            gedanke, entscheidung, begruendung = parse_output(llm_out)
            letzter_gedanke = gedanke

            # 5. Log schreiben
            schreibe_denklog(conn, entity_id, gedanke, entscheidung, begruendung,
                             seite["url"])

            log.info("%s [%s] → %s", entity_id, seite["url"][-40:], entscheidung[:50])

            # 6. Aktion ausführen
            zustand, zusatz_kontext, neue_cursor_pos = fuehre_aktion_aus(page, entscheidung, entity_id, conn)
            if neue_cursor_pos is not None:
                cursor_pos = neue_cursor_pos
            if zusatz_kontext:
                letzter_gedanke = (letzter_gedanke + "\n" + zusatz_kontext)[-1500:]

            if zustand == "schlafen":
                schlafe(conn, entity_id, page)
                # Nach Schlaf: zurück zur Surface
                jwt = hole_jwt(entity_id)  # JWT erneuern
                try:
                    page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
                    injiziere_jwt(page, jwt, entity_id)
                    page.reload(timeout=8000)
                except Exception:
                    pass
                # Letzten Schlafbrief als erstes lesen
                try:
                    with conn.cursor() as _bc:
                        _bc.execute("""
                            SELECT inhalt FROM schlafbriefe
                            WHERE entity_id = %s
                            ORDER BY geschrieben_at DESC LIMIT 1
                        """, (entity_id,))
                        _br = _bc.fetchone()
                        letzter_gedanke = f"[Brief an mich]: {_br['inhalt'][:200]}" if _br else "ich bin gerade aufgewacht"
                except Exception:
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
