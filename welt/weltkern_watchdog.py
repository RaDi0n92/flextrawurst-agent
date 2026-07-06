#!/usr/bin/env python3
"""
Weltkern-Watchdog: Prüft alle kritischen Flextrawurst-Services.

Prüft:
  - Service aktiv?
  - Port erreichbar?
  - API antwortet?
  - DB erreichbar?
  - letzte Events vorhanden?
  - alte Ollama-Locks?
  - alte Chat-Flags?
  - Log-Fehler-Burst?

Aktion nur bei klaren Kriterien. Niemals blind neustarten.
Flarum-Takte werden NICHT gestartet.
"""

import json
import logging
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests

LOG_DIR = Path("/root/werkraum/logs")
LOG_DIR.mkdir(exist_ok=True)
AUDIT_LOG = LOG_DIR / "weltkern_watchdog.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] watchdog: %(message)s",
    handlers=[
        logging.FileHandler(str(AUDIT_LOG)),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("watchdog")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:dakpass@localhost:5432/flextrawurst")

# ── Konfiguration ──────────────────────────────────────────────────────────────

LOCK_DIR = Path("/tmp/ollama_locks")
CHAT_FLAG = Path("/tmp/dak_gord_chat_aktiv")
FLARUM_LOCK = Path("/tmp/flarum_write.lock")

LOCK_MAX_AGE_MINUTES = 30
CHAT_FLAG_MAX_AGE_MINUTES = 60

# Services mit Port-Prüfung
WELTKERN_SERVICES = {
    "welt-api":             {"port": 8030, "health": "http://localhost:8030/health"},
    "welt-bruecke":         {"port": None, "health": None},
    "process-camera-preview": {"port": 8787, "health": None},  # frueher "flextrawurst-surface" genannt, Dienst wurde umbenannt
    "flextrawurst-gateway": {"port": 8010, "health": "http://localhost:8010/health"},
    "obsidian-api":         {"port": 8060, "health": None},
    "geni-hoerer":          {"port": None, "health": None},
    "geni-web":             {"port": 8020, "health": None},
    "ollama":               {"port": 11434, "health": "http://localhost:11434/api/tags"},
    "splitter-physik":      {"port": None, "health": None},
    "similarity-daemon":    {"port": None, "health": None},
    "codewesen-chat":       {"port": 8002, "health": None},
    "dak-gord-web":         {"port": 8000, "health": None},
    "entity-kern":          {"port": None, "health": None},
    "entity-takt":          {"port": None, "health": None},
    "cyberling-daemon":     {"port": None, "health": None},
    "tension-daemon":       {"port": None, "health": None},
    "themen-cluster":       {"port": None, "health": None},
}

# Veraltet (2026-07-07): Diese Liste stammte aus der Flarum-Vorphase, als diese Dienste
# absichtlich ausgeschaltet bleiben sollten. Die Flarum-Integration ist seit Wochen live,
# alle hier genannten Dienste laufen inzwischen bewusst dauerhaft. Das Guardrail unten hat
# deshalb bei jedem 10-Minuten-Lauf eine falsche ERROR-Warnung erzeugt. Liste bewusst leer
# gelassen statt geloescht, falls es je wieder eine echte "diese Dienste duerfen nicht laufen"
# Situation geben sollte.
FLARUM_SERVICES_FROZEN = set()

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def service_is_active(name: str) -> bool:
    result = subprocess.run(
        ["systemctl", "is-active", f"{name}.service"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() == "active"


def port_open(port: int) -> bool:
    import socket
    try:
        with socket.create_connection(("localhost", port), timeout=2):
            return True
    except OSError:
        return False


def api_ok(url: str) -> bool:
    try:
        r = requests.get(url, timeout=3)
        return r.status_code < 500
    except Exception:
        return False


def db_ok() -> bool:
    try:
        conn = psycopg2.connect(DB_URI)
        conn.close()
        return True
    except Exception:
        return False


def recent_events(minutes: int = 15) -> int:
    try:
        conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM events WHERE created_at >= NOW() - INTERVAL '%s minutes'",
                (minutes,),
            )
            return cur.fetchone()["cnt"]
    except Exception:
        return -1
    finally:
        try:
            conn.close()
        except Exception:
            pass


def stale_locks() -> list[str]:
    stale = []
    if not LOCK_DIR.exists():
        return stale
    now = time.time()
    for f in LOCK_DIR.iterdir():
        age_minutes = (now - f.stat().st_mtime) / 60
        if age_minutes > LOCK_MAX_AGE_MINUTES:
            stale.append(f"{f.name} ({age_minutes:.0f}min alt)")
    return stale


def stale_chat_flag() -> bool:
    if not CHAT_FLAG.exists():
        return False
    age_minutes = (time.time() - CHAT_FLAG.stat().st_mtime) / 60
    return age_minutes > CHAT_FLAG_MAX_AGE_MINUTES


def stale_flarum_lock() -> bool:
    if not FLARUM_LOCK.exists():
        return False
    age_minutes = (time.time() - FLARUM_LOCK.stat().st_mtime) / 60
    return age_minutes > 60


def flarum_services_running() -> list[str]:
    running = []
    for name in FLARUM_SERVICES_FROZEN:
        if service_is_active(name):
            running.append(name)
    return running


# ── Hauptprüfung ───────────────────────────────────────────────────────────────

def run_check() -> dict:
    now = datetime.now(timezone.utc)
    report = {
        "timestamp": now.isoformat(),
        "db": None,
        "recent_events": None,
        "services": {},
        "locks": [],
        "chat_flag_stale": False,
        "flarum_lock_stale": False,
        "flarum_services_active": [],
        "actions_taken": [],
        "warnings": [],
    }

    # DB
    report["db"] = db_ok()
    if not report["db"]:
        report["warnings"].append("DB nicht erreichbar")
        log.error("DB nicht erreichbar!")
    else:
        report["recent_events"] = recent_events(15)
        if report["recent_events"] == 0:
            report["warnings"].append("Keine Events in den letzten 15 Minuten")

    # Services
    for name, cfg in WELTKERN_SERVICES.items():
        active = service_is_active(name)
        port_ok = port_open(cfg["port"]) if cfg["port"] else None
        health = api_ok(cfg["health"]) if cfg["health"] else None

        status = "ok" if active else "down"
        if active and port_ok is False:
            status = "port_dead"
        if active and health is False:
            status = "api_dead"

        report["services"][name] = {
            "active": active,
            "port_ok": port_ok,
            "health_ok": health,
            "status": status,
        }

        if status == "down":
            report["warnings"].append(f"{name}: inaktiv")
            log.warning(f"SERVICE DOWN: {name}")
        elif status == "port_dead":
            report["warnings"].append(f"{name}: aktiv aber Port {cfg['port']} tot")
            log.warning(f"PORT DEAD: {name} Port {cfg['port']}")
        elif status == "api_dead":
            report["warnings"].append(f"{name}: aktiv aber API antwortet nicht")
            log.warning(f"API DEAD: {name}")

    # Locks
    stale = stale_locks()
    report["locks"] = stale
    if stale:
        log.warning(f"Stale Ollama-Locks: {stale}")
        for f in LOCK_DIR.iterdir():
            age = (time.time() - f.stat().st_mtime) / 60
            if age > LOCK_MAX_AGE_MINUTES:
                f.unlink(missing_ok=True)
                report["actions_taken"].append(f"stale lock entfernt: {f.name}")
                log.info(f"Stale lock entfernt: {f.name}")

    # Chat-Flag
    report["chat_flag_stale"] = stale_chat_flag()
    if report["chat_flag_stale"]:
        age = (time.time() - CHAT_FLAG.stat().st_mtime) / 60
        report["warnings"].append(f"CHAT_FLAG veraltet ({age:.0f}min)")
        log.warning(f"Veraltetes CHAT_FLAG ({age:.0f}min) — entferne")
        CHAT_FLAG.unlink(missing_ok=True)
        report["actions_taken"].append("stales CHAT_FLAG entfernt")

    # Flarum-Lock
    report["flarum_lock_stale"] = stale_flarum_lock()
    if report["flarum_lock_stale"]:
        FLARUM_LOCK.unlink(missing_ok=True)
        report["actions_taken"].append("stales flarum_write.lock entfernt")
        log.info("Stales flarum_write.lock entfernt")

    # Flarum-Services Guardrail
    flarum_running = flarum_services_running()
    report["flarum_services_active"] = flarum_running
    if flarum_running:
        log.error(f"GUARDRAIL: Flarum-Services aktiv: {flarum_running}")
        report["warnings"].append(f"GUARDRAIL: Flarum-Services aktiv: {flarum_running}")

    # Zusammenfassung
    healthy = sum(1 for s in report["services"].values() if s["status"] == "ok")
    total = len(report["services"])
    log.info(
        f"Prüfung: {healthy}/{total} Services ok | "
        f"DB: {'ok' if report['db'] else 'FEHLER'} | "
        f"Events: {report['recent_events']} | "
        f"Locks: {len(report['locks'])} stale | "
        f"Warnings: {len(report['warnings'])}"
    )

    return report


def main():
    log.info("Weltkern-Watchdog startet")
    report = run_check()

    # Bericht als JSON speichern
    report_file = LOG_DIR / "weltkern_letzter_bericht.json"
    report_file.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    if report["warnings"]:
        log.warning(f"{len(report['warnings'])} Warnungen: {'; '.join(report['warnings'])}")
    else:
        log.info("Alle Checks bestanden — Weltkern gesund")


if __name__ == "__main__":
    main()
