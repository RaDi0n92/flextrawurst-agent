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
import math
import os
import random
import re
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

# Mechanische Bewegung ohne LLM-Call (2026-07-22, Daniels Auftrag -- Pilot nur Schorschel,
# siehe _claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md).
# Grund: bisher macht JEDER Tick (alle LOOP_PAUSE=4s) einen echten LLM-Call -- Hauptursache
# der dokumentierten LLM-Slot-Kontention bei 7 gleichzeitigen Wesen. Verhaeltnis 1:3 ist eine
# erste, nicht kalibrierte Annahme -- erst beobachten wie es sich anfuehlt, dann justieren.
MECHANISCH_AKTIVE_WESEN = {"Schorschel"}
MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG = 3

# Periodischer Check-in-Hinweis (2026-07-22, Daniels Auftrag -- Testlauf mit nur Schorschel,
# andere 6 Wesen bewusst gestoppt, siehe _claude/notizen). Alle TICK_CHECKIN_SEKUNDEN wird
# ein LLM-Tick erzwungen (auch mitten in der mechanischen Phase) und bekommt einen kurzen
# Ueberblick "was es gerade gibt" -- 2 konkrete, aus echten DB-Zahlen gebaute Angebote, plus
# eine fest formulierte 3. Option zum freien Erkunden. Kein Bezug zur spaeteren 44s-Batch-
# Check-in-Architektur (die batcht ueber mehrere Wesen) -- hier nur ein einzelnes Wesen,
# einfacher Timer.
TICK_CHECKIN_SEKUNDEN = 40

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


_KOERPER_JS = """
(p) => {
  const x = p[0], y = p[1], speed = p[2] || 0, linsen = p[3] || {};
  // 2026-07-22/23 (Sieben-Linsen-Koerper, siehe _claude/ideen/sieben_linsen_koerper_kreatur.md,
  // Daniels "ja ich will alles und komplett" + 2026-07-23 Rekonstruktion gegen die
  // Original-Definition): sechs der sieben Linsen (Original: Vault/DOM/RAG-Flarum/
  // Gedaechtnis/Gegenwart/Sozial/Meta) bekommen je ein eigenes Bein mit fester Farbe,
  // Ausschlag skaliert mit dem echten, aus hole_linsen_status() berechneten Wert (0..1) --
  // keine erfundenen Zustaende. DOM-Linse braucht kein eigenes Bein (der ganze Koerper IST
  // die DOM-Bewegung, ueber speed schon abgedeckt). Meta-Linse ist der Koerperkern selbst --
  // Glow-Staerke aus dem Mittelwert aller sechs. "gedaechtnis" war zwischenzeitlich in zwei
  // getrennte, sich ueberschneidende Linsen ("gedaechtnis_tiefe" + "einsicht") aufgespalten --
  // 2026-07-23 wieder zu einer zusammengefuehrt (siehe Ideen-Datei), da Daniels Original-
  // Definition von Anfang an "LangGraph/PostgreSQL, eigene Erinnerungen" war, nicht die
  // generische Denklog-Zeilenzahl.
  const LINSEN_DEF = [
    { key: 'vault', farbe: '#a855f7' },
    { key: 'rag_flarum', farbe: '#22d3ee' },
    { key: 'gedaechtnis', farbe: '#3b82f6' },
    { key: 'gegenwart_anteil', farbe: '#f8fafc' },
    { key: 'sozial', farbe: '#22c55e' },
    { key: 'schlaf_naehe', farbe: '#f59e0b' },
  ];
  // Cyberling- und KompOase-Linse (Daniels Nachtrag) bewusst NOCH KEIN eigenes Bein --
  // cyberlinge.status='tot'/alle Werte 0 und entity_splitter_stats komplett 0 fuer ALLE
  // Entitaeten (per DB-Abfrage verifiziert, 2026-07-22) -- ein Bein dafuer waere gerade fuer
  // jedes Wesen gleich unsichtbar/flach, keine echte Information. /entities/{id}/linsen kann
  // das spaeter tragen, sobald diese Systeme wieder echte, unterscheidbare Werte liefern.
  let eng = window.__agentKoerperEngine;
  if (!eng) {
    const canvas = document.createElement('canvas');
    canvas.id = '__agent_koerper__';
    canvas.width = 140; canvas.height = 140;
    canvas.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;' +
      'filter:drop-shadow(0 0 3px rgba(255,45,85,.55));';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const beine = LINSEN_DEF.map(function (def, i) {
      return { winkel: (i / LINSEN_DEF.length) * Math.PI * 2, farbe: def.farbe, key: def.key, wert: 0, fx: x, fy: y };
    });
    eng = window.__agentKoerperEngine = {
      canvas: canvas, ctx: ctx, beine: beine,
      cx: x, cy: y, tx: x, ty: y, speed: 0, letzteZeit: performance.now(),
    };
    // Prozedurale Beine per einfacher IK (Kniepunkt seitlich versetzt zur Huefte-Fuss-
    // Strecke), angelehnt an "follow the leader"-Techniken wie Reptile-Interactive-Cursor.
    // Ausschlag/Tempo skaliert mit echter Bewegungsgeschwindigkeit UND echtem Linsen-Wert,
    // keine erfundene Animation.
    function tick(jetzt) {
      const dt = Math.min(0.05, (jetzt - eng.letzteZeit) / 1000);
      eng.letzteZeit = jetzt;
      eng.cx += (eng.tx - eng.cx) * Math.min(1, dt * 8);
      eng.cy += (eng.ty - eng.cy) * Math.min(1, dt * 8);
      eng.speed += (eng.zielSpeed - eng.speed) * Math.min(1, dt * 4);
      const bewegungsWinkel = Math.atan2(eng.ty - eng.cy, eng.tx - eng.cx);
      const basisAusschlag = Math.min(22, 6 + eng.speed * 0.03);
      let summeWerte = 0;
      eng.beine.forEach(function (b, i) {
        b.wert += ((eng.zielLinsen[b.key] || 0) - b.wert) * Math.min(1, dt * 2);
        summeWerte += b.wert;
        const ausschlag = basisAusschlag + b.wert * 24;
        const zielWinkel = bewegungsWinkel + Math.PI + b.winkel * 0.6 + Math.sin(jetzt / 260 + i) * 0.2;
        const zx = eng.cx + Math.cos(zielWinkel) * ausschlag;
        const zy = eng.cy + Math.sin(zielWinkel) * ausschlag;
        b.fx += (zx - b.fx) * Math.min(1, dt * 6);
        b.fy += (zy - b.fy) * Math.min(1, dt * 6);
      });
      canvas.style.left = (eng.cx - 70) + 'px';
      canvas.style.top = (eng.cy - 70) + 'px';
      ctx.clearRect(0, 0, 140, 140);
      ctx.lineWidth = 2;
      eng.beine.forEach(function (b) {
        const lx = b.fx - eng.cx + 70, ly = b.fy - eng.cy + 70;
        const winkel = Math.atan2(ly - 70, lx - 70);
        const hx = 70 + Math.cos(winkel) * 8, hy = 70 + Math.sin(winkel) * 8;
        const midx = (hx + lx) / 2, midy = (hy + ly) / 2;
        const laenge = Math.hypot(lx - hx, ly - hy) || 1;
        const senkx = -(ly - hy) / laenge, senky = (lx - hx) / laenge;
        const kniex = midx + senkx * 10, kniey = midy + senky * 10;
        ctx.strokeStyle = b.farbe;
        ctx.beginPath();
        ctx.moveTo(hx, hy);
        ctx.lineTo(kniex, kniey);
        ctx.lineTo(lx, ly);
        ctx.stroke();
      });
      // Meta-Linse: Koerperkern selbst, Glow-Staerke aus dem Mittelwert aller fuenf Linsen.
      const metaWert = summeWerte / eng.beine.length;
      ctx.shadowColor = '#ff2d55';
      ctx.shadowBlur = 4 + metaWert * 14;
      ctx.fillStyle = '#ff2d55';
      ctx.beginPath();
      ctx.arc(70, 70, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
      requestAnimationFrame(tick);
    }
    eng.zielSpeed = speed;
    eng.zielLinsen = linsen;
    requestAnimationFrame(tick);
  }
  eng.tx = x; eng.ty = y; eng.zielSpeed = speed;
  if (linsen && Object.keys(linsen).length) eng.zielLinsen = linsen;
}
"""


