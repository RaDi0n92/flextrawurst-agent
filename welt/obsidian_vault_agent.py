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
# gleiche Reihenfolge wie ENTITY_KEYS in browser_agent.py. Nur Schorschel ist
# bisher als Container tatsächlich aufgesetzt (Pilot, 2026-07-21).
VAULT_PORTS = {
    "Schorschel": (3093, 3193),
    "F3INSCHM3CK3R": (3094, 3194),
    "träumerlie": (3095, 3195),
    "R1ZZ1": (3096, 3196),
    "jumpa": (3097, 3197),
    "Resonanzknoten": (3098, 3198),
    "dak+gord-system": (3099, 3199),
}


def _container_name(entity_id: str) -> str:
    return f"obsidian-{entity_id.lower().replace('+', '').replace(' ', '-')}"


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
    passwort = os.environ.get(f"WESEN_VAULT_OBSIDIAN_PASSWORD_{entity_id}", "")
    if not passwort:
        raise RuntimeError(f"Kein Obsidian-Vault-Passwort für {entity_id} gesetzt "
                            f"(WESEN_VAULT_OBSIDIAN_PASSWORD_{entity_id})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1280, "height": 800},
            http_credentials={"username": entity_id.lower(), "password": passwort},
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
