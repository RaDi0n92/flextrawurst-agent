#!/usr/bin/env python3
"""
wesen_dienst_ausloesen.py — manueller Trigger fuer einen Wesen-Dienst im
Passiv-Modus (siehe wesen_dienst_generator.py:_passiv_schleife). Ein Passiv-Dienst
laeuft dauerhaft als systemd-Prozess, fuehrt aber KEINEN automatischen Takt aus --
er wartet auf genau diese Flag-Datei und loescht sie selbst wieder, sobald ein
Zyklus ausgeloest wurde (Poll-Intervall 5s).

Schreibt nur eine Datei, fasst sonst nichts an -- kein systemctl-Aufruf noetig.
"""

import argparse
import json
import sys

sys.path.insert(0, "/root/werkraum")
import codewesen_agent as ca
import wesen_eigene_dienste as wed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dienst-name", required=True)
    args = p.parse_args()

    row = wed.lade(args.dienst_name)
    if not row:
        print(json.dumps({"ok": False, "fehler": "Dienst nicht gefunden"}))
        sys.exit(1)

    flag = ca.BASE / row["wesen"] / "eigene_dienste" / args.dienst_name / "ausloesen.flag"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.touch()
    print(json.dumps({"ok": True, "dienst_name": args.dienst_name}))


if __name__ == "__main__":
    main()
