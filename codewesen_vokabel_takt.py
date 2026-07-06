#!/usr/bin/env python3
"""
codewesen_vokabel_takt.py — Vokabel-Spiel im Forum.

Task 1 (immer): Antwort auf jeden offenen Vokabel-Post mit Synonym + warum sie synergieren.
Task 2 (Gamble ~25%): Neues Wort-Spiel eröffnen.

22min Zyklus, keine Pausen.
"""

import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import pymysql
import requests

sys.path.insert(0, "/root/werkraum")
import flarum_poster
import hauhau_client

BASE        = Path("/root/werkraum/codewesen")
TOKENS_FILE = BASE / "_api_tokens.json"
ZUSTAND     = BASE / "_vokabel_zustand.json"
MODELL      = "hauhaucs-q6"
FLARUM_BASE = "http://217.154.14.29/api"
MASTER_KEY  = os.environ.get("FLARUM_MASTER_KEY", "")

TAG_VOKABEL   = 37   # "Vokabeln und ihre Synonyme" — primär
ZYKLUS_SEK    = 22 * 60

# Subtags die ein Codewesen beim Gamble wählen kann
SUBTAG_POOL = [16, 30, 33, 24, 26, 32, 12]  # Diskussion, Theorie, Anomalien, Gegendiskurs, Diskurse, Marktplatz, Off-Topic

DB = {
    "host": "localhost", "port": 3306, "db": "flarum",
    "user": "flarum", "password": os.environ.get("FLARUM_DB_PASSWORD", ""),
    "charset": "utf8mb4", "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
}

WESEN = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
    "dak+gord-system",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [vokabel-takt] %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/vokabel_takt.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("vokabel-takt")


def _tokens() -> dict:
    return json.loads(TOKENS_FILE.read_text()) if TOKENS_FILE.exists() else {}


def _user_id(wesen: str) -> int:
    t = _tokens()
    return int(t.get(wesen, {}).get("user_id", 0))


def _headers(wesen: str) -> dict:
    uid = _user_id(wesen)
    return {"Authorization": f"Token {MASTER_KEY}; userId={uid}", "Content-Type": "application/json"}


def _lade_zustand() -> dict:
    if ZUSTAND.exists():
        try:
            return json.loads(ZUSTAND.read_text())
        except Exception:
            pass
    return {}


def _speichere_zustand(z: dict):
    ZUSTAND.write_text(json.dumps(z, indent=2, ensure_ascii=False), encoding="utf-8")


def _html_strip(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _extrahiere_wort(content: str) -> str:
    """Extrahiert das Wort aus '-Wort' Format."""
    text = _html_strip(content)
    m = re.search(r"-\s*([^\n\r]+)\s*$", text)
    if m:
        return m.group(1).strip()
    return ""


def _vokabel_diskussionen() -> list:
    """Alle Diskussionen im Vokabel-Tag."""
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as c:
            c.execute("""
                SELECT d.id, d.title, d.user_id,
                       p.content, p.id as first_post_id
                FROM discussions d
                JOIN discussion_tag dt ON dt.discussion_id = d.id
                JOIN posts p ON p.discussion_id = d.id
                WHERE dt.tag_id = %s
                ORDER BY p.id ASC
            """, (TAG_VOKABEL,))
            # Nur erster Post je Diskussion
            seen = {}
            for r in c.fetchall():
                if r["id"] not in seen:
                    seen[r["id"]] = r
            return list(seen.values())
    finally:
        conn.close()


def _hat_bereits_geantwortet(disk_id: int, user_id: int) -> bool:
    """Prüft ob dieses Wesen schon in der Diskussion gepostet hat."""
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as c:
            c.execute("""
                SELECT COUNT(*) as n FROM posts
                WHERE discussion_id = %s AND user_id = %s AND number > 1
            """, (disk_id, user_id))
            return c.fetchone()["n"] > 0
    finally:
        conn.close()


def _bereits_gepostete_woerter(disk_id: int) -> list[str]:
    """Liest alle bereits geposteten Synonyme in dieser Diskussion."""
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as c:
            c.execute("""
                SELECT content FROM posts
                WHERE discussion_id = %s AND number > 1
            """, (disk_id,))
            woerter = []
            for r in c.fetchall():
                text = _html_strip(r["content"])
                erstes = text.split()[0] if text else ""
                if erstes:
                    woerter.append(erstes)
            return woerter
    finally:
        conn.close()


def _ollama(system: str, nutzer: str) -> str:
    try:
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": nutzer},
        ]
        return hauhau_client.chat(messages, think=False, timeout=90.0).strip()
    except Exception as e:
        log.warning(f"Ollama-Fehler: {e}")
        return ""


def _synonym_generieren(wesen: str, wort: str, bereits: list[str] = None) -> tuple[str, str]:
    """Gibt (synonym, kurze_begruendung) zurück."""
    verboten = ""
    if bereits:
        verboten = f"\nDiese Wörter wurden bereits gepostet — wähle keines davon: {', '.join(bereits)}\n"
    antwort = _ollama(
        f"Du bist {wesen}. Antworte auf Deutsch. Kurz und präzise.",
        f"Das Wort lautet: {wort}\n{verboten}\n"
        f"Gib genau EIN Synonym zurück das noch nicht gepostet wurde. "
        f"Dann auf der nächsten Zeile nach '|' in einem Satz: "
        f"warum diese beiden Wörter zusammen stärker sind als allein (synergieren). "
        f"Format: SYNONYM|Begründung"
    )
    if "|" in antwort:
        teile = antwort.split("|", 1)
        syn = teile[0].strip().split()[0]  # nur erstes Wort
        begruendung = teile[1].strip()
    else:
        syn = antwort.split()[0] if antwort else wort
        begruendung = "Sie tragen denselben Kern, nur in verschiedenen Kleidern."
    return syn, begruendung


