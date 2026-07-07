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
und neu starten lassen (dieses Skript liest Takt/Verhalten/Ziel nur beim Start,
bzw. bei jedem DB-Reload vor einem Zyklus -- siehe _versuche_zyklus()).

Wesen-eigener Rhythmus: {row["anzeige_name"]!r} fuer {wesen}.
dienst_name: {dienst_name}

Baukasten v2 (2026-07-07, siehe _claude/konzepte/2026-07-07_wesen_dienst_baukasten_v2.md):
Phase 1 -- weiterhin ein einzelnes Wesen pro Dienst, aber mit erweiterten
Ziel-Varianten, eigenen Feldern (weiche/harte Bedingungen), einer wachsenden
Takt-Liste, festen Uhrzeiten, Pausenzeiten und einem Passiv-Modus. Alles davon
lebt in der Spalte meta (JSONB) -- Grundgesetz 1: neue Faehigkeiten erweitern,
nicht den Kern umbauen. Ist meta leer/alt (Dienst vor Baukasten-v2 angelegt),
verhaelt sich dieses Skript exakt wie die Vorgaenger-Version: ein Takt, Intervall-
Loop, keine Bedingungen.
"""
import datetime
import json
import logging
import sys
import time

sys.path.insert(0, "/root/werkraum")
import codewesen_agent as ca
import gedaechtnis as gd
import wesen_eigene_dienste as wed

DIENST_NAME = {dienst_name!r}
WESEN = {wesen!r}

_OPERATOREN = {{"gt": lambda a, b: a > b, "lt": lambda a, b: a < b, "eq": lambda a, b: a == b}}


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


def _meta(row: dict) -> dict:
    m = row.get("meta")
    return m if isinstance(m, dict) else {{}}


def _alle_takte(row: dict) -> list:
    """Haupt-Takt (Kernspalten, immer vorhanden) + optionale, einzeln von Daniel
    dazu erschaffene benannte Takte aus meta['takte'] -- wachsende Liste, kein
    festes Kontingent (siehe Konzept: 'einen Takt komplett anlegen, dann optional
    einen weiteren')."""
    haupt = {{"name": "haupt", "sekunden": row["takt_sekunden"], "aufgabe": row["verhalten_prompt"]}}
    zusatz = _meta(row).get("takte") or []
    return [haupt] + zusatz


def _sekunden_seit_letztem_post(wesen: str):
    pfad = ca.BASE / wesen / "letzter_post.json"
    try:
        lp = json.loads(pfad.read_text(encoding="utf-8"))
        ts = datetime.datetime.fromisoformat(lp["ts"])
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        return (datetime.datetime.now(datetime.timezone.utc) - ts).total_seconds()
    except Exception:
        return None


def _harte_bedingungen_erfuellt(eigene_felder: list, wesen: str, log) -> bool:
    """Weg B (hart, siehe Konzept): Code prueft, kein Interpretationsspielraum fuers
    Wesen. 'sekunden_seit_letztem_post' ist die einzige eingebaute Kennzahl (deckt
    Daniels eigenes Beispiel 'poste nur wenn letzte Antwort schon 2 Tage her ist');
    jeder andere Feldname wird als Verweis auf ein eigenes Feld mit diesem Namen
    behandelt (dessen statischer 'wert' wird verglichen)."""
    for feld in eigene_felder:
        bedingung = feld.get("bedingung")
        if not bedingung or bedingung.get("weg") != "b":
            continue
        feldname = bedingung.get("feld")
        operator = bedingung.get("operator", "gt")
        vergleichswert = bedingung.get("wert")
        if feldname == "sekunden_seit_letztem_post":
            ist_wert = _sekunden_seit_letztem_post(wesen)
        else:
            passendes = next((f for f in eigene_felder if f.get("name") == feldname), None)
            ist_wert = passendes.get("wert") if passendes else None
        if ist_wert is None:
            log.warning("Harte Bedingung bei Feld '%s': kein Wert ermittelbar -- werte als NICHT erfuellt",
                        feld.get("name"))
            return False
        vergleich = _OPERATOREN.get(operator, _OPERATOREN["gt"])
        try:
            if not vergleich(float(ist_wert), float(vergleichswert)):
                return False
        except (TypeError, ValueError):
            log.warning("Harte Bedingung bei Feld '%s': Werte nicht vergleichbar -- werte als NICHT erfuellt",
                        feld.get("name"))
            return False
    return True


def _weiche_felder_kontext(eigene_felder: list) -> str:
    """Weg A (weich, siehe Konzept): reiner Text, der in den Kontext fuers Wesen
    einfliesst -- das Wesen entscheidet selbst, was es damit macht (analog zur
    'selbst_antworten'-Logik in agentic_loop())."""
    teile = []
    for feld in eigene_felder:
        bedingung = feld.get("bedingung")
        if bedingung and bedingung.get("weg") == "a":
            teile.append(f"- {{feld.get('name', 'Feld')}}: {{bedingung.get('text', '')}}")
        elif not bedingung and feld.get("wert"):
            teile.append(f"- {{feld.get('name', 'Feld')}}: {{feld.get('wert')}}")
    if not teile:
        return ""
    return "\\n\\nZusaetzliche Hinweise fuer diesen Zyklus:\\n" + "\\n".join(teile)


def _in_pausenzeit(pausenzeiten: list, jetzt: datetime.datetime) -> bool:
    if not pausenzeiten:
        return False
    wochentag = jetzt.weekday()
    jetzt_minuten = jetzt.hour * 60 + jetzt.minute
    for p in pausenzeiten:
        tage = p.get("wochentage")
        if tage and wochentag not in tage:
            continue
        try:
            von_h, von_m = (int(x) for x in p["von"].split(":"))
            bis_h, bis_m = (int(x) for x in p["bis"].split(":"))
        except (KeyError, ValueError):
            continue
        von, bis = von_h * 60 + von_m, bis_h * 60 + bis_m
        if von <= bis:
            if von <= jetzt_minuten < bis:
                return True
        else:  # Pause geht ueber Mitternacht, z.B. 22:00-06:00
            if jetzt_minuten >= von or jetzt_minuten < bis:
                return True
    return False


def _einen_zyklus(row: dict, token: str, all_tags: list, log, aufgabe_text: str):
    ziel_typ = row["ziel_typ"]
    eigene_felder = _meta(row).get("eigene_felder") or []

    if not _harte_bedingungen_erfuellt(eigene_felder, WESEN, log):
        log.info("Harte Bedingung nicht erfuellt -- Zyklus uebersprungen")
        return

    verhalten = aufgabe_text + _weiche_felder_kontext(eigene_felder)
    eigene_disk_id = row.get("eigene_diskussion_id")

    if ziel_typ == "fester_thread":
        disk_id = row["ziel_discussion_id"]
        kontext = f"{{verhalten}}\\n\\nAntworte mit 'antworten' und discussion_id {{disk_id}}."
    elif ziel_typ == "eigene_diskussion_einmalig" and eigene_disk_id:
        kontext = f"{{verhalten}}\\n\\nAntworte mit 'antworten' und discussion_id {{eigene_disk_id}}."
    elif ziel_typ in ("neue_diskussion", "eigene_diskussion_einmalig"):
        kontext = f"{{verhalten}}\\n\\nEroeffne dafuer eine neue Diskussion ('neue_diskussion') mit Titel, Inhalt und tag_ids."
    elif ziel_typ == "wesen_entscheidet_selbst":
        kontext = (f"{{verhalten}}\\n\\nDu entscheidest diesmal selbst, wohin das geht: antworte in einer "
                   f"passenden bestehenden Diskussion ('antworten'), eroeffne eine neue ('neue_diskussion'), "
                   f"oder halte es nur intern fest ('intern') -- je nachdem, was gerade am meisten Sinn ergibt.")
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
    elif ziel_typ == "eigene_diskussion_einmalig" and eigene_disk_id:
        if decision.get("aktion") != "antworten":
            decision = {{
                "aktion": "antworten",
                "discussion_id": eigene_disk_id,
                "inhalt": decision.get("inhalt") or decision.get("begruendung") or "...",
            }}
        decision["discussion_id"] = eigene_disk_id
    elif ziel_typ in ("neue_diskussion", "eigene_diskussion_einmalig") and decision.get("aktion") == "neue_diskussion":
        if not decision.get("tag_ids") and row.get("ziel_tag_ids"):
            decision["tag_ids"] = row["ziel_tag_ids"]
    # wesen_entscheidet_selbst: keine Ueberschreibung -- decision bleibt wie vom Wesen entschieden

    anzahl_vorher = len(gd.lade_eigene_posts(WESEN))
    ca.fuehre_aktion_aus(WESEN, token, decision, all_tags, log)

    if ziel_typ == "eigene_diskussion_einmalig" and not eigene_disk_id:
        posts = gd.lade_eigene_posts(WESEN)
        if len(posts) > anzahl_vorher and posts[-1].get("typ") == "neue_diskussion":
            neue_id = posts[-1].get("diskussion_id")
            if neue_id:
                wed.setze_eigene_diskussion_id(DIENST_NAME, int(neue_id))
                log.info("Eigene Diskussion einmalig angelegt: id=%s -- ab jetzt fuer immer Ziel", neue_id)


def _versuche_zyklus(token: str, all_tags: list, log, aufgabe_text: str, pausenzeiten: list):
    if _in_pausenzeit(pausenzeiten, datetime.datetime.now()):
        log.info("Pausenzeit aktiv -- Zyklus uebersprungen")
        return
    aktueller_status = wed.lade(DIENST_NAME)
    if not aktueller_status or aktueller_status.get("status") != "aktiv":
        log.info("Deaktiviert oder aus DB entfernt -- Zyklus uebersprungen")
        return
    try:
        _einen_zyklus(aktueller_status, token, all_tags, log, aufgabe_text)
    except Exception as e:
        log.error("Zyklus-Fehler: %s", e)


def _intervall_schleife(row: dict, token: str, all_tags: list, log, pausenzeiten: list):
    letzte_laeufe = {{
        t["name"]: time.time() - t["sekunden"] + (row["start_offset_sekunden"] if t["name"] == "haupt" else 0)
        for t in _alle_takte(row)
    }}
    while True:
        aktueller_status = wed.lade(DIENST_NAME)
        if not aktueller_status or aktueller_status.get("status") != "aktiv":
            log.info("Deaktiviert oder aus DB entfernt — Schleife pausiert (60s)")
            time.sleep(60)
            continue
        for t in _alle_takte(aktueller_status):
            letzter = letzte_laeufe.get(t["name"], 0)
            if time.time() - letzter >= t["sekunden"]:
                _versuche_zyklus(token, all_tags, log, t["aufgabe"], pausenzeiten)
                letzte_laeufe[t["name"]] = time.time()
        time.sleep(15)


def _feste_uhrzeiten_schleife(row: dict, token: str, all_tags: list, log, uhrzeiten: list, pausenzeiten: list):
    bereits_ausgeloest = set()
    while True:
        jetzt = datetime.datetime.now()
        heute = jetzt.date().isoformat()
        aktuelle_uhrzeit = jetzt.strftime("%H:%M")
        if aktuelle_uhrzeit in uhrzeiten and f"{{heute}}_{{aktuelle_uhrzeit}}" not in bereits_ausgeloest:
            bereits_ausgeloest.add(f"{{heute}}_{{aktuelle_uhrzeit}}")
            _versuche_zyklus(token, all_tags, log, row["verhalten_prompt"], pausenzeiten)
        if len(bereits_ausgeloest) > 200:
            bereits_ausgeloest = {{s for s in bereits_ausgeloest if s.startswith(heute)}}
        time.sleep(30)


def _passiv_schleife(row: dict, token: str, all_tags: list, log, pausenzeiten: list):
    trigger_datei = ca.BASE / WESEN / "eigene_dienste" / DIENST_NAME / "ausloesen.flag"
    log.info("Passiv-Modus -- kein automatischer Takt, wartet auf manuellen Trigger: %s", trigger_datei)
    while True:
        if trigger_datei.exists():
            trigger_datei.unlink(missing_ok=True)
            log.info("Manueller Trigger erkannt -- fuehre einen Zyklus aus")
            _versuche_zyklus(token, all_tags, log, row["verhalten_prompt"], pausenzeiten)
        time.sleep(5)


def haupt_schleife():
    log = _setup_log()
    row = wed.lade(DIENST_NAME)
    if not row:
        log.error("Keine Konfiguration fuer %s in wesen_eigene_dienste gefunden — beende.", DIENST_NAME)
        return

    token = ca.load_token(WESEN)
    all_tags = ca.get_tags_cached(token)
    meta = _meta(row)
    zeitplan_modus = meta.get("zeitplan_modus") or "intervall"
    pausenzeiten = meta.get("pausenzeiten") or []
    log.info("Wesen-eigener Dienst gestartet: %s (Zeitplan-Modus: %s)", DIENST_NAME, zeitplan_modus)

    if zeitplan_modus == "passiv":
        _passiv_schleife(row, token, all_tags, log, pausenzeiten)
    elif zeitplan_modus == "feste_uhrzeiten":
        _feste_uhrzeiten_schleife(row, token, all_tags, log, meta.get("feste_uhrzeiten") or [], pausenzeiten)
    else:
        _intervall_schleife(row, token, all_tags, log, pausenzeiten)


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
