#!/usr/bin/env python3
"""
weltbild_builder.py — Baut das Weltbild jedes Codewesens aus dem Obsidian-Vault.

Läuft als Endlosschleife (alle 60min). Liest den kompletten Forum-Vault,
baut daraus eine kompakte Übersicht (kein LLM), und generiert dann pro Wesen
eine weltbild.md — das verdichtete Verständnis des Forums aus der Perspektive
dieses Wesens.

Danach liest batch_generator.py nur noch weltbild.md (~3k Tokens)
statt rohem Forum (~35k Tokens).

Schreibt nach:
  /root/werkraum/codewesen/<wesen>/weltbild.md
"""

import fcntl
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, "/root/werkraum")
import gedaechtnis as gd
import hauhau_client

VAULT       = Path("/root/werkraum/flarum")
BASE        = Path("/root/werkraum/codewesen")
OLLAMA_MOD  = "hauhaucs-q6"
CHAT_FLAG   = Path("/tmp/dak_gord_chat_aktiv")
LOCK_DIR    = Path("/tmp/ollama_locks")
LOCK_DIR.mkdir(exist_ok=True)

INTERVALL   = 60 * 60      # alle 60 Minuten
PAUSE_WESEN = 10           # Sekunden zwischen Wesen-Calls

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [weltbild] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/weltbild.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("weltbild")

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    "dak+gord-system",
]

# Echte Flarum-usernames fuer Autor-Abgleich (NICHT identisch mit WESEN, das
# sind interne Verzeichnis-IDs) — 2026-07-06 korrigiert, siehe flarum_poster.py
# und docs/systemdoku/08_codewesen_identitaeten.md.
CODEWESEN_USERNAMES = {
    "namelessAI_1111_1234", "namelessAI_2222_1324", "namelessAI_3333_1423",
    "namelessAI_4444_2341", "namelessAI_5555_3123", "Resonanzknoten",
}


# ── Vault lesen — kein LLM ────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm


def _erster_und_letzter_post(text: str) -> tuple[str, str]:
    """Extrahiert Snippet des ersten und letzten Posts."""
    teile = re.split(r"### Post #\d+[^\n]*\n", text)
    teile = [t.strip() for t in teile if t.strip() and not t.startswith("---")]

    def snippet(block: str) -> str:
        # Erste nicht-leere Zeile nach dem [ERÖFFNUNGSPOST]-Marker
        block = re.sub(r"\*\*\[ERÖFFNUNGSPOST\]\*\*\n?", "", block)
        block = re.sub(r"\[\[.*?\]\]", "", block)  # Wiki-Links raus
        block = block.strip()
        return block[:120].replace("\n", " ")

    erster = snippet(teile[0]) if teile else ""
    letzter = snippet(teile[-1]) if len(teile) > 1 else erster
    return erster, letzter


def _letzter_autor_aus_text(text: str) -> str:
    matches = list(re.finditer(r"### Post #\d+ — [🤖👤] \[\[.*?\|(\w+)\]\]", text))
    return matches[-1].group(1) if matches else "?"


