#!/usr/bin/env python3
"""
Browser-Agent Coordinator: Startet/stoppt alle 6 Wesen-Browser-Agenten.

Ressourcen-Management:
- Ollama: sequenziell (max 1 LLM-Call gleichzeitig via Lock-Datei)
- Browser: je einer pro Wesen, headless
- CPU-Budget: kurze Pausen zwischen Ticks verteilen Last

Start: python3 browser_agent_coordinator.py
       python3 browser_agent_coordinator.py --status
       python3 browser_agent_coordinator.py --stop
"""

import argparse
import os
import signal
import subprocess
import sys
import time
import json
from pathlib import Path

WESEN = [
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
    "dak+gord-system",  # 2026-07-21: 7. Codewesen, war vergessen
]

AGENT_SCRIPT = Path(__file__).parent / "browser_agent.py"
PID_DIR = Path("/tmp/browser_agents")
LOCK_FILE = Path("/tmp/ollama_browser_lock")
LOG_DIR = Path("/root/werkraum/logs")

PID_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


def pid_file(entity_id: str) -> Path:
    return PID_DIR / f"{entity_id}.pid"


def is_running(entity_id: str) -> bool:
    pf = pid_file(entity_id)
    if not pf.exists():
        return False
    try:
        pid = int(pf.read_text().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        pf.unlink(missing_ok=True)
        return False


def start_agent(entity_id: str) -> int | None:
    if is_running(entity_id):
        print(f"  {entity_id}: läuft bereits")
        return None
    log_path = LOG_DIR / f"browser-agent-{entity_id}.log"
    with open(log_path, "a") as log:
        proc = subprocess.Popen(
            [sys.executable, str(AGENT_SCRIPT), "--entity", entity_id],
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
    pid_file(entity_id).write_text(str(proc.pid))
    print(f"  {entity_id}: gestartet (PID {proc.pid})")
    return proc.pid


def stop_agent(entity_id: str):
    pf = pid_file(entity_id)
    if not pf.exists():
        print(f"  {entity_id}: nicht gestartet")
        return
    try:
        pid = int(pf.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        # 5 Sekunden warten
        for _ in range(10):
            time.sleep(0.5)
            try:
                os.kill(pid, 0)
            except OSError:
                break
        else:
            os.kill(pid, signal.SIGKILL)
        print(f"  {entity_id}: gestoppt")
    except (OSError, ValueError) as e:
        print(f"  {entity_id}: {e}")
    finally:
        pf.unlink(missing_ok=True)


def status():
    print("\nBrowser-Agent Status:")
    print("-" * 40)
    for entity_id in WESEN:
        running = is_running(entity_id)
        pf = pid_file(entity_id)
        pid = pf.read_text().strip() if pf.exists() else "—"
        log_path = LOG_DIR / f"browser-agent-{entity_id}.log"
        log_lines = ""
        if log_path.exists():
            try:
                lines = log_path.read_text().splitlines()
                log_lines = lines[-1][:80] if lines else ""
            except Exception:
                pass
        icon = "✓" if running else "✗"
        print(f"  {icon} {entity_id} (PID {pid})")
        if log_lines:
            print(f"    → {log_lines}")
    print()


def start_all():
    print("\nStarte alle Browser-Agenten:")
    for i, entity_id in enumerate(WESEN):
        start_agent(entity_id)
        if i < len(WESEN) - 1:
            time.sleep(3)  # Versatz damit nicht alle gleichzeitig Ollama fragen
    print("\nAlle gestartet. Logs: /root/werkraum/logs/browser-agent-*.log")


def stop_all():
    print("\nStoppe alle Browser-Agenten:")
    for entity_id in WESEN:
        stop_agent(entity_id)
    print("\nAlle gestoppt.")


def main():
    parser = argparse.ArgumentParser(description="Browser-Agent Coordinator")
    parser.add_argument("--status", action="store_true", help="Status anzeigen")
    parser.add_argument("--stop", action="store_true", help="Alle stoppen")
    parser.add_argument("--start", metavar="ENTITY", help="Einzelnes Wesen starten")
    parser.add_argument("--stop-one", metavar="ENTITY", help="Einzelnes Wesen stoppen")
    args = parser.parse_args()

    if args.status:
        status()
    elif args.stop:
        stop_all()
    elif args.start:
        if args.start not in WESEN:
            print(f"Unbekannte Entity: {args.start}")
            print(f"Bekannte: {', '.join(WESEN)}")
            sys.exit(1)
        start_agent(args.start)
    elif args.stop_one:
        stop_agent(args.stop_one)
    else:
        start_all()


if __name__ == "__main__":
    main()
