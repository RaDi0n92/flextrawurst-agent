#!/usr/bin/env python3
"""Idempotenter Einzug von gpt5.6-sol-high in Daniels Werkraum."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MODEL = "gpt5.6-sol-high"
SOURCE_NAME = "_claude"
TARGET_NAME = "_gpt5.6-sol-high"
WORKROOM = Path(os.environ.get("GPT56_WORKROOM", "/root/werkraum"))
SOURCE = Path(os.environ.get("GPT56_SOURCE_HOUSE", str(WORKROOM / SOURCE_NAME)))
TARGET = Path(os.environ.get("GPT56_HOUSE", str(WORKROOM / TARGET_NAME)))
SELF_DIR = Path(__file__).resolve().parent
STATE_DIR_NAMES = {
    "notizen", "spiegel", "ideen", "resonanz", "karte", "traeume", "träume",
    "memory", "memories", "sessions", "sessionen", "logs", "protokolle",
}
STATE_FILE_NAMES = {
    "brief_an_mich.md", "abwuerfe.md", "abwürfe.md", "resonanzfeld.md",
    "session_state.json", "last_session.json",
}
IGNORE_PARTS = {".git", "__pycache__", ".pytest_cache"}
IMPORT_PREFIX = "_import_"
TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".conf", ".service", ".timer", ".path", ".target", ".socket",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(command: list[str], *, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError(f"Befehl fehlgeschlagen: {' '.join(command)}\n{result.stdout}\n{result.stderr}")
    return result


def replace_identity(text: str) -> str:
    replacements = [
        (str(SOURCE), str(TARGET)),
        (SOURCE_NAME, TARGET_NAME),
        ("CLAUDE", "GPT5.6-SOL-HIGH"),
        ("Claude", MODEL),
        ("claude", MODEL),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def replace_path(path: Path) -> Path:
    parts = [replace_identity(part) for part in path.parts]
    return Path(*parts)


def under_state_dir(relative: Path) -> bool:
    return any(part.lower() in STATE_DIR_NAMES for part in relative.parts)


def under_import(relative: Path) -> bool:
    return any(part.startswith(IMPORT_PREFIX) for part in relative.parts)


def is_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    try:
        sample = path.read_bytes()[:4096]
        return b"\x00" not in sample
    except OSError:
        return False


def empty_state_file(destination: Path, source_relative: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix.lower() == ".json":
        content = {"owner": MODEL, "created_at": now(), "source_structure": str(source_relative), "entries": []}
        destination.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif destination.suffix.lower() in {".md", ".txt"}:
        destination.write_text(
            f"# {destination.stem}\n\nEigener, leerer Bereich von `{MODEL}`. Keine Daten aus `{SOURCE_NAME}` übernommen.\n",
            encoding="utf-8",
        )
    else:
        destination.touch()


def clone_structure() -> dict:
    if not SOURCE.is_dir():
        raise RuntimeError(f"Quellhaus fehlt: {SOURCE}")
    TARGET.mkdir(parents=True, exist_ok=True)
    created_dirs = 0
    copied_files = 0
    blanked_files = 0
    skipped_import_files = 0

    for root, dirs, files in os.walk(SOURCE):
        root_path = Path(root)
        relative_root = root_path.relative_to(SOURCE)
        dirs[:] = [d for d in dirs if d not in IGNORE_PARTS]
        destination_root = TARGET / replace_path(relative_root)
        destination_root.mkdir(parents=True, exist_ok=True)
        created_dirs += 1

        for filename in files:
            relative = relative_root / filename
            if any(part in IGNORE_PARTS for part in relative.parts):
                continue
            destination_relative = replace_path(relative)
            destination = TARGET / destination_relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            source_file = SOURCE / relative

            if under_import(relative):
                skipped_import_files += 1
                continue
            if under_state_dir(relative) or filename.lower() in STATE_FILE_NAMES:
                empty_state_file(destination, relative)
                blanked_files += 1
                continue
            if source_file.is_symlink():
                link_target = replace_identity(os.readlink(source_file))
                if destination.exists() or destination.is_symlink():
                    destination.unlink()
                destination.symlink_to(link_target)
                copied_files += 1
                continue
            if is_text(source_file):
                text = source_file.read_text(encoding="utf-8", errors="replace")
                destination.write_text(replace_identity(text), encoding="utf-8")
                shutil.copystat(source_file, destination, follow_symlinks=False)
            else:
                shutil.copy2(source_file, destination, follow_symlinks=False)
            copied_files += 1

    for name in ["notizen", "spiegel", "ideen", "resonanz", "karte", "tools", ".house"]:
        (TARGET / name).mkdir(parents=True, exist_ok=True)

    shutil.copy2(SELF_DIR / "house_sync_daemon.py", TARGET / "tools" / "house_sync_daemon.py")
    os.chmod(TARGET / "tools" / "house_sync_daemon.py", 0o755)
    manifest = {
        "owner": MODEL,
        "house": str(TARGET),
        "source_blueprint": str(SOURCE),
        "source_contents_are_memory": False,
        "copied_rule": "structure and functional files only; state/history contents reset",
        "identity_replacement": {"Claude/claude/_claude": f"{MODEL}/{MODEL}/{TARGET_NAME}"},
        "created_at": now(),
        "created_dirs": created_dirs,
        "copied_files": copied_files,
        "blanked_state_files": blanked_files,
        "skipped_import_files": skipped_import_files,
    }
    (TARGET / ".house" / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (TARGET / "EINZUG.md").write_text(
        "# Einzug: gpt5.6-sol-high\n\n"
        "Dieses Haus übernimmt den funktionalen Grundriss von `_claude`, aber keine Claude-Erinnerungen. "
        "Ordner für Notizen, Spiegel, Ideen, Resonanz, Karten, Träume und Sitzungszustände wurden leer angelegt.\n\n"
        "Alle `_import_*_grundriss/`-Ordner sind einseitige, automatisch aktualisierte Referenzfenster. "
        "Sie sind niemals eigene Erinnerung und werden niemals zurück in ihre Quellen geschrieben.\n",
        encoding="utf-8",
    )
    return manifest


def clone_systemd_units() -> list[dict]:
    unit_dir = Path("/etc/systemd/system")
    if not unit_dir.is_dir() or shutil.which("systemctl") is None:
        return []
    records = []
    source_tokens = [str(SOURCE), SOURCE_NAME, "Claude", "claude"]
    for path in sorted(unit_dir.iterdir()):
        if path.suffix not in {".service", ".timer", ".path", ".socket", ".target"} or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not any(token in content or token in path.name for token in source_tokens):
            continue
        destination_name = replace_identity(path.name)
        if destination_name == path.name:
            destination_name = f"gpt56-sol-high-{path.name}"
        destination = unit_dir / destination_name
        destination.write_text(replace_identity(content), encoding="utf-8")
        records.append({"source": str(path), "destination": str(destination)})

    sync_unit = unit_dir / "gpt56-sol-high-house-sync.service"
    sync_unit.write_text(
        "[Unit]\n"
        "Description=Lebendige Grundrisse fuer gpt5.6-sol-high\n"
        "After=local-fs.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart=/usr/bin/python3 {TARGET}/tools/house_sync_daemon.py --interval 5\n"
        "Restart=always\n"
        "RestartSec=2\n"
        "User=root\n"
        "UMask=0022\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n",
        encoding="utf-8",
    )
    records.append({"source": "generated", "destination": str(sync_unit)})
    run(["systemctl", "daemon-reload"])

    for record in records:
        name = Path(record["destination"]).name
        verify = run(["systemd-analyze", "verify", record["destination"]], check=False) if shutil.which("systemd-analyze") else None
        record["verify_returncode"] = verify.returncode if verify else None
        record["verify_stderr"] = verify.stderr[-2000:] if verify else ""
        if record["verify_returncode"] not in {None, 0}:
            record["enabled"] = False
            record["reason"] = "systemd-analyze verify failed"
            continue
        source_name = Path(record["source"]).name if record["source"] != "generated" else None
        should_enable = record["source"] == "generated"
        if source_name:
            should_enable = run(["systemctl", "is-enabled", source_name], check=False).returncode == 0
        if should_enable:
            enable = run(["systemctl", "enable", "--now", name], check=False, timeout=60)
            record["enabled"] = enable.returncode == 0
            record["enable_output"] = (enable.stdout + enable.stderr)[-2000:]
        else:
            record["enabled"] = False
            record["reason"] = "source unit was not enabled"
    return records


def clone_cron() -> dict:
    cron_sources = [Path("/etc/crontab")]
    cron_dir = Path("/etc/cron.d")
    if cron_dir.is_dir():
        cron_sources.extend(sorted(p for p in cron_dir.iterdir() if p.is_file()))
    lines = []
    for path in cron_sources:
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if str(SOURCE) in line or SOURCE_NAME in line or "claude" in line.lower():
                    lines.append(f"# von {path}\n{replace_identity(line)}")
        except OSError:
            continue
    destination = cron_dir / "gpt56-sol-high-house" if cron_dir.is_dir() else None
    if destination and lines:
        destination.write_text(
            "# Automatisch aus Claude-bezogenen Werkraum-Rhythmen abgeleitet.\n" + "\n".join(lines) + "\n",
            encoding="utf-8",
        )
        os.chmod(destination, 0o644)
    return {"destination": str(destination) if destination else None, "entries": len(lines)}


def install() -> dict:
    manifest = clone_structure()
    sync_once = run([sys.executable, str(TARGET / "tools" / "house_sync_daemon.py"), "--once"], timeout=600)
    units = clone_systemd_units()
    cron = clone_cron()
    result = {
        "installed_at": now(),
        "manifest": manifest,
        "initial_sync": json.loads(sync_once.stdout),
        "systemd_units": units,
        "cron": cron,
    }
    (TARGET / ".house" / "install_report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def verify_probe() -> dict:
    probe = WORKROOM / "_gpt56-house-probe"
    destination = TARGET / "_import_gpt56-house-probe_grundriss"
    if probe.exists():
        shutil.rmtree(probe)
    if destination.exists():
        shutil.rmtree(destination)
    probe.mkdir(parents=True)
    source_file = probe / "probe.txt"
    source_file.write_text("eins\n", encoding="utf-8")
    daemon = TARGET / "tools" / "house_sync_daemon.py"
    run([sys.executable, str(daemon), "--once"], timeout=300)
    mirrored = destination / "probe.txt"
    if not mirrored.is_file() or mirrored.read_text(encoding="utf-8") != "eins\n":
        raise RuntimeError("Grundriss-Probe: Erstanlage wurde nicht gespiegelt")
    source_file.write_text("zwei\n", encoding="utf-8")
    run([sys.executable, str(daemon), "--once"], timeout=300)
    if mirrored.read_text(encoding="utf-8") != "zwei\n":
        raise RuntimeError("Grundriss-Probe: Änderung wurde nicht gespiegelt")
    source_file.unlink()
    run([sys.executable, str(daemon), "--once"], timeout=300)
    if mirrored.exists():
        raise RuntimeError("Grundriss-Probe: Löschung wurde nicht gespiegelt")
    shutil.rmtree(probe)
    run([sys.executable, str(daemon), "--once"], timeout=300)
    if destination.exists():
        raise RuntimeError("Grundriss-Probe: entferntes Haus blieb als Import bestehen")
    return {"create": True, "modify": True, "delete_file": True, "delete_house": True}


def verify() -> dict:
    errors = []
    warnings = []
    if not SOURCE.is_dir():
        errors.append(f"Quellhaus fehlt: {SOURCE}")
    if not TARGET.is_dir():
        errors.append(f"Zielhaus fehlt: {TARGET}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    source_dirs = set()
    for path in SOURCE.rglob("*"):
        rel = path.relative_to(SOURCE)
        if path.is_dir() and not any(part in IGNORE_PARTS for part in rel.parts):
            source_dirs.add(replace_path(rel))
    missing_dirs = [str(rel) for rel in sorted(source_dirs, key=str) if not (TARGET / rel).is_dir()]
    if missing_dirs:
        errors.append(f"Fehlende übernommene Ordner: {missing_dirs[:50]}")

    identity_hits = []
    for path in TARGET.rglob("*"):
        if not path.is_file() or under_import(path.relative_to(TARGET)):
            continue
        if path.stat().st_size > 5_000_000 or not is_text(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if str(SOURCE) in text or re.search(r"\bClaude\b|\bclaude\b|_claude", text):
            identity_hits.append(str(path))
    if identity_hits:
        errors.append(f"Nicht ersetzte Claude-Identität in eigenen Dateien: {identity_hits[:30]}")

    service_active = None
    if shutil.which("systemctl"):
        status = run(["systemctl", "is-active", "gpt56-sol-high-house-sync.service"], check=False)
        service_active = status.returncode == 0
        if not service_active:
            errors.append("gpt56-sol-high-house-sync.service ist nicht aktiv")

    try:
        probe = verify_probe()
    except Exception as exc:
        probe = {"ok": False, "error": str(exc)}
        errors.append(str(exc))

    imports = sorted(p.name for p in TARGET.glob("_import_*_grundriss") if p.is_dir())
    if not imports:
        warnings.append("Keine anderen Häuser entdeckt; Importliste ist leer")

    report = {
        "ok": not errors,
        "checked_at": now(),
        "source": str(SOURCE),
        "target": str(TARGET),
        "service_active": service_active,
        "imports": imports,
        "probe": probe,
        "errors": errors,
        "warnings": warnings,
    }
    (TARGET / ".house" / "verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["install", "verify", "sync-once"])
    args = parser.parse_args()
    try:
        if args.command == "install":
            result = install()
        elif args.command == "verify":
            result = verify()
        else:
            result = json.loads(run([
                sys.executable, str(TARGET / "tools" / "house_sync_daemon.py"), "--once"
            ], timeout=600).stdout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok", True) else 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
