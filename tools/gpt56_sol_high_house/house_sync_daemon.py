#!/usr/bin/env python3
"""Lebendige, einseitige Grundrisse aller anderen Werkraum-Häuser."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

WORKROOM = Path(os.environ.get("GPT56_WORKROOM", "/root/werkraum"))
TARGET = Path(os.environ.get("GPT56_HOUSE", "/root/werkraum/_gpt5.6-sol-high"))
INTERVAL = float(os.environ.get("GPT56_SYNC_INTERVAL", "5"))
EXCLUDED_HOMES = {TARGET.name, "_shared"}
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache"}
IMPORT_PREFIX = "_import_"
STOP = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(name: str) -> str:
    return name.lstrip("_").replace("/", "_") or "root"


def discover_homes() -> list[Path]:
    if not WORKROOM.is_dir():
        return []
    homes = []
    for item in sorted(WORKROOM.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_dir() or not item.name.startswith("_"):
            continue
        if item.name in EXCLUDED_HOMES or item.name.startswith(IMPORT_PREFIX):
            continue
        homes.append(item)
    return homes


def ignored(relative: Path) -> bool:
    return any(part in EXCLUDED_PARTS or part.startswith(IMPORT_PREFIX) for part in relative.parts)


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def python_sync(source: Path, destination: Path) -> dict[str, int]:
    destination.mkdir(parents=True, exist_ok=True)
    source_entries: set[Path] = set()
    copied = 0
    removed = 0

    for root, dirs, files in os.walk(source):
        root_path = Path(root)
        rel_root = root_path.relative_to(source)
        dirs[:] = [d for d in dirs if not ignored(rel_root / d)]
        if ignored(rel_root):
            continue
        target_root = destination / rel_root
        target_root.mkdir(parents=True, exist_ok=True)
        source_entries.add(rel_root)
        for filename in files:
            rel = rel_root / filename
            if ignored(rel):
                continue
            src = source / rel
            dst = destination / rel
            source_entries.add(rel)
            try:
                same = (
                    dst.is_file()
                    and src.stat().st_size == dst.stat().st_size
                    and int(src.stat().st_mtime) == int(dst.stat().st_mtime)
                )
                if not same:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst, follow_symlinks=False)
                    copied += 1
            except FileNotFoundError:
                continue

    for root, dirs, files in os.walk(destination, topdown=False):
        root_path = Path(root)
        rel_root = root_path.relative_to(destination)
        if rel_root.parts and ignored(rel_root):
            continue
        for filename in files:
            rel = rel_root / filename
            if rel not in source_entries:
                try:
                    (destination / rel).unlink()
                    removed += 1
                except FileNotFoundError:
                    pass
        for dirname in dirs:
            rel = rel_root / dirname
            path = destination / rel
            if rel not in source_entries:
                try:
                    path.rmdir()
                    removed += 1
                except OSError:
                    pass
    return {"copied": copied, "removed": removed}


def rsync_sync(source: Path, destination: Path) -> dict[str, int]:
    destination.mkdir(parents=True, exist_ok=True)
    command = [
        "rsync", "-a", "--delete", "--itemize-changes",
        "--exclude=.git/", "--exclude=__pycache__/", "--exclude=.pytest_cache/",
        "--exclude=_import_*/", f"{source}/", f"{destination}/",
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"rsync exit {result.returncode}")
    changed = [line for line in result.stdout.splitlines() if line.strip()]
    removed = sum(1 for line in changed if "deleting " in line)
    return {"copied": len(changed) - removed, "removed": removed}


def sync_once() -> dict:
    TARGET.mkdir(parents=True, exist_ok=True)
    import_root = TARGET
    homes = discover_homes()
    expected = set()
    details = []
    use_rsync = shutil.which("rsync") is not None

    for home in homes:
        destination = import_root / f"{IMPORT_PREFIX}{slug(home.name)}_grundriss"
        expected.add(destination.name)
        stats = rsync_sync(home, destination) if use_rsync else python_sync(home, destination)
        marker = destination / ".GRUNDRISS_REFERENZ.json"
        marker.write_text(json.dumps({
            "source": str(home),
            "destination": str(destination),
            "owner": home.name,
            "observer": "gpt5.6-sol-high",
            "is_own_memory": False,
            "direction": "one-way source-to-import",
            "delete_removed": True,
            "updated_at": utc_now(),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        details.append({"source": str(home), "destination": str(destination), **stats})

    for item in TARGET.glob(f"{IMPORT_PREFIX}*_grundriss"):
        if item.is_dir() and item.name not in expected:
            shutil.rmtree(item)
            details.append({"source": None, "destination": str(item), "removed_house": True})

    state_dir = TARGET / ".house"
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {"updated_at": utc_now(), "homes": details, "count": len(homes)}
    (state_dir / "last_sync.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return state


def handle_stop(_signum, _frame) -> None:
    global STOP
    STOP = True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=INTERVAL)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)

    if args.once:
        print(json.dumps(sync_once(), ensure_ascii=False, indent=2))
        return 0

    while not STOP:
        try:
            state = sync_once()
            print(json.dumps({"ok": True, "updated_at": state["updated_at"], "count": state["count"]}), flush=True)
        except Exception as exc:
            print(json.dumps({"ok": False, "error": str(exc), "at": utc_now()}), file=sys.stderr, flush=True)
        deadline = time.monotonic() + max(args.interval, 1.0)
        while not STOP and time.monotonic() < deadline:
            time.sleep(0.2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
