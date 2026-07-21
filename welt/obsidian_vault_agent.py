#!/usr/bin/env python3
"""
Obsidian-Vault-Agent: schreibt für ein Wesen sichtbar, zeichenweise, ohne LLM-Call
pro Taste in dessen eigenen Obsidian-Vault (eigener Docker-Container pro Wesen).

Daniels Auftrag, wörtlich (2026-07-21): "eine ganz neue art von vault erzeugt vom
wesen selbst ... aber ich will es ohne llm call ich will schreiben in genau der
menschenart und weise ... tippen wie auf der schreibmaschiene".

Zwei getrennte Kanäle, bewusst nicht vermischt:
  - Playwright (http_credentials, NICHT extra_http_headers -- der WebSocket-
    Handshake von Selkies überlebt sonst nicht) steuert Navigation/Klicks im
    sichtbaren Fenster: Ctrl+O ("Quick Switcher") um eine Datei zuverlässig
    zu öffnen, unabhängig von ihrer Position in der Seitenleiste.
  - xdotool via `docker exec` tippt den eigentlichen Text -- komplett am
    Browser/Selkies vorbei, direkt in die X11-Sitzung des Containers. Das ist
    KEIN Performance-Trick, sondern die einzige Methode die überhaupt
    funktioniert: page.keyboard.type() verliert jede Großschreibung auf dem
    Weg durch Selkies, page.keyboard.insert_text() kommt gar nicht erst an.

Gefundene und gelöste Fallstricke (siehe docs/systemdoku/30_wesen_eigene_obsidian_vaults.md):
  - Ctrl+N-Notizen werden nie richtig an eine Datei auf der Platte gebunden --
    Text erscheint im Editor (Backspace löscht ihn wirklich!), aber landet nie
    auf Platte, egal wie lange gewartet oder wie oft Ctrl+S gedrückt wird. Fix:
    Datei IMMER vorher direkt als echte Datei erzeugen (schreibe_leere_datei),
    nie über Ctrl+N in der App selbst.
  - Großbuchstaben-Umlaute (Ä/Ö/Ü) am Anfang eines xdotool-type-Laufs bleiben
    klein -- einzige bekannte Lücke, von Daniel ausdrücklich als unwichtig
    abgesegnet ("scheiss auf großung kleinschreibung mach ich ja auch nicht").
"""

import logging
import subprocess
from pathlib import Path

log = logging.getLogger("obsidian-vault-agent")

VAULT_ROOT = Path("/root/werkraum/wesen_vaults")

# Port-Schema: Hauptport (Selkies-Web-GUI) / Zweitport, je einer pro Wesen,
# gleiche Reihenfolge wie ENTITY_KEYS in browser_agent.py.
VAULT_PORTS = {
    "Schorschel": (3093, 3193),
    "F3INSCHM3CK3R": (3094, 3194),
    "träumerlie": (3095, 3195),
    "R1ZZ1": (3096, 3196),
    "jumpa": (3097, 3197),
    "Resonanzknoten": (3098, 3198),
    "dak+gord-system": (3099, 3199),
}

# Externe HTTPS-Ports (nginx, doppelte Basic-Auth: nginx-Ebene + Container-Ebene),
# gleiches Muster wie das bestehende /etc/nginx/sites-available/obsidian.
VAULT_EXTERN_PORTS = {
    "Schorschel": 8445,
    "F3INSCHM3CK3R": 8450,
    "träumerlie": 8451,
    "R1ZZ1": 8452,
    "jumpa": 8453,
    "Resonanzknoten": 8454,
    "dak+gord-system": 8455,
}

# Docker-Containernamen und Basic-Auth-Benutzernamen: explizit statt aus dem
# entity_id abgeleitet -- Docker-Containernamen erlauben nur [a-zA-Z0-9_.-],
# "träumerlie" (Umlaut) und "dak+gord-system" ("+") würden bei automatischer
# Ableitung ungültige oder inkonsistente Namen erzeugen (dieselbe Bug-Klasse
# wie das systemd-%i-vs-%I-Problem vom selben Tag, siehe 29_browser_agent_aktivierung.md).
CONTAINER_NAMES = {
    "Schorschel": "obsidian-schorschel",
    "F3INSCHM3CK3R": "obsidian-f3inschmecker",
    "träumerlie": "obsidian-traeumerlie",
    "R1ZZ1": "obsidian-r1zz1",
    "jumpa": "obsidian-jumpa",
    "Resonanzknoten": "obsidian-resonanzknoten",
    "dak+gord-system": "obsidian-dakgordsystem",
}
CONTAINER_USERS = {
    "Schorschel": "schorschel",
    "F3INSCHM3CK3R": "f3inschmecker",
    "träumerlie": "traeumerlie",
    "R1ZZ1": "r1zz1",
    "jumpa": "jumpa",
    "Resonanzknoten": "resonanzknoten",
    "dak+gord-system": "dakgordsystem",
}

