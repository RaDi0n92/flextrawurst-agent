#!/usr/bin/env python3
"""
Ideen-Scanner: liest alle Ideen-Dateien mit Frontmatter,
filtert nach Tag (optional) und zeigt offene Ideen.

Aufruf:
  python3 ideen_scan.py              → alle offenen Ideen
  python3 ideen_scan.py wesen-einzug → nur Ideen mit diesem Tag
"""
import os
import sys

IDEEN_DIR = "/root/werkraum/_codex/ideen"


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip()
    rest = text[end + 3:].strip()
    meta = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        meta[k] = v
    return meta, rest


def lade_ideen(tag_filter=None):
    ideen = []
    for fname in sorted(os.listdir(IDEEN_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(IDEEN_DIR, fname)
        with open(path) as f:
            text = f.read()
        meta, body = parse_frontmatter(text)
        if not meta:
            continue
        status = meta.get("status", "offen")
        if status == "erledigt":
            continue
        betrifft = meta.get("betrifft", [])
        if isinstance(betrifft, str):
            betrifft = [betrifft]
        if tag_filter and tag_filter not in betrifft:
            continue
        # Erste Überschrift aus body
        titel = fname.replace(".md", "")
        for line in body.splitlines():
            if line.startswith("# "):
                titel = line[2:].strip()
                break
        ideen.append({
            "datei": fname,
            "titel": titel,
            "betrifft": betrifft,
            "status": status,
        })
    return ideen


def main():
    tag_filter = sys.argv[1] if len(sys.argv) > 1 else None

    ideen = lade_ideen(tag_filter)

    if not ideen:
        if tag_filter:
            print(f"  (keine offenen Ideen für '{tag_filter}')")
        else:
            print("  (keine offenen Ideen)")
        return

    label = f" [tag: {tag_filter}]" if tag_filter else ""
    print(f"  Offene Ideen{label}:")
    for idee in ideen:
        tags = ", ".join(idee["betrifft"]) if idee["betrifft"] else "—"
        print(f"  • {idee['titel']}")
        print(f"    → {tags}")


if __name__ == "__main__":
    main()
