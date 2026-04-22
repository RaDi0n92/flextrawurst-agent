from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import unicodedata


def _projektwurzel() -> Path:
    return Path(__file__).resolve().parents[2]


SPUREN_ORDNER = _projektwurzel() / "agent" / "dak_gord_system" / "spuren"
STANDARD_DATEI = SPUREN_ORDNER / "trigger_spuren.md"


DAK_BEZUGS_MUSTER = [
    "das was du gerade gesagt hast",
    "das was du gesagt hast",
    "deine aussage",
    "dein letzter satz",
    "deine letzte antwort",
    "was du gerade gesagt hast",
]


def _zeitstempel() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _normalisiere_dateiname(text: str) -> str:
    text = (text or "").strip()
    if not text:
        text = "spur"

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")

    if not text:
        text = "spur"

    if not text.endswith(".md"):
        text += ".md"

    return text


def _auto_dateiname_aus_inhalt(inhalt: str) -> str:
    erste_sinnvolle_zeile = ""

    for zeile in inhalt.splitlines():
        kandidat = zeile.strip()
        if kandidat:
            erste_sinnvolle_zeile = kandidat
            break

    if not erste_sinnvolle_zeile:
        erste_sinnvolle_zeile = "spur"

    erste_sinnvolle_zeile = erste_sinnvolle_zeile[:60]
    zeit = datetime.now().strftime("%Y%m%d_%H%M%S")

    return _normalisiere_dateiname(f"{erste_sinnvolle_zeile}_{zeit}")


def _notizblock(quelle: str, original: str) -> str:
    return (
        f"[{_zeitstempel()}] dak+gord-system\n\n"
        f"QUELLE: {quelle}\n"
        f"ORIGINAL:\n"
        f"{original}\n\n"
    )


def _anhaengen(datei: Path, block: str) -> None:
    datei.parent.mkdir(parents=True, exist_ok=True)

    if datei.exists():
        alt = datei.read_text(encoding="utf-8")
    else:
        alt = ""

    datei.write_text(alt + block, encoding="utf-8")


def _namenskonflikt_auflosen(datei: Path) -> Path:
    if not datei.exists():
        return datei

    stemm = datei.stem
    endung = datei.suffix or ".md"
    ordner = datei.parent
    zaehler = 2

    while True:
        kandidat = ordner / f"{stemm}_{zaehler}{endung}"
        if not kandidat.exists():
            return kandidat
        zaehler += 1


def _enthaelt_wichtig(text: str) -> bool:
    t = text.lower()
    return "wichtig" in t or "wuchtig" in t


def _enthaelt_merk_dir_das(text: str) -> bool:
    return "merk dir das" in text.lower()


def _enthaelt_dak_bezug(text: str) -> bool:
    t = text.lower()
    return any(muster in t for muster in DAK_BEZUGS_MUSTER)


def _pfad_direkt_angefordert(text: str) -> tuple[bool, str | None]:
    """Erkennt 'speichere das als datei in /pfad' und Varianten."""
    t = text.strip()

    m = re.search(
        r"speicher[e]?\s+das\s+(?:als\s+datei\s+)?in\s+(/[^\s]+)",
        t,
        flags=re.IGNORECASE,
    )
    if m:
        return True, m.group(1).strip()

    return False, None


def _neue_datei_angefordert(text: str) -> tuple[bool, str | None]:
    t = text.strip()

    m = re.search(
        r"speicher das in einer neuen datei namens\s+([^\n]+)",
        t,
        flags=re.IGNORECASE,
    )
    if m:
        return True, m.group(1).strip()

    if re.search(r"speicher das in einer neuen datei", t, flags=re.IGNORECASE):
        return True, None

    return False, None


def _triggerzeile_ist(zeile: str) -> bool:
    z = zeile.strip().lower()

    if not z:
        return False

    if "speicher das in einer neuen datei namens " in z:
        return True

    if z == "speicher das in einer neuen datei":
        return True

    if z == "merk dir das":
        return True

    return False