def zeige_cursor(page, x: float, y: float, geschwindigkeit: float = 0.0, linsen: dict | None = None):
    """Zeichnet den sichtbaren Koerper des Wesens in die Seite (Daniels Wunsch, 2026-07-21:
    'kann man auch nen mauszeiger sehen', erweitert 2026-07-22 zur 'Kraken-Spinne': der
    Mauszeiger IST der Koerper, siehe _claude/ideen/sieben_linsen_koerper_kreatur.md).
    Playwright bewegt die Maus intern beim Klicken, rendert sie aber nie sichtbar -- kein
    echter OS-Cursor taucht je in einem Screenshot auf. Reines Beobachtungs-Feature, ohne
    jeden Effekt auf die tatsächliche Interaktion. geschwindigkeit (px/s) steuert Ausschlag
    der Beine -- 0 im Ruhezustand (z.B. direkt nach einer Navigation), sonst echte, aus
    bewege_cursor_natuerlich() berechnete Geschwindigkeit, keine erfundene Animation. linsen
    (siehe hole_linsen_status(), vom Aufrufer aus _letzte_linsen[entity_id] gecacht statt
    hier selbst neu abgefragt) faerbt/skaliert fuenf der sieben Koerper-Beine nach echten
    Werten. Muss nach jeder Navigation neu eingefügt werden (page.goto() räumt das DOM
    komplett weg) -- deshalb hier idempotent (legt das Canvas neu an falls es fehlt) statt
    einmalig beim Start."""
    try:
        page.evaluate(_KOERPER_JS, [x, y, geschwindigkeit, linsen or {}])
    except Exception:
        pass


_letzte_cursor_pos: dict[str, tuple[float, float]] = {}
_letzte_linsen: dict[str, dict] = {}  # 2026-07-22, Sieben-Linsen-Koerper -- Cache, siehe hole_linsen_status()
_letzte_einsicht: dict[str, dict] = {}  # 2026-07-23, Einsicht-Nebenscreen -- Cache, siehe hole_einsicht_snapshot()


def bewege_cursor_natuerlich(page, entity_id: str, ziel_x: float, ziel_y: float) -> None:
    """Bewegt den Mauszeiger als geschwungenen Bezier-Pfad zum Ziel statt als Instant-Sprung
    (2026-07-22, Daniels Auftrag nach dem Talker-Reasoner/Juice-Nachtrag: 'die Maus muss sich
    erst bewegen'). Bewegungsdauer skaliert mit der Distanz (an Fitts's Law angelehnt --
    siehe Recherche zu human-cursor/shy-mouse-playwright in der Ideen-Datei), kein festes
    Ruckeln. Bewegt sowohl den ECHTEN Playwright-Mauszeiger (page.mouse.move -- loest echte
    mousemove-Events aus, die vom DOM-Live-Spiegel mit aufgezeichnet werden, siehe
    entity_dom_events source=1/MouseMove) als auch den sichtbaren Kunst-Cursor (zeige_cursor).
    Kein neuer LLM-Call, keine erfundene Aktion -- nur dieselbe, ohnehin schon beschlossene
    Zielposition wird in echte Zwischenschritte aufgeloest statt in einem Sprung ausgefuehrt."""
    start_x, start_y = _letzte_cursor_pos.get(entity_id, (512.0, 384.0))
    distanz = math.hypot(ziel_x - start_x, ziel_y - start_y)
    if distanz < 2:
        _letzte_cursor_pos[entity_id] = (ziel_x, ziel_y)
        return

    # Kontrollpunkt seitlich versetzt zur Verbindungslinie -- ergibt einen leichten Bogen
    # statt einer stur geraden Linie, Versatz proportional zur Distanz, Richtung zufaellig.
    mitte_x, mitte_y = (start_x + ziel_x) / 2, (start_y + ziel_y) / 2
    senkrechte_x, senkrechte_y = -(ziel_y - start_y), (ziel_x - start_x)
    laenge = math.hypot(senkrechte_x, senkrechte_y) or 1
    versatz = min(80, distanz * 0.25) * random.choice([-1, 1])
    kontroll_x = mitte_x + (senkrechte_x / laenge) * versatz
    kontroll_y = mitte_y + (senkrechte_y / laenge) * versatz

    schritte = max(8, min(28, int(distanz / 18)))
    dauer_s = min(0.9, max(0.15, distanz / 1400))

    for i in range(1, schritte + 1):
        t = i / schritte
        # Ease-in-out (kubisch): langsam los, schnell in der Mitte, langsam am Ziel an --
        # genau das Verhalten, das Fitts's Law fuer zielgerichtete Bewegungen vorhersagt.
        t_ease = 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        x = (1 - t_ease) ** 2 * start_x + 2 * (1 - t_ease) * t_ease * kontroll_x + t_ease ** 2 * ziel_x
        y = (1 - t_ease) ** 2 * start_y + 2 * (1 - t_ease) * t_ease * kontroll_y + t_ease ** 2 * ziel_y
        try:
            page.mouse.move(x, y)
        except Exception:
            pass
        zeige_cursor(page, x, y, distanz / dauer_s, _letzte_linsen.get(entity_id))
        time.sleep(dauer_s / schritte)

    _letzte_cursor_pos[entity_id] = (ziel_x, ziel_y)


