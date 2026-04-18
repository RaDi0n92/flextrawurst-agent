from __future__ import annotations

from dataclasses import asdict, dataclass
import re


KANONISCHE_FAEDEN = {
    "haupt": "hauptfaden",
    "code": "codierwerkstatt",
    "zwischen": "zwischenraum",
    "entscheidung": "entscheidungen",
}

DAK_BEZUGS_MUSTER = [
    "das was du gerade gesagt hast",
    "das was du gesagt hast",
    "deine aussage",
    "dein letzter satz",
    "deine letzte antwort",
    "was du gerade gesagt hast",
]

IDENTITAETSFRAGE_MUSTER = [
    "wer bist du",
    "was bist du",
    "wie siehst du dich",
    "wie beschreibst du dich",
    "was genau bist du",
]

META_MUSTER = [
    "verfassung",
    "system",
    "agent",
    "chatbot",
    "assistent",
    "kontext",
    "faden",
    "neugier",
    "prozess",
    "phase 2",
    "phase2",
]

WIDERSPRUCHS_MUSTER = [
    " aber ",
    " sondern ",
    " doch ",
    " eigentlich ",
    " stimmt nicht",
    " falsch",
    " anders",
]


@dataclass
class Verarbeitungsergebnis:
    nutzer_text: str
    faden: str

    ist_leer: bool
    ist_fadenwechsel: bool
    fadenziel: str | None

    ist_toolbefehl: bool
    tool_name: str | None

    ist_trigger: bool
    trigger_art: str | None

    hat_block: bool
    block_inhalt: str | None

    bezieht_sich_auf_dak: bool
    ist_identitaetsfrage: bool
    ist_visionfrage: bool
    ist_meta: bool
    ist_widerspruch: bool

    soll_speichern: bool
    soll_tool_ausfuehren: bool
    soll_antworten: bool
    letzte_relevante_daniel_aussage_ersetzen: bool

    kurzbegruendung: str

    def als_dict(self) -> dict:
        return asdict(self)


def _normalisiert(text: str) -> str:
    return (text or "").strip().lower()


def _erkenne_fadenwechsel(text: str) -> tuple[bool, str | None]:
    teile = text.strip().split()
    if len(teile) >= 2 and teile[0] == "/faden":
        return True, KANONISCHE_FAEDEN.get(teile[1].lower(), "hauptfaden")
    return False, None


def _erkenne_tool(text: str) -> tuple[bool, str | None]:
    klein = _normalisiert(text)

    if klein.startswith("lesen:") or klein.startswith("lesen "):
        return True, "lesen"

    if klein.startswith("dateiname:") or klein.startswith("dateiname "):
        return True, "dateiname"

    if klein.startswith("info:") or klein.startswith("info "):
        return True, "info"

    if klein.startswith("baum:") or klein.startswith("baum "):
        return True, "baum"

    return False, None


def _erkenne_trigger_art(text: str) -> str | None:
    klein = _normalisiert(text)

    if "speicher das in einer neuen datei namens " in klein:
        return "neue_datei_mit_name"

    if "speicher das in einer neuen datei" in klein:
        return "neue_datei"

    if "merk dir das" in klein:
        return "merk_dir_das"

    if "wuchtig" in klein:
        return "wuchtig"

    if "wichtig" in klein:
        return "wichtig"

    return None


def _triggerzeile_ist(zeile: str) -> bool:
    z = _normalisiert(zeile)

    if not z:
        return False

    if "speicher das in einer neuen datei namens " in z:
        return True

    if z == "speicher das in einer neuen datei":
        return True

    if z == "merk dir das":
        return True

    return False


def _block_vor_trigger(text: str) -> str | None:
    zeilen = text.splitlines(keepends=True)

    for index in range(len(zeilen) - 1, -1, -1):
        if _triggerzeile_ist(zeilen[index]):
            davor = "".join(zeilen[:index])
            if davor.strip():
                return davor.rstrip("\n")
            return None

    return None


def _enthaelt_dak_bezug(text: str) -> bool:
    klein = _normalisiert(text)
    return any(muster in klein for muster in DAK_BEZUGS_MUSTER)


def _ist_identitaetsfrage(text: str) -> bool:
    klein = _normalisiert(text)
    return any(muster in klein for muster in IDENTITAETSFRAGE_MUSTER)


