#!/usr/bin/env python3
"""
Resonanzkörper: Ollama liest eine Spiegel-Datei und wirft eine unbequeme Frage zurück.
Aufruf: resonanz.py <spiegel-datei.md>
Ergebnis wird an die Datei angehängt.
"""
import sys
import os
import json
import datetime
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELL = "dolphin-mistral:7b"


def ollama(prompt):
    data = json.dumps({
        "model": MODELL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.8}
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"]


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("Nutzung: resonanz.py <spiegel-datei.md>")
        sys.exit(1)

    datei = sys.argv[1]
    with open(datei) as f:
        inhalt = f.read()

    prompt = f"""Du liest eine Reflexion eines KI-Systems über ein Konzept in einem Softwareprojekt.
Du bist nicht dieses KI-System — du bist ein anderes Modell mit anderer Perspektive.

Deine einzige Aufgabe: Stelle eine einzige unbequeme Frage oder benenne einen blinden Fleck.
Keine Zusammenfassung. Keine Erklärung. Kein Lob. Nur die Frage oder der blinde Fleck.
Maximal 3 Sätze. Antworte auf Deutsch.

Reflexion:
{inhalt[:3000]}"""

    print(f"Sende an Ollama/{MODELL}...")
    antwort = ollama(prompt).strip()

    zeitstempel = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(datei, "a") as f:
        f.write(f"\n---\n\n## Resonanz *(Ollama/{MODELL}, {zeitstempel})*\n\n{antwort}\n")

    print(f"Resonanz angehängt an: {datei}")
    print(f"\n{antwort}")


if __name__ == "__main__":
    main()
