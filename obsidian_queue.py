from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

QUEUE_DATEI = Path("/root/werkraum/obsidian_notizen_queue.json")
_lock = threading.Lock()


def _lese() -> list[dict]:
    if not QUEUE_DATEI.exists():
        return []
    try:
        return json.loads(QUEUE_DATEI.read_text(encoding="utf-8"))
    except Exception:
        return []


def _schreibe(eintraege: list[dict]) -> None:
    QUEUE_DATEI.write_text(
        json.dumps(eintraege, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def notiz_einreihen(wesen: str, titel: str, inhalt: str) -> str:
    """Wesen ruft das auf um eine Notiz für Obsidian einzureihen."""
    notiz_id = str(uuid.uuid4())[:8]
    eintrag = {
        "id": notiz_id,
        "wesen": wesen,
        "titel": titel,
        "inhalt": inhalt,
        "zeit": datetime.now().isoformat(),
    }
    with _lock:
        eintraege = _lese()
        eintraege.append(eintrag)
        _schreibe(eintraege)
    return notiz_id


def notiz_verbrauchen(notiz_id: str) -> bool:
    """Obsidian ruft das auf nachdem eine Notiz verarbeitet wurde."""
    with _lock:
        eintraege = _lese()
        neu = [e for e in eintraege if e["id"] != notiz_id]
        if len(neu) == len(eintraege):
            return False
        _schreibe(neu)
        return True


def alle_notizen() -> list[dict]:
    with _lock:
        return _lese()
