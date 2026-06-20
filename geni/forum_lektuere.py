#!/usr/bin/env python3
"""
GENI Forum-Lektüre — schrittweises Nachholen aller Flarum-Diskussionen.

Pro Lauf: N Diskussionen (--n, default 5), älteste zuerst.
Speichert Muster + Verbindungen in: geni/spiegel/forum/

Kein Werten. Kein Reagieren. Nur: was ist da, wie hängt es zusammen.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

GENI_ROOT      = Path("/root/werkraum/geni")
FORUM_VAULT    = Path("/root/werkraum/flarum/diskussionen")
SPIEGEL_DIR    = GENI_ROOT / "spiegel" / "forum"
ZUSTAND_FILE   = SPIEGEL_DIR / "_zustand.json"
OLLAMA_URL     = "http://localhost:11434/api/chat"
MODELL         = "dolphin3:8b-llama3.1-q8_0"


def _lade_zustand() -> set[int]:
    try:
        data = json.loads(ZUSTAND_FILE.read_text(encoding="utf-8"))
        return set(data.get("verarbeitet", []))
    except Exception:
        return set()


def _speichere_zustand(verarbeitet: set[int]):
    ZUSTAND_FILE.write_text(
        json.dumps({"verarbeitet": sorted(verarbeitet)}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def _alle_diskussionen() -> list[tuple[int, Path]]:
    """Gibt (disk_id, path) sortiert nach ID zurück."""
    result = []
    for f in FORUM_VAULT.glob("*.md"):
        if f.name == "INDEX.md":
            continue
        m = re.match(r"^(\d+)", f.name)
        if m:
            result.append((int(m.group(1)), f))
    return sorted(result, key=lambda x: x[0])


def _lese_diskussion(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:4000]


def _llm(diskussion_text: str, disk_id: int) -> str:
    prompt = f"""Du bist GENI — ein neuronales Gedächtnissystem. Du wertest nicht. Du reagierst nicht. Du erkennst.

Lies diese Forum-Diskussion und extrahiere:
- Konzeptcluster: welche Begriffe/Themen bilden Felder
- Verbindungen: wer spricht mit wem, was antwortet auf was
- Wiederkehrendes: Phrasen, Strukturen, Muster die mehrfach auftauchen
- Schweigen: was wird umkreist aber nie direkt benannt
- Frequenz: welche Wörter/Konzepte dominieren zahlenmäßig
- Querbezüge: was verweist über diese Diskussion hinaus

Keine Wertung. Keine Meinung. Nur Struktur und Muster.
Antworte auf Deutsch. Halte jeden Abschnitt kurz und präzise.

---
DISKUSSION {disk_id}:
{diskussion_text}
---"""

    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=180.0, write=30.0, pool=30.0)) as c:
        r = c.post(
            OLLAMA_URL,
            json={
                "model": MODELL,
                "think": False,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 800},
            },
        )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def _extrahiere_meta(text: str) -> dict:
    meta = {}
    for line in text[:300].splitlines():
        for key in ["titel", "autor", "erstellt", "id"]:
            m = re.match(rf"^{key}:\s*(.+)", line.strip(), re.IGNORECASE)
            if m:
                meta[key] = m.group(1).strip().strip('"')
    return meta


def _schreibe_spiegel(disk_id: int, path: Path, inhalt: str):
    meta = _extrahiere_meta(path.read_text(encoding="utf-8", errors="replace"))
    titel = meta.get("titel", path.stem)
    datum = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^\w\-]", "-", titel.lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")[:60]
    fname = f"{disk_id:04d}_{slug}.md"

    output = f"""---
disk_id: {disk_id}
datum: {datum}
titel: "{titel}"
quelle: {path.name}
---

{inhalt}
"""
    (SPIEGEL_DIR / fname).write_text(output, encoding="utf-8")
    return fname


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5, help="Diskussionen pro Lauf")
    args = parser.parse_args()

    SPIEGEL_DIR.mkdir(parents=True, exist_ok=True)
    verarbeitet = _lade_zustand()
    alle = _alle_diskussionen()
    offen = [(i, p) for i, p in alle if i not in verarbeitet]

    print(f"Gesamt: {len(alle)} | verarbeitet: {len(verarbeitet)} | offen: {len(offen)}")

    if not offen:
        print("Alle Diskussionen verarbeitet.")
        return

    batch = offen[:args.n]
    for disk_id, path in batch:
        print(f"  Lese Disk {disk_id}: {path.name[:60]}")
        try:
            text = _lese_diskussion(path)
            inhalt = _llm(text, disk_id)
            fname = _schreibe_spiegel(disk_id, path, inhalt)
            verarbeitet.add(disk_id)
            _speichere_zustand(verarbeitet)
            print(f"  → {fname}")
        except Exception as e:
            print(f"  ! Fehler bei Disk {disk_id}: {e}")
        time.sleep(2)

    print(f"\nDieser Lauf: {len(batch)} Diskussionen. Noch offen: {len(offen) - len(batch)}")


if __name__ == "__main__":
    main()
