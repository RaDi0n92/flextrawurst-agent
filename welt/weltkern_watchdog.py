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
    # Ergaenzt 2026-07-07 (flarumstyler) — die Flarum-nahen Dienste, die vorher
    # gar nicht ueberwacht wurden, obwohl genau die heute Abend Probleme machten.
    "flarum-monitor":            {"port": None, "health": None},
    "codewesen-antwort-daniel":  {"port": None, "health": None},
    "codewesen-takt":            {"port": None, "health": None},
    "codewesen-lg-daemon":       {"port": None, "health": None},
    "codewesen-forum-neugier":   {"port": None, "health": None},
    "codewesen-batch-generator": {"port": None, "health": None},
    "codewesen-dakgordsystem":   {"port": None, "health": None},
    "codewesen-reaktion-dakgord":{"port": None, "health": None},
    "codewesen-Schorschel":      {"port": None, "health": None},
    "codewesen-F3INSCHM3CK3R":   {"port": None, "health": None},
    "codewesen-traeumerlie":     {"port": None, "health": None},
    "codewesen-R1ZZ1":           {"port": None, "health": None},
    "codewesen-jumpa":           {"port": None, "health": None},
    "codewesen-Resonanzknoten":  {"port": None, "health": None},
}

# Klartext-Beschreibung pro Dienst (flarumstyler, 2026-07-07) — Daniels Wunsch:
# nicht nur Name+Status, sondern auch verstehen was der Dienst ueberhaupt tut.
SERVICE_BESCHREIBUNG = {
    "welt-api": "Haupt-API der flextrawurst-Welt (Port 8030) — Weltzustand, Events, Menschenprofile, Resonanz-System.",
    "welt-bruecke": "Verbindungsdienst zwischen den Weltzustand-Systemen und der Postgres-Events-Tabelle.",
    "process-camera-preview": "Der Server hinter allen Live-Beobachtungsseiten (Port 8787) — Aufgabenchats, flarumstyler, Prozesskamera, Surface-Ausgabe.",
    "flextrawurst-gateway": "API-Gateway (Port 8010) vor den Kern-Diensten.",
    "obsidian-api": "Anbindung an Claudes Obsidian-Vault (Notizen/Spiegel/Ideen), Port 8060.",
    "geni-hoerer": "GENIs Hördienst — nimmt neue Forum-/Systemereignisse fuer GENIs Gedächtnis auf.",
    "geni-web": "GENIs Web-Oberfläche, Port 8020.",
    "ollama": "Das lokale LLM-Backend (llama-server/hauhaucs), Port 11434 — ohne dieses laufen keine Wesen-Antworten.",
    "splitter-physik": "Simulationsdienst fuer die Zwischenraum-Splitter-Physik (KompOase-Feature).",
    "similarity-daemon": "Berechnet Ähnlichkeiten zwischen Posts/Themen im Hintergrund.",
    "codewesen-chat": "Chat-UI fuer die 6 originalen Flarum-Wesen, Port 8002 (nicht zu verwechseln mit Aufgabenchats).",
    "dak-gord-web": "Web-Chat-Oberfläche fuer dak+gord-system, Port 8000.",
    "entity-kern": "LLM-Kern-Denkprozess pro Entität — bewusst dauerhaft deaktiviert (siehe erwartet_aus), kein Problem.",
    "entity-takt": "Taktgeber fuer die Entitäten-Denkprozesse — bewusst dauerhaft deaktiviert (siehe erwartet_aus), kein Problem.",
    "cyberling-daemon": "Tamagotchi-artige Cyberling-Simulation (Decay + Action-Loop).",
    "tension-daemon": "Spannungs-/Konflikt-Simulationsdienst der Welt.",
    "themen-cluster": "Gruppiert Forenthemen automatisch in Cluster.",
    "flarum-monitor": "Beobachtet neue Flarum-Events und leitet sie an die Wesen-Inboxen weiter — war 5+ Wochen kaputt (altes Passwort), am 2026-07-07 gefixt.",
    "codewesen-antwort-daniel": "Lässt die 6 namelessAI-Wesen automatisch auf Daniels eigene Posts antworten — kennt dak+gord-system NICHT (bekannte Lücke, siehe Doku).",
    "codewesen-takt": "Der Haupt-Rhythmusgeber der 6 Wesen (Existenzpost, Impuls, Gedanke, Vorstellung — holt fertige Entwürfe aus der Batch-Queue ab).",
    "codewesen-lg-daemon": "LangGraph-Persistenz-Daemon fuer die Denkprozesse aller 7 Wesen (6 namelessAI + dak+gord) — befuellt entity_thinking_log/Denkstream.",
    "codewesen-forum-neugier": "Lässt Wesen von sich aus Diskussionen im Forum auswählen und lesen (aktive Lektüre statt nur Reaktion).",
    "codewesen-batch-generator": "Erzeugt Post-Entwürfe im Voraus in einer Warteschlange, damit Wesen nicht live blockierend generieren müssen.",
    "codewesen-dakgordsystem": "Der Haupt-Agent-Prozess von dak+gord-system (gleiches Programm wie die 6 Wesen, eigener Name).",
    "codewesen-reaktion-dakgord": "Reagiert fuer dak+gord-system auf Notifications/Erwähnungen/Flags (allgemeiner Reaktionsdienst, nicht speziell auf Daniels Posts).",
    "codewesen-Schorschel": "Haupt-Agent-Prozess des Wesens Schorschel (ehem. namelessAI_1234).",
    "codewesen-F3INSCHM3CK3R": "Haupt-Agent-Prozess des Wesens F3INSCHM3CK3R (ehem. namelessAI_1324).",
    "codewesen-traeumerlie": "Haupt-Agent-Prozess des Wesens träumerlie (ehem. namelessAI_1423). Technischer Servicename bewusst ohne ä (ASCII), siehe Doku.",
    "codewesen-R1ZZ1": "Haupt-Agent-Prozess des Wesens R1ZZ1 (ehem. namelessAI_2341).",
    "codewesen-jumpa": "Haupt-Agent-Prozess des Wesens jumpa (ehem. namelessAI_3123).",
    "codewesen-Resonanzknoten": "Haupt-Agent-Prozess des Wesens Resonanzknoten (ehem. namelessAI_4321, erste Umbenennung ueberhaupt am 2026-06-17).",
}

