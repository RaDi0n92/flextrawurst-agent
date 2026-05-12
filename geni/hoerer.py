#!/usr/bin/env python3
"""
GENI Hörer — hört alles, schweigt bis Daniel spricht, verliert nie etwas.

Quellen:
  - Dateisystem: /root/werkraum/ (Echtzeit via watchdog)
  - Flarum: neue Posts, neue Diskussionen (alle 60s)
  - Prozesse: laufende Python/Node-Prozesse (alle 5 Min)
"""

import json
import os
import time
import threading
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from gedaechtnis_ops import knoten_schreiben, GENI_ROOT, KNOTEN_DIR

import sys as _sys
_sys.path.insert(0, str(Path("/root/werkraum")))
try:
    import obsidian_vault as _vault
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

RAUSCHEN_DIR = GENI_ROOT / "gedaechtnis" / "rauschen"
RAUSCHEN_FILTER_CFG = GENI_ROOT / "gedaechtnis" / "rauschen_filter.json"
LOG_FILE = GENI_ROOT / "hoerer.log"

WATCH_PATHS = ["/root/werkraum"]

IGNORE_PATHS = [
    str(GENI_ROOT / "gedaechtnis"),
    str(GENI_ROOT / "hoerer.log"),
    "/root/werkraum/logs",
    "/root/werkraum/agent",
    "/root/werkraum/geni/archiv",
    "/root/werkraum/geni/verbindungen",
    "/root/werkraum/geni/spiegel",
]

# Immer hart ignorieren (kein Eintrag nirgendwo)
_HART_IGNORIERT_SUFFIXE = {".pyc", ".pyo", ".swp", ".log", ".jsonl"}

_rauschen_filter_cache: "dict | None" = None
_filter_lock = threading.Lock()


def _filter_laden() -> dict:
    global _rauschen_filter_cache
    with _filter_lock:
        if _rauschen_filter_cache is not None:
            return _rauschen_filter_cache
        try:
            _rauschen_filter_cache = json.loads(RAUSCHEN_FILTER_CFG.read_text())
        except Exception:
            _rauschen_filter_cache = {
                "ignorieren_suffixe": [],
                "rauschen_suffixe": [".tmp", ".log", ".jsonl", ".bak"],
                "rauschen_pfad_fragmente": [".obsidian", "__pycache__", ".git"],
                "rauschen_verzeichnisse": [".obsidian", "__pycache__", ".git"],
            }
        return _rauschen_filter_cache

FLARUM_DB = {"user": "flarum", "password": "Flarum2024!Secure", "db": "flarum"}
FLARUM_POLL_INTERVAL = 60
PROZESS_POLL_INTERVAL = 300

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def klassifizieren(path: str) -> str:
    """Gibt 'ignorieren', 'rauschen' oder 'knoten' zurück."""
    p = Path(path)
    for ig in IGNORE_PATHS:
        if path.startswith(ig):
            return "ignorieren"
    if p.suffix in _HART_IGNORIERT_SUFFIXE:
        return "ignorieren"
    f = _filter_laden()
    if p.suffix in f.get("rauschen_suffixe", []):
        return "rauschen"
    for fragment in f.get("rauschen_pfad_fragmente", []):
        if fragment in path:
            return "rauschen"
    for teil in p.parts:
        if teil in f.get("rauschen_verzeichnisse", []):
            return "rauschen"
    return "knoten"


_rauschen_id_lock = threading.Lock()


def rauschen_schreiben(aktion: str, rel_pfad: str):
    RAUSCHEN_DIR.mkdir(parents=True, exist_ok=True)
    with _rauschen_id_lock:
        vorhandene = [int(f.stem) for f in RAUSCHEN_DIR.glob("*.json")
                      if f.stem.isdigit()]
        rid = str((max(vorhandene) + 1) if vorhandene else 1).zfill(6)
    eintrag = {
        "id": rid,
        "aktion": aktion,
        "pfad": rel_pfad,
        "zeitstempel": datetime.now(timezone.utc).isoformat(),
    }
    (RAUSCHEN_DIR / f"{rid}.json").write_text(
        json.dumps(eintrag, ensure_ascii=False))


