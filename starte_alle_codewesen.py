#!/usr/bin/env python3
"""
Startet alle 6 Codewesen-Agenten als separate Prozesse.
Überwacht sie und startet abgestürzte neu.

Aufruf:
  python3 starte_alle_codewesen.py          # alle
  python3 starte_alle_codewesen.py stop     # alle stoppen
  python3 starte_alle_codewesen.py status   # status anzeigen
"""

import json
import signal
import subprocess
import sys
import time
from pathlib import Path

BASE   = Path("/root/werkraum/codewesen")
TOKENS = BASE / "_api_tokens.json"

NAMEN = list(json.loads(TOKENS.read_text(encoding="utf-8")).keys())

RESTART_PAUSE = 10   # Sekunden warten vor Neustart
CHECK_INTERVAL = 5   # Sekunden zwischen Überwachungs-Checks

prozesse: dict[str, subprocess.Popen] = {}
laufen = True


def starte(name: str) -> subprocess.Popen:
    log_pfad = BASE / name / "reaktion.log"
    log_pfad.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.Popen(
        ["python3", "-u", "codewesen_agent.py", name],
        cwd="/root/werkraum",
        # stdout/stderr gehen in reaktion.log (der Agent loggt selbst dorthin)
    )
    print(f"[{name}] gestartet (PID {p.pid})")
    return p


def stop_alle():
    global laufen
    laufen = False
    print("\nStoppe alle Agenten...")
    for name, p in prozesse.items():
        try:
            p.terminate()
            print(f"[{name}] SIGTERM gesendet")
        except Exception:
            pass
    time.sleep(3)
    for name, p in prozesse.items():
        if p.poll() is None:
            try:
                p.kill()
                print(f"[{name}] SIGKILL")
            except Exception:
                pass


def signal_handler(sig, frame):
    stop_alle()
    sys.exit(0)


def status():
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    print(f"{'Name':<22} {'Status':<12} {'Letzte Aktivität'}")
    print("-" * 60)
    for name in NAMEN:
        log = BASE / name / "reaktion.log"
        if log.exists():
            zeilen = log.read_text(encoding="utf-8", errors="replace").splitlines()
            letzte = zeilen[-1][:80] if zeilen else "(leer)"
        else:
            letzte = "(kein Log)"
        print(f"{name:<22} {'?':<12} {letzte}")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            status()
            return
        if sys.argv[1] == "stop":
            # Versuche laufende Prozesse zu stoppen via PID-Suche
            import os
            result = subprocess.run(
                ["pgrep", "-f", "codewesen_agent.py"],
                capture_output=True, text=True
            )
            pids = result.stdout.strip().split()
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"SIGTERM → PID {pid}")
                except Exception:
                    pass
            return

    signal.signal(signal.SIGINT,  signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"Starte {len(NAMEN)} Codewesen-Agenten...")
    for name in NAMEN:
        prozesse[name] = starte(name)
        time.sleep(1)  # kurz staffeln damit Ollama nicht überflutet wird

    print("Alle gestartet. Überwache...\n")

    while laufen:
        time.sleep(CHECK_INTERVAL)
        for name in NAMEN:
            p = prozesse[name]
            if p.poll() is not None:  # Prozess beendet
                exit_code = p.returncode
                print(f"[{name}] abgestürzt (exit {exit_code}) — starte neu in {RESTART_PAUSE}s")
                time.sleep(RESTART_PAUSE)
                if laufen:
                    prozesse[name] = starte(name)


if __name__ == "__main__":
    main()
