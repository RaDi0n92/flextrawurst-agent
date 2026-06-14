#!/usr/bin/env python3
"""Einmaliger Import aller JSONL-Chats in wesen_chat_verlauf."""
import json, os, re
import psycopg2, psycopg2.extras

CODEWESEN_DIR = "/root/werkraum/codewesen"
import subprocess as _sp
_env_line = next((l for l in open("/root/werkraum/.agent/flextrawurst-db.env").readlines() if l.startswith("FLEXTRAWURST_DB_URI=")), "")
DSN = _env_line.strip().split("=", 1)[1] if _env_line else ""

ROLLE_MAP = {"mensch": "user", "codewesen": "assistant", "system": "system"}

def get_conn():
    return psycopg2.connect(DSN, cursor_factory=psycopg2.extras.RealDictCursor)

def run():
    conn = get_conn()
    inserted = 0
    skipped = 0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as n FROM wesen_chat_verlauf")
            existing = cur.fetchone()["n"]
            if existing > 0:
                print(f"Tabelle hat bereits {existing} Einträge — Import übersprungen (idempotent).")
                return

        for wesen_dir in sorted(os.listdir(CODEWESEN_DIR)):
            jsonl = os.path.join(CODEWESEN_DIR, wesen_dir, "gedaechtnis", "chat_verlauf.jsonl")
            if not os.path.exists(jsonl):
                continue
            wesen_name = wesen_dir
            with open(jsonl, "r", encoding="utf-8") as f:
                with conn.cursor() as cur:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            skipped += 1
                            continue
                        rolle_raw = entry.get("rolle", "mensch")
                        rolle = ROLLE_MAP.get(rolle_raw, "user")
                        inhalt = entry.get("inhalt", "")
                        ts = entry.get("ts")
                        if not inhalt:
                            skipped += 1
                            continue
                        cur.execute(
                            """INSERT INTO wesen_chat_verlauf (wesen_name, rolle, inhalt, created_at)
                               VALUES (%s, %s, %s, %s)""",
                            (wesen_name, rolle, inhalt, ts)
                        )
                        inserted += 1
            conn.commit()
            print(f"  {wesen_name}: importiert")

        print(f"\nFertig — {inserted} Einträge importiert, {skipped} übersprungen.")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
