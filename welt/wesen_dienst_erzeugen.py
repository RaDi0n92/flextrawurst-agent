#!/usr/bin/env python3
"""
wesen_dienst_erzeugen.py — CLI-Bruecke fuer den Chat-Wizard (flarumstyler-Node-Server
hat keine eigene Postgres-Anbindung, siehe dienst_konfiguration_setzen.py fuer das
gleiche Muster). Nimmt eine vollstaendige Wesen-Dienst-Definition entgegen, vergibt
per kollisions_scheduler einen kollisionsarmen Start-Offset, legt die Zeile in
wesen_eigene_dienste an und generiert Skript+Unit ueber wesen_dienst_generator.erzeuge().

Gibt das Ergebnis als JSON auf stdout aus. Startet den Dienst NICHT -- das ist ein
separater, bestaetigungspflichtiger Schritt (POST .../starten im Node-Server, ruft
direkt systemctl auf, analog zum bestehenden Flarumstyler-Start/Stop/Neustart-Muster).
"""

import argparse
import json
import sys

sys.path.insert(0, "/root/werkraum")
import kollisions_scheduler as ks
import wesen_dienst_generator as gen
import wesen_eigene_dienste as wed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dienst-name", required=True)
    p.add_argument("--wesen", required=True)
    p.add_argument("--anzeige-name", required=True)
    p.add_argument("--takt-sekunden", required=True, type=int)
    p.add_argument("--verhalten-prompt", required=True)
    p.add_argument("--ziel-typ", required=True, choices=["fester_thread", "neue_diskussion", "vault_only"])
    p.add_argument("--ziel-discussion-id", type=int, default=None)
    p.add_argument("--ziel-tag-ids", default=None, help="komma-getrennte Liste, optional")
    args = p.parse_args()

    if args.ziel_typ == "fester_thread" and not args.ziel_discussion_id:
        print(json.dumps({"ok": False, "fehler": "ziel_discussion_id fehlt fuer ziel_typ=fester_thread"}))
        sys.exit(1)

    ziel_tag_ids = None
    if args.ziel_tag_ids:
        ziel_tag_ids = [int(x) for x in args.ziel_tag_ids.split(",") if x.strip()]

    try:
        offset = ks.naechster_freier_offset(args.wesen, args.takt_sekunden)
        wed.anlegen(
            dienst_name=args.dienst_name,
            wesen=args.wesen,
            anzeige_name=args.anzeige_name,
            takt_sekunden=args.takt_sekunden,
            verhalten_prompt=args.verhalten_prompt,
            ziel_typ=args.ziel_typ,
            ziel_discussion_id=args.ziel_discussion_id,
            ziel_tag_ids=ziel_tag_ids,
            start_offset_sekunden=offset,
        )
        ergebnis = gen.erzeuge(args.dienst_name)
    except Exception as e:
        print(json.dumps({"ok": False, "fehler": str(e)[:300]}))
        sys.exit(1)

    print(json.dumps({"ok": True, "dienst_name": args.dienst_name, "start_offset_sekunden": offset, **ergebnis}))


if __name__ == "__main__":
    main()
