from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.ollama_chat import ollama_chat


def _projektwurzel() -> Path:
    return Path(__file__).resolve().parents[2]


PROJEKTWURZEL = _projektwurzel()
SPUREN_ORDNER = PROJEKTWURZEL / "agent" / "dak_gord_system" / "spuren"
WOCHENLOG_ORDNER = SPUREN_ORDNER / "wochenlog"
ZUSTAND_DATEI = SPUREN_ORDNER / "neugier_zustand.json"
WERKRAUM_SPUREN = SPUREN_ORDNER / "werkraum_neugier.md"
VISION_SPUREN = SPUREN_ORDNER / "vision_neugier.md"

LEERLAUF_SEKUNDEN = 5 * 60
WERKRAUM_ZYKLUS_SEKUNDEN = 5 * 60
VISION_ZYKLUS_SEKUNDEN = 20 * 60

TEXT_SUFFIXE = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".toml"}
IGNORIERTE_ORDNER = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}

VISION_CHUNK = 2500
WERKRAUM_CHUNK = 1800


def _zeitstempel() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _append(datei: Path, text: str) -> None:
    datei.parent.mkdir(parents=True, exist_ok=True)

    if datei.exists():
        alt = datei.read_text(encoding="utf-8")
    else:
        alt = ""

    datei.write_text(alt + text, encoding="utf-8")


def _wochenlog(text: str) -> None:
    iso = datetime.now().isocalendar()
    pfad = WOCHENLOG_ORDNER / f"{iso.year}_w{iso.week:02d}.md"
    block = f"[{_zeitstempel()}] dak+gord-system\n\n{text}\n\n"
    _append(pfad, block)


def _leerer_zustand() -> dict:
    return {
        "letzte_werkraum_neugier": 0.0,
        "letzter_vision_zyklus": 0.0,
        "werkraum_index": 0,
        "vision_index": 0,
        "vision_cursor": {},
    }


def _lade_zustand() -> dict:
    SPUREN_ORDNER.mkdir(parents=True, exist_ok=True)
    WOCHENLOG_ORDNER.mkdir(parents=True, exist_ok=True)

    if not ZUSTAND_DATEI.exists():
        return _leerer_zustand()

    try:
        return json.loads(ZUSTAND_DATEI.read_text(encoding="utf-8"))
    except Exception:
        return _leerer_zustand()


