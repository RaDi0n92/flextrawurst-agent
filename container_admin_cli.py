#!/usr/bin/env python3
"""
container_admin_cli.py — CLI-Bruecke fuer flarumstyler (Node-Server ruft Python-
Container-Logik nicht direkt auf, siehe wesen_dienst_deaktivieren.py fuer dasselbe
Muster). Baustein 25 (2026-07-10, Container-Provenienz-Design): erlaubt Daniel,
direkt (als 'dak', sichtbar markiert, oder 'admin_still', unmarkiert) in die
echten Container eines Wesens zu schreiben oder daraus zu entfernen -- niemals vom
Wesen selbst auslösbar, immer ueber flarum_stopp_protokoll protokolliert.

Text kommt bei 'schreibe' bewusst ueber stdin (nicht argv) -- beliebig lang,
keine Shell-Escaping-Sorgen.
"""

import argparse
import json
import sys

sys.path.insert(0, "/root/werkraum")
import codewesen_container as container


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="aktion", required=True)

    schreibe_p = sub.add_parser("schreibe")
    schreibe_p.add_argument("wesen")
    schreibe_p.add_argument("container")
    schreibe_p.add_argument("quelle", choices=["dak", "admin_still"])

    entferne_p = sub.add_parser("entferne")
    entferne_p.add_argument("wesen")
    entferne_p.add_argument("container")
    entferne_p.add_argument("dateiname")

    args = p.parse_args()

    try:
        if args.aktion == "schreibe":
            text = sys.stdin.read().strip()
            if not text:
                raise ValueError("leerer Text")
            container.admin_schreibe(args.wesen, args.container, text, quelle=args.quelle)
            print(json.dumps({"ok": True}))
        else:
            ok = container.admin_entferne(args.wesen, args.container, args.dateiname)
            if not ok:
                print(json.dumps({"ok": False, "fehler": "nicht_gefunden"}))
                sys.exit(1)
            print(json.dumps({"ok": True}))
    except Exception as e:
        print(json.dumps({"ok": False, "fehler": str(e)[:300]}))
        sys.exit(1)


if __name__ == "__main__":
    main()