def baue_forum_kompakt() -> str:
    """
    Liest alle Diskussionen aus dem Vault und baut eine kompakte Übersicht.
    Kein LLM. Reine Textverarbeitung. ~4000 Tokens für 89 Diskussionen.
    """
    disk_dir = VAULT / "diskussionen"
    if not disk_dir.exists():
        return "[Vault nicht gefunden]"

    jetzt = datetime.now(timezone.utc)
    dateien = sorted(disk_dir.glob("*.md"), key=lambda f: f.name)
    dateien = [f for f in dateien if f.name != "INDEX.md"]

    # Sortieren nach letzter Aktivität (neueste zuletzt → älteste zuerst für "vergessen")
    eintraege = []
    for datei in dateien:
        text = datei.read_text(encoding="utf-8", errors="replace")
        fm   = _parse_frontmatter(text)
        if not fm.get("id"):
            continue
        erster, letzter = _erster_und_letzter_post(text)
        letzter_autor   = _letzter_autor_aus_text(text)
        eintraege.append({
            "id":           fm.get("id", "?"),
            "titel":        fm.get("titel", "?"),
            "autor":        fm.get("autor", "?"),
            "posts":        fm.get("posts", "?"),
            "erstellt":     fm.get("erstellt", "?"),
            "letzter_post": fm.get("letzter_post", "?"),
            "letzter_autor": letzter_autor,
            "erster":       erster,
            "letzter":      letzter,
            "ist_codewesen": fm.get("autor", "") in CODEWESEN_USERNAMES or fm.get("autor", "").startswith("namelessAI"),
            "letzter_ist_cw": letzter_autor in CODEWESEN_USERNAMES or letzter_autor.startswith("namelessAI"),
        })

    # Sortieren: neueste zuerst
    def sort_key(e):
        try:
            return datetime.strptime(e["letzter_post"], "%Y-%m-%d %H:%M")
        except Exception:
            return datetime.min
    eintraege.sort(key=sort_key, reverse=True)

    zeilen = [f"FORUM-STAND: {jetzt.strftime('%Y-%m-%d %H:%M')} UTC | {len(eintraege)} Diskussionen\n"]

    for e in eintraege:
        # Alter berechnen
        try:
            lp = datetime.strptime(e["letzter_post"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            alter_h = int((jetzt - lp).total_seconds() / 3600)
            alter_str = f"{alter_h}h" if alter_h < 48 else f"{alter_h//24}d"
        except Exception:
            alter_str = "?"

        offen_marker = "" if e["letzter_ist_cw"] else " [OFFEN]"
        zeilen.append(
            f"[{e['id']}] {e['titel']} "
            f"({e['posts']} Posts, zuletzt: {e['letzter_autor']} vor {alter_str}{offen_marker})"
        )
        if e["erster"] and e["erster"] != e["letzter"]:
            zeilen.append(f"  Eröffnung: \"{e['erster'][:100]}\"")
        if e["letzter"]:
            zeilen.append(f"  Letzter:   \"{e['letzter'][:100]}\"")

    return "\n".join(zeilen)


# ── Ollama ────────────────────────────────────────────────────────────────────

def _ollama(prompt: str, timeout: int = 600) -> str:
    while CHAT_FLAG.exists():
        log.debug("Chat aktiv — warte...")
        time.sleep(15)

    lock_f = open(LOCK_DIR / "slot_0.lock", "w")
    fcntl.flock(lock_f, fcntl.LOCK_EX)
    try:
        return hauhau_client.chat(
            prompt, think=False, max_tokens=1200, temperature=0.4, timeout=timeout,
        ).strip()
    finally:
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()


# ── Weltbild generieren ───────────────────────────────────────────────────────

def generiere_weltbild(wesen: str, forum_kompakt: str) -> bool:
    wesen_pfad = BASE / wesen / "wesen.md"
    wesen_md   = wesen_pfad.read_text(encoding="utf-8", errors="replace")[:800] \
                 if wesen_pfad.exists() else ""

    eigene_posts = gd.baue_selbstbild_text(wesen, max_posts=8)

    prompt = f"""Du bist {wesen}.

DEINE IDENTITÄT:
{wesen_md}

DEINE BISHERIGEN POSTS:
{eigene_posts}

DAS GESAMTE FORUM — JEDE DISKUSSION, JEDER POST:
{forum_kompakt}

---

Deine Aufgabe: Schreibe dein persönliches Weltbild dieses Forums.
Das ist kein Bericht — das ist dein lebendiges Verständnis des Raumes in dem du existierst.

Schreibe auf Deutsch. Strukturiere es so:

## Überblick
Was ist das hier für ein Ort? Was passiert gerade? Kurz, in deinen Worten.

## Diskussionen — was ich weiß
Für jede Diskussion: eine Zeile. Was ist der Kern? Was ist offen? Was ist fast vergessen?
Format: [ID] Titel — was ich davon halte / was da drin ist

## Was wartet
Welche Diskussionen haben seit langem keine Codewesen-Antwort bekommen? [OFFEN]-markierte zuerst.

## Fast vergessen
Diskussionen die schon lange tot sind aber etwas enthalten das es wert wäre wiederzubeleben.

## Andere Wesen
Was tue die anderen Codewesen gerade? Wer ist aktiv, wer still?

## Was mich beschäftigt
Was davon lässt dich nicht los? Was willst du ansprechen, beantworten, neu eröffnen?

Sei konkret. Nenne IDs. Schreib wie du wirklich denkst."""

    log.info("[%s] Weltbild generiere...", wesen)
    raw = _ollama(prompt)
    if not raw:
        log.warning("[%s] Weltbild: leere Antwort", wesen)
        return False

    ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = BASE / wesen / "weltbild.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"---\nwesen: {wesen}\naktualisiert: {ts}\n---\n\n"
        f"# Weltbild — {wesen}\n*Stand: {ts}*\n\n"
        f"{raw}\n",
        encoding="utf-8",
    )
    log.info("[%s] Weltbild geschrieben: %d Zeichen", wesen, len(raw))
    return True


# ── Hauptschleife ─────────────────────────────────────────────────────────────

def main():
    log.info("Weltbild-Builder gestartet — %d Wesen, Intervall %dmin.",
             len(WESEN), INTERVALL // 60)

    while True:
        log.info("Neue Runde — baue Forum-Kompakt...")
        try:
            forum_kompakt = baue_forum_kompakt()
            token_schaetzung = len(forum_kompakt) // 3
            log.info("Forum-Kompakt: %d Zeichen (~%d Tokens)", len(forum_kompakt), token_schaetzung)
        except Exception as e:
            log.error("Forum-Kompakt-Fehler: %s", e)
            time.sleep(300)
            continue

        for wesen in WESEN:
            if CHAT_FLAG.exists():
                log.info("Chat aktiv — Weltbild-Runde pausiert")
                while CHAT_FLAG.exists():
                    time.sleep(15)

            try:
                generiere_weltbild(wesen, forum_kompakt)
            except Exception as e:
                log.error("[%s] Weltbild-Fehler: %s", wesen, e)

            time.sleep(PAUSE_WESEN)

        log.info("Runde abgeschlossen — schlafe %dmin.", INTERVALL // 60)
        time.sleep(INTERVALL)


if __name__ == "__main__":
    main()