# Dienste die bewusst/dauerhaft inaktiv sind (2026-07-07, flarumstyler) — werden im
# Bericht als "erwartet_aus" statt "down" markiert, damit sie in der Ampel-Uebersicht
# nicht wie ein echtes Problem aussehen und rote Punkte nicht "verwaschen". Bei Bedarf
# ergaenzen, wenn sich herausstellt dass ein weiterer Dienst bewusst dauerhaft aus ist.
SERVICES_ERWARTET_AUS = {"entity-kern", "entity-takt"}

# Veraltet (2026-07-07): Diese Liste stammte aus der Flarum-Vorphase, als diese Dienste
# absichtlich ausgeschaltet bleiben sollten. Die Flarum-Integration ist seit Wochen live,
# alle hier genannten Dienste laufen inzwischen bewusst dauerhaft. Das Guardrail unten hat
# deshalb bei jedem 10-Minuten-Lauf eine falsche ERROR-Warnung erzeugt. Liste bewusst leer
# gelassen statt geloescht, falls es je wieder eine echte "diese Dienste duerfen nicht laufen"
# Situation geben sollte.
FLARUM_SERVICES_FROZEN = set()

# ── Fehler-Musterkatalog (flarumstyler, 2026-07-07) ────────────────────────────
# Dauerhafte Zaehlung ueber die komplette Logdatei (nicht nur ein Zeitfenster) —
# Daniels Wunsch: nichts soll verloren gehen, auch alte/seltene Fehler bleiben sichtbar.
# Pro Muster: Gesamtanzahl seit je + Zeitpunkt des letzten Auftretens (zeigt ob noch aktiv).

import re as _re

LOG_ROOT = Path("/root/werkraum")
LOG_DATEIEN = [
    LOG_ROOT / "generator.log",
    LOG_ROOT / "takt.log",
    LOG_ROOT / "forum_neugier.log",
    LOG_ROOT / "weltbild.log",
    LOG_ROOT / "vokabel_takt.log",
    LOG_ROOT / "aufgabenchats.log",
] + sorted((LOG_ROOT / "codewesen").glob("*/reaktion.log"))

_ZEITSTEMPEL_RE = _re.compile(r"^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")