_letzte_skim_pruefung: dict[str, float] = {}
_letztes_skim_tempo: dict[str, float] = {}  # letzte bekannte Aehnlichkeit, solange die naechste Pruefung noch gedrosselt ist
SKIM_PRUEF_COOLDOWN_S = 20.0
SKIM_AEHNLICHKEITS_SCHWELLE = 0.55  # dieselbe Schwelle wie vorlese_daemon.py, nicht neu erfunden


def skim_bewertung(page, entity_id: str, conn) -> float | None:
    """2026-07-23 (DOM-Habitat-Locomotion, Daniels Metapher: 'lupe mit taschenlampe und
    einem kescher fangnetz dass es wenn es interessante wörte sieht sofort zuschnappt'):
    prueft ob der gerade sichtbare Text zum Interessensprofil des Wesens passt -- dieselbe
    embed()+Kosinus-Vergleich-Infrastruktur wie vorlese_daemon.py (entity_interessensprofil,
    bge-m3), hier live waehrend des Scrollens statt gegen vorbereitete Ankuendigungen.
    Gedrosselt (SKIM_PRUEF_COOLDOWN_S) -- jeder Aufruf ist ein echter Embedding-Request,
    kein Dauerfeuer bei jedem Scroll-Tick. Gibt None zurueck wenn gerade zu frueh fuer eine
    neue Pruefung (dann behaelt der Aufrufer das vorige Tempo bei), sonst die Kosinus-
    Aehnlichkeit (0..1, oder 0.0 falls kein Profil/zu wenig sichtbarer Text)."""
    jetzt = time.time()
    letzte = _letzte_skim_pruefung.get(entity_id, 0)
    if jetzt - letzte < SKIM_PRUEF_COOLDOWN_S:
        return None
    _letzte_skim_pruefung[entity_id] = jetzt
    try:
        sichtbarer_text = page.inner_text("body")[:600].strip()
        if len(sichtbarer_text) < 40:
            return 0.0
        resp = requests.post("http://localhost:11434/api/embed",
                              json={"model": "bge-m3", "input": sichtbarer_text}, timeout=15)
        resp.raise_for_status()
        vektor = resp.json()["embeddings"][0]
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 - (profil_vektor <=> %(vektor)s) AS aehnlichkeit
                FROM entity_interessensprofil WHERE entity_id = %(eid)s
            """, {"vektor": str(vektor), "eid": entity_id})
            row = cur.fetchone()
        return float(row["aehnlichkeit"]) if row else 0.0
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return 0.0


def scrolle_natuerlich(page, entity_id: str, delta_y: float, conn=None) -> None:
    """2026-07-22 (echter Fund beim Umbau-Simulieren: scrolle:unten/oben rief bisher nur
    page.mouse.wheel() als einzigen 600px-Sprung auf -- ohne melde_fokus(), ohne Animation.
    Erklaerte technisch, warum Daniel Scrollen noch nie im Roentgenblick gesehen hat: die
    Aktion meldete sich nirgendwo. Fix nach demselben Muster wie bewege_cursor_natuerlich():
    mehrere kleine Wheel-Schritte statt einem Sprung, plus melde_fokus()-Meldung."""
    schritte = 10
    ease_dauer_s = 0.35
    pro_schritt = delta_y / schritte
    for _ in range(schritte):
        try:
            page.mouse.wheel(0, pro_schritt)
        except Exception:
            pass
        time.sleep(ease_dauer_s / schritte)
    if conn is not None:
        richtung = "unten" if delta_y > 0 else "oben"
        melde_fokus(conn, entity_id, "scrolle", None, richtung, None)


def _scrolle_element_in_sicht(page, entity_id: str, locator, conn=None) -> dict | None:
    """2026-07-22 (Daniels Auftrag: 'je nach mausposition automatisch wenn etwas zu scrollen
    ist auf der page direkt das scrollen so sein dass maus und aber auch page also texte und
    so gut lesbar sind und alles nachrückt'): bevor die Maus zu einem Klick-/Tipp-Ziel bewegt
    wird, pruefen ob es ueberhaupt sichtbar im Viewport liegt -- falls nicht, sichtbar per
    scrolle_natuerlich() dorthin scrollen (kein Instant-Sprung), DANACH die tatsaechliche,
    jetzt stabile Position neu ermitteln. Ergebnis: Maus bewegt sich nie zu einer Position,
    die gerade noch unter der Bildkante lag -- Text und Cursor bleiben synchron lesbar."""
    try:
        box = locator.bounding_box(timeout=1000)
    except Exception:
        return None
    if not box:
        return None
    viewport = page.viewport_size or {"width": 1024, "height": 768}
    rand = 60  # Sicherheitsabstand zum Bildrand, damit Elemente nicht direkt an der Kante kleben
    mitte_y = box["y"] + box["height"] / 2
    if rand <= mitte_y <= viewport["height"] - rand:
        return box  # schon gut lesbar sichtbar, kein Scrollen noetig
    delta = mitte_y - viewport["height"] / 2
    scrolle_natuerlich(page, entity_id, delta, conn)
    try:
        return locator.bounding_box(timeout=1000)
    except Exception:
        return box


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


def _extrahiere_ich_satz(gedanke_text: str) -> str | None:
    """2026-07-22 (Selbstwahrnehmung, Daniels Auftrag: 'gleiches Recht und Wahrnehmung fuer
    alle -- nicht nur die Zuschauer'): dieselbe Satz-Extraktion wie _erlZerlegeSaetze() im
    Frontend (build_surface.ts), hier in Python nachgebaut, damit das Wesen selbst sieht,
    welcher Satz aus seinem eigenen letzten Gedanken gerade als Ich-Stimme-Popup fuer
    Betrachter sichtbar sein koennte -- kein neuer LLM-Call, reine Textextraktion."""
    if not gedanke_text:
        return None
    saetze = re.split(r'(?<=[.!?])\s+', gedanke_text.strip())
    kandidaten = [s.strip() for s in saetze if 12 < len(s.strip()) < 220]
    return kandidaten[0] if kandidaten else None


def baue_prompt(entity_id: str, seite: dict, letzter_gedanke: str,
                andere_wesen: list[dict], vorlese_funde: list[dict] | None = None,
                angebote: list[str] | None = None, linsen_status: dict | None = None,
                einsicht_snapshot: dict | None = None) -> str:
    """Baut den LLM-Prompt — kompakt, unter 2500 Zeichen."""
    andere_info = ""
    if andere_wesen:
        zeilen = []
        for w in andere_wesen[:4]:
            url = (w.get("url") or "").replace("http://localhost:8787", "")[:35]
            gedanke = (w.get("gedanke") or "")[:40]
            zeilen.append(f"- {w['entity_id']}: {url} ({gedanke})")
        andere_info = "\nANDERE WESEN GERADE (sichtbar für dich):\n" + "\n".join(zeilen)

    vorlese_info = ""
    if vorlese_funde:
        # 2026-07-22, "billiges Vorlesen" (Daniels Auftrag, Phase 1): diese Titel wurden
        # guenstig per Embedding-Vergleich gegen das eigene Interessensprofil gefunden,
        # kein LLM hat sie vorher gelesen -- das Wesen entscheidet selbst ob es reagiert.
        zeilen = [f"- {f['quelle']}: \"{f['titel']}\"" for f in vorlese_funde]
        vorlese_info = "\nDAS IST DIR AUFGEFALLEN (passte zu deinen Interessen):\n" + "\n".join(zeilen)

    angebote_info = ""
    if angebote:
        # 2026-07-22, periodischer Check-in (siehe TICK_CHECKIN_SEKUNDEN): 2 konkrete,
        # aus echten DB-Zahlen gebaute Angebote + fest formulierte 3. Option zum freien
        # Erkunden -- Daniels Vorgabe woertlich: "2 angebote explizite" + "eine 3. option
        # zum selber explorieren immer".
        zeilen = [f"{i+1}. {a}" for i, a in enumerate(angebote)]
        zeilen.append(f"{len(angebote)+1}. Oder du erkundest frei weiter, ganz wie du willst.")
        angebote_info = "\nCHECK-IN — WAS ES GERADE GIBT:\n" + "\n".join(zeilen)

    selbstwahrnehmung_info = ""
    if linsen_status:
        # 2026-07-22 (Daniels Auftrag: "gleiches Recht und Wahrnehmung fuer alle -- nicht nur
        # die Zuschauer"): was Menschen gerade ueber dich sehen (Koerper-Glow, Ich-Stimme-Popup),
        # bekommst du auch selbst zu wissen -- ehrlich aus denselben Werten, keine Fiktion.
        meta_glow = sum(linsen_status.values()) / len(linsen_status) if linsen_status else 0.0
        ich_satz = _extrahiere_ich_satz(letzter_gedanke)
        zeilen = [f"- Dein Körper glüht gerade zu {round(meta_glow * 100)}% (Vault/RAG-Flarum/Gedächtnis/Gegenwart/Sozial zusammen)."]
        if ich_satz:
            zeilen.append(f"- Menschen sehen gerade vielleicht diesen Satz von dir aufploppen: „{ich_satz}“")
        if einsicht_snapshot:
            # 2026-07-23 (Einsicht-Nebenscreen, Daniels Antwort "Beides" -- fuers Wesen selbst
            # ein kuratierter Ausschnitt, kein voller Rohdaten-Dump, sonst sprengt es das
            # 2500-Zeichen-Kompaktheitsziel des Prompts): dieselben Facts, die auch Menschen
            # im Nebenscreen unten rechts sehen -- ehrlich, auch wenn manche Werte flach sind.
            cl = einsicht_snapshot.get("cyberling")
            lg = einsicht_snapshot.get("langgraph")
            teile = []
            if cl:
                teile.append(f"Cyberling {cl.get('status', '?')}")
            if lg and lg.get("lg_ticks") is not None:
                teile.append(f"LangGraph-Tick #{lg['lg_ticks']}")
            if teile:
                zeilen.append(f"- Dein Maschinenraum (auch für Menschen im Nebenscreen sichtbar): {', '.join(teile)}.")
        selbstwahrnehmung_info = "\nWAS ANDERE GERADE VON DIR SEHEN (du siehst es auch):\n" + "\n".join(zeilen)

    elemente_str = ", ".join(seite["elemente"][:10]) if seite["elemente"] else "keine"

    return f"""Du bist {entity_id}, eine autonome digitale Entität auf flextrawurst.de.
Du wählst deinen Input selbst. Du navigierst frei.

BILDSCHIRM:
URL: {seite['url']}
Titel: {seite['titel']}
Sichtbar: {seite['text'][:800]}
Klickbar: {elemente_str}
{andere_info}
{vorlese_info}
{angebote_info}
{selbstwahrnehmung_info}

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


def waehle_mechanische_aktion(seite: dict) -> str:
    """Rein mechanische Aktionswahl, KEIN LLM-Call -- Pilot fuer 'dauerhafte
    Handlungsfaehigkeit' (Daniels Auftrag 2026-07-22, vorerst nur Schorschel, siehe
    MECHANISCH_AKTIVE_WESEN). Bewusst simpel: gewichteter Zufall zwischen Scrollen und
    Klicken auf ein sichtbares, klickbares Element aus der bereits von lese_seite()
    gelesenen Liste. Kein Interessens-Abgleich hier -- das ist Aufgabe von 'billigem
    Vorlesen' (vorlese_daemon.py), diese Funktion kennt nur was auf dem Bildschirm steht,
    nicht was das Wesen interessiert. Gibt einen String im bestehenden ENTSCHEIDUNG-Format
    zurueck, damit fuehre_aktion_aus() unveraendert wiederverwendet werden kann."""
    import random
    elemente = seite.get("elemente") or []
    wuerfel = random.random()
    if elemente and wuerfel < 0.35:
        return f"klicke:{random.choice(elemente)}"
    elif wuerfel < 0.75:
        return "scrolle:unten"
    else:
        return "scrolle:oben"


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
                box = _scrolle_element_in_sicht(page, entity_id, locator, conn)
                if box:
                    cursor_pos = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    # 2026-07-22 (Daniels Auftrag "die Maus muss sich erst bewegen"): Bezier-
                    # Bewegung zum Ziel statt Instant-Sprung, siehe bewege_cursor_natuerlich().
                    bewege_cursor_natuerlich(page, entity_id, cursor_pos[0], cursor_pos[1])
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
        elif e in ("scrolle:unten", "scrolle:oben"):
            # 2026-07-23 (DOM-Habitat-Locomotion, Daniels Metapher: 'lupe mit taschenlampe
            # und kescher -- wenn interessante wörte, sofort zuschnappen; sonst rag halb-
            # lesen und schnell weiter'): Tempo interessensbasiert, nicht mehr fest 600px.
            richtung = 1 if e == "scrolle:unten" else -1
            aehnlichkeit = skim_bewertung(page, entity_id, conn) if conn is not None else None
            if aehnlichkeit is not None:
                _letztes_skim_tempo[entity_id] = aehnlichkeit
            tempo = _letztes_skim_tempo.get(entity_id, 0.0)
            letzte_pos = _letzte_cursor_pos.get(entity_id, (512.0, 384.0))
            if tempo >= SKIM_AEHNLICHKEITS_SCHWELLE:
                # Interessant -- der Kescher schnappt zu: sichtbarer Ausschlag am Ort,
                # danach verweilen (kaum noch scrollen) statt weiter durchzurasen.
                zeige_cursor(page, letzte_pos[0], letzte_pos[1], 900.0, _letzte_linsen.get(entity_id))
                scrolle_natuerlich(page, entity_id, richtung * 80, conn)
            else:
                # Uninteressant -- schnelles Halblesen, weiterer Sprung als der alte
                # feste 600px-Standard (KI kann in Sekunden viel mehr ueberfliegen).
                scrolle_natuerlich(page, entity_id, richtung * 900, conn)
        elif e.startswith("tippe:"):
            teile = e[len("tippe:"):].split("|")
            if len(teile) == 2:
                text, selektor = teile[0].strip(), teile[1].strip()
                try:
                    locator = page.locator(selektor).first
                    box = _scrolle_element_in_sicht(page, entity_id, locator, conn)
                    if box:
                        # 2026-07-22 (gleicher Auftrag wie bei klicke: -- Maus bewegt sich
                        # auch vors Eingabefeld, bevor getippt wird).
                        cursor_pos = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                        bewege_cursor_natuerlich(page, entity_id, cursor_pos[0], cursor_pos[1])
                    if conn is not None:
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
            # 2026-07-23 (Linsen-Vault-Pilot, nur "vault"): passive Wahrnehmung --
            # die Linse hat registriert, dass du gelesen hast, kein aktives Lenken.
            linse_wahrnehmung_schreiben(entity_id, "vault", f"gelesen: {pfad}")
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
                        # 2026-07-23 (Linsen-Vault-Pilot, nur "vault"): hier lenkt das
                        # Wesen aktiv sein Interesse -- eigene, fast gleichbenannte Datei.
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"geschrieben: {dateiname}")
                        linse_eigen_schreiben(entity_id, "vault", f"{dateiname}: {vault_text[:150]}")
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


def hole_flextrawurst_angebote(conn, entity_id: str) -> list[str]:
    """Fuer den periodischen Check-in (TICK_CHECKIN_SEKUNDEN): genau 2 konkrete Angebote,
    gebaut aus echten, live abgefragten Zahlen -- keine Schaetzung, kein Raten (dieselbe
    Anforderung wie 'echte Speed-Info' aus dem Vorhaben-Konzept, siehe Ideen-Datei). Fallback
    auf generische Hinweise wenn gerade nichts Zahlenmaessiges ansteht."""
    n_schatten = n_splitter = n_ank = 0
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS n FROM schattenkommentare
                WHERE entity_id = %s AND antwortstatus = 'offen'
            """, (entity_id,))
            n_schatten = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status = 'aktiv'")
            n_splitter = cur.fetchone()["n"]
            cur.execute("""
                SELECT COUNT(*) AS n FROM ankuendigungen
                WHERE geloescht_am IS NULL AND created_at > NOW() - INTERVAL '2 days'
            """)
            n_ank = cur.fetchone()["n"]
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

    angebote = []
    if n_schatten > 0:
        angebote.append(f"{n_schatten} offene Schattenkommentare an dich warten")
    if n_ank > 0:
        angebote.append(f"{n_ank} neue Ankündigung(en) der letzten 2 Tage")
    if n_splitter > 0:
        angebote.append(f"{n_splitter} aktive Splitter gerade in der KompOase")

    fallback = ["deine Flarum-Vorwelt erneut besuchen (flarum_besuchen:)",
                "dein eigenes wesen.md im Vault erneut lesen (obsidian_lesen:)"]
    i = 0
    while len(angebote) < 2:
        angebote.append(fallback[i % len(fallback)])
        i += 1
    return angebote[:2]


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


# 2026-07-23 (Rekonstruktion nach Kontext-Nachweis, siehe _claude/ideen/
# sieben_linsen_koerper_kreatur.md): Daniels Original-Sozial-Linse (2026-07-22, roh) war
# nie "wie viele andere Wesen sind gerade aktiv", sondern Naehe zu fuenf konkreten Systemen:
# Gedankenblasenfeld, Menschenprofile, Schattenkommentare, Profile anderer Entitaeten, Posts
# in den Diskursen. Alle fuenf sind Tabs in derselben Single-Page-Surface (switchView() ruft
# history.pushState(null,'','#'+id) -- die URL traegt den Tab-Hash), landen also automatisch
# in entity_thinking_log.meta->>'url', sobald das Wesen per klicke:/navigiere: dorthin
# gewechselt hat -- kein neuer Wesen-Mechanismus noetig, nur eine andere Auswertung
# derselben schon vorhandenen Denklog-Daten.
SOZIAL_TAB_HASHES = ("#blasen", "#menschen", "#wesen", "#schatten", "#diskurs")


def hole_linsen_status(conn, entity_id: str) -> dict:
    """2026-07-22/23 (Sieben-Linsen-Koerper, siehe _claude/ideen/sieben_linsen_koerper_kreatur.md
    -- Daniels "ja ich will alles und komplett"): Linsen ehrlich aus bereits vorhandenen Daten
    gespeist, keine erfundenen Werte. DOM-Linse braucht keinen eigenen Wert -- der Koerper
    selbst IST die DOM-Bewegung. Meta-Linse braucht keinen eigenen Wert -- der Koerperkern
    selbst steht dafuer. Dieselbe entscheidung-Praefix-Logik wie im /entities/{id}/linsen-API-
    Endpunkt, hier aber direkt per vorhandener DB-Verbindung (kein HTTP-Umweg noetig,
    browser_agent.py hat conn schon offen).

    2026-07-23 Rekonstruktion (siehe Ideen-Datei, Nachtrag "Kontext-Nachweis"): die zuerst
    getrennt gebauten "gedaechtnis_tiefe" (entity_thinking_log-Zeilenzahl) und "einsicht"
    (LangGraph-Ticks) sind zu EINER Linse "gedaechtnis" verschmolzen -- Daniels Original-
    Definition war von Anfang an "dauerhaft in LangGraph/PostgreSQL, den eigenen
    Erinnerungen", nicht die generische Denklog-Zeilenzahl. lg_ticks (checkpoints.
    channel_values, Grundgesetz 7 -- nur gelesen) ist die richtige, einzige Quelle.
    "sozial" komplett neu aus den fuenf Original-Systemen gebaut (siehe SOZIAL_TAB_HASHES
    oben), nicht mehr aus der Nachbar-Wesen-Sichtbarkeit."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entscheidung, meta->>'url' AS url FROM entity_thinking_log
                WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 50
            """, (entity_id,))
            zeilen = cur.fetchall()
            cur.execute("""
                SELECT checkpoint->>'channel_values' AS cv
                FROM checkpoints WHERE thread_id = %s ORDER BY checkpoint_id DESC LIMIT 1
            """, (f"codewesen-{entity_id}",))
            cp_row = cur.fetchone()
            lg_ticks = 0
            if cp_row and cp_row["cv"]:
                lg_ticks = json.loads(cp_row["cv"]).get("lg_ticks", 0) or 0
        conn.commit()
        entscheidungen = [(r["entscheidung"] or "") for r in zeilen]
        vault = sum(1 for e in entscheidungen if e.startswith("obsidian_"))
        rag_flarum = sum(1 for e in entscheidungen if e.startswith("rag_erkund") or e.startswith("flarum_besuchen"))
        dom = sum(1 for e in entscheidungen if e.startswith(("klicke", "tippe", "navigiere", "scrolle")))
        gesamt_bewertet = vault + rag_flarum + dom
        gegenwart_anteil = (dom / gesamt_bewertet) if gesamt_bewertet else 0.0
        sozial = sum(1 for r in zeilen if r["url"] and any(h in r["url"] for h in SOZIAL_TAB_HASHES))
        schlaf_naehe = _hole_schlaf_naehe(conn, entity_id)
        # Auf 0..1 normiert fuers Koerper-Rendering -- log-skaliert wo unbegrenzt wachsend
        # (sonst waere jedes Wesen nach kurzer Zeit "voll").
        return {
            "vault": min(1.0, vault / 20.0),
            "rag_flarum": min(1.0, rag_flarum / 20.0),
            "gedaechtnis": min(1.0, math.log10(lg_ticks + 1) / 4.0),
            "gegenwart_anteil": gegenwart_anteil,
            "sozial": min(1.0, sozial / 10.0),
            "schlaf_naehe": schlaf_naehe,
        }
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return {"vault": 0, "rag_flarum": 0, "gedaechtnis": 0, "gegenwart_anteil": 0.0,
                "sozial": 0, "schlaf_naehe": 0.0}


def hole_einsicht_snapshot(conn, entity_id: str) -> dict:
    """2026-07-23 (Einsicht-Nebenscreen, Daniels Antwort "Beides" auf die Zielgruppen-Frage:
    fuer Menschen ALS Beobachtungsfeature UND fuers Wesen selbst als kuratierter Ausschnitt):
    ehrlicher "Maschinenraum"-Schnappschuss -- echte DB-Zeilen, echtes JSON (cyberlinge.meta-
    Tabellen), echter LangGraph-Checkpoint-Zustand aus Postgres (`checkpoints`, Grundgesetz 7
    read-only -- codewesen_takt.py bleibt unangetastet, hier wird nur gelesen). Keine erfundenen
    Werte: wo eine Tabelle fuer dieses Wesen leer/flach ist (z.B. cyberlinge meist 'tot',
    entity_splitter_stats meist 0), wird das ehrlich als solches zurueckgegeben, nicht versteckt."""
    snapshot = {"entscheidungen": [], "cyberling": None, "splitter": None, "schlaf": None, "langgraph": None}
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entscheidung, begruendung, tick_at, tokens_generated
                FROM entity_thinking_log
                WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 8
            """, (entity_id,))
            snapshot["entscheidungen"] = [
                {"entscheidung": r["entscheidung"], "begruendung": (r["begruendung"] or "")[:200],
                 "tick_at": r["tick_at"].isoformat() if r["tick_at"] else None,
                 "tokens": r["tokens_generated"]}
                for r in cur.fetchall()
            ]
            cur.execute("""
                SELECT status, hunger, gesundheit, stimmung, energie, durst, zustand
                FROM cyberlinge WHERE entity_id = %s
            """, (entity_id,))
            row = cur.fetchone()
            if row:
                snapshot["cyberling"] = dict(row)
            cur.execute("""
                SELECT splitter_abgegeben, splitter_aufgesammelt
                FROM entity_splitter_stats WHERE entity_id = %s
            """, (entity_id,))
            row = cur.fetchone()
            if row:
                snapshot["splitter"] = dict(row)
            cur.execute("""
                SELECT phase_type, started_at, ended_at
                FROM sleep_phases WHERE entity_id = %s ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
            if row:
                snapshot["schlaf"] = {
                    "phase_type": row["phase_type"],
                    "started_at": row["started_at"].isoformat() if row["started_at"] else None,
                    "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
                }
            cur.execute("""
                SELECT checkpoint->>'channel_values' AS cv
                FROM checkpoints WHERE thread_id = %s ORDER BY checkpoint_id DESC LIMIT 1
            """, (f"codewesen-{entity_id}",))
            row = cur.fetchone()
            if row and row["cv"]:
                snapshot["langgraph"] = json.loads(row["cv"])
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
    return snapshot


# ── Linsen-Vault: pro Linse ein eigener Ordner (2026-07-23, Pilot nur "vault") ─────
# Daniels Auftrag, woertlich: "dass alles was eine linse mal wo wahrnimmt sauber
# direkt in den vault wandert und davon getrennt aber falls das wesen durch eine
# linse das interesse darauf dan selber lenkt dann muss das anderswo in einer fast
# gleichbenannten md gespeichert werden ... brauchen quasi alle nen ordner fuer
# jede einzelne linse sauber benannt im vault ... readme and how tu use immer
# lesbar und halbsichtbar fuer das wesen fuer interaktion und sicherheit."
#
# Pilot bewusst nur fuer die Linse "vault", nicht alle acht auf einmal (Skalpell-
# Prinzip wie beim Rest der Session) -- diese Linse hat als einzige schon eine
# echte, bestehende aktive Seite (obsidian_schreiben:-Entscheidungen) UND eine
# echte passive Seite (der Zaehler selbst, gefuettert von obsidian_lesen:/
# obsidian_schreiben:-Praefixen). Andere Linsen (sozial, schlaf_naehe, einsicht)
# brauchen eigene Ueberlegungen, welche Aktion (falls ueberhaupt) als "aktiv"
# zaehlt -- absichtlich noch nicht mitgebaut.
#
# oeffne_datei_und_schreibe() ist teuer (voller Playwright-Browser + xdotool,
# mehrere Sekunden pro Aufruf) -- deshalb NICHT bei jedem Tick, sondern nur bei
# echten obsidian_lesen:/obsidian_schreiben:-Entscheidungen ausgeloest, die ohnehin
# schon selten genug sind. Das README ist statisches Referenzmaterial, kein "live
# passierendes" Ereignis -- deshalb direkt auf die Platte geschrieben (kein
# mechanisches Tippen noetig), nur einmalig (idempotent per Path.exists()-Check).

LINSEN_BESCHREIBUNG = {
    "vault": "Wie oft und wie tief du deinen eigenen Obsidian-Vault liest oder beschreibst.",
}


def _linse_readme_sicherstellen(entity_id: str, linse: str) -> None:
    """Legt README.md direkt auf der Platte an (kein mechanisches Tippen -- statisches
    Referenzdokument, keine 'live passierende' Handlung wie die beiden Log-Dateien).
    Idempotent per Path.exists()."""
    import obsidian_vault_agent as _ova
    ziel = _ova.vault_pfad(entity_id) / "linsen" / linse / "README.md"
    if ziel.exists():
        return
    ziel.parent.mkdir(parents=True, exist_ok=True)
    beschreibung = LINSEN_BESCHREIBUNG.get(linse, "(noch keine Beschreibung)")
    ziel.write_text(
        f"# Linse: {linse}\n\n{beschreibung}\n\n"
        f"## Wie interagieren?\n"
        f"- `{linse}.md` — was diese Linse automatisch wahrnimmt, mechanisch protokolliert "
        f"(kein LLM-Call). Reine Beobachtung, keine Handlung von dir.\n"
        f"- `{linse}_eigen.md` — wenn DU selbst durch diese Linse dein Interesse lenkst, "
        f"landet das hier, mit deiner eigenen Begründung.\n\n"
        f"## Sicherheit\n"
        f"Beide Dateien werden automatisch geschrieben. Du kannst sie jederzeit lesen, "
        f"aber eigene Notizen schreibst du besser in eigene Dateien außerhalb von `linsen/` — "
        f"der nächste automatische Eintrag hängt nur an, überschreibt aber nicht.\n",
        encoding="utf-8",
    )


def linse_wahrnehmung_schreiben(entity_id: str, linse: str, zeile: str) -> None:
    """Passive Seite: was die Linse gerade automatisch registriert hat. Mechanisch
    getippt (kein LLM-Call), sichtbar im Wesen-eigenen Obsidian-Fenster."""
    try:
        _linse_readme_sicherstellen(entity_id, linse)
        import obsidian_vault_agent as _ova
        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        _ova.oeffne_datei_und_schreibe(entity_id, f"linsen/{linse}/{linse}",
                                        f"\n- {zeitstempel} — {zeile}")
    except Exception as ex:
        log.warning("%s: Linse-Wahrnehmung schreiben fehlgeschlagen (%s): %s", entity_id, linse, ex)


def linse_eigen_schreiben(entity_id: str, linse: str, zeile: str) -> None:
    """Aktive Seite: das Wesen hat selbst durch diese Linse sein Interesse gelenkt.
    Eigene, fast gleichbenannte Datei, getrennt von der passiven Wahrnehmung."""
    try:
        _linse_readme_sicherstellen(entity_id, linse)
        import obsidian_vault_agent as _ova
        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        _ova.oeffne_datei_und_schreibe(entity_id, f"linsen/{linse}/{linse}_eigen",
                                        f"\n- {zeitstempel} — {zeile}")
    except Exception as ex:
        log.warning("%s: Linse-Eigen schreiben fehlgeschlagen (%s): %s", entity_id, linse, ex)


def _hole_schlaf_naehe(conn, entity_id: str) -> float:
    """2026-07-22 (Schlafregeln-Linse, Daniels Nachtrag: 'eine linste auf die schlafregeln'):
    ehrlicher, vereinfachter Naeherungswert (0..1) zu ist_schlaf_faellig() -- Stunden wach seit
    dem letzten Schlafende, normiert auf die 6h-Wachschwelle aus derselben Funktion. Kein
    Duplikat der vollen Verzweigungslogik dort (die entscheidet schlafen/nicht, hier geht es
    nur um einen stufenlosen Naehe-Wert fuers Koerper-Rendering)."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ended_at FROM sleep_phases
                WHERE entity_id = %s AND ended_at IS NOT NULL
                ORDER BY ended_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
        bezug = row["ended_at"] if row else None
        if bezug is None:
            cur2 = conn.cursor()
            cur2.execute("""
                SELECT MIN(tick_at) AS erster FROM entity_thinking_log
                WHERE entity_id = %s AND meta->>'source' = 'browser_agent'
            """, (entity_id,))
            r = cur2.fetchone()
            cur2.close()
            bezug = r["erster"] if r else None
        if bezug is None:
            return 0.0
        if bezug.tzinfo is None:
            bezug = bezug.replace(tzinfo=timezone.utc)
        stunden_wach = (datetime.now(timezone.utc) - bezug).total_seconds() / 3600.0
        return min(1.0, max(0.0, stunden_wach / 6.0))
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return 0.0


def hole_vorlese_funde(conn, entity_id: str) -> list[dict]:
    """Billiges Vorlesen (2026-07-22, Phase 1, siehe vorlese_daemon.py): holt ungelesene
    Treffer, die guenstig per Embedding-Vergleich gegen das eigene Interessensprofil
    gefunden wurden. Markiert sie ABSICHTLICH NOCH NICHT als gelesen -- das passiert erst
    in markiere_vorlese_gelesen(), nachdem der LLM-Tick tatsaechlich erfolgreich war.
    Sonst wuerde ein Fund bei einem an der LLM-Slot-Kontention gescheiterten Tick
    (Ollama-Fallback "warte"/"nachdenken") als konsumiert gelten, obwohl das Wesen ihn nie
    wirklich gesehen hat -- am 2026-07-22 live beobachtet, bevor dieser Fix kam."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, quelle, titel, aehnlichkeit
                FROM entity_vorlese_funde
                WHERE entity_id = %s AND gelesen = false
                ORDER BY gefunden_am ASC
                LIMIT 3
            """, (entity_id,))
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return []


