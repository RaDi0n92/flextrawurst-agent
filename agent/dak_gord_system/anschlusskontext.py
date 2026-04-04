from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


def _projektwurzel() -> Path:
    return Path(__file__).resolve().parents[2]


PROJEKTWURZEL = _projektwurzel()
SPUREN_ORDNER = PROJEKTWURZEL / "agent" / "dak_gord_system" / "spuren"
ANSCHLUSSKONTEXT_DATEI = SPUREN_ORDNER / "anschlusskontext.json"


@dataclass
class AnschlussKontext:
    zeitstempel: str
    art: str
    datei: str
    textstueck: str
    spurdatei: str | None
    offset: int
    chunk_groesse: int
    nachfrage_tiefe: int

    def als_dict(self) -> dict:
        return asdict(self)


@dataclass
class FokusKontext:
    aktiv: bool
    zeitstempel: str
    art: str
    datei: str
    textstueck: str
    spurdatei: str | None
    offset: int
    chunk_groesse: int
    nachfrage_tiefe: int

    def als_dict(self) -> dict:
        return asdict(self)


def _zeitstempel() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _leerer_anschlusskontext() -> dict:
    return {
        "zeitstempel": "",
        "art": "",
        "datei": "",
        "textstueck": "",
        "spurdatei": None,
        "offset": 0,
        "chunk_groesse": 1600,
        "nachfrage_tiefe": 0,
    }


def _leerer_fokuskontext() -> dict:
    return {
        "aktiv": False,
        "zeitstempel": "",
        "art": "",
        "datei": "",
        "textstueck": "",
        "spurdatei": None,
        "offset": 0,
        "chunk_groesse": 1600,
        "nachfrage_tiefe": 0,
    }


def _leererdatensatz() -> dict:
    return {
        "anschlusskontext": _leerer_anschlusskontext(),
        "fokuskontext": _leerer_fokuskontext(),
    }


def _lade_rohdaten() -> dict:
    SPUREN_ORDNER.mkdir(parents=True, exist_ok=True)

    if not ANSCHLUSSKONTEXT_DATEI.exists():
        return _leererdatensatz()

    try:
        daten = json.loads(ANSCHLUSSKONTEXT_DATEI.read_text(encoding="utf-8"))
    except Exception:
        return _leererdatensatz()

    if not isinstance(daten, dict):
        return _leererdatensatz()

    basis = _leererdatensatz()

    anschluss = daten.get("anschlusskontext")
    if isinstance(anschluss, dict):
        basis["anschlusskontext"].update(anschluss)

    fokus = daten.get("fokuskontext")
    if isinstance(fokus, dict):
        basis["fokuskontext"].update(fokus)

    return basis


