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
    # takt-sekunden/verhalten-text sind Pflicht (das UI-Formular schickt immer den
    # vollstaendigen gewuenschten Zustand fuer diese zwei) — leerer String bedeutet
    # "kein Override, Skript-Default gilt". --meta ist optional: nicht angegeben =
    # bestehendes meta bleibt unangetastet (fuer Dienste wie codewesen-takt, die
    # mehrere benannte Werte statt einem einzigen Takt brauchen, siehe meta.intervalle).
    p = argparse.ArgumentParser()
    p.add_argument("dienst_name")
    p.add_argument("--takt-sekunden", required=True)
    p.add_argument("--verhalten-text", required=True)
    p.add_argument("--beschreibung", required=True)
    p.add_argument("--meta", default=None)
    args = p.parse_args()

    takt = int(args.takt_sekunden) if args.takt_sekunden.strip() else None
    verhalten = args.verhalten_text if args.verhalten_text.strip() else None
    beschreibung = args.beschreibung if args.beschreibung.strip() else None
    meta = None
    if args.meta is not None and args.meta.strip():
        try:
            meta = json.loads(args.meta)
        except Exception as e:
            print(json.dumps({"ok": False, "fehler": f"meta ist kein gueltiges JSON: {e}"}, ensure_ascii=False))
            sys.exit(1)

    ergebnis = dk.speichere(args.dienst_name, takt_sekunden=takt, verhalten_text=verhalten, meta=meta, beschreibung_override=beschreibung)
    print(json.dumps(ergebnis, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
