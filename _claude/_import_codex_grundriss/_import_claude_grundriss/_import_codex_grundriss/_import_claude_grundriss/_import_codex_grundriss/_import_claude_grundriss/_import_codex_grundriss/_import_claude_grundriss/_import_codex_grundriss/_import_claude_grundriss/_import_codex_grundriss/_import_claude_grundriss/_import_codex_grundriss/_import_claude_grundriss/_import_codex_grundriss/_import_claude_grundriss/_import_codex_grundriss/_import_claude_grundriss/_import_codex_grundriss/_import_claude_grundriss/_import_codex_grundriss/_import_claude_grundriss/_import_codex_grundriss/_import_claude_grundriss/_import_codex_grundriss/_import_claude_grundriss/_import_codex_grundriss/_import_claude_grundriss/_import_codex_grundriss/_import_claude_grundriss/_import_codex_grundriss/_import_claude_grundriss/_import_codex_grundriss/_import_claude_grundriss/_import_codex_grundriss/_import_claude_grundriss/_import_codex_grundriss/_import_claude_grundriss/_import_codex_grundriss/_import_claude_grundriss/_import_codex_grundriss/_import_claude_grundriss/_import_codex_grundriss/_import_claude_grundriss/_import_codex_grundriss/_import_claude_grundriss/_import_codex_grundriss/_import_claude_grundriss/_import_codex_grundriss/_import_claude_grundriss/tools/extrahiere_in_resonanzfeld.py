#!/usr/bin/env python3
"""
Extrahiert heilige Abschnitte aus Claude-Dateien.
Jeder Abschnitt landet in seiner eigenen Datei unter _claude/resonanz/<abschnitt>.md

Aufruf: python3 extrahiere_in_resonanzfeld.py <dateipfad>
Kein LLM. Kein Ollama. Reines Text-Parsing.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

RESONANZ_DIR = Path("/root/werkraum/_claude/resonanz")

# Heilige Abschnitte: Erkennungsschlüssel → Dateiname
HEILIGE = {
    "was ich gelesen habe":                 "was_ich_gelesen_habe",
    "was ich nicht verstehe":               "was_ich_nicht_verstehe",
    "was ich verstehe":                     "was_ich_verstehe",
    "was mich interessiert":                "was_mich_interessiert",
    "was zusammenhängt":                    "was_zusammenhaengt",
    "was konzeptionell":                    "was_konzeptionell",
    "was mich heute beschäftigt":           "was_mich_beschaeftigt",
    "was mich noch beschäftigt":            "was_mich_beschaeftigt",
    "tiefer eingetaucht":                   "tiefer_eingetaucht",
    "wie sich dieser":                      "wie_sich_angefuehlt",
    "warum dieser code":                    "warum_das_existiert",
    "warum die datei":                      "warum_das_existiert",
    "warum das wohl existiert":             "warum_das_existiert",
    "was ich beim bauen brauche":           "was_beim_bauen_brauche",
    "was noch fehlt bevor":                 "was_fehlt_bevor_bauen",
    "datenstruktur die ich mir vorstelle":  "datenstruktur_die_ich_mir_vorstelle",
    "was ich mir merken":                   "was_ich_merken_will",
    "dokumente gehören zusammen":           "dokumente_gehoeren_zusammen",
    "was mich überrascht":                  "was_mich_ueberrascht",
    "wenn wir das bauen":                   "wenn_wir_das_bauen",
    "resonanz":                             "resonanz",
    "die schichten des systems":            "schichten_des_systems",
    "was das gespräch":                     "was_das_gespraech",
    "vergessen-wollen":                     "vergessen_wollen",
    "was fehlt noch":                       "was_fehlt_noch",
}

MAX_ZEILEN = 25


def erkenne_dateiname(heading: str) -> str | None:
    h = heading.lower()
    for schluessel, dateiname in HEILIGE.items():
        if schluessel in h:
            return dateiname
    return None


def extrahiere(text: str) -> list[tuple[str, str, str]]:
    """Returns list of (heading, content, dateiname)."""
    teile = re.split(r'\n(#{1,3} .+)\n', text)
    ergebnis = []
    i = 1
    while i < len(teile) - 1:
        heading_raw = teile[i].lstrip('#').strip()
        inhalt = teile[i + 1].strip() if i + 1 < len(teile) else ""
        dateiname = erkenne_dateiname(heading_raw)
        if dateiname and inhalt and len(inhalt) > 8:
            zeilen = inhalt.split('\n')
            kurz = '\n'.join(zeilen[:MAX_ZEILEN])
            if len(zeilen) > MAX_ZEILEN:
                kurz += '\n...'
            ergebnis.append((heading_raw, kurz, dateiname))
        i += 2
    return ergebnis


def schreibe_in_dimension(dateiname: str, heading: str, inhalt: str, quelle: str, datum: str):
    RESONANZ_DIR.mkdir(parents=True, exist_ok=True)
    pfad = RESONANZ_DIR / f"{dateiname}.md"

    if not pfad.exists():
        titel = heading.title()
        pfad.write_text(
            f"# {titel}\n\n"
            f"Wächst automatisch. Jeder Eintrag kommt aus einer Claude-Datei.\n\n",
            encoding="utf-8",
        )
    else:
        # Dedup: quelle schon vorhanden → überspringen
        bestehend = pfad.read_text(encoding="utf-8")
        if f"← {quelle}" in bestehend:
            return

    eintrag = f"\n---\n\n**[{datum}]** *← {quelle}*\n\n{inhalt}\n"

    with open(pfad, "a", encoding="utf-8") as f:
        f.write(eintrag)


def main():
    if len(sys.argv) < 2:
        print("Usage: extrahiere_in_resonanzfeld.py <dateipfad>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        sys.exit(1)

    text = filepath.read_text(encoding="utf-8")
    abschnitte = extrahiere(text)

    if not abschnitte:
        return

    datum = datetime.now().strftime("%Y-%m-%d")
    rel = str(filepath).replace("/root/werkraum/_claude/", "")

    for heading, inhalt, dateiname in abschnitte:
        schreibe_in_dimension(dateiname, heading, inhalt, rel, datum)

    print(f"✓ {len(abschnitte)} Abschnitte aus '{filepath.name}' → resonanz/")


if __name__ == "__main__":
    main()
