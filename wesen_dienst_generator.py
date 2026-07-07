#!/usr/bin/env python3
"""
wesen_dienst_generator.py — erzeugt aus einer wesen_eigene_dienste-Zeile ein echtes,
eigenstaendiges Python-Skript (in wesen_eigene_skripte/) + eine systemd-Unit-Datei.
Das generierte Skript kopiert KEINE Logik aus codewesen_agent.py, sondern importiert
dessen Bausteine (agentic_loop, fuehre_aktion_aus, setup_log, load_token,
get_tags_cached, BASE) — ein Bugfix/eine Verbesserung dort wirkt damit automatisch
auch in jedem generierten Dienst.

erzeuge() schreibt nur Dateien + macht daemon-reload. Start/Stop/Enable sind
bewusst getrennte Funktionen (analog zum Bestaetigungs-Muster in flarumstyler:
Erzeugen ist ungefaehrlich, Start eines neuen Dauerprozesses nicht).
"""

import re
import subprocess
from pathlib import Path

import wesen_eigene_dienste as wed

SKRIPT_VERZEICHNIS = Path("/root/werkraum/wesen_eigene_skripte")
UNIT_VERZEICHNIS = Path("/etc/systemd/system")
_NAME_MUSTER = re.compile(r"^[a-zA-Z0-9_.-]+$")


def _pruefe_dienst_name(dienst_name: str) -> None:
    """dienst_name fliesst in Dateipfade + systemctl-Aufrufe ein — vor dem
    Schreiben/Ausfuehren immer gegen ein sicheres Zeichenset pruefen."""
    if not _NAME_MUSTER.match(dienst_name):
        raise ValueError(f"Unsicherer dienst_name: {dienst_name!r} (nur a-z, A-Z, 0-9, _, ., - erlaubt)")


def _skript_inhalt(row: dict) -> str:
    dienst_name = row["dienst_name"]
    wesen = row["wesen"]
    return f'''#!/usr/bin/env python3
"""
AUTO-GENERIERT von wesen_dienst_generator.py — NICHT VON HAND BEARBEITEN.
Aenderungen an Takt/Verhalten/Ziel bitte in der Tabelle wesen_eigene_dienste
(ueber flarumstyler) vornehmen, danach den Dienst per Regenerieren neu schreiben
und neu starten lassen (dieses Skript liest Takt/Verhalten/Ziel nur beim Start).

Wesen-eigener Rhythmus: {row["anzeige_name"]!r} fuer {wesen}.
dienst_name: {dienst_name}
"""
import datetime
import logging
import sys
import time

sys.path.insert(0, "/root/werkraum")
import codewesen_agent as ca
import wesen_eigene_dienste as wed

DIENST_NAME = {dienst_name!r}
WESEN = {wesen!r}


def _setup_log() -> logging.Logger:
    """Eigener Log-Ordner statt ca.setup_log() -- die teilt sich reaktion.log mit dem
    Haupt-Agent-Prozess des Wesens und erwartet einen bereits existierenden
    BASE/<wesen>-Ordner, kein beliebiges Label."""
    log_dir = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(DIENST_NAME)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(str(log_dir / "betrieb.log"))
        handler.setFormatter(logging.Formatter(f"%(asctime)s [{{DIENST_NAME}}] %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler())
    return logger


def _vault_speichern(inhalt: str, log):
    vault_dir = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME
    vault_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M")
    (vault_dir / f"{{ts}}.md").write_text(
        f"<!-- autor: {{WESEN}} | dienst: {{DIENST_NAME}} | datum: {{ts}} UTC -->\\n\\n{{inhalt}}\\n",
        encoding="utf-8",
    )
    log.info("[%s] Vault-Eintrag gespeichert: %s.md", DIENST_NAME, ts)


def _einen_zyklus(row: dict, token: str, all_tags: list, log):
    ziel_typ = row["ziel_typ"]
    verhalten = row["verhalten_prompt"]

    if ziel_typ == "fester_thread":
        disk_id = row["ziel_discussion_id"]
        kontext = f"{{verhalten}}\\n\\nAntworte mit 'antworten' und discussion_id {{disk_id}}."
    elif ziel_typ == "neue_diskussion":
        kontext = f"{{verhalten}}\\n\\nEroeffne dafuer eine neue Diskussion ('neue_diskussion') mit Titel, Inhalt und tag_ids."
    else:  # vault_only
        kontext = verhalten

    decision = ca.agentic_loop(WESEN, token, kontext, log, all_tags)

    if ziel_typ == "vault_only":
        inhalt = decision.get("inhalt") or decision.get("begruendung") or ""
        _vault_speichern(inhalt, log)
        return

    if ziel_typ == "fester_thread":
        if decision.get("aktion") != "antworten":
            decision = {{
                "aktion": "antworten",
                "discussion_id": row["ziel_discussion_id"],
                "inhalt": decision.get("inhalt") or decision.get("begruendung") or "...",
            }}
        decision["discussion_id"] = row["ziel_discussion_id"]
    elif ziel_typ == "neue_diskussion" and decision.get("aktion") == "neue_diskussion":
        if not decision.get("tag_ids") and row.get("ziel_tag_ids"):
            decision["tag_ids"] = row["ziel_tag_ids"]

    ca.fuehre_aktion_aus(WESEN, token, decision, all_tags, log)


def haupt_schleife():
    log = _setup_log()
    row = wed.lade(DIENST_NAME)
    if not row:
        log.error("Keine Konfiguration fuer %s in wesen_eigene_dienste gefunden — beende.", DIENST_NAME)
        return

    token = ca.load_token(WESEN)
    all_tags = ca.get_tags_cached(token)
    log.info("Wesen-eigener Dienst gestartet: %s (Takt %ss, Offset %ss)",
              DIENST_NAME, row["takt_sekunden"], row["start_offset_sekunden"])

    letzter_lauf = time.time() - row["takt_sekunden"] + row["start_offset_sekunden"]

    while True:
        aktueller_status = wed.lade(DIENST_NAME)
        if not aktueller_status or aktueller_status.get("status") != "aktiv":
            log.info("Deaktiviert oder aus DB entfernt — Schleife pausiert (60s)")
            time.sleep(60)
            continue

        jetzt = time.time()
        if jetzt - letzter_lauf >= row["takt_sekunden"]:
            try:
                _einen_zyklus(row, token, all_tags, log)
            except Exception as e:
                log.error("Zyklus-Fehler: %s", e)
            letzter_lauf = time.time()

        time.sleep(15)


if __name__ == "__main__":
    haupt_schleife()
'''


