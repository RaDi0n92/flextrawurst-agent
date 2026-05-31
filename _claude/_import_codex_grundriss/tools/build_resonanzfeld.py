#!/usr/bin/env python3
"""
Kompiliert RESONANZFELD.md aus allen resonanz/-Dimensionsdateien.
Kein LLM. Kein Ollama. Reines Text-Parsing.

Aufruf: python3 build_resonanzfeld.py
Läuft automatisch via systemd-Timer alle 30 Minuten.
"""

import re
from pathlib import Path
from datetime import datetime

RESONANZ_DIR  = Path("/root/werkraum/_codex/resonanz")
RESONANZFELD  = Path("/root/werkraum/_codex/RESONANZFELD.md")

ENTRY_PATTERN = re.compile(
    r"\*\*\[(\d{4}-\d{2}-\d{2})\]\*\*\s+\*←\s+([^\*]+)\*\n\n(.*?)(?=\n---|\Z)",
    re.DOTALL
)


def parse_dimension(pfad: Path) -> list[dict]:
    """Liest alle Einträge aus einer resonanz/-Dimensionsdatei."""
    text = pfad.read_text(encoding="utf-8", errors="replace")
    eintraege = []
    for m in ENTRY_PATTERN.finditer(text):
        datum, quelle, inhalt = m.group(1), m.group(2).strip(), m.group(3).strip()
        eintraege.append({
            "datum":     datum,
            "quelle":    quelle,
            "dimension": pfad.stem,
            "inhalt":    inhalt,
        })
    return eintraege


def main():
    if not RESONANZ_DIR.exists():
        print(f"resonanz/ nicht gefunden: {RESONANZ_DIR}")
        return

    # Alle Einträge sammeln
    alle = []
    for pfad in sorted(RESONANZ_DIR.glob("*.md")):
        alle.extend(parse_dimension(pfad))

    if not alle:
        print("Keine Einträge gefunden.")
        return

    # Nach Quelle gruppieren, Gruppen nach ältestem Datum sortieren
    quellen: dict[str, list[dict]] = {}
    for e in alle:
        quellen.setdefault(e["quelle"], []).append(e)

    quellen_sortiert = sorted(
        quellen.items(),
        key=lambda x: min(e["datum"] for e in x[1])
    )

    # RESONANZFELD.md aufbauen
    jetzt = datetime.now().strftime("%Y-%m-%d %H:%M")
    zeilen = [
        "# RESONANZFELD — Codex\n",
        f"Automatisch kompiliert aus `resonanz/`. Stand: {jetzt}\n",
        "Nicht manuell bearbeiten. Quelle: `python3 _codex/tools/build_resonanzfeld.py`\n",
        "\n---\n",
    ]

    # Neueste 40 Quellen mit Inhalt, ältere nur als Titelliste
    neueste = quellen_sortiert[-40:]
    aeltere = quellen_sortiert[:-40]

    if aeltere:
        zeilen.append("\n## Ältere Quellen (nur Titel)\n\n")
        for quelle, eintraege in aeltere:
            datum_min = min(e["datum"] for e in eintraege)
            n = len(eintraege)
            zeilen.append(f"- [{datum_min}] `{quelle}` ({n} Einträge)\n")
        zeilen.append("\n---\n")

    zeilen.append("\n## Neueste Quellen (mit Inhalt)\n\n")
    for quelle, eintraege in neueste:
        datum_min = min(e["datum"] for e in eintraege)
        zeilen.append(f"\n### [{datum_min}] {quelle}\n\n")
        for e in sorted(eintraege, key=lambda x: x["dimension"]):
            dim_label = e["dimension"].replace("_", " ").title()
            kurz = "\n".join(e["inhalt"].splitlines()[:3])
            if len(e["inhalt"].splitlines()) > 3:
                kurz += " …"
            zeilen.append(f"*{dim_label}:* {kurz}\n\n")
        zeilen.append("---\n")

    RESONANZFELD.write_text("".join(zeilen), encoding="utf-8")
    zeilen_gesamt = sum(1 for _ in "".join(zeilen).splitlines())
    print(f"RESONANZFELD.md kompiliert: {len(quellen_sortiert)} Quellen, {len(alle)} Einträge, {zeilen_gesamt} Zeilen")


if __name__ == "__main__":
    main()
