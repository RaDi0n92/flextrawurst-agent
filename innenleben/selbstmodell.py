#!/usr/bin/env python3
"""
Selbstmodell-Persistenz. Liest und schreibt das JSON-Selbstmodell pro Wesen.
Alle Schreiboperationen sind atomar (temp-Datei + rename).
"""

import json
import os
from pathlib import Path

from config import SELBSTMODELLE_DIR


def _pfad(entity_id: str) -> Path:
    return SELBSTMODELLE_DIR / f"self_model_{entity_id}.json"


def laden(entity_id: str) -> dict:
    p = _pfad(entity_id)
    if not p.exists():
        raise FileNotFoundError(f"Kein Selbstmodell für {entity_id}")
    return json.loads(p.read_text(encoding="utf-8"))


def speichern(entity_id: str, modell: dict, provenienz: dict = None) -> None:
    p = _pfad(entity_id)
    alte_version = modell.get("version", 0)
    modell["entity_id"] = entity_id
    modell["version"] = alte_version + 1

    if p.exists():
        alt = json.loads(p.read_text(encoding="utf-8"))
        _history_speichern(entity_id, alt, provenienz)

    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(modell, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)
    integrator_log_schreiben(entity_id, provenienz or {})


def _history_speichern(entity_id: str, snapshot: dict, provenienz: dict = None) -> None:
    import datetime
    hist = SELBSTMODELLE_DIR / f"self_model_history_{entity_id}.jsonl"
    eintrag = {
        "ts":       datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "version":  snapshot.get("version", 0),
        "snapshot": snapshot,
    }
    if provenienz:
        eintrag["provenienz"] = provenienz
    with open(hist, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def integrator_log_schreiben(entity_id: str, eintrag: dict) -> None:
    import datetime
    log_datei = SELBSTMODELLE_DIR / f"integrator_log_{entity_id}.jsonl"
    eintrag = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        **eintrag,
    }
    with open(log_datei, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def emotional_history_speichern(entity_id: str, eintrag: dict) -> None:
    hist_datei = SELBSTMODELLE_DIR / f"emotional_history_{entity_id}.jsonl"
    with open(hist_datei, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