def _block_vor_trigger(nutzer_text: str) -> str | None:
    zeilen = nutzer_text.splitlines(keepends=True)

    for index in range(len(zeilen) - 1, -1, -1):
        if _triggerzeile_ist(zeilen[index]):
            davor = "".join(zeilen[:index])

            if davor.strip():
                return davor.rstrip("\n")

            return None

    return None


def _zieltext_und_quelle(
    nutzer_text: str,
    letzte_antwort_von_dak: str,
    letzte_relevante_aussage_von_daniel: str,
) -> tuple[str, str]:
    block = _block_vor_trigger(nutzer_text)
    if block is not None:
        return block, "daniel"

    if _enthaelt_dak_bezug(nutzer_text) and letzte_antwort_von_dak.strip():
        return letzte_antwort_von_dak, "dak+gord-system"

    if letzte_relevante_aussage_von_daniel.strip():
        return letzte_relevante_aussage_von_daniel, "daniel"

    if letzte_antwort_von_dak.strip():
        return letzte_antwort_von_dak, "dak+gord-system"

    return "", "daniel"


def verarbeite_speichertrigger(
    nutzer_text: str,
    letzte_antwort_von_dak: str,
    letzte_relevante_aussage_von_daniel: str,
) -> list[str]:
    nutzer_text = nutzer_text or ""
    letzte_antwort_von_dak = letzte_antwort_von_dak or ""
    letzte_relevante_aussage_von_daniel = letzte_relevante_aussage_von_daniel or ""

    pfad_direkt, zielpfad_roh = _pfad_direkt_angefordert(nutzer_text)
    if pfad_direkt and zielpfad_roh:
        inhalt = letzte_antwort_von_dak.strip()
        if not inhalt:
            inhalt = letzte_relevante_aussage_von_daniel.strip()
        if inhalt:
            ziel = Path(zielpfad_roh)
            if ziel.is_dir():
                ziel = _namenskonflikt_auflosen(ziel / _auto_dateiname_aus_inhalt(inhalt))
            else:
                ziel.parent.mkdir(parents=True, exist_ok=True)
                ziel = _namenskonflikt_auflosen(ziel)
                if not ziel.suffix:
                    ziel = ziel.with_suffix(".md")
            ziel.parent.mkdir(parents=True, exist_ok=True)
            ziel.write_text(inhalt, encoding="utf-8")
            return [str(ziel)]
        return []

    neue_datei, dateiname = _neue_datei_angefordert(nutzer_text)

    if neue_datei:
        original, quelle = _zieltext_und_quelle(
            nutzer_text=nutzer_text,
            letzte_antwort_von_dak=letzte_antwort_von_dak,
            letzte_relevante_aussage_von_daniel=letzte_relevante_aussage_von_daniel,
        )

        if not original.strip():
            return []

        block = _notizblock(quelle, original)

        if dateiname:
            ziel = SPUREN_ORDNER / _normalisiere_dateiname(dateiname)
        else:
            ziel = SPUREN_ORDNER / _auto_dateiname_aus_inhalt(original)

        ziel = _namenskonflikt_auflosen(ziel)
        _anhaengen(ziel, block)
        return [str(ziel)]

    if _enthaelt_merk_dir_das(nutzer_text):
        original, quelle = _zieltext_und_quelle(
            nutzer_text=nutzer_text,
            letzte_antwort_von_dak=letzte_antwort_von_dak,
            letzte_relevante_aussage_von_daniel=letzte_relevante_aussage_von_daniel,
        )

        if not original.strip():
            return []

        block = _notizblock(quelle, original)
        _anhaengen(STANDARD_DATEI, block)
        return [str(STANDARD_DATEI)]

    if _enthaelt_wichtig(nutzer_text):
        block = _notizblock("daniel", nutzer_text)
        _anhaengen(STANDARD_DATEI, block)
        return [str(STANDARD_DATEI)]

    return []
