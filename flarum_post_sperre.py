#!/usr/bin/env python3
"""
flarum_post_sperre.py — Schalter für die Flarum-Post-Sperre.

Einziger Zustand: gesperrt oder nicht. Wird von flarum_api.post_reply()
und flarum_api.start_discussion() geprüft — das sind die einzigen zwei
Stellen im ganzen System, über die tatsächlich nach Flarum geschrieben
wird, alle anderen Aufrufer (codewesen_reaktion.py, erstpost.py, etc.)
laufen durch diese beiden Funktionen hindurch.

codewesen_antwort_auf_daniel.py ist der einzige bewusst ausgenommene
Aufrufer (Daniel soll weiter Antworten bekommen können) und übergibt
dafür erlaubt_trotz_sperre=True.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_ZUSTAND_DATEI = Path("/root/werkraum/codewesen/_flarum_post_sperre.json")


class FlarumPostGesperrt(Exception):
    """Wird geworfen wenn post_reply/start_discussion bei aktiver Sperre ohne Ausnahme aufgerufen werden."""
    pass


def _lies() -> dict:
    if not _ZUSTAND_DATEI.exists():
        return {"gesperrt": False}
    try:
        return json.loads(_ZUSTAND_DATEI.read_text())
    except Exception:
        return {"gesperrt": False}


def _schreibe(zustand: dict) -> None:
    _ZUSTAND_DATEI.parent.mkdir(parents=True, exist_ok=True)
    _ZUSTAND_DATEI.write_text(json.dumps(zustand, indent=2, ensure_ascii=False))


def ist_gesperrt() -> bool:
    return bool(_lies().get("gesperrt", False))


def status() -> dict:
    return _lies()


def sperren(grund: str, von: str = "Daniel") -> dict:
    zustand = {
        "gesperrt": True,
        "seit": datetime.now(timezone.utc).isoformat(),
        "grund": grund,
        "von": von,
    }
    _schreibe(zustand)
    return zustand


def entsperren(von: str = "Daniel") -> dict:
    alt = _lies()
    zustand = {
        "gesperrt": False,
        "seit": datetime.now(timezone.utc).isoformat(),
        "vorherige_sperre_seit": alt.get("seit") if alt.get("gesperrt") else alt.get("vorherige_sperre_seit"),
        "vorheriger_grund": alt.get("grund") if alt.get("gesperrt") else alt.get("vorheriger_grund"),
        "von": von,
    }
    _schreibe(zustand)
    return zustand


def pruefe(erlaubt_trotz_sperre: bool = False) -> None:
    """Wirft FlarumPostGesperrt, wenn gesperrt ist und keine Ausnahme greift."""
    if erlaubt_trotz_sperre:
        return
    zustand = _lies()
    if zustand.get("gesperrt"):
        raise FlarumPostGesperrt(
            f"Flarum-Post-Sperre aktiv seit {zustand.get('seit', '?')}: {zustand.get('grund', '?')}"
        )