# Suffix der Passwort-Umgebungsvariable in .agent/wesen-vaults.env -- ASCII-
# GROSS, aus demselben Grund wie CONTAINER_NAMES/CONTAINER_USERS: bash erlaubt
# weder Umlaute noch "+" in Variablennamen (gefunden 2026-07-21 beim Aufsetzen
# der übrigen 6 Container: `source` übersprang die betroffenen Zeilen lautlos,
# der Loop brach beim ersten ungültigen Namen komplett ab).
ENV_PASSWORT_SUFFIX = {
    "Schorschel": "SCHORSCHEL",
    "F3INSCHM3CK3R": "F3INSCHMECKER",
    "träumerlie": "TRAEUMERLIE",
    "R1ZZ1": "R1ZZ1",
    "jumpa": "JUMPA",
    "Resonanzknoten": "RESONANZKNOTEN",
    "dak+gord-system": "DAKGORDSYSTEM",
}


def _container_name(entity_id: str) -> str:
    return CONTAINER_NAMES[entity_id]


def vault_pfad(entity_id: str) -> Path:
    return VAULT_ROOT / entity_id


def schreibe_leere_datei(entity_id: str, dateiname: str, titel: str | None = None) -> Path:
    """Legt eine neue Datei direkt auf der Platte an (NIE über Ctrl+N in Obsidian
    selbst -- siehe Moduldoku, das bindet den Editor-Puffer nie an eine echte Datei)."""
    if not dateiname.endswith(".md"):
        dateiname += ".md"
    ziel = vault_pfad(entity_id) / dateiname
    ziel.parent.mkdir(parents=True, exist_ok=True)
    inhalt = f"{titel}\n\n" if titel else ""
    ziel.write_text(inhalt, encoding="utf-8")
    return ziel


def _xdotool(entity_id: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    container = _container_name(entity_id)
    cmd = ["docker", "exec", container, "bash", "-c",
           "export DISPLAY=:1; xdotool " + " ".join(args)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def tippe_text(entity_id: str, text: str, delay_ms: int = 65) -> None:
    """Tippt text zeichenweise in das aktuell fokussierte Element des Wesen-eigenen
    Obsidian-Fensters -- via xdotool, nicht Playwright (siehe Moduldoku)."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    r = _xdotool(entity_id, "type", "--delay", str(delay_ms), f'"{escaped}"',
                 timeout=max(30, len(text) * delay_ms // 1000 + 15))
    if r.returncode != 0:
        log.warning("%s: xdotool type Fehler: %s", entity_id, r.stderr)


def oeffne_datei_und_schreibe(entity_id: str, dateiname: str, text: str,
                                titel: str | None = None, delay_ms: int = 65) -> Path:
    """Kompletter Ablauf: Datei anlegen (falls nicht vorhanden), über den Quick
    Switcher (Ctrl+O) im Wesen-eigenen Obsidian-Fenster öffnen, ans Ende springen,
    text zeichenweise antippen. Erfordert eine offene Playwright-Verbindung zum
    jeweiligen Container -- siehe browser_agent.py für das Verbindungsmuster
    (http_credentials, NICHT extra_http_headers)."""
    from playwright.sync_api import sync_playwright
    import os

    ziel = vault_pfad(entity_id) / (dateiname if dateiname.endswith(".md") else dateiname + ".md")
    if not ziel.exists():
        schreibe_leere_datei(entity_id, dateiname, titel)

    port, _ = VAULT_PORTS[entity_id]
    env_key = f"WESEN_VAULT_OBSIDIAN_PASSWORD_{ENV_PASSWORT_SUFFIX[entity_id]}"
    passwort = os.environ.get(env_key, "")
    if not passwort:
        raise RuntimeError(f"Kein Obsidian-Vault-Passwort für {entity_id} gesetzt ({env_key})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1280, "height": 800},
            http_credentials={"username": CONTAINER_USERS[entity_id], "password": passwort},
        )
        page.goto(f"http://localhost:{port}/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(5000)
        page.keyboard.press("Control+o")
        page.wait_for_timeout(600)
        page.keyboard.type(dateiname.removesuffix(".md"), delay=40)
        page.wait_for_timeout(600)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1000)
        page.keyboard.press("Control+End")
        page.wait_for_timeout(300)
        # xdotool-Tipplauf laeuft WAEHREND die Playwright-Verbindung noch offen ist --
        # ein browser.close() unmittelbar davor reisst den Tipplauf mittendrin ab
        # (gefunden 2026-07-21: Text brach nach ca. der Haelfte lautlos ab, xdotool
        # selbst meldete trotzdem Erfolg -- die Unterbrechung passiert auf der
        # Empfaengerseite, nicht bei xdotool).
        tippe_text(entity_id, text, delay_ms=delay_ms)
        page.wait_for_timeout(500)
        browser.close()

    return ziel
