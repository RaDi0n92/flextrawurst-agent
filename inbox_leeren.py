#!/usr/bin/env python3
"""
Inbox aller Wesen sicher leeren — archiviert Items vor dem Entfernen.
Aufruf: python3 inbox_leeren.py [grund]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from codewesen_reaktion import inbox_archivieren_und_leeren, CODEWESEN

grund = sys.argv[1] if len(sys.argv) > 1 else "manuell"

gesamt = 0
for name in CODEWESEN:
    n = inbox_archivieren_und_leeren(name, grund)
    print(f"  {name}: {n} Items → archiv/{grund}")
    gesamt += n

print(f"\n{gesamt} Items archiviert (nicht gelöscht). Archiv: codewesen/<name>/archiv/")
