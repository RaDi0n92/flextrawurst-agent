#!/usr/bin/env python3
"""
wesen_dienst_ausloesen.py — manueller Trigger fuer einen Wesen-Dienst, unabhaengig
vom Zeitplan-Modus (Phase 2, siehe wesen_dienst_generator.py:_pruefe_ausloeser --
vorher nur im Passiv-Modus verdrahtet, jetzt bei ALLEN Modi aktiv, weil Verkettung
sonst gegen einen Intervall-/Feste-Uhrzeiten-Dienst nie gefeuert haette). Der
laufende Dienst-Prozess wartet auf genau diese Flag-Datei und loescht sie selbst
wieder, sobald ein Zyklus ausgeloest wurde (Poll-Intervall 5-30s je nach Modus).

--trockenlauf schreibt den Flag-Inhalt {"trockenlauf": true} -- der Dienst fuehrt
dann dieselbe Entscheidungslogik aus, postet aber nichts wirklich (siehe Konzept:
Trockenlauf-Modus). Schreibt nur eine Datei, fasst sonst nichts an -- kein
systemctl-Aufruf noetig.
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
    p.add_argument("--trockenlauf", action="store_true", help="Nur simulieren, nicht wirklich posten")
    args = p.parse_args()

    row = wed.lade(args.dienst_name)
    if not row:
        print(json.dumps({"ok": False, "fehler": "Dienst nicht gefunden"}))
        sys.exit(1)

    flag = ca.BASE / row["wesen"] / "eigene_dienste" / args.dienst_name / "ausloesen.flag"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(json.dumps({"trockenlauf": args.trockenlauf}), encoding="utf-8")
    print(json.dumps({"ok": True, "dienst_name": args.dienst_name, "trockenlauf": args.trockenlauf}))


if __name__ == "__main__":
    main()
