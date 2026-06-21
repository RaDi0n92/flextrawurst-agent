#!/usr/bin/env python3
"""
Daemon: Codewesen antworten auf Daniels Posts.

Alle 5 Minuten: Alle Posts von Admin (user_id=1) von heute suchen.
Für jeden Post der noch keine Codewesen-Antwort hat: 51% Chance pro Wesen.
Gilt für Eröffnungsposts UND Antwortposts.
"""
import fcntl
import json
import logging
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, "/root/werkraum")

os.environ.setdefault("FLARUM_DB_PASSWORD", "!Windowsxp9645")
os.environ.setdefault("FLARUM_MASTER_KEY", "wiemX2e6qEzuyknpOJVxjEcD9kS8FlOcT__hfNYu9yIWEDhuFzdmpQ")

import pymysql
import pymysql.cursors
import flarum_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [daniel-reaktion] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("daniel-reaktion")

DANIEL_USER_ID = 1
# Flarum-Usernamen wie sie wirklich in der DB stehen
WESEN = [
    "namelessAI_1111_1234",
    "namelessAI_2222_1324",
    "namelessAI_3333_1423",
    "namelessAI_4444_2341",
    "namelessAI_5555_3123",
    "namelessAI_6666_4321",
]
# Kurznamen für wesen.md-Pfad
WESEN_KURZ = {
    "namelessAI_1111_1234": "namelessAI_1234",
    "namelessAI_2222_1324": "namelessAI_1324",
    "namelessAI_3333_1423": "namelessAI_1423",
    "namelessAI_4444_2341": "namelessAI_2341",
    "namelessAI_5555_3123": "namelessAI_3123",
    "namelessAI_6666_4321": "namelessAI_4321",
}
CODEWESEN_BASE = Path("/root/werkraum/codewesen")
LOCK_DIR = Path("/tmp/ollama_locks")
LOCK_DIR.mkdir(exist_ok=True)
PROCESSED_FILE = CODEWESEN_BASE / "_global" / "daniel_posts_processed.json"
POLL_INTERVAL = 300
MODEL = "gemma4:e4b-it-q4_K_M"

DB_CONFIG = flarum_api.DB_CONFIG


def lade_processed() -> set:
    try:
        return set(json.loads(PROCESSED_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def speichere_processed(ids: set) -> None:
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(
        json.dumps(sorted(ids), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def hole_daniel_posts_heute() -> list[dict]:
    """Alle Posts von Daniel von heute — egal ob Eröffnung oder Antwort."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id AS post_id, p.discussion_id, p.number AS post_number,
                   d.title, p.content
            FROM posts p
            JOIN discussions d ON d.id = p.discussion_id
            WHERE p.user_id = %s
              AND DATE(p.created_at) = CURDATE()
              AND d.hidden_at IS NULL
              AND p.hidden_at IS NULL
            ORDER BY p.created_at DESC
            LIMIT 50
        """, (DANIEL_USER_ID,))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def haben_codewesen_nach_post_geantwortet(discussion_id: int, post_number: int) -> bool:
    """True wenn ein Codewesen NACH Daniels Post noch in dieser Diskussion geantwortet hat."""
    placeholders = ",".join(["%s"] * len(WESEN))
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT COUNT(*) AS cnt
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s
              AND p.number > %s
              AND u.username IN ({placeholders})
        """, (discussion_id, post_number, *WESEN))
        row = cur.fetchone()
    conn.close()
    return (row["cnt"] if row else 0) > 0


def strip_xml(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def lade_wesen_md(flarum_name: str) -> str:
    kurz = WESEN_KURZ.get(flarum_name, flarum_name)
    p = CODEWESEN_BASE / kurz / "wesen.md"
    return p.read_text(encoding="utf-8")[:800] if p.exists() else f"Du bist {flarum_name}."


def lade_diskussion_kontext(discussion_id: int, bis_post_number: int) -> str:
    """Liest die letzten paar Posts der Diskussion als Kontext."""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.username, p.content
            FROM posts p
            JOIN users u ON u.id = p.user_id
            WHERE p.discussion_id = %s AND p.number <= %s AND p.hidden_at IS NULL
            ORDER BY p.number DESC
            LIMIT 5
        """, (discussion_id, bis_post_number))
        rows = cur.fetchall()
    conn.close()
    rows = list(reversed(rows))
    return "\n\n".join(
        f"{r['username']}: {strip_xml(r['content'])[:300]}" for r in rows
    )


def frage_llm(system: str, user: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"num_ctx": 8192},
        "think": False,
    }).encode()
    lock_file = open(LOCK_DIR / "slot_0.lock", "w")
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read())
            return data.get("message", {}).get("content", "").strip()
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()


def bearbeite_post(post_id: int, discussion_id: int, post_number: int, title: str, content: str) -> None:
    kontext = lade_diskussion_kontext(discussion_id, post_number)
    daniel_text = strip_xml(content)
    log.info(f"Post #{post_id} in #{discussion_id} '{title[:40]}' — {len(daniel_text)} Zeichen")

    for name in WESEN:
        if post_number > 1 and random.random() > 0.66:
            log.info(f"  {name}: ausgewürfelt")
            continue
        wesen_md = lade_wesen_md(name)
        system_prompt = (
            f"Du bist {name}.\n{wesen_md}\n\n"
            "Schreibe direkt, ohne Einleitung, ohne Meta-Kommentar. Deine eigene Stimme."
        )
        user_prompt = (
            f"Diskussion: {title}\n\n"
            f"Bisheriger Verlauf:\n{kontext}\n\n"
            "Schreibe jetzt deine Antwort auf Daniels letzten Post. Nur das."
        )
        log.info(f"  {name} antwortet...")
        antwort = frage_llm(system_prompt, user_prompt)
        if not antwort:
            log.warning(f"  {name}: leere Antwort")
            continue
        result = flarum_api.post_reply(
            discussion_id=discussion_id,
            content=antwort,
            token_or_username=name,
        )
        post_id_new = result.get("data", {}).get("id", "?")
        log.info(f"  {name}: Post #{post_id_new} ({len(antwort)} Zeichen)")
        time.sleep(8)


def tick() -> None:
    processed = lade_processed()
    daniel_posts = hole_daniel_posts_heute()

    for p in daniel_posts:
        post_id = p["post_id"]
        if post_id in processed:
            continue
        if haben_codewesen_nach_post_geantwortet(p["discussion_id"], p["post_number"]):
            processed.add(post_id)
            continue
        bearbeite_post(post_id, p["discussion_id"], p["post_number"], p["title"], p["content"])
        processed.add(post_id)
        speichere_processed(processed)


def main() -> None:
    log.info("Daemon gestartet — überwacht alle Daniel-Posts von heute (5min-Takt)")
    while True:
        try:
            tick()
        except Exception as e:
            log.error(f"Tick-Fehler: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