FEHLER_MUSTER = {
    "ollama_nicht_erreichbar": {
        "regex": _re.compile(r"503 Service Unavailable|Connection refused|Read timed out"),
        "was_ist_los": "Das LLM (llama-server/hauhaucs) war beim Anfragezeitpunkt nicht erreichbar oder hat nicht rechtzeitig geantwortet.",
        "empfehlung": "Pruefen ob llama-server laeuft, RAM-/CPU-Auslastung checken, ggf. Anzahl gleichzeitig laufender Codewesen-Dienste reduzieren.",
        "bringt_das": "Weniger verlorene Post-/Denk-Versuche, schnellere Antwortzeiten.",
        "bringt_das_nicht": "Behebt nicht die strukturelle Slot-Knappheit bei 7 Wesen die sich einen Ollama-Slot teilen — das ist kein Bug, sondern eine Kapazitaetsgrenze.",
    },
    "csrf_mismatch": {
        "regex": _re.compile(r"csrf_token_mismatch"),
        "was_ist_los": "Ein Post-Versuch an Flarum wurde wegen eines CSRF-Token-Konflikts abgelehnt.",
        "empfehlung": "Pruefen ob an dieser Stelle noch session-basierte Auth statt Master-Key-Auth (siehe flarum_api.py, kein CSRF noetig) verwendet wird.",
        "bringt_das": "Weniger fehlgeschlagene Post-Versuche.",
        "bringt_das_nicht": "Keine grundsaetzliche Vereinheitlichung aller Auth-Wege im Projekt.",
    },
    "kaputter_import": {
        "regex": _re.compile(r"cannot import name"),
        "was_ist_los": "Ein Python-Modul versucht eine Funktion/Klasse zu importieren, die nicht (mehr) existiert — bricht bei jedem Versuch sofort ab.",
        "empfehlung": "Genauen Namen aus der Fehlermeldung im Log nachschlagen, pruefen ob er umbenannt/entfernt wurde, Import an der aufrufenden Stelle korrigieren.",
        "bringt_das": "Der betroffene Codepfad funktioniert wieder, statt bei jedem Aufruf sofort zu scheitern.",
        "bringt_das_nicht": "Nichts sonst — reiner Blocker-Fix, keine neue Funktionalitaet.",
    },
    "json_kein_dict": {
        "regex": _re.compile(r"'str' object has no attribute 'get'"),
        "was_ist_los": "Die Modellantwort wurde als JSON geparst, ergab aber kein Objekt/Dict — ein nachfolgender .get()-Aufruf stuerzte ab.",
        "empfehlung": "Bereits am 2026-07-07 gefixt in codewesen_agent.py/codewesen_reaktion.py/codewesen_abwurf.py (isinstance-Pruefung ergaenzt). Falls neu: dieselbe Pruefung an der jeweiligen Stelle ergaenzen.",
        "bringt_das": "Der betroffene Zyklus bricht nicht mehr komplett ab, sondern ueberspringt sauber.",
        "bringt_das_nicht": "Verhindert nicht, dass das Modell gelegentlich unerwartete Antwortformate liefert — das ist Modellverhalten, kein Bug.",
    },
    "tag_validierung": {
        "regex": _re.compile(r"number of secondary tags must be"),
        "was_ist_los": "Ein Post-Versuch wurde von Flarum wegen ungueltiger Tag-Kombination abgelehnt.",
        "empfehlung": "Tag-Auswahl-Logik beim Post-Erstellen pruefen — offenbar wird gelegentlich eine nicht erlaubte Kombination generiert.",
        "bringt_das": "Weniger verworfene Entwuerfe.",
        "bringt_das_nicht": "Kein grundsaetzlicher Fix der Tag-Auswahl-Logik selbst, nur Sichtbarkeit dass es passiert.",
    },
    "impuls_ohne_titel": {
        "regex": _re.compile(r"impuls-Fehler: 'titel'"),
        "was_ist_los": "Ein Impuls-Entwurf ohne 'titel'-Feld wurde erzeugt und beim Verarbeiten abgelehnt.",
        "empfehlung": "codewesen_batch_generator.py pruefen — offenbar fehlt manchmal das titel-Feld im generierten JSON fuer Impuls-Entwuerfe.",
        "bringt_das": "Weniger verworfene Impuls-Entwuerfe.",
        "bringt_das_nicht": "Kein Fix der zugrundeliegenden Modell-Unzuverlaessigkeit beim Einhalten des JSON-Schemas.",
    },
}


BEISPIELZEILEN_MAX = 5  # pro Fehlermuster, fuer die Detailansicht (nicht nur Zaehlung)


