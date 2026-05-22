#!/usr/bin/env python3
"""
Schlaf-Synthese: läuft nachts per Cron.
Liest alle Spiegel-Dateien, lässt Ollama Verbindungen ziehen
die ich (Codex) vielleicht nicht explizit gesehen habe.
Ergebnis: _codex/ideen/synthese_YYYY-MM-DD.md
"""
import os
import json
import datetime
import urllib.request
import urllib.error

SPIEGEL_DIR = "/root/werkraum/_codex/spiegel"
OUTPUT_DIR  = "/root/werkraum/_codex/ideen"
OLLAMA_URL  = "http://localhost:11434/api/generate"
MODELL      = "dolphin-mistral:7b"
MAX_ZEICHEN = 600  # pro Spiegel-Datei


def lade_spiegel():
    texte = []
    for fname in sorted(os.listdir(SPIEGEL_DIR)):
        if not fname.endswith(".md"):
            continue
        with open(os.path.join(SPIEGEL_DIR, fname)) as f:
            inhalt = f.read()
        texte.append(f"## {fname}\n{inhalt[:MAX_ZEICHEN]}")
    return "\n\n---\n\n".join(texte)


def ollama(prompt):
    data = json.dumps({
        "model": MODELL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["response"]


def main():
    heute = datetime.date.today().isoformat()
    outfile = os.path.join(OUTPUT_DIR, f"synthese_{heute}.md")

    if os.path.exists(outfile):
        print(f"Synthese für {heute} existiert bereits: {outfile}")
        return

    spiegel_text = lade_spiegel()
    if not spiegel_text.strip():
        print("Keine Spiegel-Dateien gefunden.")
        return

    prompt = f"""Du liest Reflexionen eines KI-Systems (Codex) über ein Projekt namens flextrawurst.
Das System hat diese Reflexionen selbst geschrieben. Du bist nicht Codex.

Aufgabe: Finde 3-5 Verbindungen oder Muster die in diesen Reflexionen stecken,
die das schreibende System vielleicht nicht explizit formuliert hat.

Kein Einleitung. Keine Zusammenfassung. Nur die Verbindungen — nummeriert, direkt, konkret.

{spiegel_text[:7000]}"""

    print(f"Sende {len(spiegel_text[:7000])} Zeichen an Ollama/{MODELL}...")
    antwort = ollama(prompt)

    inhalt = f"""---
name: synthese-{heute}
type: schlaf-synthese
modell: {MODELL}
datum: {heute}
---

# Schlaf-Synthese {heute}

*Nicht von Codex. Generiert von Ollama/{MODELL} während Codex schlief.*

---

{antwort.strip()}
"""

    with open(outfile, "w", encoding="utf-8", newline="\n") as f:
        f.write(inhalt)

    print(f"Geschrieben: {outfile}")


if __name__ == "__main__":
    main()
