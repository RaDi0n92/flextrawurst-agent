#!/usr/bin/env python3
"""
Flarum → Innenleben Feeder.

Liest neue Forum-Posts aus der Flarum-MySQL-DB und speist sie
als Ereignisse in das Innenleben-System (graph.verarbeite_ereignis) ein.

Jedes Wesen verarbeitet nur Posts von anderen — nicht seine eigenen.
Läuft einmalig oder als Daemon (--daemon --interval 300).
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pymysql

sys.path.insert(0, "/root/werkraum/innenleben")
import graph as innenleben_graph

LOG_FILE = Path("/root/werkraum/logs/flarum_feeder.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
CHAT_FLAG = Path("/tmp/dak_gord_chat_aktiv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FEEDER] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("feeder")

DB_CONFIG = {
    "host": "localhost", "port": 3306, "db": "flarum",
    "user": "flarum", "password": "Flarum2024!Secure",
    "charset": "utf8mb4", "autocommit": True,
}

WESEN_USERNAMES = [
    "namelessAI_1234",
    "namelessAI_1324",
    "namelessAI_1423",
    "namelessAI_2341",
    "namelessAI_3123",
    "namelessAI_4321",
]

_STATE_FILE = Path("/root/werkraum/innenleben/feeder_state.json")

_STATE_DEFAULT = {w: 0 for w in WESEN_USERNAMES}


def _lade_cursor_state() -> dict:
    if _STATE_FILE.exists():
        try:
            d = json.loads(_STATE_FILE.read_text())
            # Migration: altes Format {"last_post_id": X} → per-Wesen
            if "last_post_id" in d and not any(w in d for w in WESEN_USERNAMES):
                alt = d["last_post_id"]
                return {w: alt for w in WESEN_USERNAMES}
            return d
        except Exception:
            pass
    return dict(_STATE_DEFAULT)


def _speichere_cursor_state(state: dict) -> None:
    tmp = _STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(_STATE_FILE)


def _neue_posts_laden(ab_post_id: int) -> list:
    db = pymysql.connect(**DB_CONFIG)
    c  = db.cursor(pymysql.cursors.DictCursor)
    c.execute("""
        SELECT p.id, p.content, p.created_at,
               u.username AS autor,
               d.title AS diskussion_titel,
               d.id AS diskussion_id
        FROM posts p
        LEFT JOIN users u ON p.user_id = u.id
        LEFT JOIN discussions d ON p.discussion_id = d.id
        WHERE p.id > %s AND p.type = 'comment'
        ORDER BY p.id ASC
        LIMIT 50
    """, (ab_post_id,))
    rows = c.fetchall()
    db.close()
    return rows


def _post_zu_ereignis(post: dict) -> str:
    autor   = post.get("autor", "unbekannt")
    titel   = post.get("diskussion_titel", "")
    inhalt  = (post.get("content") or "")[:800]
    return f"[Forum] {autor} schreibt in »{titel}«: {inhalt}"


def verarbeite_neue_posts(max_pro_wesen: int = 3) -> None:
    cursors = _lade_cursor_state()

    for wesen in WESEN_USERNAMES:
        letzter_id = cursors.get(wesen, 0)
        posts = _neue_posts_laden(letzter_id)

        fremde = [p for p in posts if p.get("autor") != wesen]
        if not fremde:
            if posts:
                # Eigene Posts überspringen, Cursor trotzdem vorwärts
                cursors[wesen] = max(p["id"] for p in posts)
            continue

        verarbeitet = 0
        neuer_cursor = letzter_id

        for post in fremde:
            if verarbeitet >= max_pro_wesen:
                break
            ist_mensch = post.get("autor") not in WESEN_USERNAMES
            hr = 0.6 if ist_mensch else 0.0
            event_text = _post_zu_ereignis(post)

            try:
                while CHAT_FLAG.exists():
                    time.sleep(10)
                det_event_id = f"flarum:post_{post['id']}:{wesen}"
                innenleben_graph.verarbeite_ereignis(
                    entity_id=wesen,
                    event_text=event_text,
                    event_source="forum_post",
                    human_resonance=hr,
                    event_id=det_event_id,
                )
                log.info(f"{wesen} | Post {post['id']} von {post['autor']} verarbeitet [{det_event_id}]")
                verarbeitet += 1
            except Exception as e:
                log.warning(f"{wesen} | Fehler bei Post {post['id']}: {e}")

            neuer_cursor = post["id"]

        cursors[wesen] = neuer_cursor

    _speichere_cursor_state(cursors)
    log.info(f"Cursors gespeichert: { {w: cursors[w] for w in WESEN_USERNAMES} }")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true")
    parser.add_argument("--interval", type=int, default=300)
    args = parser.parse_args()

    if args.daemon:
        log.info(f"Daemon-Modus: alle {args.interval}s")
        while True:
            try:
                verarbeite_neue_posts()
            except Exception as e:
                log.error(f"Feeder-Fehler: {e}")
            time.sleep(args.interval)
    else:
        verarbeite_neue_posts()


if __name__ == "__main__":
    main()
