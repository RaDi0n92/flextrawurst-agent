#!/usr/bin/env python3
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

GENI_ROOT = Path("/root/werkraum/geni")
KNOTEN_DIR = GENI_ROOT / "gedaechtnis" / "knoten"
KANTEN_DIR = GENI_ROOT / "gedaechtnis" / "kanten"

_id_lock = threading.Lock()
_tiefe_lock = threading.Lock()


def naechste_id(verzeichnis: Path) -> str:
    zahlen = []
    for f in verzeichnis.glob("*.json"):
        if f.stem == "schema":
            continue
        try:
            zahlen.append(int(f.stem))
        except ValueError:
            pass
    return str((max(zahlen) + 1) if zahlen else 1).zfill(4)


def knoten_schreiben(typ: str, inhalt: str, quelle: str, tags: list = None, zugriffsschicht: int = 0) -> str:
    with _id_lock:
        kid = naechste_id(KNOTEN_DIR)
        k = {
            "id": kid,
            "typ": typ,
            "inhalt": inhalt,
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "quelle": quelle,
            "zugriffsschicht": zugriffsschicht,
            "verbindungen": [],
            "gewicht": 1.0,
            "tiefe": 0,
            "verblasst": False,
            "tags": tags or [],
        }
        (KNOTEN_DIR / f"{kid}.json").write_text(json.dumps(k, ensure_ascii=False, indent=2))
        return kid


def kante_schreiben(von: str, nach: str, typ: str, staerke: float = 1.0):
    with _id_lock:
        kid = naechste_id(KANTEN_DIR)
        k = {
            "id": kid,
            "von": von,
            "nach": nach,
            "typ": typ,
            "stärke": staerke,
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "richtung": "gerichtet",
        }
        (KANTEN_DIR / f"{kid}.json").write_text(json.dumps(k, ensure_ascii=False, indent=2))


def tiefe_erhoehen(knoten_id: str):
    pfad = KNOTEN_DIR / f"{knoten_id}.json"
    if not pfad.exists():
        return
    with _tiefe_lock:
        try:
            k = json.loads(pfad.read_text())
            neu = min(3, k.get("tiefe", 0) + 1)
            if neu != k.get("tiefe", 0):
                k["tiefe"] = neu
                pfad.write_text(json.dumps(k, ensure_ascii=False, indent=2))
        except Exception:
            pass
