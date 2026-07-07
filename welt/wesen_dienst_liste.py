#!/usr/bin/env python3
"""
wesen_dienst_liste.py — gibt alle Wesen-Dienste als JSON aus (fuer flarumstyler
Verlauf-Tab + das Verkettung-Dropdown im Wizard). Reiner Read-Only-CLI nach
demselben Muster wie die uebrigen wesen_dienst_*.py-Bruecken -- der Node-Server
hat keine eigene Postgres-Anbindung.
"""

import json
import sys

sys.path.insert(0, "/root/werkraum")
import wesen_eigene_dienste as wed


def main():
    dienste = wed.lade_alle(nur_aktive=False)
    for d in dienste:
        for feld in ("id", "created_at", "updated_at"):
            if d.get(feld) is not None:
                d[feld] = str(d[feld])
    print(json.dumps(dienste, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
