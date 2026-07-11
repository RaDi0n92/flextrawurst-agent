#!/usr/bin/env python3
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

GENI_ROOT = Path("/root/werkraum/geni")
KNOTEN_DIR = GENI_ROOT / "gedaechtnis" / "knoten"
KANTEN_DIR = GENI_ROOT / "gedaechtnis" / "kanten"
RAUSCHEN_DIR = GENI_ROOT / "gedaechtnis" / "rauschen"

# Sharding (2026-07-11): KNOTEN_DIR hatte 18,96 Mio. Dateien flach in einem
# Verzeichnis -- ueber ext4s htree-Kapazitaetsgrenze (ohne large_dir-Feature)
# hinaus, Ursache fuer den 5h-Haenger vom 2026-07-07 und zwei ENOSPC-Abstuerze
# am 2026-07-11. Aufteilung nach den letzten 3 Ziffern der ID (id % 1000) in
# 1000 gleichmaessig befuellte Unterordner -- gilt fuer KNOTEN_DIR und
# RAUSCHEN_DIR (KANTEN_DIR hat nur ~1300 Dateien, unkritisch, bleibt flach).
_SHARDED_VERZEICHNISSE = (KNOTEN_DIR, RAUSCHEN_DIR)


def sharded_pfad(verzeichnis: Path, kid) -> Path:
    if verzeichnis in _SHARDED_VERZEICHNISSE:
        shard = f"{int(kid) % 1000:03d}"
        return verzeichnis / shard / f"{kid}.json"
    return verzeichnis / f"{kid}.json"

_id_lock = threading.Lock()
_tiefe_lock = threading.Lock()
_max_ids: dict[str, int] = {}

_COUNTER_FILE = GENI_ROOT / "gedaechtnis" / "_counter.json"


def _counter_lesen() -> dict:
    try:
        return json.loads(_COUNTER_FILE.read_text())
    except Exception:
        return {}


def _counter_schreiben(daten: dict) -> None:
    tmp = _COUNTER_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten), encoding="utf-8")
    tmp.replace(_COUNTER_FILE)


def _lade_max_id(verzeichnis: Path) -> int:
    zahlen = []
    orte = verzeichnis.glob("*/") if verzeichnis in _SHARDED_VERZEICHNISSE else [verzeichnis]
    for ort in orte:
        if not ort.is_dir():
            continue
        for f in ort.iterdir():
            if f.suffix == ".json" and f.stem != "schema":
                try:
                    zahlen.append(int(f.stem))
                except ValueError:
                    pass
    return max(zahlen) if zahlen else 0


def knoten_max_id() -> int:
    key = str(KNOTEN_DIR)
    if key in _max_ids:
        return _max_ids[key]
    with _id_lock:
        if key in _max_ids:
            return _max_ids[key]
        # Counter-Datei lesen (O(1)) — nur beim ersten Start
        cached = _counter_lesen()
        if "knoten_max_id" in cached:
            _max_ids[key] = cached["knoten_max_id"]
        else:
            # Einmaliger Scan — schreibt danach Counter-Datei
            val = _lade_max_id(KNOTEN_DIR)
            _max_ids[key] = val
            try:
                cached["knoten_max_id"] = val
                _counter_schreiben(cached)
            except Exception:
                pass
    return _max_ids[key]


def naechste_id(verzeichnis: Path, counter_key: str | None = None) -> str:
    key = str(verzeichnis)
    if verzeichnis == KNOTEN_DIR:
        counter_key = "knoten_max_id"
    if key not in _max_ids:
        if counter_key:
            # Counter-Datei lesen statt Vollscan des Verzeichnisses
            cached = _counter_lesen()
            if counter_key in cached:
                _max_ids[key] = cached[counter_key]
            else:
                _max_ids[key] = _lade_max_id(verzeichnis)
        else:
            _max_ids[key] = _lade_max_id(verzeichnis)
    _max_ids[key] += 1
    if counter_key:
        try:
            cached = _counter_lesen()
            cached[counter_key] = _max_ids[key]
            _counter_schreiben(cached)
        except Exception:
            pass
    return str(_max_ids[key]).zfill(4)


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
        pfad = sharded_pfad(KNOTEN_DIR, kid)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(json.dumps(k, ensure_ascii=False, indent=2), encoding="utf-8")
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
        (KANTEN_DIR / f"{kid}.json").write_text(json.dumps(k, ensure_ascii=False, indent=2), encoding="utf-8")


def tiefe_erhoehen(knoten_id: str):
    pfad = sharded_pfad(KNOTEN_DIR, knoten_id)
    if not pfad.exists():
        return
    with _tiefe_lock:
        try:
            k = json.loads(pfad.read_text())
            neu = min(3, k.get("tiefe", 0) + 1)
            if neu != k.get("tiefe", 0):
                k["tiefe"] = neu
                pfad.write_text(json.dumps(k, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
