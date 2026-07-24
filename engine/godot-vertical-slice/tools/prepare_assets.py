#!/usr/bin/env python3
"""Reconstruct and verify binary assets that travel as UTF-8-safe base64 payloads."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_DIR / "assets"
MANIFEST_PATH = PROJECT_DIR / "data" / "asset_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    for entry in manifest["assets"]:
        payload_path = PROJECT_DIR / entry["payload_path"]
        output_path = PROJECT_DIR / entry["output_path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        raw = base64.b64decode(payload_path.read_text(encoding="ascii"), validate=True)
        output_path.write_bytes(raw)

        actual_size = output_path.stat().st_size
        actual_hash = sha256(output_path)
        if actual_size != entry["size_bytes"]:
            failures.append(
                f"{entry['asset_id']}: size {actual_size} != {entry['size_bytes']}"
            )
        if actual_hash != entry["sha256"]:
            failures.append(
                f"{entry['asset_id']}: sha256 {actual_hash} != {entry['sha256']}"
            )

        print(
            json.dumps(
                {
                    "asset_id": entry["asset_id"],
                    "output": str(output_path),
                    "size_bytes": actual_size,
                    "sha256": actual_hash,
                    "status": "PASS" if not failures else "CHECK",
                },
                ensure_ascii=False,
            )
        )

    if failures:
        for failure in failures:
            print(f"ASSET_PREPARE_FAIL: {failure}")
        return 1

    print("FLEXTRAWURST_ENGINE_ASSET_PREPARE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