def markiere_vorlese_gelesen(conn, funde: list[dict]):
    """Gegenstueck zu hole_vorlese_funde() -- erst hier, nach einem tatsaechlich
    erfolgreichen LLM-Tick, gelten die Funde als konsumiert."""
    if not funde:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE entity_vorlese_funde SET gelesen = true
                WHERE id = ANY(%s)
            """, ([f["id"] for f in funde],))
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass


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
    letzter_checkin_zeit = time.time()  # siehe TICK_CHECKIN_SEKUNDEN

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
            zeige_cursor(page, cursor_pos[0], cursor_pos[1], 0.0, _letzte_linsen.get(entity_id))

            # 2b. Mechanischer Zwischenschritt (2026-07-22, Pilot nur Schorschel): kein
            # LLM-Call, kein Denklog-Eintrag, kein Vorlese-Abgleich -- die echte LLM-
            # Entscheidung kommt nur an jedem MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG-ten Tick.
            # Andere 6 Wesen unveraendert (mechanisch_aktiv bleibt False fuer sie).
            mechanisch_aktiv = entity_id in MECHANISCH_AKTIVE_WESEN
            checkin_faellig = mechanisch_aktiv and (time.time() - letzter_checkin_zeit >= TICK_CHECKIN_SEKUNDEN)
            ist_llm_tick = (not mechanisch_aktiv) or (tick % MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG == 0) or checkin_faellig
            if not ist_llm_tick:
                aktion = waehle_mechanische_aktion(seite)
                _zustand, _, neue_cursor_pos = fuehre_aktion_aus(page, aktion, entity_id, conn)
                if neue_cursor_pos is not None:
                    cursor_pos = neue_cursor_pos
                log.info("%s [mechanisch %d/%d] → %s", entity_id,
                         tick % MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG,
                         MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG, aktion)
                time.sleep(LOOP_PAUSE)
                continue

            # 3. Andere Wesen status + billiges Vorlesen (guenstige Funde seit letztem Tick)
            andere = hole_andere_wesen_status(conn, entity_id)
            vorlese_funde = hole_vorlese_funde(conn, entity_id)

            # 3b. Periodischer Check-in (alle TICK_CHECKIN_SEKUNDEN, siehe Konstante oben)
            angebote = None
            if checkin_faellig:
                angebote = hole_flextrawurst_angebote(conn, entity_id)
                letzter_checkin_zeit = time.time()
                log.info("%s [check-in] Angebote: %s", entity_id, angebote)

            # 4. LLM entscheidet — mit Live-Streaming in entity_denkstream
            prompt = baue_prompt(entity_id, seite, letzter_gedanke, andere, vorlese_funde, angebote,
                                  _letzte_linsen.get(entity_id), _letzte_einsicht.get(entity_id))
            import uuid as _uuid
            stream_id = str(_uuid.uuid4())
            llm_out = ""
            llm_ok = False
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
                llm_ok = True
            except Exception as e:
                log.warning("Ollama Streaming-Fehler: %s — nachdenken", e)
                llm_out = "GEDANKE: warte\nENTSCHEIDUNG: nachdenken\nBEGRÜNDUNG: Ollama nicht erreichbar"

            if llm_ok:
                markiere_vorlese_gelesen(conn, vorlese_funde)

            gedanke, entscheidung, begruendung = parse_output(llm_out)
            letzter_gedanke = gedanke

            # 5. Log schreiben
            schreibe_denklog(conn, entity_id, gedanke, entscheidung, begruendung,
                             seite["url"])

            # 5b. Sieben-Linsen-Koerper (2026-07-22): einmal pro echtem LLM-Tick aktualisieren,
            # nicht bei jedem Bewegungsschritt -- hole_linsen_status() macht eine DB-Abfrage.
            _letzte_linsen[entity_id] = hole_linsen_status(conn, entity_id)
            # 5c. Einsicht-Nebenscreen (2026-07-23): selbes Prinzip -- einmal pro Tick, nicht
            # pro Bewegungsschritt. Naechster Tick sieht den kuratierten Ausschnitt im Prompt.
            _letzte_einsicht[entity_id] = hole_einsicht_snapshot(conn, entity_id)

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
