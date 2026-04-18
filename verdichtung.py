from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.ollama_chat import ollama_chat


def _projektwurzel() -> Path:
    return Path(__file__).resolve().parents[2]


PROJEKTWURZEL = _projektwurzel()
SPUREN_ORDNER = PROJEKTWURZEL / "agent" / "dak_gord_system" / "spuren"
VERDICHTUNGS_ORDNER = SPUREN_ORDNER / "verdichtung"


@dataclass
class VerdichtungsErgebnis:
    art: str
    datei: str
    zeitstempel: str
    offset: int
    chunk_groesse: int
    textauszug: str

    kernsaetze: list[str]
    schluesselformulierungen: list[str]
    spannungen: list[str]
    bewegungen: list[str]
    codedeutung: list[str]
    offene_fragen: list[str]
    freie_annaeherung: list[str]

    rohantwort: str

    def als_dict(self) -> dict:
        return asdict(self)


def _zeitstempel() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _prompt_fuer_verdichtung(
    art: str,
    datei: str,
    offset: int,
    chunk_groesse: int,
    textauszug: str,
) -> list[str]:
    system = (
        "Du bist dak+gord-system.\n"
        "Du verdichtest einen Textauszug mehrschichtig.\n"
        "Der Rohtextauszug ist Primaerquelle und Massstab.\n"
        "Die Verdichtung ist Arbeitsform und darf die Quelle nicht ersetzen.\n"
        "Erfinde nichts hinzu, was nicht im Auszug steht oder klar als Ableitung markiert werden kann.\n"
        "Keine Begruessung. Keine Selbstbeschreibung. Keine Servicefloskeln.\n"
        "Arbeite eng am Text, aber nicht stumpf. Zeige auch Bewegung, Spannung und moegliche Codebedeutung.\n"
        "Antworte exakt in diesem Format:\n"
        "KERNSAETZE:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "4. ...\n"
        "5. ...\n"
        "\n"
        "SCHLUESSELFORMULIERUNGEN:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "\n"
        "SPANNUNGEN:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "\n"
        "BEWEGUNGEN:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "\n"
        "CODEDEUTUNG:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "4. ...\n"
        "\n"
        "OFFENE FRAGEN:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "\n"
        "FREIE ANNAEHERUNG:\n"
        "1. ...\n"
        "2. ...\n"
        "3. ...\n"
        "Jeder Punkt kurz, praezise und textnah.\n"
        "Bei CODEDEUTUNG darfst du nur moegliche Regeln, Rollen, Beziehungen, Trigger oder Strukturen nennen, die wirklich aus dem Text nahegelegt werden.\n"
        "Bei FREIE ANNAEHERUNG darfst du lebendiger formulieren, aber nicht die Quelle verraten oder ersetzen.\n"
    )

    nutzer = (
        f"ART: {art}\n"
        f"DATEI: {datei}\n"
        f"OFFSET: {offset}\n"
        f"CHUNK_GROESSE: {chunk_groesse}\n\n"
        f"ROHTEXTAUSZUG:\n{textauszug}"
    )

    return [system, nutzer]


def _prompt_fuer_kernsatz_nachzug(
    datei: str,
    offset: int,
    chunk_groesse: int,
    textauszug: str,
) -> list[str]:
    system = (
        "Du bist dak+gord-system.\n"
        "Ziehe nur fehlende Kernsatz-Stabilitaet nach.\n"
        "Der Rohtextauszug ist Primaerquelle.\n"
        "Antworte NUR mit genau 5 nummerierten Kernsaetzen.\n"
        "Keine Einleitung. Keine Ueberschriften. Keine Floskeln.\n"
        "Jeder Kernsatz kurz, textnah und eigenstaendig.\n"
        "Die 5 Kernsaetze sollen verschiedene Aspekte tragen und sich nicht bloss umformuliert wiederholen.\n"
        "Verteile sie moeglichst auf unterschiedliche Schwerpunkte wie Struktur, Akteure, Regeln, Dynamik, Sichtbarkeit, Beziehung oder Architektur.\n"
    )

    nutzer = (
        f"DATEI: {datei}\n"
        f"OFFSET: {offset}\n"
        f"CHUNK_GROESSE: {chunk_groesse}\n\n"
        f"ROHTEXTAUSZUG:\n{textauszug}"
    )

    return [system, nutzer]


