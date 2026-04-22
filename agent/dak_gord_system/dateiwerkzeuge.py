from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


STANDARD_BASISPFAD = Path("/root/werkraum")

IGNORIERTE_ORDNERNAMEN = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}

VIRTUELLE_SYSTEMPFADE = [
    Path("/proc"),
    Path("/sys"),
    Path("/dev"),
    Path("/run"),
]

TEXT_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin-1",
]


def _pfad_aufloesen(text: str) -> Path:
    text = (text or "").strip()

    if not text:
        return STANDARD_BASISPFAD.resolve()

    pfad = Path(text)

    if pfad.is_absolute():
        return pfad.resolve()

    return (STANDARD_BASISPFAD / pfad).resolve()


def _liegt_unter(pfad: Path, wurzel: Path) -> bool:
    try:
        pfad.resolve().relative_to(wurzel.resolve())
        return True
    except Exception:
        return False


def _ist_virtueller_systempfad(pfad: Path) -> bool:
    aufgeloest = pfad.resolve()

    for systempfad in VIRTUELLE_SYSTEMPFADE:
        if _liegt_unter(aufgeloest, systempfad):
            return True

    return False


def _soll_ignoriert_werden(pfad: Path) -> bool:
    if any(name in IGNORIERTE_ORDNERNAMEN for name in pfad.parts):
        return True

    if _ist_virtueller_systempfad(pfad):
        return True

    return False


