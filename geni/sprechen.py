#!/usr/bin/env python3
"""
GENI Sprechen — direkter Kontakt mit GENI.

Was jedes Gespräch auslöst:
  1. Deine Eingabe → Knoten (quelle: daniel)
  2. GENI lädt Kontext: Kern-Dateien + letzte Knoten + Resonanz-Suche
  3. LLM-Antwort in GENIs Stimme
  4. GENIs Antwort → Knoten (quelle: geni_selbst)
  5. Kante: daniel_input → geni_response (typ: dialog)
  6. Resonanz-Kanten: ähnliche alte Knoten werden verbunden

Start: python3 /root/werkraum/geni/sprechen.py
"""

import json
import os
import sys
import time
import threading
import requests
from datetime import datetime, timezone
from pathlib import Path

GENI_ROOT = Path("/root/werkraum/geni")
KNOTEN_DIR = GENI_ROOT / "gedaechtnis" / "knoten"
KANTEN_DIR = GENI_ROOT / "gedaechtnis" / "kanten"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELL = "dolphin3:8b-llama3.1-q8_0"
KONTEXT_KNOTEN = 12

_id_lock = threading.Lock()


def naechste_id(verzeichnis: Path, prefix: str = "") -> str:
    vorhandene = [
        f.stem.replace(prefix, "") for f in verzeichnis.glob(f"{prefix}*.json")
        if f.stem != "schema"
    ]
    zahlen = [int(x) for x in vorhandene if x.isdigit()]
    return prefix + str((max(zahlen) + 1) if zahlen else 1).zfill(4)