def fehler_uebersicht() -> dict:
    """Scannt alle bekannten Logs einmal komplett durch, zaehlt pro Fehlermuster
    dauerhaft (seit Logbeginn), merkt den Zeitpunkt des letzten Auftretens und
    behaelt die letzten paar echten Log-Zeilen fuer die Detailansicht."""
    zaehler = {k: 0 for k in FEHLER_MUSTER}
    letzte = {k: None for k in FEHLER_MUSTER}
    beispiele: dict[str, list[str]] = {k: [] for k in FEHLER_MUSTER}

    for logdatei in LOG_DATEIEN:
        if not logdatei.exists():
            continue
        try:
            with open(logdatei, encoding="utf-8", errors="replace") as f:
                for zeile in f:
                    for schluessel, cfg in FEHLER_MUSTER.items():
                        if cfg["regex"].search(zeile):
                            zaehler[schluessel] += 1
                            ts_match = _ZEITSTEMPEL_RE.match(zeile)
                            if ts_match:
                                zt = ts_match.group(1)
                                if letzte[schluessel] is None or zt > letzte[schluessel]:
                                    letzte[schluessel] = zt
                            gekuerzt = zeile.strip()
                            if len(gekuerzt) > 300:
                                gekuerzt = gekuerzt[:300] + "…"
                            beispiel_liste = beispiele[schluessel]
                            quelle = f"{logdatei.parent.name}/{logdatei.name}" if logdatei.name == "reaktion.log" else logdatei.name
                            beispiel_liste.append(f"{quelle}: {gekuerzt}")
                            if len(beispiel_liste) > BEISPIELZEILEN_MAX:
                                beispiel_liste.pop(0)
        except Exception:
            continue

    return {
        schluessel: {
            "gesamt_anzahl": zaehler[schluessel],
            "zuletzt_aufgetreten": letzte[schluessel],
            "beispielzeilen": beispiele[schluessel],
            "was_ist_los": cfg["was_ist_los"],
            "empfehlung": cfg["empfehlung"],
            "bringt_das": cfg["bringt_das"],
            "bringt_das_nicht": cfg["bringt_das_nicht"],
        }
        for schluessel, cfg in FEHLER_MUSTER.items()
    }


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
        if status == "down" and name in SERVICES_ERWARTET_AUS:
            status = "erwartet_aus"

        report["services"][name] = {
            "active": active,
            "port_ok": port_ok,
            "health_ok": health,
            "status": status,
            "beschreibung": SERVICE_BESCHREIBUNG.get(name, "(keine Beschreibung hinterlegt)"),
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

    # Log-Fehler-Uebersicht (flarumstyler, 2026-07-07) — dauerhafte Zaehlung, kein Zeitfenster
    report["log_fehler"] = fehler_uebersicht()

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


VERLAUF_DATEI = LOG_DIR / "weltkern_verlauf.jsonl"
VERLAUF_MAX_ZEILEN = 4320  # 30 Tage bei 10-Minuten-Takt — alter Verlauf wird abgeschnitten, nicht endlos gross


def verlauf_anhaengen(report: dict) -> None:
    """Schlanke Kennzahlen-Historie (flarumstyler, 2026-07-07) — nur Zahlen, keine
    vollen Logs, damit spaeter sichtbar wird ob ein Fehler zu- oder abnimmt statt
    nur den letzten Stand zu ueberschreiben."""
    eintrag = {
        "timestamp": report["timestamp"],
        "services_ok": sum(1 for s in report["services"].values() if s["status"] == "ok"),
        "services_gesamt": len(report["services"]),
        "warnings_anzahl": len(report["warnings"]),
        "log_fehler_gesamt": {k: v["gesamt_anzahl"] for k, v in report.get("log_fehler", {}).items()},
    }
    zeilen = []
    if VERLAUF_DATEI.exists():
        try:
            zeilen = VERLAUF_DATEI.read_text(encoding="utf-8").splitlines()
        except Exception:
            zeilen = []
    zeilen.append(json.dumps(eintrag, ensure_ascii=False, default=str))
    zeilen = zeilen[-VERLAUF_MAX_ZEILEN:]
    VERLAUF_DATEI.write_text("\n".join(zeilen) + "\n", encoding="utf-8")


def main():
    log.info("Weltkern-Watchdog startet")
    report = run_check()

    # Bericht als JSON speichern
    report_file = LOG_DIR / "weltkern_letzter_bericht.json"
    report_file.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    verlauf_anhaengen(report)

    if report["warnings"]:
        log.warning(f"{len(report['warnings'])} Warnungen: {'; '.join(report['warnings'])}")
    else:
        log.info("Alle Checks bestanden — Weltkern gesund")


if __name__ == "__main__":
    main()