def _formatiere_zeitstempel(st_mtime: float) -> str:
    return datetime.fromtimestamp(st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _lese_textdatei_mit_fallbacks(pfad: Path, max_len: int) -> tuple[str | None, str | None]:
    for encoding in TEXT_ENCODINGS:
        try:
            with pfad.open("r", encoding=encoding) as datei:
                inhalt = datei.read(max_len + 1)
            return inhalt, encoding
        except UnicodeDecodeError:
            continue
        except Exception as fehler:
            return f"Lesefehler bei {pfad}: {fehler}", None

    return None, None


def datei_info(text: str) -> str:
    pfad = _pfad_aufloesen(text)

    if not pfad.exists():
        return f"Nicht gefunden: {pfad}"

    try:
        info = pfad.stat()
    except Exception as fehler:
        return f"Stat-Fehler bei {pfad}: {fehler}"

    art = "Ordner" if pfad.is_dir() else "Datei"

    return (
        f"PFAD: {pfad}\n"
        f"ART: {art}\n"
        f"GROESSE: {info.st_size}\n"
        f"GEAENDERT: {_formatiere_zeitstempel(info.st_mtime)}\n"
    )


def datei_lesen(text: str, max_len: int = 6000) -> str:
    pfad = _pfad_aufloesen(text)

    if not pfad.exists():
        return f"Nicht gefunden: {pfad}"

    if pfad.is_dir():
        return f"Das ist ein Ordner, keine Datei: {pfad}"

    if _ist_virtueller_systempfad(pfad):
        return f"Virtueller Systempfad wird hier nicht direkt gelesen: {pfad}"

    inhalt, encoding = _lese_textdatei_mit_fallbacks(pfad, max_len)

    if encoding is None:
        if isinstance(inhalt, str) and inhalt.startswith("Lesefehler bei "):
            return inhalt
        return f"Datei ist nicht als Text lesbar: {pfad}"

    if len(inhalt) > max_len:
        return inhalt[:max_len] + f"\n\n... ABGESCHNITTEN ...\n[ENCODING: {encoding}]"

    return inhalt + f"\n\n[ENCODING: {encoding}]"


def dateiname_suchen(muster: str, startpfad: str = ".", max_treffer: int = 100) -> str:
    muster = (muster or "").strip().lower()
    if not muster:
        return "Kein Suchmuster angegeben."

    wurzel = _pfad_aufloesen(startpfad)

    if not wurzel.exists():
        return f"Nicht gefunden: {wurzel}"

    if not wurzel.is_dir():
        return f"Das ist kein Ordner: {wurzel}"

    if _ist_virtueller_systempfad(wurzel):
        return f"Suche in virtuellem Systempfad ist hier nicht erlaubt: {wurzel}"

    treffer: list[str] = []

    for basis, ordnernamen, dateinamen in os.walk(wurzel):
        basis_pfad = Path(basis)

        ordnernamen[:] = [
            name
            for name in ordnernamen
            if not _soll_ignoriert_werden(basis_pfad / name)
        ]

        for dateiname in dateinamen:
            kandidat = basis_pfad / dateiname

            if _soll_ignoriert_werden(kandidat):
                continue

            if muster in dateiname.lower():
                treffer.append(str(kandidat))

                if len(treffer) >= max_treffer:
                    return "\n".join(treffer)

    if not treffer:
        return f"Keine Dateinamen-Treffer fuer: {muster}"

    return "\n".join(treffer)


SCHREIB_BASISPFAD = Path("/root/werkraum")

_VERBOTENE_SCHREIBPFADE = [
    Path("/root/.ssh"),
    Path("/root/.claude"),
    Path("/etc"),
    Path("/bin"),
    Path("/sbin"),
    Path("/usr"),
]


def datei_schreiben(pfad_text: str, inhalt: str) -> str:
    """Schreibt Inhalt in eine Datei innerhalb von /root/werkraum/.
    Erstellt fehlende Verzeichnisse automatisch.
    Gibt Erfolgsmeldung oder Fehlerbeschreibung zurück.
    """
    pfad = _pfad_aufloesen(pfad_text)

    # Sicherheit: nur innerhalb werkraum
    if not _liegt_unter(pfad, SCHREIB_BASISPFAD):
        return f"Schreiben verweigert: Pfad liegt außerhalb von {SCHREIB_BASISPFAD}: {pfad}"

    # Sicherheit: keine kritischen Systempfade
    for verboten in _VERBOTENE_SCHREIBPFADE:
        if _liegt_unter(pfad, verboten):
            return f"Schreiben verweigert: Schutzpfad {verboten}: {pfad}"

    if _ist_virtueller_systempfad(pfad):
        return f"Schreiben verweigert: virtueller Systempfad: {pfad}"

    try:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(inhalt, encoding="utf-8")
        return f"Geschrieben: {pfad} ({len(inhalt)} Zeichen)"
    except Exception as fehler:
        return f"Schreibfehler bei {pfad}: {fehler}"


def verzeichnis_erstellen(pfad_text: str) -> str:
    """Erstellt ein Verzeichnis (und alle Elternordner) innerhalb von /root/werkraum/."""
    pfad = _pfad_aufloesen(pfad_text)

    if not _liegt_unter(pfad, SCHREIB_BASISPFAD):
        return f"Erstellen verweigert: Pfad liegt außerhalb von {SCHREIB_BASISPFAD}: {pfad}"

    try:
        pfad.mkdir(parents=True, exist_ok=True)
        return f"Verzeichnis erstellt: {pfad}"
    except Exception as fehler:
        return f"Fehler beim Erstellen von {pfad}: {fehler}"


def baum(text: str = ".", max_tiefe: int = 3, max_eintraege: int = 200) -> str:
    wurzel = _pfad_aufloesen(text)

    if not wurzel.exists():
        return f"Nicht gefunden: {wurzel}"

    if not wurzel.is_dir():
        return f"Das ist kein Ordner: {wurzel}"

    if _ist_virtueller_systempfad(wurzel):
        return f"Baum fuer virtuellen Systempfad ist hier nicht erlaubt: {wurzel}"

    zeilen: list[str] = []
    anzahl = 0

    for basis, ordnernamen, dateinamen in os.walk(wurzel):
        basis_pfad = Path(basis)

        relative_basis = basis_pfad.relative_to(wurzel)
        tiefe = 0 if str(relative_basis) == "." else len(relative_basis.parts)

        ordnernamen[:] = [
            name
            for name in ordnernamen
            if not _soll_ignoriert_werden(basis_pfad / name)
        ]

        if tiefe > max_tiefe:
            ordnernamen[:] = []
            continue

        if basis_pfad != wurzel:
            zeilen.append(str(basis_pfad))
            anzahl += 1
            if anzahl >= max_eintraege:
                zeilen.append("... ABGESCHNITTEN ...")
                return "\n".join(zeilen)

        if tiefe == max_tiefe:
            ordnernamen[:] = []

        for dateiname in sorted(dateinamen):
            kandidat = basis_pfad / dateiname

            if _soll_ignoriert_werden(kandidat):
                continue

            zeilen.append(str(kandidat))
            anzahl += 1

            if anzahl >= max_eintraege:
                zeilen.append("... ABGESCHNITTEN ...")
                return "\n".join(zeilen)

    if not zeilen:
        return "(leer)"

    return "\n".join(zeilen)
