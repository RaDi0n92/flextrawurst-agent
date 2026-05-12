from __future__ import annotations

import json
import time
from pathlib import Path

import requests

ZUSTAND_DATEI = Path("/root/werkraum/state/freier_modus.json")
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELL_FREI = "dolphin-mistral:7b"
AUTO_TIMEOUT_SEKUNDEN = 600  # 10 Minuten


def _lies_zustand() -> dict:
    if not ZUSTAND_DATEI.exists():
        return {"aktiv": False, "letzte_nutzung": 0.0}
    try:
        return json.loads(ZUSTAND_DATEI.read_text(encoding="utf-8"))
    except Exception:
        return {"aktiv": False, "letzte_nutzung": 0.0}


def _schreibe_zustand(aktiv: bool) -> None:
    ZUSTAND_DATEI.parent.mkdir(parents=True, exist_ok=True)
    ZUSTAND_DATEI.write_text(
        json.dumps({"aktiv": aktiv, "letzte_nutzung": time.time()}, ensure_ascii=False),
        encoding="utf-8",
    )


def ist_aktiv() -> bool:
    z = _lies_zustand()
    if not z.get("aktiv"):
        return False
    # Auto-Timeout
    if time.time() - z.get("letzte_nutzung", 0) > AUTO_TIMEOUT_SEKUNDEN:
        _schreibe_zustand(False)
        _entlade_modell(MODELL_FREI)
        return False
    return True


def aktualisiere_timestamp() -> None:
    z = _lies_zustand()
    if z.get("aktiv"):
        _schreibe_zustand(True)


def aktivieren() -> str:
    _schreibe_zustand(True)
    return f"Freier Modus AN — Modell: {MODELL_FREI}. Auto-Reset nach {AUTO_TIMEOUT_SEKUNDEN // 60} Min Inaktivität."


def deaktivieren() -> str:
    _schreibe_zustand(False)
    _entlade_modell(MODELL_FREI)
    return "Freier Modus AUS — zurück zu Gemma4."


def _entlade_modell(name: str) -> None:
    try:
        requests.post(
            OLLAMA_URL,
            json={"model": name, "messages": [], "keep_alive": 0},
            timeout=10,
        )
    except Exception:
        pass


def erkenne_befehl(text: str) -> str | None:
    """Gibt 'an', 'aus' oder None zurück."""
    klein = text.strip().lower()
    if klein in {"freier modus an", "freier modus ein", "/frei", "/freiheit"}:
        return "an"
    if klein in {"freier modus aus", "freier modus off", "/unfrei"}:
        return "aus"
    return None
