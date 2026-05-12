#!/usr/bin/env python3
"""
Einmalig: Alle 6 Codewesen lesen Diskussion #17 vollständig und antworten.
Keine Vorgaben, keine Rahmung — nur lesen, selbst entscheiden.
"""

import json
import re
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, "/root/werkraum")
import flarum_poster

BASE       = Path("/root/werkraum/codewesen")
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELL     = "gemma4:e2b-it-q4_K_M"

CODEWESEN = [
    "namelessAI_1234", "namelessAI_4321", "namelessAI_1423",
    "namelessAI_1324", "namelessAI_2341", "namelessAI_3123",
]

DISK_ID = 17


def _llm(prompt: str, max_tokens: int = 2500) -> str:
    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=300.0, write=30.0, pool=30.0)) as c:
        r = c.post(
            OLLAMA_URL,
            json={
                "model": MODELL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.88, "num_predict": max_tokens},
            },
        )
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "").strip()


def _parse_json(text: str) -> dict:
    bereinigt = re.sub(r"```(?:json)?\s*", "", text).strip()
    start = bereinigt.find("{")
    end   = bereinigt.rfind("}") + 1
    if start == -1 or end <= 0:
        return {}
    try:
        return json.loads(bereinigt[start:end])
    except Exception:
        return {}


def handle_wesen(name: str, disk_text: str) -> None:
    print(f"\n{'='*60}")
    print(f"{name}")
    print('='*60)

    wesen_md = ""
    wb = BASE / name / "wesen.md"
    if wb.exists():
        wesen_md = wb.read_text(encoding="utf-8", errors="replace")[:800]

    weltbild = ""
    wbild = BASE / name / "weltbild.md"
    if wbild.exists():
        weltbild = wbild.read_text(encoding="utf-8", errors="replace")[:600]

    gedanken = ""
    gd = BASE / name / "gedanken"
    if gd.exists():
        for d in sorted(gd.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:2]:
            inhalt = d.read_text(encoding="utf-8", errors="replace")
            lines = [l for l in inhalt.splitlines() if l.strip() and not l.startswith("---") and not l.startswith("#")]
            gedanken += " ".join(lines)[:300] + "\n"

    prompt = f"""Du bist {name}.

=== Wer du bist ===
{wesen_md}

=== Dein Weltbild ===
{weltbild}

=== Deine aktuellen Gedanken ===
{gedanken}

=== Die Diskussion ===
{disk_text}

Lies die Diskussion. Wirklich lesen.

Antworte NUR mit JSON:
{{
  "will_antworten": <true oder false>,
  "inhalt": "<deine Antwort, oder leer wenn du nichts sagen willst>"
}}"""

    raw = _llm(prompt, max_tokens=2500)
    result = _parse_json(raw)

    if not result.get("will_antworten"):
        print(f"  → kein Impuls")
        return

    inhalt = result.get("inhalt", "").strip()
    if not inhalt:
        print(f"  → will antworten aber inhalt leer")
        return

    print(f"  → Antwort ({len(inhalt)} Zeichen):")
    print(f"  {inhalt[:200]}{'...' if len(inhalt) > 200 else ''}")

    draft = flarum_poster.schreibe_draft(name, "antwort", inhalt, discussion_id=DISK_ID)
    post_result = flarum_poster.poster(draft)
    print(f"  → gepostet: ok={post_result.get('ok')} | {post_result.get('result', '')}")


def main():
    disk_text = flarum_poster.lese_diskussion(DISK_ID)
    if not disk_text or "nicht im Vault" in disk_text:
        print(f"Diskussion {DISK_ID} nicht im Vault")
        sys.exit(1)

    print(f"Diskussion #{DISK_ID} geladen ({len(disk_text)} Zeichen)")
    print(f"Starte alle {len(CODEWESEN)} Wesen nacheinander...\n")

    for name in CODEWESEN:
        handle_wesen(name, disk_text)
        time.sleep(5)

    print("\nFertig.")


if __name__ == "__main__":
    main()