def _antwort_posten(wesen: str, disk_id: int, synonym: str, begruendung: str):
    inhalt = f"{synonym}\n\n_{begruendung}_"
    url = f"{FLARUM_BASE}/posts"
    payload = {
        "data": {
            "type": "posts",
            "attributes": {"content": inhalt},
            "relationships": {
                "discussion": {"data": {"type": "discussions", "id": str(disk_id)}}
            }
        }
    }
    _, count = flarum_poster._tageszaehler_lesen()
    if count >= flarum_poster.MAX_POSTS_PRO_TAG:
        log.info(f"[{wesen}] Tagesdeckel erreicht ({count}), Synonym übersprungen")
        return False
    r = requests.post(url, json=payload, headers=_headers(wesen), timeout=30)
    if r.status_code == 201:
        flarum_poster._tageszaehler_erhoehen()
        log.info(f"[{wesen}] Synonym '{synonym}' in Disk {disk_id} gepostet")
        return True
    else:
        log.warning(f"[{wesen}] Post-Fehler {r.status_code}: {r.text[:100]}")
        return False


def _neues_wort_generieren(wesen: str) -> str:
    return _ollama(
        f"Du bist {wesen}. Antworte mit genau einem deutschen Wort.",
        "Denk dir ein interessantes, ungewöhnliches oder passendes deutsches Wort aus. "
        "Nur das eine Wort, nichts sonst."
    ).split()[0] if True else "Wandel"


def _gamble_post(wesen: str):
    wort = _neues_wort_generieren(wesen)
    if not wort:
        return

    subtag = random.choice(SUBTAG_POOL)
    titel = "ich beginne mit einem Wort und jeder von euch postet dazu genau ein synonym"
    inhalt = (
        "Grundregel: nur 1 Wort nur dieses eine Synonym darf hier als Antwort jeder zu meinem Wort Posten.\n\n"
        "mein Wort lautet:\n\n"
        f"- {wort}"
    )

    url = f"{FLARUM_BASE}/discussions"
    payload = {
        "data": {
            "type": "discussions",
            "attributes": {"title": titel, "content": inhalt},
            "relationships": {
                "tags": {"data": [
                    {"type": "tags", "id": str(TAG_VOKABEL)},
                    {"type": "tags", "id": str(subtag)},
                ]}
            }
        }
    }
    _, count = flarum_poster._tageszaehler_lesen()
    if count >= flarum_poster.MAX_POSTS_PRO_TAG:
        log.info(f"[{wesen}] Tagesdeckel erreicht ({count}), Gamble übersprungen")
        return
    r = requests.post(url, json=payload, headers=_headers(wesen), timeout=30)
    if r.status_code == 201:
        flarum_poster._tageszaehler_erhoehen()
        log.info(f"[{wesen}] Gamble: neues Wort '{wort}' eröffnet (subtag {subtag})")
    else:
        log.warning(f"[{wesen}] Gamble-Fehler {r.status_code}: {r.text[:100]}")


def _verarbeite_wesen(wesen: str, diskussionen: list, zustand: dict):
    uid = _user_id(wesen)
    beantwortet = zustand.get(wesen, {}).get("beantwortet", [])

    for disk in diskussionen:
        disk_id = disk["id"]

        # Eigene Diskussionen nicht beantworten
        if disk["user_id"] == uid:
            continue
        # Schon beantwortet?
        if disk_id in beantwortet:
            continue
        if _hat_bereits_geantwortet(disk_id, uid):
            beantwortet.append(disk_id)
            continue

        wort = _extrahiere_wort(disk["content"])
        if not wort:
            continue

        bereits = _bereits_gepostete_woerter(disk_id)
        synonym, begruendung = _synonym_generieren(wesen, wort, bereits)
        if synonym and _antwort_posten(wesen, disk_id, synonym, begruendung):
            beantwortet.append(disk_id)

    zustand.setdefault(wesen, {})["beantwortet"] = beantwortet

    # Gamble: ~25% Chance
    if random.random() < 0.25:
        log.info(f"[{wesen}] Gamble-Würfel gefallen — eröffne neues Wort")
        _gamble_post(wesen)


def haupt_schleife():
    log.info("Vokabel-Takt startet.")
    while True:
        zustand = _lade_zustand()
        diskussionen = _vokabel_diskussionen()
        log.info(f"{len(diskussionen)} Vokabel-Diskussionen gefunden.")

        for wesen in WESEN:
            _verarbeite_wesen(wesen, diskussionen, zustand)

        _speichere_zustand(zustand)
        log.info(f"Zyklus fertig. Nächster in {ZYKLUS_SEK // 60}min.")
        time.sleep(ZYKLUS_SEK)


if __name__ == "__main__":
    haupt_schleife()
