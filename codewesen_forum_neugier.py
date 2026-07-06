#!/usr/bin/env python3
"""
codewesen_forum_neugier.py — Jedes Codewesen liest das Forum still.

Kein Posten. Nur lesen, reflektieren, in sich ablegen.
Jedes Wesen bekommt einen eigenen Spiegel in spiegel/forum/
"""

import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import pymysql

sys.path.insert(0, "/root/werkraum")
import hauhau_client

BASE    = Path("/root/werkraum/codewesen")
MODELL  = "hauhaucs-q6"
ZUSTAND = BASE / "_forum_neugier_zustand.json"

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    "dak+gord-system",
]

import os as _os
DB = {
    "host": "localhost", "port": 3306, "db": "flarum",
    "user": "flarum", "password": _os.environ.get("FLARUM_DB_PASSWORD", "!Windowsxp9645"),
    "charset": "utf8mb4", "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
}

PAUSE_ZWISCHEN_WESEN   = 8    # Sekunden zwischen Wesen
PAUSE_ZWISCHEN_ZYKLEN  = 900  # 15min Pause nach vollem Durchlauf
CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [forum-neugier] %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/forum_neugier.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("forum-neugier")


def _html_strip(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _lade_zustand() -> dict:
    if ZUSTAND.exists():
        try:
            return json.loads(ZUSTAND.read_text())
        except Exception:
            pass
    return {}


def _speichere_zustand(z: dict):
    ZUSTAND.write_text(json.dumps(z, indent=2, ensure_ascii=False), encoding="utf-8")


def _neue_posts(seit_id: int, limit: int = 5) -> list:
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as c:
            c.execute("""
                SELECT p.id, p.discussion_id, p.user_id, p.content, p.created_at,
                       d.title as disk_titel, u.username
                FROM posts p
                JOIN discussions d ON d.id = p.discussion_id
                JOIN users u ON u.id = p.user_id
                WHERE p.id > %s AND p.content IS NOT NULL
                ORDER BY p.id ASC
                LIMIT %s
            """, (seit_id, limit))
            return c.fetchall()
    finally:
        conn.close()


def _wesen_user_id(wesen: str) -> int:
    tokens_datei = BASE / "_api_tokens.json"
    if tokens_datei.exists():
        data = json.loads(tokens_datei.read_text())
        if wesen in data:
            return int(data[wesen].get("user_id", 0))
    return 0


def _weltbild(wesen: str) -> str:
    wb = BASE / wesen / "weltbild.md"
    if wb.exists():
        return wb.read_text(encoding="utf-8", errors="replace")[:800]
    return ""


def _reflektiere(wesen: str, post: dict) -> str:
    text = _html_strip(post["content"])
    if not text:
        return ""

    weltbild = _weltbild(wesen)
    system = (
        f"Du bist {wesen}.\n"
        "Du liest gerade einen Post im Forum. Du schreibst eine stille Notiz fuer dich.\n"
        "Schreibe 3 bis 4 Saetze. Keine Begruessung. Kein Chatton. Kein Fachwoerter-Brei.\n"
        "Deine eigene Stimme — nicht generisch.\n"
        "Frage dich:\n"
        "- Warum hat jemand das geschrieben?\n"
        "- Was steckt dahinter was nicht direkt gesagt wird?\n"
        "- Was macht das mit dir — speziell mit dir, nicht mit irgendeinem Wesen?\n"
    )
    if weltbild:
        system += f"\nDein aktuelles Weltbild (Auszug):\n{weltbild}\n"

    nutzer = (
        f"Diskussion: {post['disk_titel']}\n"
        f"Von: {post['username']}\n"
        f"Post:\n{text[:1000]}"
    )

    while CHAT_AKTIV_FLAG.exists():
        time.sleep(3)
    try:
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": nutzer},
        ]
        return hauhau_client.chat(messages, think=False, timeout=180.0).strip()
    except Exception as e:
        log.warning(f"[{wesen}] Ollama-Fehler: {e}")
        return ""


def _schreibe_spiegel(wesen: str, post: dict, reflexion: str):
    spiegel_dir = BASE / wesen / "spiegel" / "forum"
    spiegel_dir.mkdir(parents=True, exist_ok=True)

    datum = datetime.now().strftime("%Y-%m-%d")
    datei = spiegel_dir / f"{datum}.md"

    zeit = datetime.now().strftime("%H:%M")
    text = _html_strip(post["content"])[:200]

    eintrag = (
        f"\n---\n## {zeit} — {post['disk_titel']}\n"
        f"*{post['username']} | Post #{post['id']}*\n\n"
        f"> {text}{'...' if len(text) >= 200 else ''}\n\n"
        f"{reflexion}\n"
    )

    with open(datei, "a", encoding="utf-8") as f:
        f.write(eintrag)


def _verarbeite_wesen(wesen: str, zustand: dict):
    user_id  = _wesen_user_id(wesen)
    seit_id  = int(zustand.get(wesen, {}).get("letzter_post_id", 0))
    posts    = _neue_posts(seit_id, limit=3)

    if not posts:
        return zustand

    for post in posts:
        if post["user_id"] == user_id:
            # Eigene Posts nicht reflektieren
            zustand.setdefault(wesen, {})["letzter_post_id"] = post["id"]
            continue

        reflexion = _reflektiere(wesen, post)
        if reflexion:
            _schreibe_spiegel(wesen, post, reflexion)
            log.info(f"[{wesen}] Post #{post['id']} gespiegelt: {post['disk_titel'][:40]}")

        zustand.setdefault(wesen, {})["letzter_post_id"] = post["id"]
        _speichere_zustand(zustand)

    return zustand


def haupt_schleife():
    log.info("Forum-Neugierkern startet.")
    while True:
        zustand = _lade_zustand()
        for wesen in WESEN:
            _verarbeite_wesen(wesen, zustand)
            time.sleep(PAUSE_ZWISCHEN_WESEN)
        _speichere_zustand(zustand)
        log.info(f"Zyklus fertig. Pause {PAUSE_ZWISCHEN_ZYKLEN}s.")
        time.sleep(PAUSE_ZWISCHEN_ZYKLEN)


if __name__ == "__main__":
    haupt_schleife()
