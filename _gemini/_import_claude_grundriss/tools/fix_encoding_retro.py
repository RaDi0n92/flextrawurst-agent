#!/usr/bin/env python3
"""
Retroaktiver Encoding-Fix: findet .md-Dateien die noch in Windows-1252
vorliegen (echte Latin-1-Bytes, noch kein U+FFFD) und konvertiert sie zu UTF-8.

Aufruf:
  python3 fix_encoding_retro.py /root/werkraum
  python3 fix_encoding_retro.py /root/werkraum/projekt
  python3 fix_encoding_retro.py --dry-run /root/werkraum
"""
import argparse
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".cache", "dist", "build"}


def needs_conversion(path: Path) -> bool:
    content = path.read_bytes()
    try:
        content.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


def convert(path: Path) -> str:
    content = path.read_bytes()
    try:
        text = content.decode("windows-1252")
        encoding_used = "windows-1252"
    except UnicodeDecodeError:
        text = content.decode("latin-1")
        encoding_used = "latin-1"
    path.write_bytes(text.encode("utf-8"))
    return encoding_used


def iter_md_files(root: Path):
    for dirpath, dirnames, filenames in __import__("os").walk(root, followlinks=False):
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not (Path(dirpath) / d).is_symlink()
        ]
        for name in filenames:
            if name.endswith(".md"):
                p = Path(dirpath) / name
                if not p.is_symlink():
                    yield p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="/root/werkraum")
    parser.add_argument("--dry-run", action="store_true",
                        help="Nur anzeigen, nicht schreiben")
    args = parser.parse_args()

    root = Path(args.root)
    converted = []

    for md in iter_md_files(root):
        if needs_conversion(md):
            if args.dry_run:
                print(f"  [würde konvertieren] {md}")
            else:
                enc = convert(md)
                rel = md.relative_to(root)
                print(f"  konvertiert ({enc}): {rel}")
                converted.append(str(rel))

    if args.dry_run:
        print("(dry-run — nichts geschrieben)")
    else:
        print(f"\n{len(converted)} Dateien konvertiert.")


if __name__ == "__main__":
    main()
