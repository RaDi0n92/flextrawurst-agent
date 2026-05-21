#!/usr/bin/env python3
"""
Synchronisiert Codex' Bereich als importierten Grundriss fuer Claude.

Quelle:
  /root/werkraum/_codex

Ziel:
  /root/werkraum/_claude/_import_codex_grundriss

Wichtig:
  Das Ziel ist Referenzmaterial. Es ist nicht Claudes Erinnerung.
  Der Sync fasst keine eigenen Claude-Dateien ausserhalb des Importordners an.
"""

from __future__ import annotations

import argparse
import filecmp
import logging
import shutil
import signal
import sys
import time
from pathlib import Path

SOURCE = Path("/root/werkraum/_codex").resolve()
TARGET = Path("/root/werkraum/_claude/_import_codex_grundriss").resolve()
INTERVAL_SECONDS = 5

IGNORE_DIRS = {"__pycache__", "_import_claude_grundriss"}
IGNORE_SUFFIXES = {".pyc", ".pyo", ".swp", ".tmp"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [codex-grundriss-sync] %(levelname)s %(message)s",
)
log = logging.getLogger("codex-grundriss-sync")

_running = True


def _stop(*_: object) -> None:
    global _running
    _running = False


def _ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    return path.suffix in IGNORE_SUFFIXES


def _iter_source_files() -> dict[Path, Path]:
    files: dict[Path, Path] = {}
    for path in SOURCE.rglob("*"):
        rel = path.relative_to(SOURCE)
        if _ignored(rel):
            continue
        if path.is_file():
            files[rel] = path
    return files


def _iter_target_files() -> set[Path]:
    files: set[Path] = set()
    if not TARGET.exists():
        return files
    for path in TARGET.rglob("*"):
        rel = path.relative_to(TARGET)
        if _ignored(rel):
            continue
        if path.is_file():
            files.add(rel)
    return files


def _copy_if_changed(src: Path, dst: Path) -> bool:
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(f".{dst.name}.tmp")
    shutil.copy2(src, tmp)
    tmp.replace(dst)
    return True


def _cleanup_empty_dirs() -> None:
    if not TARGET.exists():
        return
    for path in sorted(TARGET.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass


def sync_once(delete_removed: bool = True) -> dict[str, int]:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Quelle fehlt: {SOURCE}")

    TARGET.mkdir(parents=True, exist_ok=True)

    source_files = _iter_source_files()
    target_files = _iter_target_files()

    copied = 0
    deleted = 0

    for rel, src in sorted(source_files.items()):
        dst = TARGET / rel
        if _copy_if_changed(src, dst):
            copied += 1

    if delete_removed:
        for rel in sorted(target_files - set(source_files)):
            dst = TARGET / rel
            try:
                dst.unlink()
                deleted += 1
            except FileNotFoundError:
                pass

    if delete_removed:
        _cleanup_empty_dirs()

    return {"copied": copied, "deleted": deleted, "seen": len(source_files)}


def watch(interval: int) -> None:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    log.info("Start: %s -> %s alle %ss", SOURCE, TARGET, interval)
    while _running:
        try:
            result = sync_once(delete_removed=True)
            if result["copied"] or result["deleted"]:
                log.info(
                    "Sync: %s aktualisiert, %s geloescht, %s Dateien gesehen",
                    result["copied"],
                    result["deleted"],
                    result["seen"],
                )
        except Exception as exc:
            log.exception("Sync fehlgeschlagen: %s", exc)
        time.sleep(interval)
    log.info("Stop")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="einmal synchronisieren und beenden")
    parser.add_argument("--interval", type=int, default=INTERVAL_SECONDS)
    parser.add_argument("--no-delete", action="store_true", help="im Ziel keine entfernten Dateien loeschen")
    args = parser.parse_args()

    if args.once:
        result = sync_once(delete_removed=not args.no_delete)
        print(
            f"copied={result['copied']} deleted={result['deleted']} seen={result['seen']}"
        )
        return 0

    watch(max(1, args.interval))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