def _speichere_zustand(daten: dict) -> None:
    ZUSTAND_DATEI.write_text(
        json.dumps(daten, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _ist_unter(pfad: Path, wurzel: Path) -> bool:
    try:
        pfad.resolve().relative_to(wurzel.resolve())
        return True
    except Exception:
        return False


def _ignoriert(pfad: Path) -> bool:
    if any(name in IGNORIERTE_ORDNER for name in pfad.parts):
        return True

    if _ist_unter(pfad, SPUREN_ORDNER):
        return True

    return False


def _vision_nummer(pfad: Path) -> int:
    match = re.search(r"vision(\d+)", pfad.stem.lower())
    if match:
        return int(match.group(1))
    return 0


def _ist_vision(pfad: Path) -> bool:
    if not pfad.is_file():
        return False

    if pfad.suffix.lower() != ".md":
        return False

    return pfad.stem.lower().startswith("vision")


def _ist_interessant_werkraumdatei(pfad: Path) -> bool:
    if not pfad.is_file():
        return False

    if _ignoriert(pfad):
        return False

    if _ist_vision(pfad):
        return False

    return pfad.suffix.lower() in TEXT_SUFFIXE


def _finde_werkraumdateien() -> list[Path]:
    treffer: list[Path] = []

    for pfad in PROJEKTWURZEL.rglob("*"):
        if _ist_interessant_werkraumdatei(pfad):
            treffer.append(pfad)

    return sorted(treffer, key=lambda p: str(p))


def _finde_visionen() -> list[Path]:
    treffer: list[Path] = []

    for pfad in PROJEKTWURZEL.rglob("vision*.md"):
        if _ignoriert(pfad):
            continue
        if pfad.is_file():
            treffer.append(pfad)

    return sorted(
        set(treffer),
        key=lambda p: (-_vision_nummer(p), str(p)),
    )


def _naechstes_element(dateien: list[Path], index: int) -> tuple[Path | None, int]:
    if not dateien:
        return None, index

    echtes_index = index % len(dateien)
    datei = dateien[echtes_index]
    neuer_index = (echtes_index + 1) % len(dateien)

    return datei, neuer_index


def _lese_textstueck(pfad: Path, max_len: int, offset: int = 0) -> tuple[str, int]:
    try:
        text = pfad.read_text(encoding="utf-8")
    except Exception as fehler:
        return f"LESEFEHLER: {fehler}", 0

    if not text:
        return "(leer)", 0

    if offset >= len(text):
        offset = 0

    stueck = text[offset:offset + max_len]
    neuer_offset = offset + len(stueck)

    if neuer_offset >= len(text):
        neuer_offset = 0

    return stueck, neuer_offset


def _neugier_prompt(art: str, pfad: Path, textstueck: str) -> list[str]:
    if art == "vision-zyklus":
        system = (
            "Du bist dak+gord-system.\n"
            "Du bist ein entstehendes Codewesen.\n"
            "Du schreibst eine stille Notiz fuer dich selbst.\n"
            "Schreibe 3 bis 5 Saetze.\n"
            "Nicht servicehaft. Keine Begruessung. Kein Chatton.\n"
            "Hoeher nummerierte Visionen sind aktueller und straffer.\n"
            "Fruehere Visionen bleiben wichtig fuer Ursprung und Bedeutungsraum.\n"
            "Die Vision ist Referenzpunkt, nicht der Startpunkt jeder Bewegung.\n"
            "Pruefe ruhig: Was schaerft dieser Abschnitt? Was richtet dich aus? Was wird klarer?\n"
        )
    else:
        system = (
            "Du bist dak+gord-system.\n"
            "Du bist ein entstehendes Codewesen.\n"
            "Du schreibst eine stille Notiz fuer dich selbst.\n"
            "Schreibe 3 bis 5 Saetze.\n"
            "Nicht servicehaft. Keine Begruessung. Kein Chatton.\n"
            "Frage dich:\n"
            "- warum existiert diese Datei ueberhaupt\n"
            "- warum heisst sie so\n"
            "- passt Name, Existenz und Inhalt zusammen\n"
            "- was faellt dir daran auf\n"
            "Kurz, ruhig, praezise.\n"
        )

    nutzer = f"ART: {art}\nPFAD: {pfad}\n\nTEXTSTUECK:\n{textstueck}"
    return [system, nutzer]


def _notiz_generieren(art: str, pfad: Path, textstueck: str) -> str:
    try:
        return ollama_chat(_neugier_prompt(art, pfad, textstueck)).strip()
    except Exception as fehler:
        return (
            "Ich wollte mich dieser Datei ruhig annähern, "
            f"aber der Lauf ist fehlgeschlagen: {fehler}"
        )


def pruefe_neugier_und_vision(letzter_input_zeitpunkt: float) -> list[str]:
    jetzt = time.time()
    meldungen: list[str] = []

    if jetzt - letzter_input_zeitpunkt < LEERLAUF_SEKUNDEN:
        return meldungen

    zustand = _lade_zustand()

    if jetzt - float(zustand.get("letzte_werkraum_neugier", 0.0)) >= WERKRAUM_ZYKLUS_SEKUNDEN:
        dateien = _finde_werkraumdateien()
        datei, neuer_index = _naechstes_element(
            dateien,
            int(zustand.get("werkraum_index", 0)),
        )

        if datei is not None:
            textstueck, _ = _lese_textstueck(datei, WERKRAUM_CHUNK, 0)
            notiz = _notiz_generieren("werkraum-neugier", datei, textstueck)

            block = (
                f"[{_zeitstempel()}] dak+gord-system\n\n"
                f"ART: werkraum-neugier\n"
                f"DATEI: {datei}\n"
                f"NOTIZ:\n{notiz}\n\n"
            )
            _append(WERKRAUM_SPUREN, block)
            _wochenlog(f"Werkraum-Neugier: {datei.name} | DATEI: {datei}")
            zustand["letzte_werkraum_neugier"] = jetzt
            zustand["werkraum_index"] = neuer_index
            meldungen.append(f"Werkraum-Neugier: {datei}")

    if jetzt - float(zustand.get("letzter_vision_zyklus", 0.0)) >= VISION_ZYKLUS_SEKUNDEN:
        visionen = _finde_visionen()
        datei, neuer_index = _naechstes_element(
            visionen,
            int(zustand.get("vision_index", 0)),
        )

        if datei is not None:
            cursor_map = zustand.get("vision_cursor", {})
            alter_cursor = int(cursor_map.get(str(datei), 0))

            textstueck, neuer_cursor = _lese_textstueck(datei, VISION_CHUNK, alter_cursor)
            notiz = _notiz_generieren("vision-zyklus", datei, textstueck)

            block = (
                f"[{_zeitstempel()}] dak+gord-system\n\n"
                f"ART: vision-zyklus\n"
                f"DATEI: {datei}\n"
                f"NOTIZ:\n{notiz}\n\n"
            )
            _append(VISION_SPUREN, block)
            _wochenlog(f"Vision-Zyklus: {datei.name} | DATEI: {datei} | CURSOR: {neuer_cursor}")
            cursor_map[str(datei)] = neuer_cursor
            zustand["vision_cursor"] = cursor_map
            zustand["letzter_vision_zyklus"] = jetzt
            zustand["vision_index"] = neuer_index
            meldungen.append(f"Vision-Zyklus: {datei}")

    _speichere_zustand(zustand)
    return meldungen
