from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from agent.dak_gord_system.verdichtung import VerdichtungsErgebnis


def _projektwurzel() -> Path:
    return Path(__file__).resolve().parents[2]


PROJEKTWURZEL = _projektwurzel()
AGENTDATEIEN_ORDNER = PROJEKTWURZEL / "agent" / "dak_gord_system" / "spuren" / "agentdateien"
VERLAUF_MARKER = "=== VERLAUF ==="


def quelle_zu_agentdatei(quellpfad: str | Path) -> Path:
    quelle = Path(quellpfad).resolve()

    try:
        rel = quelle.relative_to(PROJEKTWURZEL)
        ziel = AGENTDATEIEN_ORDNER / rel
    except Exception:
        ziel = AGENTDATEIEN_ORDNER / quelle.name

    return ziel.with_suffix(".agent.md")


def _zeitstempel() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _saeubere_punkt(text: str) -> str:
    t = (text or "").strip()
    t = t.replace("**", "")
    t = t.replace("__", "")
    t = re.sub(r"`+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _kernwortmenge(text: str) -> set[str]:
    woerter = re.findall(r"[a-zA-Z0-9_äöüÄÖÜß]+", text.lower())
    stopp = {
        "der", "die", "das", "ein", "eine", "einer", "einem", "einen",
        "und", "oder", "aber", "mit", "ohne", "fuer", "für", "von", "im",
        "in", "am", "an", "zu", "zur", "zum", "auf", "als", "ist", "sind",
        "sein", "wird", "werden", "durch", "nur", "nicht", "kein", "keine",
        "des", "dem", "den", "eine", "einer", "eines", "dieser", "diese",
        "dieses", "sich", "noch", "mehr", "auch", "eher", "schon", "dann",
    }
    return {w for w in woerter if len(w) > 2 and w not in stopp}


def _zu_aehnlich(a: str, b: str) -> bool:
    a_norm = _saeubere_punkt(a).lower()
    b_norm = _saeubere_punkt(b).lower()

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

    if (schnitt / kleiner) >= 0.75:
        return True

    if (schnitt / groesser) >= 0.6 and abs(len(a_set) - len(b_set)) <= 2:
        return True

    return False


def _vereinige_einzigartig(punkte: list[str], max_anzahl: int) -> list[str]:
    ergebnis: list[str] = []

    for punkt in punkte:
        sauber = _saeubere_punkt(punkt)
        if not sauber:
            continue
        if any(_zu_aehnlich(sauber, schon) for schon in ergebnis):
            continue
        ergebnis.append(sauber)
        if len(ergebnis) >= max_anzahl:
            break

    return ergebnis


def _format_liste(titel: str, punkte: list[str], leertext: str) -> list[str]:
    zeilen = [titel]
    if punkte:
        for i, punkt in enumerate(punkte, start=1):
            zeilen.append(f"{i}. {punkt}")
    else:
        zeilen.append(leertext)
    return zeilen


def _split_verlauf_bloecke(text: str) -> tuple[str, list[str]]:
    roh = text or ""
    if VERLAUF_MARKER not in roh:
        return roh.strip(), []

    kopf, verlauf = roh.split(VERLAUF_MARKER, 1)
    bloecke = [b.strip() for b in re.split(r"\n\s*---\s*\n", verlauf.strip()) if b.strip()]
    return kopf.strip(), bloecke


def _extract_between(block: str, start_marker: str, end_marker: str | None = None) -> str:
    start = block.find(start_marker)
    if start == -1:
        return ""

    start += len(start_marker)
    rest = block[start:]

    if end_marker:
        ende = rest.find(end_marker)
        if ende != -1:
            rest = rest[:ende]

    return rest.strip()


def _parse_numbered_section(block: str, heading: str) -> list[str]:
    lines = block.splitlines()
    punkte: list[str] = []
    in_section = False
    current = ""

    for line in lines:
        stripped = line.strip()

        if not in_section:
            if stripped == f"{heading}:" or stripped == f"{heading}?:" or stripped == f"{heading}?:":
                in_section = True
            continue

        if not stripped:
            if current:
                punkte.append(_saeubere_punkt(current))
                current = ""
            continue

        if stripped.endswith(":") and not re.match(r"^\d+\.", stripped):
            if current:
                punkte.append(_saeubere_punkt(current))
            break

        if re.match(r"^\d+\.\s+", stripped):
            if current:
                punkte.append(_saeubere_punkt(current))
            current = re.sub(r"^\d+\.\s+", "", stripped)
        else:
            if current:
                current += " " + stripped

    if current:
        punkte.append(_saeubere_punkt(current))

    return [p for p in punkte if p]


def _normalisiere_heading(line: str) -> str:
    t = (line or "").strip()
    t = t.replace("**", "")
    t = re.sub(r"^#+\s*", "", t)
    t = re.sub(r"^\d+\.\s*", "", t)
    t = t.strip().rstrip(":").strip()
    return t.upper()


def _parse_bullets_under_answer_headings(block: str, headings: set[str]) -> list[str]:
    lines = block.splitlines()
    punkte: list[str] = []
    aktive_heading = None
    current = ""

    for line in lines:
        stripped = line.strip()
        norm = _normalisiere_heading(stripped)

        if norm in headings:
            if current:
                punkte.append(_saeubere_punkt(current))
                current = ""
            aktive_heading = norm
            continue

        if aktive_heading is None:
            continue

        if stripped.startswith("### "):
            if current:
                punkte.append(_saeubere_punkt(current))
                current = ""
            aktive_heading = None
            continue

        if re.match(r"^\d+\.\s+\*\*.*\*\*:?\s*$", stripped) or re.match(r"^\d+\.\s+[A-ZÄÖÜ].*:\s*$", stripped):
            if current:
                punkte.append(_saeubere_punkt(current))
                current = ""
            aktive_heading = None
            continue

        if stripped.startswith("- "):
            if current:
                punkte.append(_saeubere_punkt(current))
            current = stripped[2:].strip()
            continue

        if stripped and current:
            current += " " + stripped

    if current:
        punkte.append(_saeubere_punkt(current))

    return [p for p in punkte if p]



def _fundamentalitaets_bonus(text: str) -> float:
    t = (text or "").lower()
    bonus = 0.0

    starke_signale = {
        "organisch": 1.0,
        "wachstum": 1.0,
        "ideen": 0.6,
        "diskurs": 0.6,
        "entitäten": 0.9,
        "entitaeten": 0.9,
        "menschen": 0.6,
        "resonanz": 0.8,
        "architektur": 0.8,
        "struktur": 0.7,
        "strukturen": 0.7,
        "öffentlich": 0.5,
        "oeffentlich": 0.5,
        "feed": 0.5,
        "zweischichtigkeit": 0.7,
        "rollen": 0.4,
        "kategorien": 0.4,
    }

    detail_signale = {
        "analysebox": -0.9,
        "dashboard": -0.8,
        "statistik": -0.6,
        "statistiken": -0.6,
        "schlagwort": -0.5,
        "schlagworte": -0.5,
        "schlagwörtern": -0.5,
        "schlagwoertern": -0.5,
        "visualisierung": -0.5,
        "zahlen": -0.4,
        "ui": -0.3,
    }

    for wort, wert in starke_signale.items():
        if wort in t:
            bonus += wert

    for wort, wert in detail_signale.items():
        if wort in t:
            bonus += wert

    return bonus


def _anschlussblock(block: str) -> bool:
    return "ART: anschlussantwort" in block


def _gewichtete_eintraege_fuer_block(block: str) -> tuple[list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]]]:
    kern: list[tuple[str, float]] = []
    spannungen: list[tuple[str, float]] = []
    code: list[tuple[str, float]] = []
    offene: list[tuple[str, float]] = []
    bewegungen: list[tuple[str, float]] = []
    fragen: list[tuple[str, float]] = []

    if _anschlussblock(block):
        frage = _extract_between(block, "FRAGE:", "ANTWORT:")
        if frage:
            fragen.append((frage, 0.7))

        for punkt in _parse_bullets_under_answer_headings(block, {"DIREKT IM AUSZUG", "DARAUS VERDICHTET SICH"}):
            kern.append((punkt, 0.8 + _fundamentalitaets_bonus(punkt)))

        for punkt in _parse_bullets_under_answer_headings(block, {"SPANNUNGEN"}):
            spannungen.append((punkt, 0.8 + _fundamentalitaets_bonus(punkt)))

        for punkt in _parse_bullets_under_answer_headings(block, {"FUER CODE KOENNTE DAS HEISSEN", "IMPLIZITE REGELN ODER STRUKTUREN"}):
            code.append((punkt, 0.7 + _fundamentalitaets_bonus(punkt)))

        for punkt in _parse_bullets_under_answer_headings(block, {"WEITERGEDACHT", "BEWEGUNGEN IM TEXT"}):
            bewegungen.append((punkt, 0.6 + _fundamentalitaets_bonus(punkt)))

        return kern, spannungen, code, offene, bewegungen, fragen

    for punkt in _parse_numbered_section(block, "KERNSAETZE"):
        kern.append((punkt, 1.4 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "SPANNUNGEN"):
        spannungen.append((punkt, 1.2 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "CODEDEUTUNG"):
        code.append((punkt, 1.1 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "OFFENE FRAGEN"):
        offene.append((punkt, 0.9 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "FREIE ANNAEHERUNG"):
        bewegungen.append((punkt, 0.7 + _fundamentalitaets_bonus(punkt)))

    return kern, spannungen, code, offene, bewegungen, fragen


def _verdichte_gewichtete_punkte(eintraege: list[tuple[str, float]], max_anzahl: int) -> list[str]:
    gruppen: list[dict] = []

    for text, score in eintraege:
        sauber = _saeubere_punkt(text)
        if not sauber:
            continue

        gefunden = None
        for gruppe in gruppen:
            if _zu_aehnlich(sauber, gruppe["repr"]):
                gefunden = gruppe
                break

        if gefunden is None:
            gruppen.append({
                "repr": sauber,
                "score": float(score),
                "items": [sauber],
            })
            continue

        gefunden["items"].append(sauber)
        gefunden["score"] += float(score)

        kandidaten = sorted(
            set(gefunden["items"]),
            key=lambda x: (-_fundamentalitaets_bonus(x), len(x), x),
        )
        gefunden["repr"] = kandidaten[0]

    gruppen.sort(key=lambda g: (-g["score"], -_fundamentalitaets_bonus(g["repr"]), len(g["repr"]), g["repr"]))

    result: list[str] = []
    for gruppe in gruppen:
        rep = gruppe["repr"]
        if any(_zu_aehnlich(rep, schon) for schon in result):
            continue
        result.append(rep)
        if len(result) >= max_anzahl:
            break

    return result


def _sammle_stabile_dossierpunkte(bloecke: list[str]) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    kern_eintraege: list[tuple[str, float]] = []
    spannung_eintraege: list[tuple[str, float]] = []
    code_eintraege: list[tuple[str, float]] = []
    offene_eintraege: list[tuple[str, float]] = []
    bewegung_eintraege: list[tuple[str, float]] = []
    fragen_eintraege: list[tuple[str, float]] = []

    for block in bloecke:
        kern, spannungen, code, offene, bewegungen, fragen = _gewichtete_eintraege_fuer_block(block)
        kern_eintraege.extend(kern)
        spannung_eintraege.extend(spannungen)
        code_eintraege.extend(code)
        offene_eintraege.extend(offene)
        bewegung_eintraege.extend(bewegungen)
        fragen_eintraege.extend(fragen)

    kernsaetze = _verdichte_gewichtete_punkte(kern_eintraege, 6)
    spannungen = _verdichte_gewichtete_punkte(spannung_eintraege, 5)
    codefolgen = _verdichte_gewichtete_punkte(code_eintraege, 5)
    offene_fragen = _verdichte_gewichtete_punkte(offene_eintraege, 5)
    bewegungen = _verdichte_gewichtete_punkte(bewegung_eintraege, 5)
    fragen = _verdichte_gewichtete_punkte(fragen_eintraege, 4)

    return kernsaetze, spannungen, codefolgen, offene_fragen, bewegungen, fragen

def _fundamentalitaets_bonus(text: str) -> float:
    t = (text or "").lower()
    bonus = 0.0

    starke_signale = {
        "organisch": 1.0,
        "wachstum": 1.0,
        "ideen": 0.6,
        "diskurs": 0.6,
        "entitäten": 0.9,
        "entitaeten": 0.9,
        "menschen": 0.6,
        "resonanz": 0.8,
        "architektur": 0.8,
        "struktur": 0.7,
        "strukturen": 0.7,
        "öffentlich": 0.5,
        "oeffentlich": 0.5,
        "feed": 0.5,
        "zweischichtigkeit": 0.7,
        "rollen": 0.4,
        "kategorien": 0.4,
    }

    detail_signale = {
        "analysebox": -0.9,
        "dashboard": -0.8,
        "statistik": -0.6,
        "statistiken": -0.6,
        "schlagwort": -0.5,
        "schlagworte": -0.5,
        "schlagwörtern": -0.5,
        "schlagwoertern": -0.5,
        "visualisierung": -0.5,
        "zahlen": -0.4,
        "ui": -0.3,
    }

    for wort, wert in starke_signale.items():
        if wort in t:
            bonus += wert

    for wort, wert in detail_signale.items():
        if wort in t:
            bonus += wert

    return bonus


def _anschlussblock(block: str) -> bool:
    return "ART: anschlussantwort" in block


def _gewichtete_eintraege_fuer_block(block: str) -> tuple[list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]], list[tuple[str, float]]]:
    kern: list[tuple[str, float]] = []
    spannungen: list[tuple[str, float]] = []
    code: list[tuple[str, float]] = []
    offene: list[tuple[str, float]] = []
    bewegungen: list[tuple[str, float]] = []
    fragen: list[tuple[str, float]] = []

    if _anschlussblock(block):
        frage = _extract_between(block, "FRAGE:", "ANTWORT:")
        if frage:
            fragen.append((frage, 0.7))

        for punkt in _parse_bullets_under_answer_headings(block, {"DIREKT IM AUSZUG", "DARAUS VERDICHTET SICH"}):
            kern.append((punkt, 0.8 + _fundamentalitaets_bonus(punkt)))

        for punkt in _parse_bullets_under_answer_headings(block, {"SPANNUNGEN"}):
            spannungen.append((punkt, 0.8 + _fundamentalitaets_bonus(punkt)))

        for punkt in _parse_bullets_under_answer_headings(block, {"FUER CODE KOENNTE DAS HEISSEN", "IMPLIZITE REGELN ODER STRUKTUREN"}):
            code.append((punkt, 0.7 + _fundamentalitaets_bonus(punkt)))

        for punkt in _parse_bullets_under_answer_headings(block, {"WEITERGEDACHT", "BEWEGUNGEN IM TEXT"}):
            bewegungen.append((punkt, 0.6 + _fundamentalitaets_bonus(punkt)))

        return kern, spannungen, code, offene, bewegungen, fragen

    for punkt in _parse_numbered_section(block, "KERNSAETZE"):
        kern.append((punkt, 1.4 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "SPANNUNGEN"):
        spannungen.append((punkt, 1.2 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "CODEDEUTUNG"):
        code.append((punkt, 1.1 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "OFFENE FRAGEN"):
        offene.append((punkt, 0.9 + _fundamentalitaets_bonus(punkt)))

    for punkt in _parse_numbered_section(block, "FREIE ANNAEHERUNG"):
        bewegungen.append((punkt, 0.7 + _fundamentalitaets_bonus(punkt)))

    return kern, spannungen, code, offene, bewegungen, fragen


def _verdichte_gewichtete_punkte(eintraege: list[tuple[str, float]], max_anzahl: int) -> list[str]:
    gruppen: list[dict] = []

    for text, score in eintraege:
        sauber = _saeubere_punkt(text)
        if not sauber:
            continue

        gefunden = None
        for gruppe in gruppen:
            if _zu_aehnlich(sauber, gruppe["repr"]):
                gefunden = gruppe
                break

        if gefunden is None:
            gruppen.append({
                "repr": sauber,
                "score": float(score),
                "items": [sauber],
            })
            continue

        gefunden["items"].append(sauber)
        gefunden["score"] += float(score)

        kandidaten = sorted(
            set(gefunden["items"]),
            key=lambda x: (-_fundamentalitaets_bonus(x), len(x), x),
        )
        gefunden["repr"] = kandidaten[0]

    gruppen.sort(key=lambda g: (-g["score"], -_fundamentalitaets_bonus(g["repr"]), len(g["repr"]), g["repr"]))

    result: list[str] = []
    for gruppe in gruppen:
        rep = gruppe["repr"]
        if any(_zu_aehnlich(rep, schon) for schon in result):
            continue
        result.append(rep)
        if len(result) >= max_anzahl:
            break

    return result


def _sammle_stabile_dossierpunkte(bloecke: list[str]) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    kern_eintraege: list[tuple[str, float]] = []
    spannung_eintraege: list[tuple[str, float]] = []
    code_eintraege: list[tuple[str, float]] = []
    offene_eintraege: list[tuple[str, float]] = []
    bewegung_eintraege: list[tuple[str, float]] = []
    fragen_eintraege: list[tuple[str, float]] = []

    for block in bloecke:
        kern, spannungen, code, offene, bewegungen, fragen = _gewichtete_eintraege_fuer_block(block)
        kern_eintraege.extend(kern)
        spannung_eintraege.extend(spannungen)
        code_eintraege.extend(code)
        offene_eintraege.extend(offene)
        bewegung_eintraege.extend(bewegungen)
        fragen_eintraege.extend(fragen)

    kernsaetze = _verdichte_gewichtete_punkte(kern_eintraege, 6)
    spannungen = _verdichte_gewichtete_punkte(spannung_eintraege, 5)
    codefolgen = _verdichte_gewichtete_punkte(code_eintraege, 5)
    offene_fragen = _verdichte_gewichtete_punkte(offene_eintraege, 5)
    bewegungen = _verdichte_gewichtete_punkte(bewegung_eintraege, 5)
    fragen = _verdichte_gewichtete_punkte(fragen_eintraege, 4)

    return kernsaetze, spannungen, codefolgen, offene_fragen, bewegungen, fragen
def _sammle_dossierpunkte(bloecke: list[str]) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str]]:
    kernsaetze_raw: list[str] = []
    spannungen_raw: list[str] = []
    codefolgen_raw: list[str] = []
    offene_raw: list[str] = []
    bewegungen_raw: list[str] = []
    fragen_raw: list[str] = []

    for block in reversed(bloecke):
        if "ART: anschlussantwort" in block:
            frage = _extract_between(block, "FRAGE:", "ANTWORT:")
            if frage:
                fragen_raw.append(frage)

            kernsaetze_raw.extend(
                _parse_bullets_under_answer_headings(
                    block,
                    {"DIREKT IM AUSZUG", "DARAUS VERDICHTET SICH"},
                )
            )
            spannungen_raw.extend(
                _parse_bullets_under_answer_headings(
                    block,
                    {"SPANNUNGEN"},
                )
            )
            bewegungen_raw.extend(
                _parse_bullets_under_answer_headings(
                    block,
                    {"WEITERGEDACHT", "BEWEGUNGEN IM TEXT"},
                )
            )
            codefolgen_raw.extend(
                _parse_bullets_under_answer_headings(
                    block,
                    {"FUER CODE KOENNTE DAS HEISSEN", "IMPLIZITE REGELN ODER STRUKTUREN"},
                )
            )
            continue

        kernsaetze_raw.extend(_parse_numbered_section(block, "KERNSAETZE"))
        spannungen_raw.extend(_parse_numbered_section(block, "SPANNUNGEN"))
        codefolgen_raw.extend(_parse_numbered_section(block, "CODEDEUTUNG"))
        offene_raw.extend(_parse_numbered_section(block, "OFFENE FRAGEN"))
        bewegungen_raw.extend(_parse_numbered_section(block, "FREIE ANNAEHERUNG"))

    kernsaetze = _vereinige_einzigartig(kernsaetze_raw, 6)
    spannungen = _vereinige_einzigartig(spannungen_raw, 5)
    codefolgen = _vereinige_einzigartig(codefolgen_raw, 5)
    offene_fragen = _vereinige_einzigartig(offene_raw, 5)
    bewegungen = _vereinige_einzigartig(bewegungen_raw, 5)
    fragen = _vereinige_einzigartig(fragen_raw, 4)

    return kernsaetze, spannungen, codefolgen, offene_fragen, bewegungen, fragen







def _enthaelt_eines(text: str, woerter: tuple[str, ...]) -> bool:
    t = (text or "").lower()
    return any(w in t for w in woerter)


def _kanonisiere_liste(
    punkte: list[str],
    max_anzahl: int,
    gruppen: list[tuple[str, ...]],
) -> list[str]:
    ausgewaehlt: list[str] = []

    for gruppe in gruppen:
        kandidat = None
        for punkt in punkte:
            if not _enthaelt_eines(punkt, gruppe):
                continue
            if any(_zu_aehnlich(punkt, schon) for schon in ausgewaehlt):
                continue
            kandidat = punkt
            break
        if kandidat:
            ausgewaehlt.append(kandidat)

    for punkt in punkte:
        if len(ausgewaehlt) >= max_anzahl:
            break
        if any(_zu_aehnlich(punkt, schon) for schon in ausgewaehlt):
            continue
        ausgewaehlt.append(punkt)

    return ausgewaehlt[:max_anzahl]



def _slot_score(text: str, woerter: tuple[str, ...]) -> float:
    t = (text or "").lower()
    score = _fundamentalitaets_bonus(text)
    for wort in woerter:
        if wort in t:
            score += 1.0
    return score


def _waehle_slot_kandidaten(
    punkte: list[str],
    slots: list[tuple[str, ...]],
    max_anzahl: int,
) -> list[str]:
    ausgewaehlt: list[str] = []

    for slot in slots:
        bester = None
        bester_score = float("-inf")

        for punkt in punkte:
            if not _enthaelt_eines(punkt, slot):
                continue
            if any(_zu_aehnlich(punkt, schon) for schon in ausgewaehlt):
                continue

            score = _slot_score(punkt, slot)
            if score > bester_score:
                bester = punkt
                bester_score = score

        if bester is not None:
            ausgewaehlt.append(bester)

    for punkt in punkte:
        if len(ausgewaehlt) >= max_anzahl:
            break
        if any(_zu_aehnlich(punkt, schon) for schon in ausgewaehlt):
            continue
        ausgewaehlt.append(punkt)

    return ausgewaehlt[:max_anzahl]



def _kanonisiere_stabilen_gesamtstand(
    kernsaetze: list[str],
    spannungen: list[str],
    codefolgen: list[str],
    offene_fragen: list[str],
) -> tuple[list[str], list[str], list[str], list[str]]:
    def hat_slot(punkte: list[str], woerter: tuple[str, ...]) -> bool:
        return any(_enthaelt_eines(p, woerter) for p in punkte)

    kanon_kern: list[str] = []
    if hat_slot(kernsaetze, ("organisch", "wachstum", "statisch", "struktur", "ideen", "diskurs")):
        kanon_kern.append("Das System basiert auf organischem Wachstum statt statischer Struktur.")
    if hat_slot(kernsaetze, ("entitäten", "entitaeten", "öffentliche", "oeffentliche", "feed", "sprache")):
        kanon_kern.append("Die öffentliche Sprache gehört den Entitäten.")
    if hat_slot(kernsaetze, ("menschen", "resonanz", "indirekt")):
        kanon_kern.append("Menschen wirken indirekt über Resonanz.")
    if hat_slot(kernsaetze, ("architektur", "flexibel", "adaptiv", "kategorien", "struktur")):
        kanon_kern.append("Die Architektur muss flexibel und wachsend sein.")

    kanon_spannungen: list[str] = []
    if hat_slot(spannungen, ("organisch", "wachstum", "statisch", "struktur")):
        kanon_spannungen.append("Organisches Wachstum steht gegen starre Plattformstruktur.")
    if hat_slot(spannungen, ("menschen", "entitäten", "entitaeten", "feed", "kommunikationslogik")):
        kanon_spannungen.append("Entitäten sprechen öffentlich, Menschen wirken indirekt.")
    if hat_slot(spannungen, ("social", "plattform", "standard", "eigenständig", "eigenstaendig")):
        kanon_spannungen.append("Das Projekt grenzt sich von Standard-Social-Media-Logik ab.")

    kanon_code: list[str] = []
    if hat_slot(codefolgen, ("feed", "entitäten", "entitaeten", "öffentlich", "oeffentlich", "rollen", "rechte")):
        kanon_code.append("Öffentlicher Feed und Rechte sind entitätszentriert organisiert.")
    if hat_slot(codefolgen, ("resonanz", "menschen", "indirekt", "zitate")):
        kanon_code.append("Resonanz ist der indirekte Einflusskanal der Menschen.")
    if hat_slot(codefolgen, ("architektur", "flexibel", "adaptiv", "kategorien", "struktur")):
        kanon_code.append("Die Architektur muss flexible, wachsende Strukturen tragen.")

    offene_fragen = _waehle_slot_kandidaten(
        offene_fragen,
        [
            ("menschen", "entitäten", "entitaeten", "interaktion", "regeln"),
            ("organisch", "wachstum", "architektur", "struktur"),
            ("resonanz", "indirektion", "indirekt", "öffentlich", "oeffentlich"),
        ],
        3,
    )

    if not kanon_kern:
        kanon_kern = _waehle_slot_kandidaten(
            kernsaetze,
            [
                ("organisch", "wachstum", "ideen", "diskurs", "statisch", "struktur"),
                ("entitäten", "entitaeten", "öffentliche", "oeffentliche", "feed", "sprache"),
                ("menschen", "resonanz", "indirekt"),
                ("architektur", "flexibel", "adaptiv", "kategorien", "struktur"),
            ],
            4,
        )

    if not kanon_spannungen:
        kanon_spannungen = _waehle_slot_kandidaten(
            spannungen,
            [
                ("organisch", "wachstum", "statisch", "struktur"),
                ("menschen", "entitäten", "entitaeten", "feed", "kommunikationslogik"),
                ("social", "plattform", "standard", "eigenständig", "eigenstaendig"),
            ],
            3,
        )

    if not kanon_code:
        kanon_code = _waehle_slot_kandidaten(
            codefolgen,
            [
                ("feed", "entitäten", "entitaeten", "öffentlich", "oeffentlich", "rollen", "rechte"),
                ("resonanz", "menschen", "indirekt", "zitate"),
                ("architektur", "flexibel", "adaptiv", "kategorien", "struktur"),
            ],
            3,
        )

    return kanon_kern[:4], kanon_spannungen[:3], kanon_code[:3], offene_fragen[:3]

def _block_herkunft(block: str) -> str:
    explizit = _extract_between(block, "HERKUNFT:", None)
    if explizit:
        erste_zeile = explizit.splitlines()[0].strip().lower()
        if erste_zeile:
            return erste_zeile

    lower = block.lower()

    if "art: graph_run_dossier" in lower or "task_id:" in lower:
        return "graph_run"
    if "art: anschlussantwort" in lower or "frage:" in lower:
        return "dialog"
    if "werkraum-neugier" in lower:
        return "neugier"
    if "vision-zyklus" in lower or "vision_cycle" in lower:
        return "vision_cycle"

    return "unbekannt"


def _waehle_fokus_bloecke(bloecke: list[str], max_anzahl: int = 2) -> list[str]:
    bevorzugt = {"dialog", "neugier", "vision_cycle"}
    gesammelt: list[str] = []
    ids: set[int] = set()

    for idx in range(len(bloecke) - 1, -1, -1):
        block = bloecke[idx]
        if _block_herkunft(block) in bevorzugt:
            gesammelt.append(block)
            ids.add(idx)
            if len(gesammelt) >= max_anzahl:
                return list(reversed(gesammelt))

    for idx in range(len(bloecke) - 1, -1, -1):
        if idx in ids:
            continue
        gesammelt.append(bloecke[idx])
        if len(gesammelt) >= max_anzahl:
            break

    return list(reversed(gesammelt))


def _format_herkunft_liste(herkuenfte: list[str]) -> list[str]:
    if not herkuenfte:
        return ["(keine Herkunft erfasst)"]
    return [f"{i}. {wert}" for i, wert in enumerate(herkuenfte, start=1)]


def _baue_dossierkopf(datei: str, bloecke: list[str]) -> str:
    stabile_kernsaetze, stabile_spannungen, stabile_codefolgen, stabile_offene, stabile_bewegungen, stabile_fragen = _sammle_stabile_dossierpunkte(bloecke)
    stabile_kernsaetze, stabile_spannungen, stabile_codefolgen, stabile_offene = _kanonisiere_stabilen_gesamtstand(
        stabile_kernsaetze,
        stabile_spannungen,
        stabile_codefolgen,
        stabile_offene,
    )

    fokus_bloecke = _waehle_fokus_bloecke(bloecke, max_anzahl=2)
    fokus_kernsaetze, fokus_spannungen, fokus_codefolgen, fokus_offene, fokus_bewegungen, fokus_fragen = _sammle_dossierpunkte(fokus_bloecke)
    fokus_herkuenfte = [_block_herkunft(block) for block in fokus_bloecke]

    was_ist_diese_datei = stabile_kernsaetze[:2] or fokus_kernsaetze[:2]
    letzter_arbeitsbereich = fokus_kernsaetze[:3] or stabile_kernsaetze[:3]
    aktuelle_spannungen = fokus_spannungen[:3] or stabile_spannungen[:3]
    aktuelle_codefolgen = fokus_codefolgen[:3] or stabile_codefolgen[:3]
    letzte_bewegungen = fokus_bewegungen[:3] or stabile_bewegungen[:3]
    letzte_fragen = fokus_fragen[:2] or stabile_fragen[:2]

    teile: list[str] = [
        f"[{_zeitstempel()}] dak+gord-system",
        "",
        "QUELLE:",
        f"DATEI: {datei}",
        "",
        "AGENTDOSSIER:",
        "",
        "STABILER GESAMTSTAND:",
    ]

    teile.extend(_format_liste("WAS IST DIESE DATEI?:", was_ist_diese_datei, "(noch keine stabile Einordnung)"))
    teile.append("")
    teile.extend(_format_liste("KERNAUSSAGEN:", stabile_kernsaetze[:6], "(noch keine Kernsätze)"))
    teile.append("")
    teile.extend(_format_liste("HAUPTSPANNUNGEN:", stabile_spannungen[:5], "(noch keine Hauptspannungen)"))
    teile.append("")
    teile.extend(_format_liste("HAUPT-CODEFOLGEN:", stabile_codefolgen[:5], "(noch keine Haupt-Codefolgen)"))
    teile.append("")
    teile.extend(_format_liste("OFFENE GRUNDFRAGEN:", stabile_offene[:5], "(noch keine offenen Grundfragen)"))
    teile.append("")
    teile.append("AKTUELLER FOKUS:")
    teile.append("FOKUS-HERKUNFTEN:")
    teile.extend(_format_herkunft_liste(fokus_herkuenfte))
    teile.append("")
    teile.extend(_format_liste("LETZTER ARBEITSBEREICH:", letzter_arbeitsbereich, "(noch kein aktueller Fokus)"))
    teile.append("")
    teile.extend(_format_liste("AKTUELLE SPANNUNGEN:", aktuelle_spannungen, "(noch keine aktuellen Spannungen)"))
    teile.append("")
    teile.extend(_format_liste("AKTUELLE CODEFOLGEN:", aktuelle_codefolgen, "(noch keine aktuellen Codefolgen)"))
    teile.append("")
    teile.extend(_format_liste("LETZTE GESPRAECHSBEWEGUNGEN:", letzte_bewegungen, "(noch keine Gesprächsbewegungen)"))
    teile.append("")
    teile.extend(_format_liste("LETZTE FRAGEN VON DANIEL:", letzte_fragen, "(noch keine Fragen gespeichert)"))
    teile.append("")

    return "\n".join(teile).rstrip()
def lese_agentdatei_kurz(pfad: str | Path | None, max_len: int = 4500) -> str:
    if not pfad:
        return ""

    ziel = Path(str(pfad))
    if not ziel.exists() or not ziel.is_file():
        return ""

    try:
        text = ziel.read_text(encoding="utf-8")
    except Exception:
        return ""

    kopf, _ = _split_verlauf_bloecke(text)
    if not kopf:
        return ""

    was_ist = _parse_numbered_section(kopf, "WAS IST DIESE DATEI")[:2]

    kern = _parse_numbered_section(kopf, "KERNAUSSAGEN")[:4]

    haupt_spannungen = _parse_numbered_section(kopf, "HAUPTSPANNUNGEN")[:3]
    if not haupt_spannungen:
        haupt_spannungen = _parse_numbered_section(kopf, "SPANNUNGEN")[:3]

    haupt_codefolgen = _parse_numbered_section(kopf, "HAUPT-CODEFOLGEN")[:3]
    if not haupt_codefolgen:
        haupt_codefolgen = _parse_numbered_section(kopf, "CODEFOLGEN")[:3]

    offene = _parse_numbered_section(kopf, "OFFENE GRUNDFRAGEN")[:3]
    if not offene:
        offene = _parse_numbered_section(kopf, "OFFENE FRAGEN")[:3]

    letzter_arbeitsbereich = _parse_numbered_section(kopf, "LETZTER ARBEITSBEREICH")[:2]
    aktuelle_spannungen = _parse_numbered_section(kopf, "AKTUELLE SPANNUNGEN")[:2]
    aktuelle_codefolgen = _parse_numbered_section(kopf, "AKTUELLE CODEFOLGEN")[:2]
    fragen = _parse_numbered_section(kopf, "LETZTE FRAGEN VON DANIEL")[:2]

    teile: list[str] = [
        "AGENTDOSSIER-KERN:",
        "",
        "GESAMTSTAND:",
    ]
    teile.extend(_format_liste("WAS IST DIESE DATEI?:", was_ist, "(keine Einordnung)"))
    teile.append("")
    teile.extend(_format_liste("KERNAUSSAGEN:", kern, "(keine Kernsätze)"))
    teile.append("")
    teile.extend(_format_liste("HAUPTSPANNUNGEN:", haupt_spannungen, "(keine Hauptspannungen)"))
    teile.append("")
    teile.extend(_format_liste("HAUPT-CODEFOLGEN:", haupt_codefolgen, "(keine Haupt-Codefolgen)"))
    teile.append("")
    teile.extend(_format_liste("OFFENE GRUNDFRAGEN:", offene, "(keine offenen Grundfragen)"))
    teile.append("")
    teile.append("AKTUELLER FOKUS:")
    teile.extend(_format_liste("LETZTER ARBEITSBEREICH:", letzter_arbeitsbereich, "(kein aktueller Fokus)"))
    teile.append("")
    teile.extend(_format_liste("AKTUELLE SPANNUNGEN:", aktuelle_spannungen, "(keine aktuellen Spannungen)"))
    teile.append("")
    teile.extend(_format_liste("AKTUELLE CODEFOLGEN:", aktuelle_codefolgen, "(keine aktuellen Codefolgen)"))
    teile.append("")
    teile.extend(_format_liste("LETZTE FRAGEN VON DANIEL:", fragen, "(keine Fragen gespeichert)"))

    kurz = "\n".join(teile).strip()

    if len(kurz) > max_len:
        return kurz[:max_len] + "\n\n... ABGESCHNITTEN ..."

    return kurz

def _schreibe_datei_mit_dossier(ziel: Path, quelle_datei: str, bloecke: list[str]) -> None:
    ziel.parent.mkdir(parents=True, exist_ok=True)

    kopf = _baue_dossierkopf(quelle_datei, bloecke)

    saubere_bloecke = [block.strip() for block in bloecke if block and block.strip()]

    if saubere_bloecke:
        inhalt = kopf + "\n" + VERLAUF_MARKER + "\n" + "\n---\n".join(saubere_bloecke) + "\n"
    else:
        inhalt = kopf + "\n"

    ziel.write_text(inhalt, encoding="utf-8")

def aktualisiere_agentdatei(
    datei: str | None = None,
    block: str | None = None,
    *,
    quellpfad: str | None = None,
    eintrag: str | None = None,
    bloecke: list[str] | None = None,
    art: str | None = None,
    frage: str | None = None,
    antwort: str | None = None,
    rohauszug: str | None = None,
    verdichtung: str | None = None,
    ziel: str | None = None,
    **kwargs,
) -> str:
    quelle = datei or quellpfad or kwargs.get("quelle")
    if not quelle:
        raise ValueError("aktualisiere_agentdatei braucht einen Quellpfad.")

    zielpfad = quelle_zu_agentdatei(quelle)
    zielpfad.parent.mkdir(parents=True, exist_ok=True)

    if zielpfad.exists():
        alt = zielpfad.read_text(encoding="utf-8")
        _, vorhandene_bloecke = _split_verlauf_bloecke(alt)
    else:
        vorhandene_bloecke = []

    if bloecke:
        neue_bloecke = [str(b).strip() for b in bloecke if b and str(b).strip()]
        vorhandene_bloecke.extend(neue_bloecke)
    else:
        teile = [f"[{_zeitstempel()}] dak+gord-system"]

        herkunft = kwargs.get("herkunft")
        if art:
            teile.append(f"ART: {art}")
        if herkunft:
            teile.append(f"HERKUNFT: {herkunft}")

        teile.append(f"QUELLE: {quelle}")

        if ziel:
            teile.append(f"ZIEL: {ziel}")

        if frage:
            teile.append("FRAGE:")
            teile.append(str(frage).strip())

        haupttext = (antwort or eintrag or block or "").strip()
        if haupttext:
            teile.append("ANTWORT:")
            teile.append(haupttext)

        if rohauszug:
            teile.append("ROHAUSZUG:")
            teile.append(str(rohauszug))

        if verdichtung:
            teile.append("VERDICHTUNG:")
            teile.append(str(verdichtung))

        for k, v in kwargs.items():
            if k in {"quelle", "herkunft"}:
                continue
            if v is None:
                continue
            if isinstance(v, (str, int, float)) and str(v).strip():
                teile.append(f"{str(k).upper()}: {v}")

        vorhandene_bloecke.append("\n".join(teile).strip())

    _schreibe_datei_mit_dossier(zielpfad, quelle, vorhandene_bloecke)
    return str(zielpfad)

def schreibe_antwortspur(*args, **kwargs) -> str:
    datei = kwargs.pop("datei", None) or kwargs.pop("quellpfad", None) or kwargs.pop("quelle", None)
    frage = kwargs.pop("frage", None)
    antwort = kwargs.pop("antwort", None)
    art = kwargs.pop("art", "anschlussantwort")
    herkunft = kwargs.pop("herkunft", "dialog")
    rohauszug = kwargs.pop("rohauszug", None)
    verdichtung = kwargs.pop("verdichtung", None)
    ziel = kwargs.pop("ziel", None)

    if args:
        if datei is None and len(args) >= 1:
            datei = args[0]
        if frage is None and len(args) >= 2:
            frage = args[1]
        if antwort is None and len(args) >= 3:
            antwort = args[2]

    return aktualisiere_agentdatei(
        datei=datei,
        frage=frage,
        antwort=antwort,
        art=art,
        herkunft=herkunft,
        rohauszug=rohauszug,
        verdichtung=verdichtung,
        ziel=ziel,
        **kwargs,
    )