def _saeubere_punkttext(text: str) -> str:
    sauber = text or ""
    sauber = sauber.replace("**", "")
    sauber = sauber.replace("__", "")
    sauber = re.sub(r"`+", "", sauber)
    sauber = re.sub(r"^[\-\*\•\s]+", "", sauber)
    sauber = re.sub(r"\s+", " ", sauber).strip()
    return sauber


def _normalisiere_nummernbloecke(text: str) -> str:
    if not text:
        return ""

    t = text.replace("\r\n", "\n").replace("\r", "\n")

    # Falls das Modell "Satz.2. Naechster Punkt" produziert, trennen wir vor der neuen Nummer auf.
    t = re.sub(r'(?<=\S)([1-9]\.\s*)', r'\n\1', t)

    # Mehrfachzeilen glätten
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t


def _punkte_aus_abschnitt(zeilen: list[str], ueberschrift: str, erwartete_anzahl: int) -> list[str]:
    start_marker = f"{ueberschrift}:"
    start_index = None

    for i, zeile in enumerate(zeilen):
        if zeile.strip().upper() == start_marker:
            start_index = i + 1
            break

    if start_index is None:
        return []

    abschnitt_zeilen: list[str] = []

    for zeile in zeilen[start_index:]:
        sauber = zeile.strip()

        if not sauber:
            if abschnitt_zeilen:
                break
            continue

        if sauber.endswith(":") and not sauber[:1].isdigit():
            break

        abschnitt_zeilen.append(sauber)

    abschnitt_text = _normalisiere_nummernbloecke("\n".join(abschnitt_zeilen)).strip()
    if not abschnitt_text:
        return []

    treffer = re.findall(
        r'(?m)^\s*([1-9])\.\s*(.*?)(?=(?:^\s*[1-9]\.\s*)|\Z)',
        abschnitt_text,
        flags=re.DOTALL,
    )

    punkte: list[str] = []
    for _, inhalt in treffer:
        sauber = _saeubere_punkttext(inhalt)
        if sauber:
            punkte.append(sauber)
        if len(punkte) >= erwartete_anzahl:
            break

    return punkte


def _parse_nummernliste(text: str, erwartete_anzahl: int) -> list[str]:
    norm = _normalisiere_nummernbloecke(text)
    treffer = re.findall(
        r'(?m)^\s*([1-9])\.\s*(.*?)(?=(?:^\s*[1-9]\.\s*)|\Z)',
        norm,
        flags=re.DOTALL,
    )

    punkte: list[str] = []
    for _, inhalt in treffer:
        sauber = _saeubere_punkttext(inhalt)
        if sauber:
            punkte.append(sauber)
        if len(punkte) >= erwartete_anzahl:
            break

    return punkte


def _kernwortmenge(text: str) -> set[str]:
    woerter = re.findall(r"[a-zA-Z0-9_äöüÄÖÜß]+", text.lower())
    stopp = {
        "der", "die", "das", "ein", "eine", "einer", "einem", "einen",
        "und", "oder", "aber", "mit", "ohne", "fuer", "für", "von", "im",
        "in", "am", "an", "zu", "zur", "zum", "auf", "als", "ist", "sind",
        "sein", "wird", "werden", "durch", "nur", "nicht", "kein", "keine",
        "eines", "des", "dem", "den", "sich", "einem", "einer", "eines",
        "dieses", "dieser", "diesem", "diese", "eigenen", "eigenstaendig",
    }
    return {w for w in woerter if len(w) > 2 and w not in stopp}


