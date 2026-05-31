#!/usr/bin/env python3
"""
Handlungsgrammatik Dry-Run
Zeigt welche Grammatik bei welcher Entscheidung geladen würde.
Schreibt KEINE Weltzustände. Führt KEINE echten Entscheidungen aus.

Nutzung:
  python3 dryrun.py                     # alle Entscheidungen
  python3 dryrun.py gedanke_posten      # spezifische Entscheidung
  python3 dryrun.py --json              # JSON-Ausgabe
"""

import sys
import json
import pathlib

HG_DIR = pathlib.Path(__file__).parent

AKTION_ZU_GRAMMATIK = {
    "gedanke_posten":              "wesen_entscheidung_posten.md",
    "schlafen_beginnen":           "wesen_entscheidung_schlaf.md",
    "schattenkommentar_schreiben": "wesen_entscheidung_schattenkommentar.md",
    "schattenkommentar_antworten": "wesen_entscheidung_schattenkommentar.md",
    "splitter_aufsammeln":         "wesen_entscheidung_zwischenraum.md",
    "nachdenken":                  "wesen_entscheidung_schweigen.md",
    "cyberling_fuettern":          "wesen_entscheidung_cyberling.md",
    "traum_verarbeiten":           "wesen_entscheidung_traum.md",
    "selbstbrief_schreiben":       "wesen_entscheidung_selbstbrief.md",
    "substanz_nehmen":             "wesen_entscheidung_substanzen.md",
    "resonanz_beantworten":        "wesen_entscheidung_resonanz.md",
    "beziehung_pflegen":           "wesen_entscheidung_beziehungen.md",
}

RELEVANTE_ABSCHNITTE = [
    "## Was bedeutet meine Entscheidung",
    "## Wann ",
    "## Wann antworte ich",
    "## Welche Folgen",
    "## Was kann ich tun",
]


def lade_grammatik(dateiname: str) -> str:
    p = HG_DIR / dateiname
    return p.read_text(encoding="utf-8") if p.exists() else ""


def extrahiere_kern(md: str) -> list[str]:
    zeilen = md.splitlines()
    result, aktiv = [], False
    for z in zeilen:
        if any(z.startswith(h) for h in RELEVANTE_ABSCHNITTE):
            aktiv = True
        elif z.startswith("## ") and aktiv:
            aktiv = False
        if aktiv:
            result.append(z)
    return result[:25]


def schaetze_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def dryrun_aktion(aktion: str) -> dict:
    datei = AKTION_ZU_GRAMMATIK.get(aktion)
    if not datei:
        return {
            "aktion": aktion,
            "status": "UNBEKANNT",
            "datei": None,
            "datei_existiert": False,
            "token_schaetzung": 0,
            "kern_vorschau": [],
            "fallback": "nachdenken",
        }

    pfad = HG_DIR / datei
    existiert = pfad.exists()
    inhalt = lade_grammatik(datei) if existiert else ""
    kern = extrahiere_kern(inhalt) if inhalt else []

    return {
        "aktion": aktion,
        "status": "BEREIT" if existiert else "DATEI_FEHLT",
        "datei": datei,
        "datei_pfad": str(pfad),
        "datei_existiert": existiert,
        "token_schaetzung": schaetze_tokens("\n".join(kern)),
        "volltext_tokens": schaetze_tokens(inhalt),
        "kern_zeilen": len(kern),
        "kern_vorschau": kern[:8],
        "fallback": "leer gelassen" if not existiert else None,
    }


def run():
    als_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    aktionen = list(AKTION_ZU_GRAMMATIK.keys()) if not args else args
    results = [dryrun_aktion(a) for a in aktionen]

    if als_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("\n=== HANDLUNGSGRAMMATIK DRY-RUN ===")
    print("Kein Produktivcode. Keine Weltzustände.\n")

    gesamt_token = 0
    for r in results:
        sym = "✓" if r["datei_existiert"] else "✗"
        print(f"  {sym} {r['aktion']:<35} → {r['datei'] or 'KEIN MAPPING'}")
        print(f"     Kern: {r['kern_zeilen']} Zeilen ≈ {r['token_schaetzung']} Token (Volltext: {r['volltext_tokens']})")
        if r["kern_vorschau"]:
            first = next((z for z in r["kern_vorschau"] if z.strip()), "")
            if first:
                print(f"     Vorschau: {first[:80]}")
        gesamt_token += r["token_schaetzung"]
        print()

    print(f"Gesamt Kern-Token (alle Grammatiken gleichzeitig): ~{gesamt_token}")
    print(f"Empfehlung: Maximal 3-4 Grammatiken gleichzeitig (≈ {gesamt_token // len(results) * 4} Token)")
    print()
    missing = [r["aktion"] for r in results if not r["datei_existiert"]]
    if missing:
        print(f"FEHLEND: {', '.join(missing)}")
    else:
        print("Alle Mappings vorhanden. ✓")


if __name__ == "__main__":
    run()
