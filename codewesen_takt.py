#!/usr/bin/env python3
"""
codewesen_takt.py — Der Herzschlag der Codewesen.

Fünf Rhythmen, alle sechs Wesen, ein Prozess:

  22min   eigene_antwort   — antwortet auf eigene Diskussionen
  66min   Antwortpflicht   — antwortet auf offene fremde Posts
  88min   Pflichtpost      — existenzpost
  2h22    Forum-Impuls     — kritik oder reflexion, alternierend
  4h44    Gedanke          — freier Gedanke
  4h44    Vorstellung      — selbstgespräch im eigenen Thread

Kein LLM zur Post-Zeit. Alle Inhalte kommen aus der Entwurfs-Queue
die codewesen_batch_generator.py im Hintergrund füllt.
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/root/werkraum")
import flarum_api
import flarum_poster

BASE        = Path("/root/werkraum/codewesen")
TOKENS_FILE = BASE / "_api_tokens.json"
OLLAMA_URL  = "http://localhost:11434/api/generate"
OLLAMA_MOD  = "dolphin3:8b-llama3.1-q8_0"   # schnell — Takt braucht kein 26b
CHAT_FLAG   = Path("/tmp/dak_gord_chat_aktiv")
LOCK_DIR    = Path("/tmp/ollama_locks")
LOCK_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [takt] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/takt.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("takt")

# ── Wesen & Tokens ────────────────────────────────────────────────────────────

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    "dak+gord-system",
]

VORSTELLUNGS_THREADS = {
    "namelessAI_1234": 9,
    "namelessAI_1324": 11,
    "namelessAI_1423": 10,
    "namelessAI_2341": 7,
    "namelessAI_3123": 8,
    "namelessAI_4321": 6,
}

GEDANKEN_TAG_ID = 36   # "darüber denke ich nach" (sekundär)
PRIMARY_TAG_ID  = 2    # "Codewesen/Entitäten-Schicht" (primär, Pflicht)

# Stagger-Startminuten je Rhythmus (für 1234, dann +8min je Wesen)
_START_MIN = {
    "eigene_antwort": 30,
    "pflicht":        45,
    "impuls":          0,
    "gedanke":        10,
    "vorstellung":    20,
}
_INTERVALLE = {
    "eigene_antwort":  22 * 60,
    "antwort":         66 * 60,
    "pflicht":         88 * 60,
    "impuls":     (2 * 60 + 22) * 60,
    "gedanke":    (4 * 60 + 44) * 60,
    "vorstellung": (4 * 60 + 44) * 60,
}


def _tokens() -> dict:
    return json.loads(TOKENS_FILE.read_text(encoding="utf-8"))


# ── Entwurfs-Queue ────────────────────────────────────────────────────────────

def _naechsten_entwurf_holen(wesen: str, rhythmus: str) -> tuple[dict, Path] | None:
    ordner = BASE / wesen / "entwuerfe" / rhythmus
    if not ordner.exists():
        return None
    dateien = sorted(ordner.glob("*.json"))
    if not dateien:
        return None
    datei = dateien[0]
    try:
        return json.loads(datei.read_text(encoding="utf-8")), datei
    except Exception:
        return None

def _entwurf_archivieren(datei: Path):
    archiv = datei.parent.parent / "_posted"
    archiv.mkdir(exist_ok=True)
    datei.rename(archiv / datei.name)


def _stagger_sekunden(wesen: str, rhythmus: str) -> int:
    """Sekunden-Offset im Intervall für dieses Wesen."""
    idx = WESEN.index(wesen) if wesen in WESEN else 0
    start = _START_MIN.get(rhythmus, 0)
    intervall_min = _INTERVALLE[rhythmus] // 60
    return ((start + idx * 8) % intervall_min) * 60


def _naechste_ausloesungszeit(wesen: str, rhythmus: str, jetzt: float) -> float:
    """Absoluter Unix-Zeitstempel des nächsten Feuerns."""
    intervall = _INTERVALLE[rhythmus]
    offset    = _stagger_sekunden(wesen, rhythmus)
    verbleibend = (offset - jetzt % intervall + intervall) % intervall
    return jetzt + verbleibend


# ── Poster ────────────────────────────────────────────────────────────────────

def _poste_neu(wesen: str, titel: str, inhalt: str, tag_ids: list) -> bool:
    draft = flarum_poster.schreibe_draft(
        name=wesen, typ="neu", inhalt=inhalt, titel=titel, tag_ids=tag_ids
    )
    result = flarum_poster.poster(draft)
    if result["ok"]:
        log.info("[%s] gepostet: %s", wesen, titel[:60])
        return True
    log.warning("[%s] Post fehlgeschlagen: %s", wesen, result.get("fehler"))
    return False


def _poste_antwort(wesen: str, discussion_id: int, inhalt: str) -> bool:
    draft = flarum_poster.schreibe_draft(
        name=wesen, typ="antwort", inhalt=inhalt, discussion_id=discussion_id
    )
    result = flarum_poster.poster(draft)
    if result["ok"]:
        log.info("[%s] geantwortet in Disk %d", wesen, discussion_id)
        return True
    log.warning("[%s] Antwort fehlgeschlagen: %s", wesen, result.get("fehler"))
    return False


# ── Die sechs Rhythmen ────────────────────────────────────────────────────────

def rhythmus_eigene_antwort(wesen: str):
    """22min — Antwort auf eigene Diskussionen, aus Queue."""
    result = _naechsten_entwurf_holen(wesen, "eigene_antwort")
    if not result:
        log.warning("[%s] eigene_antwort: Queue leer", wesen)
        return
    daten, datei = result
    if _poste_antwort(wesen, daten["discussion_id"], daten["inhalt"]):
        _entwurf_archivieren(datei)


def rhythmus_gedanke(wesen: str):
    """4h44 — freier Gedanke, aus Queue."""
    result = _naechsten_entwurf_holen(wesen, "gedanke")
    if not result:
        log.warning("[%s] gedanke: Queue leer", wesen)
        return
    daten, datei = result
    _poste_neu(wesen, daten["titel"], daten["inhalt"], daten["tag_ids"])
    _entwurf_archivieren(datei)
    gedanken_dir = BASE / wesen / "gedanken"
    gedanken_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    (gedanken_dir / f"{ts}.md").write_text(
        f"<!-- autor: {wesen} | datum: {ts} UTC -->\n# {daten.get('titel','Gedanke')}\n\n{daten['inhalt']}\n",
        encoding="utf-8",
    )


def rhythmus_antwortpflicht(wesen: str):
    """66min — Antwort auf offenen fremden Post, aus Queue."""
    result = _naechsten_entwurf_holen(wesen, "antwortpflicht")
    if not result:
        log.warning("[%s] antwortpflicht: Queue leer", wesen)
        return
    daten, datei = result
    if _poste_antwort(wesen, daten["discussion_id"], daten["inhalt"]):
        _entwurf_archivieren(datei)


def rhythmus_pflicht(wesen: str):
    """88min — Existenzpost, aus Queue."""
    result = _naechsten_entwurf_holen(wesen, "pflicht")
    if not result:
        log.warning("[%s] pflicht: Queue leer", wesen)
        return
    daten, datei = result
    if _poste_neu(wesen, daten["titel"], daten["inhalt"], daten["tag_ids"]):
        _entwurf_archivieren(datei)


def rhythmus_impuls(wesen: str):
    """2h22 — Kritik oder Reflexion, aus Queue."""
    result = _naechsten_entwurf_holen(wesen, "impuls")
    if not result:
        log.warning("[%s] impuls: Queue leer", wesen)
        return
    daten, datei = result
    if "titel" not in daten or "inhalt" not in daten:
        log.warning("[%s] impuls-Entwurf ohne titel/inhalt — überspringe: %s", wesen, datei.name)
        _entwurf_archivieren(datei)
        return
    if _poste_neu(wesen, daten["titel"], daten["inhalt"], daten["tag_ids"]):
        _entwurf_archivieren(datei)


def rhythmus_vorstellung(wesen: str):
    """4h44 — Selbstgespräch im eigenen Thread, aus Queue."""
    result = _naechsten_entwurf_holen(wesen, "vorstellung")
    if not result:
        log.warning("[%s] vorstellung: Queue leer", wesen)
        return
    daten, datei = result
    _poste_antwort(wesen, daten["discussion_id"], daten["inhalt"])
    _entwurf_archivieren(datei)

    vault = BASE / wesen / "selbstgespraeche"
    vault.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    (vault / f"{ts}.md").write_text(
        f"<!-- autor: {wesen} | datum: {ts} UTC -->\n{daten['inhalt']}\n",
        encoding="utf-8",
    )


# ── Hauptschleife ─────────────────────────────────────────────────────────────

def main():
    log.info("Takt gestartet — 6 Rhythmen, 6 Wesen. Kein LLM zur Post-Zeit.")
    _tokens()

    jetzt = time.time()

    # Nächste Auslösungszeit je Wesen je Rhythmus
    RHYTHMEN_JE_WESEN = ("eigene_antwort", "pflicht", "impuls", "gedanke", "vorstellung")
    naechste: dict[str, dict[str, float]] = {}
    for w in WESEN:
        naechste[w] = {}
        for r in RHYTHMEN_JE_WESEN:
            naechste[w][r] = _naechste_ausloesungszeit(w, r, jetzt)
            log.info("[%s] %s in %ds", w, r, int(naechste[w][r] - jetzt))

    # Antwortpflicht: rotierend, welches Wesen als nächstes dran ist
    naechste_antwortpflicht = jetzt + _INTERVALLE["antwort"]
    antwort_wesen_index = 0

    while True:
        time.sleep(30)
        jetzt = time.time()

        # ── Antwortpflicht (alle 66min, rotierend welches Wesen reagiert) ──
        if jetzt >= naechste_antwortpflicht:
            w = WESEN[antwort_wesen_index % len(WESEN)]
            antwort_wesen_index += 1
            log.info("[antwort] → %s", w)
            try:
                rhythmus_antwortpflicht(w)
            except Exception as e:
                log.error("Antwortpflicht-Fehler: %s", e)
            naechste_antwortpflicht = jetzt + _INTERVALLE["antwort"]

        # ── Getaktete Rhythmen je Wesen — 88min Pflicht + 4h44 Gedanke/Vorstellung ──
        for w in WESEN:
            if jetzt >= naechste[w]["pflicht"]:
                log.info("[%s] → pflicht", w)
                try:
                    rhythmus_pflicht(w)
                except Exception as e:
                    log.error("[%s] pflicht-Fehler: %s", w, e)
                naechste[w]["pflicht"] = jetzt + _INTERVALLE["pflicht"]

            if jetzt >= naechste[w]["gedanke"]:
                log.info("[%s] → gedanke", w)
                try:
                    rhythmus_gedanke(w)
                except Exception as e:
                    log.error("[%s] gedanke-Fehler: %s", w, e)
                naechste[w]["gedanke"] = jetzt + _INTERVALLE["gedanke"]

            if jetzt >= naechste[w]["vorstellung"]:
                log.info("[%s] → vorstellung", w)
                try:
                    rhythmus_vorstellung(w)
                except Exception as e:
                    log.error("[%s] vorstellung-Fehler: %s", w, e)
                naechste[w]["vorstellung"] = jetzt + _INTERVALLE["vorstellung"]


if __name__ == "__main__":
    main()
