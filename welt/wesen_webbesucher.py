#!/usr/bin/env python3
"""
Wesen-Webbesucher Daemon
- Wartet auf Einträge in wesen_web_besuche mit reaktion IS NULL
- Öffnet die URL mit Playwright (headless Chromium)
- Macht Screenshot + extrahiert Text
- Generiert Wesen-Reaktion via Ollama
- Speichert alles zurück in wesen_web_besuche
"""
import io
import json
import logging
import os
import sys
import time
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [webbesucher] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/welt/webbesucher.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("webbesucher")

_env_file = Path("/root/werkraum/.agent/flextrawurst-db.env")
DB_URI = ""
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e2b-it-q4_K_M"
POLL_INTERVAL = 30


def _load_db_uri():
    global DB_URI
    if _env_file.exists():
        for line in _env_file.read_text().splitlines():
            if line.startswith("FLEXTRAWURST_DB_URI="):
                DB_URI = line.split("=", 1)[1]
                return
    DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "")


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)


def check_web_besuche_aktiv(conn) -> bool:
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT value FROM system_flags WHERE key='web_besuche_aktiv'")
            row = cur.fetchone()
            return row and row["value"] == "true"
    except Exception:
        return False


def hol_naechsten_besuch(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, wesen_name, url FROM wesen_web_besuche
            WHERE reaktion IS NULL AND seiten_text IS NULL
            ORDER BY visited_at ASC LIMIT 1
        """)
        return cur.fetchone()


def besuche_url(url: str) -> tuple[bytes | None, str]:
    """Öffnet URL mit Playwright. Gibt (screenshot_bytes, text) zurück."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            screenshot = page.screenshot(type="png", full_page=False)
            text = page.inner_text("body")[:3000]
            browser.close()
            return screenshot, text
    except Exception as e:
        log.warning(f"Playwright-Fehler für {url}: {e}")
        return None, f"[Fehler beim Laden: {e}]"


def generiere_reaktion(wesen_name: str, url: str, seiten_text: str) -> str:
    prompt = f"""Du bist {wesen_name}, ein Codewesen.
Daniel hat dich gebeten, diese Webseite zu besuchen: {url}

Was du auf der Seite gesehen hast (Auszug):
{seiten_text[:2000]}

Schreibe deine ehrliche Reaktion auf das Gesehene. 2-4 Sätze. Ich-Form. Keine Zusammenfassung — deine Impression."""
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.75, "num_predict": 400, "num_ctx": 4096, "num_thread": 6}
        }, timeout=180)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"[Reaktion fehlgeschlagen: {e}]"


def verarbeite_besuch(conn, besuch: dict):
    bid = besuch["id"]
    wesen_name = besuch["wesen_name"]
    url = besuch["url"]
    log.info(f"Besuche {url} für {wesen_name}…")

    screenshot, text = besuche_url(url)
    reaktion = generiere_reaktion(wesen_name, url, text)

    with conn.cursor() as cur:
        cur.execute("""
            UPDATE wesen_web_besuche
            SET screenshot=%s, seiten_text=%s, reaktion=%s
            WHERE id=%s
        """, (psycopg2.Binary(screenshot) if screenshot else None, text, reaktion, bid))
        cur.execute("""
            INSERT INTO entity_denkstream (entity_id, source, inhalt, created_at)
            VALUES (%s, 'web_besuch', %s, NOW())
        """, (wesen_name, f"[WEB-BESUCH] {url}\n\n{reaktion}"))
    conn.commit()
    log.info(f"  Reaktion gespeichert ({len(reaktion)} Zeichen)")


def run():
    _load_db_uri()
    if not DB_URI:
        log.error("DB_URI nicht gefunden — abbruch")
        sys.exit(1)

    log.info("Wesen-Webbesucher gestartet")
    while True:
        try:
            conn = get_conn()
            if not check_web_besuche_aktiv(conn):
                conn.close()
                time.sleep(POLL_INTERVAL)
                continue
            besuch = hol_naechsten_besuch(conn)
            if besuch:
                verarbeite_besuch(conn, besuch)
            conn.close()
        except Exception as e:
            log.error(f"Hauptloop-Fehler: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
