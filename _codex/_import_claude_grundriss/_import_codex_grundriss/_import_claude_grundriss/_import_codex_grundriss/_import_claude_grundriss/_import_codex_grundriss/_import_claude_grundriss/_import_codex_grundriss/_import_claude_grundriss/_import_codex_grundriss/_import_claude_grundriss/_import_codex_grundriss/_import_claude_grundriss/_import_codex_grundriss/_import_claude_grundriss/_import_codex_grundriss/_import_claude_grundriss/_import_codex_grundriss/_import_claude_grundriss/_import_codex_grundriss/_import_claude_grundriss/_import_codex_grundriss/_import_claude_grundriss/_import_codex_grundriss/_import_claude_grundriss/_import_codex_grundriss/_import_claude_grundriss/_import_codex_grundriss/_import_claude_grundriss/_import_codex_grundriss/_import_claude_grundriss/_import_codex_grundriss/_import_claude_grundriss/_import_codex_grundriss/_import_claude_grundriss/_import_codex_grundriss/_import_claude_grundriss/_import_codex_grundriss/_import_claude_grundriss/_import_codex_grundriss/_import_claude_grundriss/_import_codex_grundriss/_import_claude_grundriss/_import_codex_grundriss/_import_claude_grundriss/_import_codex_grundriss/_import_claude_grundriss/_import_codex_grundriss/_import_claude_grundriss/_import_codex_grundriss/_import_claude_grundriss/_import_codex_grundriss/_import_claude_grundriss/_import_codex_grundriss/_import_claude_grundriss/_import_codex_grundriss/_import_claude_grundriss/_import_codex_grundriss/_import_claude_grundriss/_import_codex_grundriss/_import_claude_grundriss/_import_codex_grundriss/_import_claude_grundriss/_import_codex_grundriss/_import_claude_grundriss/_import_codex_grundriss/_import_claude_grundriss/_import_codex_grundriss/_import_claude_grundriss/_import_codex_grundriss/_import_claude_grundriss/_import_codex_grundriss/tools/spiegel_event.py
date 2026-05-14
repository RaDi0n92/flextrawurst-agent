#!/usr/bin/env python3
"""
Spiegel als Event: schreibt eine neue Spiegel-Datei als Event in den Weltstream.
Aufruf: spiegel_event.py <pfad-zur-spiegel-datei>
"""
import sys
import json
import subprocess
import datetime
import os

DB = "postgresql://dak:dakpass@localhost:5432/flextrawurst"


def main():
    if len(sys.argv) < 2:
        print("Nutzung: spiegel_event.py <spiegel-datei.md>")
        sys.exit(1)

    datei = os.path.abspath(sys.argv[1])
    if not os.path.exists(datei):
        print(f"Datei nicht gefunden: {datei}")
        sys.exit(1)

    with open(datei) as f:
        inhalt = f.read()

    titel = os.path.basename(datei).replace(".md", "")
    erste_zeile = next(
        (l.lstrip("#").strip() for l in inhalt.split("\n") if l.strip() and not l.startswith("---")),
        ""
    )

    payload = json.dumps({
        "datei": datei,
        "titel": titel,
        "erste_zeile": erste_zeile[:200],
        "zeichen": len(inhalt)
    }, ensure_ascii=False)

    sql = """
INSERT INTO events (event_type, actor_type, actor_id, payload, origin_type, visibility_layer)
VALUES ('codex.spiegel', 'codex', 'codex_hauptinstanz', %s, 'obsidian_import', 'internal');
"""

    result = subprocess.run(
        ["psql", DB, "-c", sql % f"'{payload.replace(chr(39), chr(39)+chr(39))}'"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"Event: codex.spiegel / {titel}")
    else:
        print(f"DB-Fehler: {result.stderr.strip()}")


if __name__ == "__main__":
    main()