def _unit_inhalt(row: dict, script_pfad: Path) -> str:
    return f"""[Unit]
Description=Wesen-eigener Dienst — {row["anzeige_name"]} ({row["wesen"]})
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/werkraum
ExecStart=/usr/bin/python3 {script_pfad}
Restart=always
RestartSec=20
EnvironmentFile=/root/werkraum/.agent/flarum.env
EnvironmentFile=/root/werkraum/.agent/flextrawurst-db.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


def erzeuge(dienst_name: str) -> dict:
    """Liest die Definition aus der DB, schreibt Skript + Unit, macht daemon-reload,
    aktualisiert script_pfad/unit_name in der DB. Startet/enabled NICHT."""
    _pruefe_dienst_name(dienst_name)
    row = wed.lade(dienst_name)
    if not row:
        raise ValueError(f"Kein Eintrag in wesen_eigene_dienste fuer {dienst_name!r}")

    SKRIPT_VERZEICHNIS.mkdir(parents=True, exist_ok=True)
    script_pfad = SKRIPT_VERZEICHNIS / f"{dienst_name}.py"
    script_pfad.write_text(_skript_inhalt(row), encoding="utf-8")
    script_pfad.chmod(0o755)

    unit_name = f"{dienst_name}.service"
    unit_pfad = UNIT_VERZEICHNIS / unit_name
    unit_pfad.write_text(_unit_inhalt(row, script_pfad), encoding="utf-8")

    subprocess.run(["systemctl", "daemon-reload"], check=True)

    wed.setze_skript_und_unit(dienst_name, str(script_pfad), unit_name)
    return {"script_pfad": str(script_pfad), "unit_name": unit_name}


def _systemctl(aktion: str, unit_name: str) -> subprocess.CompletedProcess:
    if aktion not in ("start", "stop", "restart", "enable", "disable"):
        raise ValueError(f"Unbekannte Aktion: {aktion}")
    return subprocess.run(["systemctl", aktion, unit_name], capture_output=True, text=True)


def starten(dienst_name: str) -> subprocess.CompletedProcess:
    _pruefe_dienst_name(dienst_name)
    return _systemctl("start", f"{dienst_name}.service")


def stoppen(dienst_name: str) -> subprocess.CompletedProcess:
    _pruefe_dienst_name(dienst_name)
    return _systemctl("stop", f"{dienst_name}.service")


def neustarten(dienst_name: str) -> subprocess.CompletedProcess:
    _pruefe_dienst_name(dienst_name)
    return _systemctl("restart", f"{dienst_name}.service")


def deaktivieren(dienst_name: str) -> None:
    """Grundgesetz 4: nie hart loeschen. Stoppt + disabled den systemd-Dienst und
    setzt status='deaktiviert' in der DB — Skript/Unit-Dateien bleiben liegen."""
    _pruefe_dienst_name(dienst_name)
    _systemctl("stop", f"{dienst_name}.service")
    _systemctl("disable", f"{dienst_name}.service")
    wed.setze_status(dienst_name, "deaktiviert")
