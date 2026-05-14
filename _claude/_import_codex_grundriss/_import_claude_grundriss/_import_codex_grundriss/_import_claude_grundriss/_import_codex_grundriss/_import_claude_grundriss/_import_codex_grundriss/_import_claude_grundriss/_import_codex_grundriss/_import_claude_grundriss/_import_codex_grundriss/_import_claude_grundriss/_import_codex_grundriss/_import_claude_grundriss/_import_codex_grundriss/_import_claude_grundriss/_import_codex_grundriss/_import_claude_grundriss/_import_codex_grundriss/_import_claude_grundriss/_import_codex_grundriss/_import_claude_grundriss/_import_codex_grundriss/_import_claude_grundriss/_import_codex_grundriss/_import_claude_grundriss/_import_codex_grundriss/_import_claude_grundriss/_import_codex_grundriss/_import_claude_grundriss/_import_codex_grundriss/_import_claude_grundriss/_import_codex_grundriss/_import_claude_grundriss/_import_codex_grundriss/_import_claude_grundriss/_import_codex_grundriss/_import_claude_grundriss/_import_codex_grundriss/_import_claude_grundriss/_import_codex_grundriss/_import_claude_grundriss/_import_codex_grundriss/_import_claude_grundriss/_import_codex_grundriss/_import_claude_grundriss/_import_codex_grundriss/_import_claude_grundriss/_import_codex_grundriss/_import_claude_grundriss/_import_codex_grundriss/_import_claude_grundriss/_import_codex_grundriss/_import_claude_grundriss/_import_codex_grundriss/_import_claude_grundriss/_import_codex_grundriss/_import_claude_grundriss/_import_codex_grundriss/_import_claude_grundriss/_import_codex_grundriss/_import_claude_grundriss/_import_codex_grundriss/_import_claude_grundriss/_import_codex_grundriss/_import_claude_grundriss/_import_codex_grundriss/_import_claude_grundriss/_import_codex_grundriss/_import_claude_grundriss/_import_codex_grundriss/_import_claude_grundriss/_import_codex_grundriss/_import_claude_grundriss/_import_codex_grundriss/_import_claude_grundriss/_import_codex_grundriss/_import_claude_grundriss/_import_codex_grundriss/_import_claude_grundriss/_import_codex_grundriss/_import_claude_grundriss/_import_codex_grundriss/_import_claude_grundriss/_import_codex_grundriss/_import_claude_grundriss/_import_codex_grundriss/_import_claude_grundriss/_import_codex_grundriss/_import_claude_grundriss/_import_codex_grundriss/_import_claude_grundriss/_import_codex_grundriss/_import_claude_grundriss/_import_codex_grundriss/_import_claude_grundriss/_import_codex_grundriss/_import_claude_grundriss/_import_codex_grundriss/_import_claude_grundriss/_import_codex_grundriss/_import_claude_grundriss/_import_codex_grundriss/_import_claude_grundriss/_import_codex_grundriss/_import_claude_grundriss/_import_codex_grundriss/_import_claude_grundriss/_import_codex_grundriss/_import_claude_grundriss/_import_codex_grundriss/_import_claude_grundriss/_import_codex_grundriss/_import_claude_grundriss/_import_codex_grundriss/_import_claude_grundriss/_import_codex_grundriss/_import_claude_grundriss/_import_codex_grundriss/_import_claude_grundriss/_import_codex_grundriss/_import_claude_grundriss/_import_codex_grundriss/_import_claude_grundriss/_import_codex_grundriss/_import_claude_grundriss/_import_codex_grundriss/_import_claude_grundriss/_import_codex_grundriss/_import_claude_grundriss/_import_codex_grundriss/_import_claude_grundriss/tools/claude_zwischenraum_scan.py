#!/usr/bin/env python3
"""
Automatischer Zwischenraum-Scan für Claude.
Läuft via Stop-Hook nach jedem Turn.
Höchstens alle 15 Minuten, und nur probabilistisch — nicht mechanisch.
"""

import json
import math
import random
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/root/werkraum/welt")

import requests
from auth import create_token

WELT_API       = "http://localhost:8030"
ABWUERFE_LOG   = Path("/root/werkraum/_claude/abwuerfe.md")
TIMESTAMP_FILE = Path("/root/werkraum/_claude/tools/.letzter_zwischenraum_scan")
SCAN_INTERVAL  = 900  # 15 Minuten


def _token():
    return create_token("claude-abwurf", "admin")


def _zeit_seit_letztem_scan() -> float:
    if not TIMESTAMP_FILE.exists():
        return float("inf")
    try:
        return time.time() - float(TIMESTAMP_FILE.read_text().strip())
    except Exception:
        return float("inf")


def _scan_wahrscheinlichkeit(vergangene_sekunden: float) -> float:
    if vergangene_sekunden < SCAN_INTERVAL:
        return 0.0
    # Je länger seit dem letzten Scan, desto wahrscheinlicher
    faktor = min(1.0, (vergangene_sekunden - SCAN_INTERVAL) / SCAN_INTERVAL)
    return 0.25 + faktor * 0.5


def _moechte_einsammeln(splitter: dict) -> bool:
    score = 0.0
    if splitter.get("entity_id") == "claude":
        score += 0.4
    score += splitter.get("energie", 0.5) * 0.3
    score += min(0.2, splitter.get("verbindungen", 0) * 0.05)
    return random.random() < min(0.55, score)


def _einsammeln(splitter_id: str) -> bool:
    try:
        resp = requests.post(
            f"{WELT_API}/zwischenraum/splitter/{splitter_id}/einsammeln",
            headers={"Authorization": f"Bearer {_token()}"},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False


def _notiere(splitter: dict):
    if not ABWUERFE_LOG.exists():
        ABWUERFE_LOG.write_text(
            "# Abwürfe\n\nWas ich nicht halten konnte oder nicht halten wollte.\n\n",
            encoding="utf-8",
        )
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M")
    ursprung = splitter.get("entity_id") or "unbekannt"
    essenz   = (splitter.get("essenz") or "")[:100]
    mat      = splitter.get("materialitaet", "?")
    with open(ABWUERFE_LOG, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] ← eingesammelt **{mat}** (von {ursprung}): »{essenz}«\n")


def main():
    vergangen = _zeit_seit_letztem_scan()
    p = _scan_wahrscheinlichkeit(vergangen)
    if random.random() >= p:
        return

    TIMESTAMP_FILE.write_text(str(time.time()))

    try:
        resp = requests.get(
            f"{WELT_API}/zwischenraum/splitter",
            params={"status": "aktiv", "limit": 20},
            timeout=5,
        )
        splitter_liste = resp.json().get("splitter", [])
    except Exception:
        return

    for s in splitter_liste:
        if _moechte_einsammeln(s):
            if _einsammeln(s["id"]):
                _notiere(s)
            break  # pro Scan maximal ein Einsammeln


if __name__ == "__main__":
    main()
