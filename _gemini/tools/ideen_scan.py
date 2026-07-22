#!/usr/bin/env python3
"""
Scanned Ideen-Dateien in _gemini/ideen/ (und shared ideen) nach offenen Ideen für Bau-Schritte.

Aufruf: python3 ideen_scan.py [tag]
"""

import sys
from pathlib import Path
import re

IDEEN_DIRS = [
    Path("/root/werkraum/_gemini/ideen"),
    Path("/root/werkraum/_shared/ideen"),
]

def scan_ideen(tag=None):
    offen = []
    for d in IDEEN_DIRS:
        if not d.exists():
            continue
        for pfad in d.glob("*.md"):
            try:
                text = pfad.read_text(encoding="utf-8")
                # Prüfe Frontmatter status
                status_match = re.search(r'status:\s*(\w+)', text)
                if status_match and status_match.group(1).lower() == 'erledigt':
                    continue
                
                # Tags lesen
                tags_match = re.search(r'tags:\s*\[(.*?)\]', text)
                tags = [t.strip() for t in tags_match.group(1).split(',')] if tags_match else []
                
                if tag and tag.lower() not in [t.lower() for t in tags]:
                    continue
                
                # Erste Überschrift oder Dateiname als Titel
                titel_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
                titel = titel_match.group(1) if titel_match else pfad.stem
                
                offen.append({
                    "pfad": pfad,
                    "titel": titel,
                    "tags": tags
                })
            except Exception:
                pass
    return offen

def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else None
    ideen = scan_ideen(tag)
    if not ideen:
        if tag:
            print(f"  Keine offenen Ideen für Tag '{tag}' gefunden.")
        else:
            print("  Keine offenen Ideen gefunden.")
        return

    print(f"  Offene Ideen{' für ' + tag if tag else ''}:")
    for item in ideen:
        tags_str = ", ".join(item["tags"]) if item["tags"] else "keine Tags"
        print(f"  • {item['titel']}\n    → {tags_str}")

if __name__ == "__main__":
    main()