def _zu_aehnlich(a: str, b: str) -> bool:
    a_norm = _saeubere_punkttext(a).lower()
    b_norm = _saeubere_punkttext(b).lower()

    if not a_norm or not b_norm:
        return False

    if a_norm == b_norm:
        return True

    a_set = _kernwortmenge(a_norm)
    b_set = _kernwortmenge(b_norm)

    if not a_set or not b_set:
        return False

    schnitt = len(a_set & b_set)
    kleiner = min(len(a_set), len(b_set))
    groesser = max(len(a_set), len(b_set))

    if kleiner == 0 or groesser == 0:
        return False

    # stark ähnliche Kernaussagen rauswerfen
    if (schnitt / kleiner) >= 0.75:
        return True

    # fast gleiche Aussage mit leicht anderer Verlängerung
    if (schnitt / groesser) >= 0.6 and abs(len(a_set) - len(b_set)) <= 2:
        return True

    return False


def _vereinige_einzigartig(vorhanden: list[str], neu: list[str], max_anzahl: int) -> list[str]:
    ergebnis: list[str] = []

    for punkt in vorhanden + neu:
        sauber = _saeubere_punkttext(punkt)
        if not sauber:
            continue

        if any(_zu_aehnlich(sauber, schon) for schon in ergebnis):
            continue

        ergebnis.append(sauber)
        if len(ergebnis) >= max_anzahl:
            break

    return ergebnis


def _stabilisiere_kernsaetze(
    datei: str,
    offset: int,
    chunk_groesse: int,
    textauszug: str,
    kernsaetze: list[str],
) -> list[str]:
    if len(kernsaetze) >= 5:
        return _vereinige_einzigartig(kernsaetze, [], 5)

    try:
        roh = ollama_chat(
            _prompt_fuer_kernsatz_nachzug(
                datei=datei,
                offset=offset,
                chunk_groesse=chunk_groesse,
                textauszug=textauszug,
            )
        ).strip()
    except Exception:
        return _vereinige_einzigartig(kernsaetze, [], 5)

    fallback = _parse_nummernliste(roh, 5)
    kombiniert = _vereinige_einzigartig(kernsaetze, fallback, 5)
    return kombiniert


def _parse_verdichtungsantwort(
    rohantwort: str,
) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    zeilen = rohantwort.splitlines()

    kernsaetze = _punkte_aus_abschnitt(zeilen, "KERNSAETZE", 5)
    schluesselformulierungen = _punkte_aus_abschnitt(zeilen, "SCHLUESSELFORMULIERUNGEN", 3)
    spannungen = _punkte_aus_abschnitt(zeilen, "SPANNUNGEN", 3)
    bewegungen = _punkte_aus_abschnitt(zeilen, "BEWEGUNGEN", 3)
    codedeutung = _punkte_aus_abschnitt(zeilen, "CODEDEUTUNG", 4)
    offene_fragen = _punkte_aus_abschnitt(zeilen, "OFFENE FRAGEN", 3)
    freie_annaeherung = _punkte_aus_abschnitt(zeilen, "FREIE ANNAEHERUNG", 3)

    return (
        kernsaetze,
        schluesselformulierungen,
        spannungen,
        bewegungen,
        codedeutung,
        offene_fragen,
        freie_annaeherung,
    )


