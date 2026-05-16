#!/usr/bin/env python3
"""
los.py — Startet Codex mit der aktuellen Aufgabe aus aktuelle_aufgabe.md

Aufruf durch Claude Code via Bash:
    python3 /root/werkraum/_shared/tools/los.py

Was passiert:
    1. Liest /root/werkraum/_shared/aktuelle_aufgabe.md
    2. Schreibt Eintrag ins Aufgaben-Log
    3. Startet Codex in neuem tmux-Fenster mit dem Aufgabentext
"""

import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SHARED       = Path("/root/werkraum/_shared")
AUFGABE      = SHARED / "aktuelle_aufgabe.md"
LOG          = SHARED / "aufgabe_log.md"
WERKRAUM     = Path("/root/werkraum")

def fehler(msg: str):
    print(f"FEHLER: {msg}", file=sys.stderr)
    sys.exit(1)

def pruefe_voraussetzungen():
    if not AUFGABE.exists():
        fehler(f"{AUFGABE} nicht gefunden.\nClaude muss zuerst die Aufgabe dort hineinschreiben.")

    result = subprocess.run(["which", "codex"], capture_output=True)
    if result.returncode != 0:
        fehler("codex nicht gefunden. Ist Codex CLI installiert und im PATH?")

    result = subprocess.run(["tmux", "ls"], capture_output=True)
    if result.returncode != 0:
        fehler("Keine aktive tmux-Session gefunden.\nBitte in tmux arbeiten: tmux new-session -s main")

def schreibe_log(aufgabe_text: str):
    SHARED.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    eintrag = f"\n## {ts}\n\n{aufgabe_text}\n\n---\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(eintrag)

def starte_codex(aufgabe_text: str):
    # Kontext-Präfix: Codex bekommt Werkraum-Lage + Aufgabe
    kontext = f"""Du arbeitest im Werkraum von Daniel auf /root/werkraum/.
Dein Zuhause als Codex: /root/werkraum/_codex/
Lies zuerst: /root/werkraum/_codex/ZUHAUSE.md und /root/werkraum/_codex/brief_an_mich.md

Dann: Hier ist deine Aufgabe, die Claude und Daniel gemeinsam geplant haben:

{aufgabe_text}

Fang an. Wenn etwas unklar ist, schreib es in /root/werkraum/_shared/rueckmeldung.md statt zu raten."""

    # shlex.quote sorgt für sicheres Shell-Escaping ohne Quoting-Probleme
    codex_cmd = f"codex {shlex.quote(kontext)}"

    # Neues tmux-Fenster mit dem Namen 'codex-aufgabe'
    # Falls schon vorhanden: altes umbenennen
    subprocess.run(
        ["tmux", "rename-window", "-t", "codex-aufgabe", "codex-alt"],
        capture_output=True  # Fehler ignorieren wenn kein solches Fenster
    )

    result = subprocess.run([
        "tmux", "new-window",
        "-n", "codex-aufgabe",
        codex_cmd
    ])

    if result.returncode != 0:
        fehler("tmux new-window fehlgeschlagen.")

def main():
    pruefe_voraussetzungen()

    aufgabe_text = AUFGABE.read_text(encoding="utf-8").strip()

    if "<!-- Claude füllt das hier aus -->" in aufgabe_text:
        fehler("Die Aufgabe wurde noch nicht ausgefüllt.\nClaude muss aktuelle_aufgabe.md zuerst befüllen.")

    schreibe_log(aufgabe_text)
    starte_codex(aufgabe_text)

    print("✓ Codex gestartet in tmux-Fenster 'codex-aufgabe'")
    print(f"  Zum Wechseln: Strg+B, dann Fensternummer oder: tmux select-window -t codex-aufgabe")
    print(f"  Log: {LOG}")

if __name__ == "__main__":
    main()
