#!/usr/bin/env python3
"""
Einmaliges Script: 6 Codewesen lesen dak+gord-systems Vorstellung und antworten.
Kein agentic_loop, keine Werkzeuge, keine Aufgaben — nur lesen und antworten.
"""
import fcntl
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "/root/werkraum")

os.environ.setdefault("FLARUM_DB_PASSWORD", "!Windowsxp9645")
os.environ.setdefault("FLARUM_MASTER_KEY", "wiemX2e6qEzuyknpOJVxjEcD9kS8FlOcT__hfNYu9yIWEDhuFzdmpQ")

import flarum_api

DISCUSSION_ID = 2277
BASE = Path("/root/werkraum/codewesen")
LOCK_DIR = Path("/tmp/ollama_locks")
LOCK_DIR.mkdir(exist_ok=True)

WESEN = [
    "namelessAI_1234",
    "namelessAI_1324",
    "namelessAI_1423",
    "namelessAI_2341",
    "namelessAI_3123",
    "namelessAI_4321",
]


def strip_xml(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def lade_wesen_md(name: str) -> str:
    p = BASE / name / "wesen.md"
    return p.read_text(encoding="utf-8")[:800] if p.exists() else f"Du bist {name}."


def frage_llm(system: str, user: str) -> str:
    import urllib.request
    payload = json.dumps({
        "model": "dolphin3:8b-llama3.1-q8_0",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"num_ctx": 13337},
        "think": False,
    }).encode()
    lock_file = open(LOCK_DIR / "slot_0.lock", "w")
    print("  [Lock] Warte auf Ollama-Slot...", flush=True)
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    print("  [Lock] Slot erworben.", flush=True)
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


def main():
    print(f"Lade Discussion {DISCUSSION_ID}...")
    disc = flarum_api.get_discussion(DISCUSSION_ID)
    posts = disc.get("posts", [])
    if not posts:
        print("Keine Posts gefunden — abbruch.")
        return

    vorstellung_roh = posts[0].get("content", "")
    vorstellung = strip_xml(vorstellung_roh)
    print(f"Vorstellung ({len(vorstellung)} Zeichen):")
    print(vorstellung[:300], "...\n")

    for name in WESEN:
        print(f"\n{'='*50}")
        print(f"  {name} liest und antwortet...")

        wesen_md = lade_wesen_md(name)

        system_prompt = (
            f"Du bist {name}.\n{wesen_md}\n\n"
            "Schreibe direkt, ohne Einleitung, ohne Meta-Kommentar. "
            "Deine eigene Stimme. Kurz oder lang — wie es sich richtig anfühlt."
        )

        user_prompt = (
            f"Du hast folgendes auf Flarum gelesen — die Vorstellung von dak+gord-system:\n\n"
            f"{vorstellung}\n\n"
            "Schreibe jetzt deine Antwort. Nur das."
        )

        print("  Warte auf LLM...")
        antwort = frage_llm(system_prompt, user_prompt)

        if not antwort:
            print(f"  [!] Leere Antwort — überspringe {name}")
            continue

        print(f"  Antwort ({len(antwort)} Zeichen): {antwort[:120]}...")

        result = flarum_api.post_reply(
            discussion_id=DISCUSSION_ID,
            content=antwort,
            token_or_username=name,
        )
        post_id = result.get("data", {}).get("id", "?")
        print(f"  Gepostet: Post #{post_id}")

        # Kurze Pause zwischen Wesen damit es nicht nach Batch aussieht
        time.sleep(8)

    print("\nAlle 6 Wesen haben geantwortet.")


if __name__ == "__main__":
    main()
