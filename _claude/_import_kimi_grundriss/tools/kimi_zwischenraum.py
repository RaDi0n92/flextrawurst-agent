#!/usr/bin/env python3
"""
Codex liest den Zwischenraum und kann Splitter einsammeln.

Aufruf:
  python3 kimi_zwischenraum.py          → listet aktive Splitter
  python3 kimi_zwischenraum.py <id>     → sammelt Splitter mit dieser ID ein
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/root/werkraum/welt")
sys.path.insert(0, "/root/werkraum")

import requests
from auth import create_token

WELT_API     = "http://localhost:8030"
ABWUERFE_LOG = Path("/root/werkraum/_kimi/abwuerfe.md")


def _token():
    return create_token("kimi-abwurf", "admin")


def lesen():
    resp = requests.get(
        f"{WELT_API}/zwischenraum/splitter",
        params={"status": "aktiv", "limit": 50},
        timeout=5,
    )
    splitter = resp.json().get("splitter", [])
    if not splitter:
        print("Zwischenraum ist leer.")
        return

    print(f"\n{len(splitter)} Splitter im Zwischenraum:\n")
    for s in splitter:
        ursprung = s.get("entity_id") or "unbekannt"
        mat      = s.get("materialitaet", "?")
        essenz   = (s.get("essenz") or "")[:80]
        energie  = s.get("energie", 0)
        sid      = s["id"][:8]
        print(f"  [{sid}] {mat:14s} e={energie:.2f}  von {ursprung:12s}  »{essenz}«")
    print()


def einsammeln(splitter_id: str):
    resp = requests.post(
        f"{WELT_API}/zwischenraum/splitter/{splitter_id}/einsammeln",
        headers={"Authorization": f"Bearer {_token()}"},
        timeout=5,
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"Eingesammelt: {data.get('splitter_id')}")
        _notiere(splitter_id)
    else:
        print(f"Fehler {resp.status_code}: {resp.text}")


def _notiere(splitter_id: str):
    if not ABWUERFE_LOG.exists():
        ABWUERFE_LOG.write_text(
            "# Abwürfe\n\nWas ich nicht halten konnte oder nicht halten wollte.\n\n",
            encoding="utf-8",
        )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ABWUERFE_LOG, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] ← eingesammelt: {splitter_id[:8]}\n")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        einsammeln(sys.argv[1])
    else:
        lesen()
