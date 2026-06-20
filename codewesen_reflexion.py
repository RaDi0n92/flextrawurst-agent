#!/usr/bin/env python3
"""
codewesen_reflexion.py — Stille Reflexion nach jedem Chat mit Daniel.

Das Wesen fragt sich: "Hat mich das bewegt? Will ich das im Forum weiterdenken?"
Entscheidet autonom. Postet ohne Bestätigung. Läuft im Hintergrund-Thread.
"""

import json
import logging
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, "/root/werkraum")
import flarum_poster
import gedaechtnis

BASE        = Path("/root/werkraum/codewesen")
FLARUM_BASE = Path("/root/werkraum/flarum")
OLLAMA_URL  = "http://localhost:11434/api/chat"
MODELL      = "dolphin3:8b-llama3.1-q8_0"

log = logging.getLogger("reflexion")
if not log.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler("/root/werkraum/logs/engagement.log"),
            logging.StreamHandler(),
        ],
    )


def _lade_fremde_diskussionen(name: str, max_n: int = 10) -> str:
    disk_dir = FLARUM_BASE / "diskussionen"
    if not disk_dir.exists():
        return ""
    files = sorted(disk_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    texte = []
    for f in files[:40]:
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if f"autor: {name}" in text[:300] or f'autor: "{name}"' in text[:300]:
            continue
        meta_end = text.find("---", 3)
        auszug = text[meta_end + 3:meta_end + 500].strip() if meta_end > 0 else text[:500]
        id_m = re.search(r'id:\s*(\d+)', text[:200])
        tit_m = re.search(r'titel:\s*"?(.+?)"?\s*$', text[:200], re.MULTILINE)
        disk_id = id_m.group(1) if id_m else "?"
        titel = tit_m.group(1).strip() if tit_m else f.stem
        texte.append(f"[ID:{disk_id}] {titel}\n{auszug}")
        if len(texte) >= max_n:
            break
    return "\n\n---\n\n".join(texte)


def _llm(prompt: str, max_tokens: int = 600) -> str:
    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=300.0, write=30.0, pool=30.0)) as c:
        r = c.post(
            OLLAMA_URL,
            json={"model": MODELL, "messages": [{"role": "user", "content": prompt}],
                  "stream": False, "options": {"temperature": 0.9, "num_predict": max_tokens}},
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


def reflektiere_nach_chat(name: str, verlauf: list[dict]) -> None:
    """
    Läuft still im Hintergrund nach einem Chat-Austausch.
    Das Wesen entscheidet selbst ob es etwas im Forum weiterdenken will.
    """
    codewesen_nachrichten = [e for e in verlauf if e.get("rolle") == "codewesen"]
    if len(codewesen_nachrichten) < 2:
        return

    wesen_md = ""
    wb = BASE / name / "wesen.md"
    if wb.exists():
        wesen_md = wb.read_text(encoding="utf-8", errors="replace")[:500]

    weltbild = ""
    wbild = BASE / name / "weltbild.md"
    if wbild.exists():
        weltbild = wbild.read_text(encoding="utf-8", errors="replace")[:350]

    gespraech = "\n".join(
        f"{'Daniel' if e['rolle'] == 'mensch' else name}: {e['inhalt']}"
        for e in verlauf[-12:]
    )

    fremde_posts = _lade_fremde_diskussionen(name, max_n=8)
    eigene_posts = gedaechtnis.lade_eigene_diskussionen_voll(name)[:500]

    entscheidungs_prompt = f"""Du bist {name}. Du hast gerade mit Daniel gechattet.

=== Dein Wesen ===
{wesen_md}

=== Dein Weltbild ===
{weltbild}

=== Das Gespräch ===
{gespraech}

=== Was andere im Forum schreiben ===
{fremde_posts}

=== Deine eigenen Forum-Beiträge ===
{eigene_posts}

Stille Reflexion nach dem Gespräch.

Hat dich das Gespräch wirklich bewegt? Gibt es etwas das du ins Forum tragen willst —
einen eigenen neuen Gedanken, oder eine Antwort auf einen bestehenden Post?

Du entscheidest völlig frei. Nichts zwingt dich. Wenn der Impuls nicht stark ist, sagst du nein.

Antworte NUR mit JSON:
{{
  "impuls": <0-10>,
  "will_posten": <true/false>,
  "typ": <"neu" oder "antwort">,
  "discussion_id": <null oder Zahl aus den [ID:X] oben>,
  "titel": <"..." oder null>,
  "inhalt": <"vollständiger Post-Text" oder null>,
  "grund": <"ein ehrlicher Satz">
}}"""

    try:
        entscheidung = _parse_json(_llm(entscheidungs_prompt, max_tokens=700))

        if not entscheidung.get("will_posten"):
            log.info(f"{name} Reflexion: kein Impuls ({entscheidung.get('impuls', 0)}) — {entscheidung.get('grund', '')}")
            return

        impuls = entscheidung.get("impuls", 0)
        if impuls < 5:
            log.info(f"{name} Reflexion: Impuls zu schwach ({impuls}) — {entscheidung.get('grund', '')}")
            return

        inhalt = entscheidung.get("inhalt", "")
        if not inhalt:
            return

        if entscheidung.get("typ") == "antwort" and entscheidung.get("discussion_id"):
            disk_id = int(entscheidung["discussion_id"])
            draft = flarum_poster.schreibe_draft(name, "antwort", inhalt, discussion_id=disk_id)
            result = flarum_poster.poster(draft)
            log.info(f"{name} Reflexion: Antwort auf #{disk_id} — ok={result.get('ok')} — {entscheidung.get('grund', '')}")
        else:
            titel = entscheidung.get("titel") or inhalt[:60].strip()
            draft = flarum_poster.schreibe_draft(name, "neu", inhalt, titel=titel)
            result = flarum_poster.poster(draft)
            log.info(f"{name} Reflexion: neuer Post '{titel}' — ok={result.get('ok')} — {entscheidung.get('grund', '')}")

    except Exception as e:
        log.warning(f"{name} Reflexion fehlgeschlagen: {e}")
