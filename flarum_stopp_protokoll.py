#!/usr/bin/env python3
"""
flarum_stopp_protokoll.py — deterministisches Protokoll für die Zeit der
Flarum-Post-Sperre (docs/2026-07-09_flarum_stopp_bericht.md, Baustein 4).

Menschensprachlich (wer/was/wann/wie lange), append-only, ohne eigenen
LLM-Call fürs Loggen selbst — das Schreiben eines Eintrags ist reiner
deterministischer Code. Die LLM-Entscheidungen, die protokolliert werden
(z.B. was ein Wesen im umgedrehten Neugier-Dienst gelesen/entschieden hat),
passieren woanders; hier wird nur festgehalten, dass und was passiert ist.

Zwei Ablagen pro Eintrag:
- global: alle Ereignisse zusammen, für flarumstyler/Admin-Übersicht
- pro Wesen: nur die eigenen Ereignisse, damit ein Wesen seine eigene
  Geschichte in dieser Zeit nachlesen kann — Provenienz auch für sich selbst
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

GLOBAL_PROTOKOLL = Path("/root/werkraum/flarum_stopp_protokoll_global.jsonl")
CODEWESEN_BASIS = Path("/root/werkraum/codewesen")

TYPEN = (
    "sperre_aktiviert",
    "sperre_aufgehoben",
    "container_verschoben",
    "container_kopiert",
    "neugier_session_start",
    "neugier_entscheidung",
    "neugier_session_ende",
)


def _wesen_datei(wesen: str) -> Path:
    return CODEWESEN_BASIS / wesen / "flarum_stopp_protokoll.jsonl"


def schreibe(typ: str, text: str, wesen: Optional[str] = None,
             dauer_sekunden: Optional[float] = None, meta: Optional[dict] = None) -> dict:
    """Schreibt einen Protokolleintrag. wesen=None für globale/admin-Ereignisse
    (z.B. Sperre aktivieren/aufheben), sonst für wesen-bezogene Ereignisse."""
    eintrag = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "typ": typ,
        "wesen": wesen,
        "text": text,
        "dauer_sekunden": dauer_sekunden,
        "meta": meta or {},
    }
    zeile = json.dumps(eintrag, ensure_ascii=False) + "\n"

    GLOBAL_PROTOKOLL.parent.mkdir(parents=True, exist_ok=True)
    with GLOBAL_PROTOKOLL.open("a", encoding="utf-8") as f:
        f.write(zeile)

    if wesen:
        wesen_datei = _wesen_datei(wesen)
        wesen_datei.parent.mkdir(parents=True, exist_ok=True)
        with wesen_datei.open("a", encoding="utf-8") as f:
            f.write(zeile)

    return eintrag


def lies(wesen: Optional[str] = None, limit: int = 200) -> list[dict]:
    """Liest die letzten `limit` Einträge — global oder für ein bestimmtes Wesen."""
    datei = _wesen_datei(wesen) if wesen else GLOBAL_PROTOKOLL
    if not datei.exists():
        return []
    zeilen = [z for z in datei.read_text(encoding="utf-8").splitlines() if z.strip()]
    ergebnis = []
    for z in zeilen[-limit:]:
        try:
            ergebnis.append(json.loads(z))
        except Exception:
            continue
    return ergebnis
