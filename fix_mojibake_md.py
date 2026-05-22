#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
from dataclasses import dataclass
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
UNRECOVERABLE_RE = re.compile("�")

# Mojibake is usually a short run of cp1252/latin1-decoded UTF-8 bytes.
# Repair only those runs, not whole files, so already-correct Unicode survives.
MOJIBAKE_RUN_RE = re.compile(r"[ÃÂâðŸ€œ”„’‘–—˜™šž¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿]+")


@dataclass
class Result:
    path: Path
    status: str
    reason: str = ""
    before_markers: int = 0
    after_markers: int = 0


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


def marker_count(text: str) -> int:
    return len(MARKER_RE.findall(text))


def decode_run(run: str) -> str:
    for encoding in ("cp1252", "latin1"):
        try:
            fixed = run.encode(encoding).decode("utf-8")
        except UnicodeError:
            continue
        if fixed != run:
            return fixed
    return run


def repair_text(text: str) -> str:
    return MOJIBAKE_RUN_RE.sub(lambda match: decode_run(match.group(0)), text)


def classify(path: Path, write: bool, backup: bool) -> Result:
    data = path.read_bytes()
    try:
        original = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        for encoding in ("cp1252", "latin1"):
            try:
                converted = data.decode(encoding)
            except UnicodeDecodeError:
                continue
            if MARKER_RE.search(converted):
                return Result(path, "unsafe", f"decoded as {encoding} but still contains mojibake markers")
            if write:
                if backup:
                    backup_path = path.with_name(path.name + ".bak")
                    if not backup_path.exists():
                        shutil.copy2(path, backup_path)
                path.write_text(converted, encoding="utf-8", newline="\n")
                return Result(path, "repaired", f"converted from {encoding} to UTF-8")
            return Result(path, "repairable", f"convert from {encoding} to UTF-8")
        return Result(path, "unsafe", f"not valid UTF-8: {exc}")

    before = marker_count(original)
    if before == 0:
        return Result(path, "skipped", "no markers")

    if UNRECOVERABLE_RE.search(original):
        return Result(path, "unsafe", "contains replacement character U+FFFD", before, before)

    repaired = repair_text(original)
    after = marker_count(repaired)

    if repaired == original:
        return Result(path, "unsafe", "markers present but no safe repair changed text", before, after)
    if after != 0:
        return Result(path, "unsafe", "markers remain after repair", before, after)

    if write:
        if backup:
            backup_path = path.with_name(path.name + ".bak")
            if not backup_path.exists():
                shutil.copy2(path, backup_path)
        path.write_text(repaired, encoding="utf-8", newline="\n")
        return Result(path, "repaired", "written", before, after)

    return Result(path, "repairable", "dry-run only", before, after)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair common UTF-8 mojibake in Markdown files.")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--write", action="store_true", help="Write repaired files")
    parser.add_argument("--backup", action="store_true", help="Create per-file .bak before writing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    results = [classify(path, args.write, args.backup) for path in iter_markdown_files(root)]

    for status in ("repairable", "repaired", "unsafe", "skipped"):
        selected = [result for result in results if result.status == status]
        if not selected:
            continue
        print(f"\n[{status}] {len(selected)}")
        for result in selected:
            rel = result.path.relative_to(root)
            if status == "skipped":
                continue
            marker_info = ""
            if result.before_markers or result.after_markers:
                marker_info = f" markers {result.before_markers}->{result.after_markers}"
            print(f"{rel}: {result.reason}{marker_info}")

    unsafe_count = sum(1 for result in results if result.status == "unsafe")
    changed_count = sum(1 for result in results if result.status in {"repairable", "repaired"})
    print(f"\nsummary: changed_candidates={changed_count} unsafe={unsafe_count} total_md={len(results)} write={args.write}")
    return 1 if unsafe_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