def _speichere_rohdaten(daten: dict) -> None:
    SPUREN_ORDNER.mkdir(parents=True, exist_ok=True)
    ANSCHLUSSKONTEXT_DATEI.write_text(
        json.dumps(daten, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def merke_anschlusskontext(
    art: str,
    datei: str | Path,
    textstueck: str,
    spurdatei: str | Path | None = None,
    offset: int = 0,
    chunk_groesse: int = 1600,
    nachfrage_tiefe: int = 0,
) -> AnschlussKontext:
    rohdaten = _lade_rohdaten()

    datei_text = str(Path(datei).resolve()) if str(datei).strip() else ""
    spurdatei_text = None

    if spurdatei is not None and str(spurdatei).strip():
        spurdatei_text = str(Path(spurdatei).resolve())

    daten = {
        "zeitstempel": _zeitstempel(),
        "art": (art or "").strip(),
        "datei": datei_text,
        "textstueck": textstueck or "",
        "spurdatei": spurdatei_text,
        "offset": max(0, int(offset)),
        "chunk_groesse": max(1, int(chunk_groesse)),
        "nachfrage_tiefe": max(0, int(nachfrage_tiefe)),
    }

    rohdaten["anschlusskontext"] = daten
    _speichere_rohdaten(rohdaten)
    return AnschlussKontext(**daten)


def hole_anschlusskontext() -> AnschlussKontext | None:
    daten = _lade_rohdaten()["anschlusskontext"]

    if not daten.get("datei") and not daten.get("textstueck"):
        return None

    return AnschlussKontext(**daten)


def aktualisiere_anschlusskontext(
    textstueck: str,
    offset: int,
    nachfrage_tiefe: int,
) -> AnschlussKontext | None:
    rohdaten = _lade_rohdaten()
    daten = rohdaten["anschlusskontext"]

    if not daten.get("datei"):
        return None

    daten["zeitstempel"] = _zeitstempel()
    daten["textstueck"] = textstueck or ""
    daten["offset"] = max(0, int(offset))
    daten["nachfrage_tiefe"] = max(0, int(nachfrage_tiefe))

    rohdaten["anschlusskontext"] = daten
    _speichere_rohdaten(rohdaten)
    return AnschlussKontext(**daten)


def setze_fokus_aus_anschlusskontext() -> FokusKontext | None:
    rohdaten = _lade_rohdaten()
    daten = rohdaten["anschlusskontext"]

    if not daten.get("datei") and not daten.get("textstueck"):
        return None

    fokus = {
        "aktiv": True,
        "zeitstempel": _zeitstempel(),
        "art": daten.get("art", ""),
        "datei": daten.get("datei", ""),
        "textstueck": daten.get("textstueck", ""),
        "spurdatei": daten.get("spurdatei"),
        "offset": int(daten.get("offset", 0)),
        "chunk_groesse": int(daten.get("chunk_groesse", 1600)),
        "nachfrage_tiefe": int(daten.get("nachfrage_tiefe", 0)),
    }

    rohdaten["fokuskontext"] = fokus
    _speichere_rohdaten(rohdaten)
    return FokusKontext(**fokus)


def hole_fokuskontext() -> FokusKontext | None:
    daten = _lade_rohdaten()["fokuskontext"]

    if not daten.get("aktiv"):
        return None

    if not daten.get("datei") and not daten.get("textstueck"):
        return None

    return FokusKontext(**daten)


def aktualisiere_fokuskontext(
    textstueck: str,
    offset: int,
    nachfrage_tiefe: int,
) -> FokusKontext | None:
    rohdaten = _lade_rohdaten()
    daten = rohdaten["fokuskontext"]

    if not daten.get("aktiv"):
        return None

    daten["zeitstempel"] = _zeitstempel()
    daten["textstueck"] = textstueck or ""
    daten["offset"] = max(0, int(offset))
    daten["nachfrage_tiefe"] = max(0, int(nachfrage_tiefe))

    rohdaten["fokuskontext"] = daten
    _speichere_rohdaten(rohdaten)
    return FokusKontext(**daten)


def loesche_fokuskontext() -> None:
    rohdaten = _lade_rohdaten()
    rohdaten["fokuskontext"] = _leerer_fokuskontext()
    _speichere_rohdaten(rohdaten)


def loesche_anschlusskontext() -> None:
    rohdaten = _lade_rohdaten()
    rohdaten["anschlusskontext"] = _leerer_anschlusskontext()
    _speichere_rohdaten(rohdaten)


def formatiere_schreibblock(
    art: str,
    datei: str | Path,
    inhalt: str,
    anmerkung: str | None = None,
    frage: str | None = None,
) -> str:
    datei_text = str(Path(datei).resolve()) if str(datei).strip() else ""

    block = (
        f"[{_zeitstempel()}] dak+gord-system\n\n"
        f"ART: {(art or '').strip()}\n"
        f"DATEI: {datei_text}\n"
        f"INHALT:\n{inhalt.rstrip()}\n"
    )

    if anmerkung and anmerkung.strip():
        block += f"\nANMERKUNG:\n{anmerkung.rstrip()}\n"

    if frage and frage.strip():
        block += f"\nFRAGE:\n{frage.rstrip()}\n"

    block += "\n"
    return block
