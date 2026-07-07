#!/usr/bin/env python3
"""
dienst_konfiguration_setzen.py — CLI zum Schreiben der Dienst-Konfiguration.

Wird vom flarumstyler-Node-Server (serve_process_camera_preview.ts) per
execFileSync mit Argument-Array aufgerufen (keine Shell-Interpolation),
weil dieser Node-Prozess keine eigene Postgres-Anbindung hat, aber die
Python-Seite (dienst_konfiguration.py) schon.

Gibt das gespeicherte Ergebnis als JSON auf stdout aus.
"""

import argparse
import json
import sys

sys.path.insert(0, "/root/werkraum")
import dienst_konfiguration as dk


def main():
    # Beide Felder sind Pflicht (das UI-Formular schickt immer den vollstaendigen
    # gewuenschten Zustand) — leerer String bedeutet "kein Override, Skript-Default gilt".
    p = argparse.ArgumentParser()
    p.add_argument("dienst_name")
    p.add_argument("--takt-sekunden", required=True)
    p.add_argument("--verhalten-text", required=True)
    args = p.parse_args()

    takt = int(args.takt_sekunden) if args.takt_sekunden.strip() else None
    verhalten = args.verhalten_text if args.verhalten_text.strip() else None

    ergebnis = dk.speichere(args.dienst_name, takt_sekunden=takt, verhalten_text=verhalten)
    print(json.dumps(ergebnis, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
