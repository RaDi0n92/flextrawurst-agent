#!/usr/bin/env python3
"""Sofort-Batch: GENI liest Kerndateien und erklaert warum sie existieren."""

import sys
sys.path.insert(0, "/root/werkraum")

from pathlib import Path
from datetime import datetime
import ollama

SPIEGELAGENTEN = Path("/root/werkraum/erkenntnis/spiegelagenten")
SPIEGELAGENTEN.mkdir(parents=True, exist_ok=True)

KERNDATEIEN = [
    # GENI
    "/root/werkraum/geni/ICH.md",
    "/root/werkraum/geni/kern/prinzipien.md",
    "/root/werkraum/geni/kern/sprache.md",
    "/root/werkraum/geni/kern/startimpuls.md",
    "/root/werkraum/geni/hoerer.py",
    "/root/werkraum/geni/web.py",
    # dak+gord
    "/root/werkraum/agent/dak_gord_system/neugierkern.py",
    "/root/werkraum/agent/dak_gord_system/graphen/gespraechsgraf.py",
    "/root/werkraum/starte_dak_gord_system.py",
    "/root/werkraum/agent/dak_gord_system/kerne/beziehungsorgan.py",
    "/root/werkraum/agent/dak_gord_system/kerne/erinnerungsgedaechtnis.py",
    # Codewesen
    "/root/werkraum/codewesen_chat.py",
    "/root/werkraum/codewesen_takt.py",
    "/root/werkraum/codewesen_reaktion.py",
    "/root/werkraum/codewesen_werkzeuge.py",
    # Visionen
    "/root/werkraum/projekt/vision5.md",
    "/root/werkraum/projekt/vision6.md",
    "/root/werkraum/projekt/vision7.md",
    # System
    "/root/werkraum/web_chat.py",
    "/root/werkraum/watchdog_daemon.py",
]

SYSTEM = (
    "Du bist GENI. Neuronales Gedaechtnis-Wesen.\n"
    "Du liest eine Datei aus deiner Welt.\n"
    "Schreibe 4 bis 6 Saetze. Keine Begruessung. Kein Chatton.\n"
    "Beantworte:\n"
    "- Warum existiert diese Datei ueberhaupt?\n"
    "- Was waere ohne sie anders oder kaputt?\n"
    "- Was erkennst du in ihr das nicht sofort sichtbar ist?\n"
    "Deine eigene Stimme. Nicht generisch.\n"
)

def spiegle(pfad_str: str):
    pfad = Path(pfad_str)
    if not pfad.exists():
        print(f"  FEHLT: {pfad_str}")
        return

    try:
        inhalt = pfad.read_text(encoding="utf-8", errors="replace")[:3000]
    except Exception as e:
        print(f"  LESEFEHLER: {pfad_str} — {e}")
        return

    nutzer = f"DATEI: {pfad}\n\nINHALT:\n{inhalt}"

    try:
        antwort = ollama.chat(
            model="dolphin3:8b-llama3.1-q8_0",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": nutzer},
            ]
        )
        notiz = antwort["message"]["content"].strip()
    except Exception as e:
        print(f"  OLLAMA-FEHLER: {pfad_str} — {e}")
        return

    # Dateiname fuer Spiegelagent
    if pfad.suffix.lower() == ".md":
        spiegel_name = pfad.stem + ".md"
    else:
        spiegel_name = pfad.name + ".md"
    spiegel_datei = SPIEGELAGENTEN / spiegel_name

    zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M")
    eintrag = (
        f"\n---\n## GENI-Spiegel {zeitstempel}\n"
        f"Datei: `{pfad}`\n\n"
        f"{notiz}\n"
    )

    with open(spiegel_datei, "a", encoding="utf-8") as f:
        f.write(eintrag)

    print(f"  OK: {pfad.name}")

if __name__ == "__main__":
    print(f"GENI-Spiegel-Batch startet — {len(KERNDATEIEN)} Kerndateien\n")
    for pfad in KERNDATEIEN:
        print(f"Lese: {Path(pfad).name} ...")
        spiegle(pfad)
    print("\nFertig.")