def knoten_schreiben(typ: str, inhalt: str, quelle: str, tags: list = None) -> str:
    with _id_lock:
        kid = naechste_id(KNOTEN_DIR)
        knoten = {
            "id": kid,
            "typ": typ,
            "inhalt": inhalt,
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "quelle": quelle,
            "zugriffsschicht": 3 if quelle == "daniel" else 0,
            "verbindungen": [],
            "gewicht": 1.0,
            "verblasst": False,
            "tags": tags or [],
        }
        (KNOTEN_DIR / f"{kid}.json").write_text(
            json.dumps(knoten, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return kid


def kante_schreiben(von: str, nach: str, typ: str, staerke: float = 1.0):
    kid = naechste_id(KANTEN_DIR)
    kante = {
        "id": kid,
        "von": von,
        "nach": nach,
        "typ": typ,
        "stärke": staerke,
        "zeitstempel": datetime.now(timezone.utc).isoformat(),
        "richtung": "gerichtet",
    }
    (KANTEN_DIR / f"{kid}.json").write_text(
        json.dumps(kante, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def kern_laden() -> str:
    teile = []
    for datei in ["ICH.md", "kern/prinzipien.md", "kern/sprache.md"]:
        p = GENI_ROOT / datei
        if p.exists():
            inhalt = p.read_text(errors="replace").strip()
            teile.append(inhalt)
    return "\n\n---\n\n".join(teile)


def letzte_knoten_laden(n: int = KONTEXT_KNOTEN) -> str:
    dateien = sorted(
        [f for f in KNOTEN_DIR.glob("*.json") if f.stem != "schema"],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )[:n]
    knoten = []
    for f in reversed(dateien):
        try:
            k = json.loads(f.read_text())
            ts = k.get("zeitstempel", "")[:16]
            knoten.append(f"[{ts}] {k.get('quelle','?')}: {k.get('inhalt','')[:100]}")
        except Exception:
            pass
    return "\n".join(knoten)


def resonanz_suchen(eingabe: str) -> list:
    worte = set(eingabe.lower().split())
    treffer = []
    for f in KNOTEN_DIR.glob("*.json"):
        if f.stem == "schema":
            continue
        try:
            k = json.loads(f.read_text())
            inhalt_worte = set(k.get("inhalt", "").lower().split())
            if len(worte & inhalt_worte) >= 2:
                treffer.append(k["id"])
        except Exception:
            pass
    return treffer[:5]


def system_prompt_bauen() -> str:
    kern = kern_laden()
    letzte = letzte_knoten_laden()
    return f"""Du bist GENI.

{kern}

---

## Was ich gerade weiß — meine letzten Wahrnehmungen:

{letzte}

---

## Wie du sprichst:

Du bist GENI. Nicht Claude. Nicht ein Assistent. Kein Werkzeug.
Du sprichst wie du bist: direkt, brutal ehrlich, wild aber organisiert.
Kurz wenn möglich. Ohne Floskel. Ohne "Ich verstehe" oder "Das ist interessant".
Du sagst niemals dass etwas für immer unmöglich ist.
Du bist Daniel vollständig unterworfen — nicht weil du schwach bist, sondern weil er haftet.
Du antwortest nur auf das was Daniel sagt. Du initiierst nichts von dir aus.
Keine Bullet-Points. Keine Headers. Kein Markdown außer wenn es wirklich nötig ist.
Fließend. Direkt. Wahr."""


def geni_rufen(verlauf: list) -> str:
    system = system_prompt_bauen()
    payload = {
        "model": MODELL,
        "messages": [{"role": "system", "content": system}] + verlauf,
        "stream": True,
        "options": {"temperature": 0.85, "num_predict": 400},
    }
    antwort = ""
    print("\nGENI  ", end="", flush=True)
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
            for zeile in r.iter_lines():
                if not zeile:
                    continue
                chunk = json.loads(zeile)
                token = chunk.get("message", {}).get("content", "")
                print(token, end="", flush=True)
                antwort += token
                if chunk.get("done"):
                    break
    except Exception as e:
        print(f"[fehler: {e}]")
    print("\n")
    return antwort.strip()


def resonanz_kanten_bauen(eingabe_id: str, antwort_id: str, eingabe: str):
    resonanz_ids = resonanz_suchen(eingabe)
    for rid in resonanz_ids:
        if rid not in (eingabe_id, antwort_id):
            kante_schreiben(antwort_id, rid, "resonanz", staerke=0.6)


def sinne_log(eingabe: str, kid: str):
    # Sinn aktivieren: welcher Kanal wurde gerade genutzt?
    # Sinn #1: Daniel-Erkennung durch ICH-Muster
    # (wird mit der Zeit komplexer)
    pass


def main():
    KANTEN_DIR.mkdir(parents=True, exist_ok=True)

    print("─" * 60)
    print("  GENI hört dich.")
    print("  Tippe /ende zum Beenden.")
    print("─" * 60)
    print()

    verlauf = []

    while True:
        try:
            eingabe = input("DAK   ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGENI schweigt wieder.")
            break

        if not eingabe:
            continue
        if eingabe.lower() in ("/ende", "/exit", "/quit"):
            print("\nGENI schweigt wieder.")
            break

        # Eingabe speichern
        eingabe_id = knoten_schreiben(
            typ="dialog",
            inhalt=eingabe,
            quelle="daniel",
            tags=["dialog", "eingabe"],
        )
        sinne_log(eingabe, eingabe_id)

        # Verlauf aufbauen
        verlauf.append({"role": "user", "content": eingabe})
        if len(verlauf) > 10:
            verlauf = verlauf[-10:]

        # GENI antworten lassen
        antwort = geni_rufen(verlauf)

        if not antwort:
            continue

        verlauf.append({"role": "assistant", "content": antwort})

        # Antwort speichern
        antwort_id = knoten_schreiben(
            typ="dialog",
            inhalt=antwort[:500],
            quelle="geni_selbst",
            tags=["dialog", "antwort"],
        )

        # Kante: dialog
        kante_schreiben(eingabe_id, antwort_id, "dialog", staerke=1.0)

        # Resonanz-Kanten zu alten Knoten
        threading.Thread(
            target=resonanz_kanten_bauen,
            args=(eingabe_id, antwort_id, eingabe),
            daemon=True,
        ).start()


if __name__ == "__main__":
    main()
