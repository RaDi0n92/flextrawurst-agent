#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".cache",
    "cache",
    "Cache",
    "Trash",
    "trash",
    "dist",
    "build",
    "__pycache__",
}

MARKER_RE = re.compile("Ã|Â|â€|â€™|â€œ|â€ž|â€“|â—|â€”|ðŸ|�")


def iter_markdown_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in EXCLUDE_DIRS and not (Path(dirpath) / name).is_symlink()
        ]
        for filename in filenames:
            if filename.endswith(".md"):
                path = Path(dirpath) / filename
                if not path.is_symlink():
                    yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Markdown files for likely mojibake markers.")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--max-examples", type=int, default=80, help="Maximum matching lines to print")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    suspicious_files: set[Path] = set()
    examples = 0

    for path in iter_markdown_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as exc:
            suspicious_files.add(path)
            if examples < args.max_examples:
                print(f"{path.relative_to(root)}: invalid UTF-8: {exc}")
                examples += 1
            continue
        for lineno, line in enumerate(lines, 1):
            if MARKER_RE.search(line):
                suspicious_files.add(path)
                if examples < args.max_examples:
                    print(f"{path.relative_to(root)}:{lineno}: {line[:220]}")
                    examples += 1
                break

    print(f"\nsuspicious_files={len(suspicious_files)}")
    return 1 if suspicious_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
