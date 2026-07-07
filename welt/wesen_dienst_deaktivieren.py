#!/usr/bin/env python3
"""
wesen_dienst_deaktivieren.py — CLI-Bruecke fuer flarumstyler (Node-Server hat keine
eigene Postgres-Anbindung, siehe wesen_dienst_erzeugen.py fuer dasselbe Muster).
Ruft wesen_dienst_generator.deaktivieren(): stoppt+disabled den systemd-Dienst und
setzt status='deaktiviert' in wesen_eigene_dienste (Grundgesetz 4 -- nie hart loeschen,
Skript/Unit-Dateien bleiben liegen).
"""

import argparse
import json
import sys

sys.path.insert(0, "/root/werkraum")
import wesen_dienst_generator as gen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dienst_name")
    args = p.parse_args()

    try:
        gen.deaktivieren(args.dienst_name)
    except Exception as e:
        print(json.dumps({"ok": False, "fehler": str(e)[:300]}))
        sys.exit(1)

    print(json.dumps({"ok": True, "dienst_name": args.dienst_name}))


if __name__ == "__main__":
    main()
