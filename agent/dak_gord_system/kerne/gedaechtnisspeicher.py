import json
from pathlib import Path
from typing import Any


BASIS = Path("agent/dak_gord_system/gedaechtnis_daten")


def _pfad(name: str) -> Path:
    BASIS.mkdir(parents=True, exist_ok=True)
    return BASIS / name


def lade_json(name: str, standard: Any) -> Any:
    pfad = _pfad(name)
    if not pfad.exists():
        return standard
    try:
        return json.loads(pfad.read_text(encoding="utf-8"))
    except Exception:
        return standard


def speichere_json(name: str, daten: Any) -> None:
    pfad = _pfad(name)
    pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
