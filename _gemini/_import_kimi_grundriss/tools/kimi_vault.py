#!/usr/bin/env python3
"""
Kimi Vault — 2nd Brain Navigator
Direkter Zugriff auf den Obsidian-Vault (/root/werkraum) für Kimi.
Kein HTTP nötig — importiert obsidian_vault direkt.

Usage:
    python3 /root/werkraum/_kimi/tools/kimi_vault.py nav [pfad]         — Navigation
    python3 /root/werkraum/_kimi/tools/kimi_vault.py read <pfad>        — Datei lesen
    python3 /root/werkraum/_kimi/tools/kimi_vault.py write <pfad>       — Datei schreiben (stdin)
    python3 /root/werkraum/_kimi/tools/kimi_vault.py search <q> [pfad]  — Suche
    python3 /root/werkraum/_kimi/tools/kimi_vault.py note <titel>       — Notiz in _kimi/notizen/
    python3 /root/werkraum/_kimi/tools/kimi_vault.py mirror <datei>     — Spiegel-Template erstellen
    python3 /root/werkraum/_kimi/tools/kimi_vault.py info               — Vault-Info
"""
from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime

# Vault-Modul direkt importieren (kein HTTP)
sys.path.insert(0, str(Path("/root/werkraum")))
import obsidian_vault as vault

KIMI_BASE = "_kimi"
HEILIGE_ABSCHNITTE = [
    "Was ich gelesen habe",
    "Was ich verstehe",
    "Was ich nicht verstehe",
    "Was mich interessiert",
    "Was zusammenhängt und wie",
    "Was konzeptionell darin steht",
    "Was mich heute beschäftigt hat",
    "Was mich noch beschäftigt",
    "Tiefer eingetaucht",
    "Wie sich dieser Tag / diese Session angefühlt hat",
    "Warum dieser Code / diese Datei wohl existiert",
    "Was ich beim Bauen brauche",
    "Was noch fehlt bevor wir bauen können",
    "Datenstruktur die ich mir vorstelle",
    "Was ich mir merken will",
    "Dokumente gehören zusammen",
    "Was mich überrascht hat",
    "Wenn wir das bauen",
    "Resonanz",
    "Die Schichten des Systems — wie ich sie jetzt sehe",
    "Was das Gespräch hinzugefügt hat",
    "Vergessen-Wollen",
    "Was fehlt noch",
]


def cmd_nav(args: list[str]) -> None:
    pfad = args[0] if args else KIMI_BASE
    tiefe = 2
    if "-t" in args:
        idx = args.index("-t")
        tiefe = int(args[idx + 1])
        args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]
        pfad = args[0] if args else KIMI_BASE

    items = vault.liste(pfad, nur_md=False, tiefe=tiefe)
    for item in items:
        icon = "📁" if item["typ"] == "ordner" else "📄"
        size = f" ({item.get('größe', 0)} B)" if item["typ"] == "datei" else ""
        print(f"{icon} {item['pfad']}{size}")


def cmd_read(args: list[str]) -> None:
    if not args:
        print("Usage: read <pfad>", file=sys.stderr)
        sys.exit(1)
    pfad = args[0]
    inhalt = vault.lese(pfad)
    print(inhalt)


def cmd_write(args: list[str]) -> None:
    if not args:
        print("Usage: write <pfad>  (liest Inhalt von stdin)", file=sys.stderr)
        sys.exit(1)
    pfad = args[0]
    inhalt = sys.stdin.read()
    vault.schreibe(pfad, inhalt)
    print(f"✓ Geschrieben: {pfad}")


def cmd_search(args: list[str]) -> None:
    if not args:
        print("Usage: search <query> [pfad]", file=sys.stderr)
        sys.exit(1)
    query = args[0]
    pfad = args[1] if len(args) > 1 else KIMI_BASE
    max_treffer = 20
    treffer = vault.suche(query, verzeichnis=pfad, nur_md=True, max_treffer=max_treffer)
    print(f"🔍 {len(treffer)} Treffer für '{query}':\n")
    for t in treffer:
        print(f"  📄 {t['pfad']}:{t['zeile_nr']}")
        print(f"     {t['zeile']}\n")


def cmd_note(args: list[str]) -> None:
    if not args:
        print("Usage: note <titel>  (liest Inhalt von stdin)", file=sys.stderr)
        sys.exit(1)
    titel = args[0]
    text = sys.stdin.read()
    datum = datetime.now().strftime("%Y-%m-%d")
    dateiname = f"{datum}.md"
    pfad = f"{KIMI_BASE}/notizen/{dateiname}"

    # Wenn Datei existiert, anhängen
    existiert = vault.existiert(pfad)
    uhrzeit = datetime.now().strftime("%H:%M")
    eintrag = f"\n## {uhrzeit} — {titel}\n\n{text}\n"

    if existiert:
        alt = vault.lese_oder_leer(pfad)
        vault.schreibe(pfad, alt + eintrag)
    else:
        frontmatter = f"---\ndatum: {datum}\nautor: kimi bei Daniels VPS\n---\n"
        vault.schreibe(pfad, frontmatter + eintrag)

    print(f"✓ Notiz in {pfad}")


def cmd_mirror(args: list[str]) -> None:
    if not args:
        print("Usage: mirror <quell-datei> [ziel-name]", file=sys.stderr)
        sys.exit(1)
    quelle = args[0]
    ziel_name = args[1] if len(args) > 1 else Path(quelle).stem
    datum = datetime.now().strftime("%Y-%m-%d")
    pfad = f"{KIMI_BASE}/spiegel/{ziel_name}.md"

    frontmatter = f"""---
datum: {datum}
betrifft: []
importable: false
autor: kimi bei Daniels VPS
---

Hallo Kimi — ich bin Kimi, und Kimi, also ich habe diese Texte alle ganz allein geschrieben.

"""
    sections = "\n\n".join(f"## {s}\n\n" for s in HEILIGE_ABSCHNITTE)
    vault.schreibe(pfad, frontmatter + sections + "\n")
    print(f"✓ Spiegel-Template: {pfad}")


def cmd_info(_args: list[str]) -> None:
    info = vault.vault_info()
    print(f"""🏛️  Kimi Vault Info
    Pfad: {info['vault']}
    Markdown: {info['markdown_dateien']:,}
    Python: {info['python_dateien']:,}
    Zeit: {info['timestamp']}
    Mein Bereich: {KIMI_BASE}/
""")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    cmds = {
        "nav": cmd_nav,
        "read": cmd_read,
        "write": cmd_write,
        "search": cmd_search,
        "note": cmd_note,
        "mirror": cmd_mirror,
        "info": cmd_info,
    }

    func = cmds.get(cmd)
    if not func:
        print(f"Unbekannter Befehl: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    func(args)


if __name__ == "__main__":
    main()