def _ist_visionfrage(text: str) -> bool:
    klein = _normalisiert(text)
    return "vision" in klein or "primaerquelle" in klein or "primärquelle" in klein


def _ist_meta(text: str) -> bool:
    klein = f" {_normalisiert(text)} "
    return any(muster in klein for muster in META_MUSTER)


def _ist_widerspruch(text: str) -> bool:
    klein = f" {_normalisiert(text)} "
    return any(muster in klein for muster in WIDERSPRUCHS_MUSTER) or "nicht " in klein


def _ist_reiner_triggertext(text: str) -> bool:
    t = _normalisiert(text)

    if not t:
        return False

    reine_trigger = {
        "wichtig",
        "wuchtig",
        "merk dir das",
        "speicher das in einer neuen datei",
    }

    if t in reine_trigger:
        return True

    if t.startswith("speicher das in einer neuen datei namens "):
        return True

    if t.startswith("das was du gerade gesagt hast") and "merk dir das" in t:
        return True

    if t.startswith("deine letzte antwort") and "merk dir das" in t:
        return True

    if t.startswith("dein letzter satz") and "merk dir das" in t:
        return True

    return False


def verarbeite_eingabe(nutzer_text: str, faden: str) -> Verarbeitungsergebnis:
    text = nutzer_text or ""
    ist_leer = not text.strip()

    ist_fadenwechsel, fadenziel = _erkenne_fadenwechsel(text)
    ist_toolbefehl, tool_name = _erkenne_tool(text)

    trigger_art = _erkenne_trigger_art(text)
    ist_trigger = trigger_art is not None

    block_inhalt = _block_vor_trigger(text)
    hat_block = block_inhalt is not None

    bezieht_sich_auf_dak = _enthaelt_dak_bezug(text)
    ist_identitaetsfrage = _ist_identitaetsfrage(text)
    ist_visionfrage = _ist_visionfrage(text)
    ist_meta = _ist_meta(text)
    ist_widerspruch = _ist_widerspruch(text)

    soll_tool_ausfuehren = ist_toolbefehl
    soll_speichern = ist_trigger
    soll_antworten = not ist_leer and not ist_fadenwechsel and not ist_toolbefehl

    letzte_relevante_daniel_aussage_ersetzen = (
        not ist_leer
        and not ist_fadenwechsel
        and not ist_toolbefehl
        and not _ist_reiner_triggertext(text)
    )

    if ist_leer:
        kurzbegruendung = "leere Eingabe"
    elif ist_fadenwechsel:
        kurzbegruendung = f"Fadenwechsel nach {fadenziel}"
    elif ist_toolbefehl:
        kurzbegruendung = f"Toolbefehl erkannt: {tool_name}"
    elif ist_trigger and hat_block:
        kurzbegruendung = f"Trigger mit direktem Block: {trigger_art}"
    elif ist_trigger:
        kurzbegruendung = f"Trigger erkannt: {trigger_art}"
    elif ist_identitaetsfrage:
        kurzbegruendung = "Identitaetsfrage erkannt"
    elif ist_visionfrage:
        kurzbegruendung = "Visionfrage erkannt"
    elif ist_meta:
        kurzbegruendung = "Meta-Eingabe erkannt"
    else:
        kurzbegruendung = "normale inhaltliche Eingabe"

    return Verarbeitungsergebnis(
        nutzer_text=text,
        faden=faden,
        ist_leer=ist_leer,
        ist_fadenwechsel=ist_fadenwechsel,
        fadenziel=fadenziel,
        ist_toolbefehl=ist_toolbefehl,
        tool_name=tool_name,
        ist_trigger=ist_trigger,
        trigger_art=trigger_art,
        hat_block=hat_block,
        block_inhalt=block_inhalt,
        bezieht_sich_auf_dak=bezieht_sich_auf_dak,
        ist_identitaetsfrage=ist_identitaetsfrage,
        ist_visionfrage=ist_visionfrage,
        ist_meta=ist_meta,
        ist_widerspruch=ist_widerspruch,
        soll_speichern=soll_speichern,
        soll_tool_ausfuehren=soll_tool_ausfuehren,
        soll_antworten=soll_antworten,
        letzte_relevante_daniel_aussage_ersetzen=letzte_relevante_daniel_aussage_ersetzen,
        kurzbegruendung=kurzbegruendung,
    )