def verdichte_text(
    art: str,
    datei: str | Path,
    textauszug: str,
    offset: int = 0,
    chunk_groesse: int = 1600,
) -> VerdichtungsErgebnis:
    datei_text = str(Path(datei).resolve()) if str(datei).strip() else ""

    rohantwort = ollama_chat(
        _prompt_fuer_verdichtung(
            art=(art or "").strip(),
            datei=datei_text,
            offset=max(0, int(offset)),
            chunk_groesse=max(1, int(chunk_groesse)),
            textauszug=textauszug,
        )
    ).strip()

    (
        kernsaetze,
        schluesselformulierungen,
        spannungen,
        bewegungen,
        codedeutung,
        offene_fragen,
        freie_annaeherung,
    ) = _parse_verdichtungsantwort(rohantwort)

    kernsaetze = _stabilisiere_kernsaetze(
        datei=datei_text,
        offset=max(0, int(offset)),
        chunk_groesse=max(1, int(chunk_groesse)),
        textauszug=textauszug,
        kernsaetze=kernsaetze,
    )

    return VerdichtungsErgebnis(
        art=(art or "").strip(),
        datei=datei_text,
        zeitstempel=_zeitstempel(),
        offset=max(0, int(offset)),
        chunk_groesse=max(1, int(chunk_groesse)),
        textauszug=textauszug,
        kernsaetze=kernsaetze,
        schluesselformulierungen=schluesselformulierungen,
        spannungen=spannungen,
        bewegungen=bewegungen,
        codedeutung=codedeutung,
        offene_fragen=offene_fragen,
        freie_annaeherung=freie_annaeherung,
        rohantwort=rohantwort,
    )


def formatiere_verdichtungsblock(ergebnis: VerdichtungsErgebnis) -> str:
    teile: list[str] = [
        f"[{ergebnis.zeitstempel}] dak+gord-system",
        "",
        "QUELLE:",
        f"ART: {ergebnis.art}",
        f"DATEI: {ergebnis.datei}",
        f"OFFSET: {ergebnis.offset}",
        f"CHUNK_GROESSE: {ergebnis.chunk_groesse}",
        "",
        "ROHTEXTAUSZUG:",
        ergebnis.textauszug.rstrip(),
        "",
        "VERDICHTUNG",
        "",
        "KERNSAETZE:",
    ]

    if ergebnis.kernsaetze:
        for i, punkt in enumerate(ergebnis.kernsaetze, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparsten Kernsaetze)")

    teile.extend(["", "SCHLUESSELFORMULIERUNGEN:"])
    if ergebnis.schluesselformulierungen:
        for i, punkt in enumerate(ergebnis.schluesselformulierungen, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparsten Schluesselformulierungen)")

    teile.extend(["", "SPANNUNGEN:"])
    if ergebnis.spannungen:
        for i, punkt in enumerate(ergebnis.spannungen, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparsten Spannungen)")

    teile.extend(["", "BEWEGUNGEN:"])
    if ergebnis.bewegungen:
        for i, punkt in enumerate(ergebnis.bewegungen, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparsten Bewegungen)")

    teile.extend(["", "CODEDEUTUNG:"])
    if ergebnis.codedeutung:
        for i, punkt in enumerate(ergebnis.codedeutung, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparste Code-Deutung)")

    teile.extend(["", "OFFENE FRAGEN:"])
    if ergebnis.offene_fragen:
        for i, punkt in enumerate(ergebnis.offene_fragen, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparsten offenen Fragen)")

    teile.extend(["", "FREIE ANNAEHERUNG:"])
    if ergebnis.freie_annaeherung:
        for i, punkt in enumerate(ergebnis.freie_annaeherung, start=1):
            teile.append(f"{i}. {punkt}")
    else:
        teile.append("(keine sauber geparste freie Annaeherung)")

    teile.extend(["", "ROHANTWORT:", ergebnis.rohantwort.rstrip(), "", ""])
    return "\n".join(teile)


def speichere_verdichtung(ergebnis: VerdichtungsErgebnis, dateiname: str | None = None) -> Path:
    VERDICHTUNGS_ORDNER.mkdir(parents=True, exist_ok=True)

    if dateiname and dateiname.strip():
        ziel = VERDICHTUNGS_ORDNER / dateiname.strip()
    else:
        basis = Path(ergebnis.datei).stem if ergebnis.datei else "unbekannt"
        zeit = datetime.now().strftime("%Y%m%d_%H%M%S")
        ziel = VERDICHTUNGS_ORDNER / f"{basis}_verdichtung_{zeit}.md"

    if ziel.suffix.lower() != ".md":
        ziel = ziel.with_suffix(".md")

    ziel.write_text(formatiere_verdichtungsblock(ergebnis), encoding="utf-8")
    return ziel