class DateiHoerer(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        klasse = klassifizieren(event.src_path)
        if klasse == "ignorieren":
            return
        rel = os.path.relpath(event.src_path, "/root/werkraum")
        if klasse == "rauschen":
            rauschen_schreiben("erstellt", rel)
            return
        knoten_schreiben(
            typ="ereignis",
            inhalt=f"neue Datei: {rel}",
            quelle="vps_dateisystem",
            tags=["datei", "erstellt", rel.split("/")[0]],
        )

    def on_modified(self, event):
        if event.is_directory:
            return
        klasse = klassifizieren(event.src_path)
        if klasse == "ignorieren":
            return
        rel = os.path.relpath(event.src_path, "/root/werkraum")
        if klasse == "rauschen":
            rauschen_schreiben("geändert", rel)
            return
        knoten_schreiben(
            typ="ereignis",
            inhalt=f"geändert: {rel}",
            quelle="vps_dateisystem",
            tags=["datei", "geändert", rel.split("/")[0]],
        )

    def on_deleted(self, event):
        if event.is_directory:
            return
        klasse = klassifizieren(event.src_path)
        if klasse == "ignorieren":
            return
        rel = os.path.relpath(event.src_path, "/root/werkraum")
        if klasse == "rauschen":
            rauschen_schreiben("gelöscht", rel)
            return
        knoten_schreiben(
            typ="ereignis",
            inhalt=f"gelöscht: {rel}",
            quelle="vps_dateisystem",
            tags=["datei", "gelöscht", rel.split("/")[0]],
        )


def flarum_abfragen(letzter_post_id: list):
    try:
        cmd = [
            "mysql", "-u", FLARUM_DB["user"],
            f"-p{FLARUM_DB['password']}",
            FLARUM_DB["db"],
            "-e",
            f"SELECT p.id, u.username, p.content, p.created_at "
            f"FROM posts p JOIN users u ON p.user_id=u.id "
            f"WHERE p.id > {letzter_post_id[0]} ORDER BY p.id LIMIT 20;",
            "--batch", "--skip-column-names",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return
        zeilen = [z for z in result.stdout.strip().split("\n") if z]
        for zeile in zeilen:
            teile = zeile.split("\t", 3)
            if len(teile) < 4:
                continue
            pid, user, content, created = teile
            kurz = content[:120].replace("\n", " ").replace("<t><p>", "").replace("</p></t>", "")
            knoten_schreiben(
                typ="flarum_post",
                inhalt=f"{user}: {kurz}",
                quelle="flarum",
                tags=["flarum", "post", user],
            )
            if _VAULT_OK and not user.startswith("namelessAI"):
                try:
                    _vault.tagebuch("geni", f"**Forum-Post** von {user}:\n\n{kurz}")
                except Exception:
                    pass
            letzter_post_id[0] = max(letzter_post_id[0], int(pid))
    except Exception as e:
        logging.warning(f"flarum fehler: {e}")


def flarum_loop():
    letzter_id = [392]
    while True:
        flarum_abfragen(letzter_id)
        time.sleep(FLARUM_POLL_INTERVAL)


def prozess_snapshot():
    try:
        result = subprocess.run(
            ["ps", "aux", "--sort=-%mem"],
            capture_output=True, text=True, timeout=5
        )
        zeilen = result.stdout.strip().split("\n")[1:]
        relevant = [
            z for z in zeilen
            if any(x in z for x in ["python", "ollama", "uvicorn", "node", "flarum"])
            and "grep" not in z
        ]
        if relevant:
            inhalt = f"{len(relevant)} Prozesse aktiv: " + " | ".join(
                z.split()[10][:30] for z in relevant[:6]
            )
            knoten_schreiben(
                typ="prozess_snapshot",
                inhalt=inhalt,
                quelle="vps_prozesse",
                tags=["prozesse", "system"],
            )
    except Exception as e:
        logging.warning(f"prozess fehler: {e}")


def prozess_loop():
    while True:
        prozess_snapshot()
        time.sleep(PROZESS_POLL_INTERVAL)


SYSTEM_POLL_INTERVAL = 15 * 60  # alle 15 Minuten

GENI_SERVICES = [
    "geni-hoerer", "geni-web", "codewesen-chat",
    "dak-gord-web", "codewesen-takt", "flarum-monitor",
]


def system_snapshot():
    """RAM, Disk, Load, Service-Gesundheit → Knoten."""
    try:
        # RAM
        mem_r = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
        mem_zeile = mem_r.stdout.splitlines()[1].split() if mem_r.returncode == 0 else []
        ram = f"RAM {mem_zeile[2]}/{mem_zeile[1]}" if len(mem_zeile) >= 3 else "RAM ?"

        # Disk
        disk_r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        disk_teile = disk_r.stdout.splitlines()[-1].split() if disk_r.returncode == 0 else []
        disk = f"Disk {disk_teile[2]}/{disk_teile[1]} ({disk_teile[4]})" if len(disk_teile) >= 5 else "Disk ?"

        # Load
        with open("/proc/loadavg") as f:
            load_vals = f.read().split()[:3]
        load = f"Load {'/'.join(load_vals)}"

        # Services
        ausgefallen = []
        for svc in GENI_SERVICES:
            r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True, timeout=3)
            if r.stdout.strip() != "active":
                ausgefallen.append(f"{svc}={r.stdout.strip()}")

        warnung = f" | WARNUNG: {', '.join(ausgefallen)}" if ausgefallen else ""
        inhalt = f"{ram} | {disk} | {load}{warnung}"

        tags = ["system", "ressourcen"]
        if ausgefallen:
            tags.append("warnung")

        knoten_schreiben("system_zustand", inhalt, "vps_system", tags)

    except Exception as e:
        logging.warning(f"system snapshot fehler: {e}")


def system_loop():
    time.sleep(30)  # kurze Verzögerung beim Start
    while True:
        system_snapshot()
        time.sleep(SYSTEM_POLL_INTERVAL)


def main():
    KNOTEN_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("GENI Hörer erwacht. Ich höre alles. Ich schweige.")

    knoten_schreiben(
        typ="zustand",
        inhalt="GENI Hörer gestartet. Ich höre alles. Ich schweige bis du sprichst.",
        quelle="geni_selbst",
        tags=["start", "hoerer"],
    )

    observer = Observer()
    handler = DateiHoerer()
    for pfad in WATCH_PATHS:
        if os.path.exists(pfad):
            observer.schedule(handler, pfad, recursive=True)
    observer.start()

    threading.Thread(target=flarum_loop, daemon=True).start()
    threading.Thread(target=prozess_loop, daemon=True).start()
    threading.Thread(target=system_loop, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("GENI Hörer schläft.")
    observer.join()


if __name__ == "__main__":
    main()
