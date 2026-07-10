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
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests

sys.path.insert(0, "/root/werkraum")
import dienst_konfiguration as dk
import wesen_eigene_dienste as wed

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
    "llama-hauhaucs":              {"port": 11435, "health": None},
    "llama-hauhaucs-hintergrund":  {"port": 11436, "health": None},
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
    # Ergaenzt 2026-07-07 (zweiter Nachtrag) — beim Aufbau der Fehler-zu-Dienst-
    # Zuordnung aufgefallen, dass diese Dienste noch gar nicht in der Liste waren.
    "codewesen-aufgabenchats":   {"port": None, "health": None},
    "codewesen-engagement":      {"port": None, "health": None},
    "codewesen-weltbild":        {"port": None, "health": None},
    "codewesen-vokabel-takt":    {"port": None, "health": None},
    "codewesen-reaktion@Schorschel":      {"port": None, "health": None},
    "codewesen-reaktion@F3INSCHM3CK3R":   {"port": None, "health": None},
    "codewesen-reaktion-traeumerlie":     {"port": None, "health": None},
    "codewesen-reaktion@R1ZZ1":           {"port": None, "health": None},
    "codewesen-reaktion@jumpa":           {"port": None, "health": None},
    "codewesen-reaktion@Resonanzknoten":  {"port": None, "health": None},
    # Ergaenzt 2026-07-10 -- der Dienst existiert und laeuft seit 2026-07-09
    # (systemd-Unit angelegt, Baustein 3), war aber NIE in dieser Liste
    # eingetragen: WELTKERN_SERVICES ist die einzige Quelle, aus der der
    # watchdog "services" im Bericht ueberhaupt aufbaut (siehe die Schleife
    # weiter unten) -- ohne Eintrag hier taucht ein Dienst im flarumstyler
    # gar nicht erst auf, unabhaengig von DIENSTE_MIT_KONFIGURATION.
    "codewesen-umgekehrte-neugier":       {"port": None, "health": None},
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
    "ollama": "Korrigiert 2026-07-06: NICHT mehr das Haupt-Backend — nur noch Freier-Modus + Vision-Modell, Port 11434. Das eigentliche Wesen-LLM laeuft ueber llama-hauhaucs/-hintergrund (siehe dort).",
    "llama-hauhaucs": "Das eigentliche LLM-Backend fuer LIVE-Chat (hauhaucs-q6, Qwen3.6-35B), Port 11435 — hier laufen Aufgabenchats/Chat-UI-Antworten durch, wenn ein Mensch live zuschaut.",
    "llama-hauhaucs-hintergrund": "Das LLM-Backend fuer ALLE Hintergrund-Denkprozesse (Batch-Generator, Takt, Reaktionen, Reflexion), Port 11436 — der gemeinsame, oft ueberlastete Slot den sich alle 7 Wesen teilen (siehe slot_0.lock-Kontention).",
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
    "codewesen-aufgabenchats": "Fuehrt die Selbstgespraech-Sessions der Aufgabenchats aus (fruehers 'Klon'), gesteuert ueber Start/Stop/Impuls.",
    "codewesen-engagement": "Autonomes Forum-Engagement der Wesen — INAKTIV laut Systemdoku, pruefe ob das noch so gewollt ist falls es hier als aktiv/inaktiv ueberrascht.",
    "codewesen-weltbild": "Destilliert Forum-Wissen pro Wesen zu einem Weltbild-Text, der in den Systemprompt einfliesst.",
    "codewesen-vokabel-takt": "Synonym-/Vokabel-Spiel-Rhythmus der Wesen (22-Minuten-Takt) — bewusst deaktiviert seit 2026-07-07 (Daniel).",
    "codewesen-reaktion@Schorschel": "Reaktionsdienst (Notifications/Erwaehnungen/Flags) fuer Schorschel — teilt sich reaktion.log mit dem Haupt-Agent-Prozess.",
    "codewesen-reaktion@F3INSCHM3CK3R": "Reaktionsdienst (Notifications/Erwaehnungen/Flags) fuer F3INSCHM3CK3R — teilt sich reaktion.log mit dem Haupt-Agent-Prozess.",
    "codewesen-reaktion-traeumerlie": "Reaktionsdienst (Notifications/Erwaehnungen/Flags) fuer träumerlie — eigenstaendiger Dienst statt @-Template wegen ASCII-Limit von systemd (siehe Doku).",
    "codewesen-reaktion@R1ZZ1": "Reaktionsdienst (Notifications/Erwaehnungen/Flags) fuer R1ZZ1 — teilt sich reaktion.log mit dem Haupt-Agent-Prozess.",
    "codewesen-reaktion@jumpa": "Reaktionsdienst (Notifications/Erwaehnungen/Flags) fuer jumpa — teilt sich reaktion.log mit dem Haupt-Agent-Prozess.",
    "codewesen-reaktion@Resonanzknoten": "Reaktionsdienst (Notifications/Erwaehnungen/Flags) fuer Resonanzknoten — teilt sich reaktion.log mit dem Haupt-Agent-Prozess.",
    "codewesen-umgekehrte-neugier": "Das Gegenstueck zu codewesen-forum-neugier waehrend die Flarum-Post-Sperre aktiv ist — fragt jedes Wesen zuerst was es lesen will, sucht/liest live in der Flarum-DB, schreibt aber NIE zurueck nach Flarum (Funde landen nur in privaten Containern). Siehe docs/systemdoku/20_flarum_stopp.md.",
}

# Dienste die bewusst/dauerhaft inaktiv sind (2026-07-07, flarumstyler) — werden im
# Bericht als "erwartet_aus" statt "down" markiert, damit sie in der Ampel-Uebersicht
# nicht wie ein echtes Problem aussehen und rote Punkte nicht "verwaschen". Bei Bedarf
# ergaenzen, wenn sich herausstellt dass ein weiterer Dienst bewusst dauerhaft aus ist.
SERVICES_ERWARTET_AUS = {"entity-kern", "entity-takt", "codewesen-vokabel-takt"}

# Gruppierung fuer die flarumstyler-Ansicht (2026-07-07) — Daniel: "gruperungen, ganz
# oben die in flarum und andere darunter". Alles was mit den Wesen/Flarum direkt zu tun
# hat kommt in "flarum", der Rest (Welt-Infrastruktur, GENI, Simulation) in "welt".
SERVICES_GRUPPE_FLARUM = {
    "flarum-monitor", "codewesen-antwort-daniel", "codewesen-takt", "codewesen-lg-daemon",
    "codewesen-forum-neugier", "codewesen-batch-generator", "codewesen-dakgordsystem",
    "codewesen-reaktion-dakgord", "codewesen-chat", "dak-gord-web",
    "codewesen-Schorschel", "codewesen-F3INSCHM3CK3R", "codewesen-traeumerlie",
    "codewesen-R1ZZ1", "codewesen-jumpa", "codewesen-Resonanzknoten",
    "codewesen-aufgabenchats", "codewesen-engagement", "codewesen-weltbild", "codewesen-vokabel-takt",
    "codewesen-reaktion@Schorschel", "codewesen-reaktion@F3INSCHM3CK3R", "codewesen-reaktion-traeumerlie",
    "codewesen-reaktion@R1ZZ1", "codewesen-reaktion@jumpa", "codewesen-reaktion@Resonanzknoten",
}

# Dienste die im flarumstyler NICHT ueber Start/Stop/Neustart-Buttons steuerbar sind
# (2026-07-07) — Daniel wollte Steuerung, aber diese vier haben Blast-Radius fuer ALLE
# Wesen gleichzeitig (geteiltes Ollama, der Server der diese Seite selbst ausliefert,
# die Kern-Welt-API/-Bruecke). Mein eigener Vorsichts-Vorschlag, kann jederzeit
# angepasst werden falls Daniel das anders will.
SERVICES_GESPERRT_FUER_AKTIONEN = {"ollama", "process-camera-preview", "welt-api", "welt-bruecke"}

# Dienste die bereits auf dienst_konfiguration (Takt+Verhalten aus der DB) umgestellt sind
# (2026-07-07, Individualisierungs-Ausbau) — Proof-of-Concept startet mit genau einem Dienst,
# weitere kommen nach Bestaetigung dazu (siehe Systemdoku 18_flarumstyler.md).
DIENSTE_MIT_KONFIGURATION = {
    "codewesen-vokabel-takt", "codewesen-antwort-daniel", "codewesen-weltbild",
    "codewesen-forum-neugier", "codewesen-engagement", "codewesen-batch-generator",
    "codewesen-takt",
    "codewesen-reaktion@Schorschel", "codewesen-reaktion@F3INSCHM3CK3R",
    "codewesen-reaktion-traeumerlie", "codewesen-reaktion@R1ZZ1",
    "codewesen-reaktion@jumpa", "codewesen-reaktion@Resonanzknoten",
    "codewesen-reaktion-dakgord", "codewesen-aufgabenchats", "codewesen-chat",
    "codewesen-lg-daemon",
    "codewesen-Schorschel", "codewesen-F3INSCHM3CK3R", "codewesen-traeumerlie",
    "codewesen-R1ZZ1", "codewesen-jumpa", "codewesen-Resonanzknoten",
    "codewesen-dakgordsystem",
    # 2026-07-10, Daniel: bis hierhin fehlte dieser Dienst komplett in dieser
    # Liste -- takt_sekunden/verhalten_text waren zwar im Skript schon lesbar
    # (dk.lade() in haupt_schleife()), aber im flarumstyler ohne diesen Eintrag
    # UNERREICHBAR (nur der "noch nicht umstellbar"-Hinweistext erschien).
    "codewesen-umgekehrte-neugier",
}


# ── Individualisierungs-Erklaerung pro Dienst (2026-07-07, Daniel: "sie sind alle
# immernoch auf diese 3 kaestchenweise individualisierbar und nix wird erklaert") ──
# Nicht jeder konfigurierbare Dienst nutzt Takt/Verhalten gleich — z.B. hat
# codewesen-engagement gar keinen eigenen Sleep-Loop (Takt kommt aus systemd
# RestartSec), codewesen-takt nutzt statt einem einzigen Takt sechs benannte Werte
# in meta.intervalle. Das Frontend soll nur die Felder zeigen, die fuer den
# jeweiligen Dienst wirklich etwas bewirken — mit Erklaerung wieso.
TAKT_EINFACH_DIENSTE = {
    "codewesen-vokabel-takt", "codewesen-antwort-daniel", "codewesen-weltbild",
    "codewesen-forum-neugier", "codewesen-lg-daemon",
    "codewesen-umgekehrte-neugier",  # PAUSE_ZWISCHEN_ZYKLEN, einzelner Takt wie forum-neugier
}
TAKT_KEIN_DIENSTE = {
    "codewesen-engagement", "codewesen-batch-generator",
    "codewesen-aufgabenchats", "codewesen-chat",
}
VERHALTEN_KEIN_DIENSTE = {"codewesen-takt"}

# Braucht Neustart, damit ein Override wirkt (Code liest dk.lade() nur EINMAL beim
# Prozessstart, nicht pro Zyklus) — geprueft 2026-07-07 nach Daniels "raffst nix"-
# Kritik, per Zeilennummer im jeweiligen Skript nachgesehen, nicht geraten:
# codewesen_takt.py Z.282+302, codewesen_reaktion.py Z.844+876 (Kommentar dort
# nennt es explizit), codewesen_lg_daemon.py Z.498+518, codewesen_agent.py Z.1222+1257.
# Alle anderen konfigurierbaren Dienste lesen dk.lade() INNERHALB ihrer while-True-
# Schleife (vokabel-takt, antwort-daniel, weltbild, forum-neugier, batch-generator)
# oder pro Aufruf/Session (engagement: kompletter Prozess pro RestartSec-Zyklus neu,
# aufgabenchats: pro neuer Session, chat: pro HTTP-Request) — dort gilt ein
# gespeicherter Override wirklich ohne Neustart.
BRAUCHT_NEUSTART_DIENSTE = {
    "codewesen-takt", "codewesen-lg-daemon",
    "codewesen-reaktion@Schorschel", "codewesen-reaktion@F3INSCHM3CK3R",
    "codewesen-reaktion-traeumerlie", "codewesen-reaktion@R1ZZ1",
    "codewesen-reaktion@jumpa", "codewesen-reaktion@Resonanzknoten",
    "codewesen-reaktion-dakgord",
    "codewesen-Schorschel", "codewesen-F3INSCHM3CK3R", "codewesen-traeumerlie",
    "codewesen-R1ZZ1", "codewesen-jumpa", "codewesen-Resonanzknoten",
    "codewesen-dakgordsystem",
}

TAKT_KEIN_ERKLAERUNG = {
    "codewesen-engagement": "Kein eigener Sleep-Loop — der Rhythmus kommt aus systemd (RestartSec=7200), nicht aus Python. Takt hier aendern: direkt am systemd-Unit.",
    "codewesen-batch-generator": "Erzeugt Post-Entwuerfe auf Vorrat in einer Warteschlange, nicht auf eigenem Zeittakt — laeuft, sobald die Queue leer wird.",
    "codewesen-aufgabenchats": "Kein Zeittakt — startet, wenn eine Flag-Datei gesetzt wird (Aufgabenchat-Session angestossen), nicht periodisch.",
    "codewesen-chat": "Webserver, request-getrieben — reagiert auf ankommende Chat-Anfragen, hat keinen eigenen Rhythmus.",
}

# ── Ausfuehrliche Doku direkt aus dem Skript (2026-07-07, Daniel: "warum kannst
# du hier fast ne dina4seite erklaeren und warum ist das nicht genau so in der
# UI?") — der Modul-Docstring jedes Skripts ist bereits die Quelle, aus der diese
# Erklaerungen stammen. Statt es nochmal von Hand zu schreiben (doppelte Wahrheit,
# veraltet zwei Sekunden nach der naechsten Codeaenderung): direkt auslesen.
SCRIPT_FUER_DIENST = {
    "codewesen-vokabel-takt": "codewesen_vokabel_takt.py",
    "codewesen-antwort-daniel": "codewesen_antwort_auf_daniel.py",
    "codewesen-weltbild": "weltbild_builder.py",
    "codewesen-forum-neugier": "codewesen_forum_neugier.py",
    "codewesen-engagement": "codewesen_engagement.py",
    "codewesen-batch-generator": "codewesen_batch_generator.py",
    "codewesen-takt": "codewesen_takt.py",
    "codewesen-aufgabenchats": "codewesen_aufgabenchats.py",
    "codewesen-chat": "codewesen_chat.py",
    "codewesen-lg-daemon": "codewesen_lg_daemon.py",
    "codewesen-umgekehrte-neugier": "codewesen_umgekehrte_neugier.py",
}
REAKTION_DIENSTE = {
    "codewesen-reaktion@Schorschel", "codewesen-reaktion@F3INSCHM3CK3R",
    "codewesen-reaktion-traeumerlie", "codewesen-reaktion@R1ZZ1",
    "codewesen-reaktion@jumpa", "codewesen-reaktion@Resonanzknoten",
    "codewesen-reaktion-dakgord",
}
AGENT_DIENSTE = {
    "codewesen-Schorschel", "codewesen-F3INSCHM3CK3R", "codewesen-traeumerlie",
    "codewesen-R1ZZ1", "codewesen-jumpa", "codewesen-Resonanzknoten",
    "codewesen-dakgordsystem",
}

import ast as _ast

def _technische_doku(name: str) -> str | None:
    pfad = None
    if name in SCRIPT_FUER_DIENST:
        pfad = Path("/root/werkraum") / SCRIPT_FUER_DIENST[name]
    elif name in REAKTION_DIENSTE:
        pfad = Path("/root/werkraum/codewesen_reaktion.py")
    elif name in AGENT_DIENSTE:
        pfad = Path("/root/werkraum/codewesen_agent.py")
    if not pfad or not pfad.exists():
        return None
    try:
        baum = _ast.parse(pfad.read_text(encoding="utf-8"))
        return _ast.get_docstring(baum)
    except Exception:
        return None


# Einzelne benannte Zeitwerte statt einem JSON-Blob, damit Daniel jeden Wert
# einzeln anklicken/aendern kann (nicht per Hand JSON tippen). Key = wie im
# jeweiligen Skript in meta.intervalle verwendet, Wert = (Label, Standard-Sekunden).
META_FELD_LABELS = {
    "codewesen-takt": {
        "eigene_antwort": ("Eigene Antwort — auf eigene Diskussionen", 22 * 60),
        "antwort": ("Antwortpflicht — rotierend, ein Wesen pro Durchlauf", 66 * 60),
        "pflicht": ("Pflichtpost — neuer Existenz-Thread", 88 * 60),
        "impuls": ("Forum-Impuls — Kritik/Reflexion abwechselnd", (2 * 60 + 22) * 60),
        "gedanke": ("Freier Gedanke — neuer Thread + Markdown-Ablage", (4 * 60 + 44) * 60),
        "vorstellung": ("Vorstellung — Selbstgespraech im Fest-Thread", (4 * 60 + 44) * 60),
    },
    "_reaktion": {
        "check_interval": ("Inbox-Check — wie oft auf neue Notifications schauen", 600),
        "reflexions_interval": ("Selbstreflexions-Check", 300),
        "forum_entwicklung_interval": ("Forum-Entwicklung beobachten", 142 * 60),
        "themen_beitrag_interval": ("Themen-Beitrag", 88 * 60),
        "zwischenraum_scan_interval": ("Zwischenraum-Scan — neugierig reinschauen", 900),
        "fehler_retry_interval": ("Fehler-Items zurueck in Inbox versuchen", 300),
    },
    "_agent": {
        "check_reflexion": ("Selbstreflexions-Check", 28800),
        "check_scan": ("Forum-Scan-Check", 7200),
        "gedanke": ("Freier Gedanke", 66 * 60),
        "pflichtpost": ("Pflichtpost — Existenz-Thread", 88 * 60),
        "impuls": ("Forum-Impuls", 142 * 60),
    },
}


def _meta_felder(name: str) -> dict | None:
    if name in META_FELD_LABELS:
        return META_FELD_LABELS[name]
    if name in REAKTION_DIENSTE:
        return META_FELD_LABELS["_reaktion"]
    if name in AGENT_DIENSTE:
        return META_FELD_LABELS["_agent"]
    return None


# Schalter-Felder (2026-07-10, Daniel: "weder zahlen noch text [...] sondern
# ein toggle button" -- ein Wert aus einer festen, kleinen Optionsliste, kein
# Zeitwert (meta_felder) und kein Freitext (verhalten_text). Key landet als
# TOP-LEVEL meta-Feld (nicht unter meta.intervalle) unter demselben Namen, den
# das jeweilige Skript per dk.lade() erwartet.
SCHALTER_FELD_LABELS = {
    "codewesen-antwort-daniel": {
        "llm_pool": {
            "label": "LLM-Pool",
            "erklaerung": (
                "Welche llama-server-Instanz fuer die Antworten auf Daniels Posts "
                "genutzt wird. 'Hintergrund-Pool' (Standard): teilt sich den einen "
                "Postgres-Scheduler-Slot (server=hintergrund, Port 11436) mit den "
                "15 anderen Hintergrund-Diensten (Agent-/Reaktions-Loops, "
                "Engagement, Batch-Generator, ...) — bei vollem Slot wartet dieser "
                "Dienst trotz PRIO_HOCH bis zu 600s. 'Eigener Chat-Pool': nutzt "
                "denselben exklusiven Slot wie die Live-Chats (server=chat, "
                "id_slot=0, Port 11435) — dort konkurrieren nur echte, seltene "
                "Chat-Anfragen, keine der 15 Hintergrund-Schleifen."
            ),
            "optionen": [
                {"wert": "hintergrund", "label": "Hintergrund-Pool (Standard)"},
                {"wert": "chat", "label": "Eigener Chat-Pool (exklusiv, id_slot=0)"},
            ],
            "standard": "hintergrund",
        },
    },
    "codewesen-umgekehrte-neugier": {
        "budget_modus": {
            "label": "Lese-Budget",
            "erklaerung": (
                "Steuert, woran die Lese-Phase ihr Ende und den fruehesten "
                "Diskussions-Wechsel misst. 'Token-Budget' (Baustein 14/17, "
                "Standard): LESE_TOKEN_BUDGET=5555 Tokens gesamt, Posts in "
                "500-Token-Fenstern, Wechsel ab 250 gelesenen Tokens im Fund. "
                "'Zeit-/Postzahl' (Baustein 11-13, alter Modus): 6 Min/2 "
                "Diskussionen gesamt, Posts komplett am Stueck, Wechsel ab "
                "3 Min + 2 Posts im Fund."
            ),
            "optionen": [
                {"wert": "token", "label": "Token-Budget (Standard)"},
                {"wert": "zeit", "label": "Zeit-/Postzahl (alter Modus)"},
            ],
            "standard": "token",
        },
    },
}

# Mehrfach-Toggle-Felder (2026-07-10, Daniel: "sowohl als auch" -- ersetzt den
# ersten Entwurf von wesen_filter, der nur "alle" ODER "genau eines" erlaubte,
# per Rueckfrage. Jede Option ist unabhaengig an/aus schaltbar, kein exklusives
# Radio-Verhalten wie bei SCHALTER_FELD_LABELS. Key landet als TOP-LEVEL
# meta-Feld (Liste der aktiven wert-Strings), Standard = alle Optionen aktiv.
MEHRFACH_FELD_LABELS = {
    "codewesen-umgekehrte-neugier": {
        "wesen_aktiv": {
            "label": "Aktive Wesen",
            "erklaerung": (
                "Welche Wesen die Schleife pro Zyklus mitlaufen laesst. Standard: "
                "alle 7 aktiv (bisheriges Verhalten, zeitversetzt in derselben "
                "Runde, sichtbar im Tab 'Live-Aktivitaet'). Einzelne Wesen "
                "abwaehlen laesst sie diesen und alle folgenden Zyklen aus, bis "
                "sie hier wieder angehakt werden -- z.B. um nur ein paar gezielt "
                "laufen zu lassen, ohne dass die restlichen denselben LLM-Slot "
                "mitbeanspruchen. Mindestens ein Wesen muss aktiv bleiben; eine "
                "leere Auswahl wird beim Speichern wie 'alle' behandelt."
            ),
            "optionen": [
                {"wert": "Schorschel", "label": "Schorschel"},
                {"wert": "F3INSCHM3CK3R", "label": "F3INSCHM3CK3R"},
                {"wert": "träumerlie", "label": "träumerlie"},
                {"wert": "R1ZZ1", "label": "R1ZZ1"},
                {"wert": "jumpa", "label": "jumpa"},
                {"wert": "Resonanzknoten", "label": "Resonanzknoten"},
                {"wert": "dak+gord-system", "label": "dak+gord-system"},
            ],
            "standard": ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"],
        },
    },
}


def _mehrfach_felder(name: str) -> list[dict]:
    felder = MEHRFACH_FELD_LABELS.get(name, {})
    return [{"key": k, **v} for k, v in felder.items()]


def _schalter_felder(name: str) -> list[dict]:
    felder = SCHALTER_FELD_LABELS.get(name, {})
    return [{"key": k, **v} for k, v in felder.items()]


def _individualisierung_hinweis(name: str) -> dict | None:
    if name not in DIENSTE_MIT_KONFIGURATION:
        return None
    braucht_neustart = name in BRAUCHT_NEUSTART_DIENSTE
    wirkt_wann = (
        "Wird erst nach einem NEUSTART dieses Dienstes wirksam — der Prozess liest die Konfiguration nur einmal beim Start, nicht laufend. Speichern allein reicht hier nicht."
        if braucht_neustart else
        "Gilt dauerhaft ab dem naechsten Zyklus, ohne Neustart — der Prozess liest die Konfiguration laufend neu. Kein Einmal-Effekt: bleibt so, bis du das Feld hier wieder aenderst oder leerst."
    )
    if name in TAKT_EINFACH_DIENSTE:
        takt = {"typ": "einfach", "erklaerung": f"Ein einzelner Takt in Sekunden — ersetzt den fest im Skript codierten Standardwert. {wirkt_wann}"}
    elif name in TAKT_KEIN_DIENSTE:
        takt = {"typ": "keiner", "erklaerung": TAKT_KEIN_ERKLAERUNG.get(name, "Dieser Dienst hat keinen ueberschreibbaren Einzel-Takt.")}
    else:
        felder = _meta_felder(name) or {}
        meta_felder_liste = [
            {"key": k, "label": lbl, "standard_sek": std}
            for k, (lbl, std) in felder.items()
        ]
        takt = {
            "typ": "meta",
            "erklaerung": f"Kein einzelner Takt — dieser Dienst braucht mehrere benannte Zeitwerte gleichzeitig (z.B. verschiedene Post-Arten). Jeder Wert unten einzeln aenderbar. {wirkt_wann}",
            "meta_felder": meta_felder_liste,
        }
    verhalten = name not in VERHALTEN_KEIN_DIENSTE
    verhalten_erklaerung = (
        "Dieser Dienst nutzt kein LLM — es gibt keinen System-Prompt, an den ein Verhaltenstext angehaengt werden koennte."
        if not verhalten else
        f"Der Text wird woertlich ans Ende der KI-Anweisung angehaengt — z.B. \"schreib kuerzer\" oder \"sei sarkastischer\". Feste Format-Vorgaben im Skript bleiben trotzdem bestehen (die werden nicht ersetzt, nur ergaenzt). {wirkt_wann}"
    )
    return {
        "takt": takt, "verhalten_moeglich": verhalten, "verhalten_erklaerung": verhalten_erklaerung,
        "braucht_neustart": braucht_neustart, "schalter": _schalter_felder(name),
        "mehrfach": _mehrfach_felder(name),
    }


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

# Welcher Dienst schreibt welches Log — fuer die direkte Fehler-Zuordnung pro Dienst
# (Daniel: "jeden Fehler direkt dort dann aufploppen lassen mit Hinweis woher es kommt").
# reaktion.log wird von ZWEI Diensten geschrieben (Haupt-Agent + reaktion@-Instanz),
# hier bewusst dem Haupt-Agent zugeordnet, da der praesenter/bekannter ist.
LOG_DATEI_ZU_DIENST = {
    "generator.log": "codewesen-batch-generator",
    "takt.log": "codewesen-takt",
    "forum_neugier.log": "codewesen-forum-neugier",
    "weltbild.log": "codewesen-weltbild",
    "vokabel_takt.log": "codewesen-vokabel-takt",
    "aufgabenchats.log": "codewesen-aufgabenchats",
}
REAKTION_LOG_DIENST_PRAEFIX = "codewesen-"  # reaktion.log -> codewesen-<Ordnername>

_ZEITSTEMPEL_RE = _re.compile(r"^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")

FEHLER_MUSTER = {
    "llama_server_nicht_erreichbar": {
        # Umbenannt von "ollama_nicht_erreichbar" (2026-07-07, Daniel: "ollama ist wohl
        # nicht erreichbar" — verwechselt mit dem Ollama-Dienst, der seit der hauhaucs-
        # Migration nur noch Freier-Modus+Vision ist). Dieses Muster erfasst NUR die
        # llama-server-Instanzen (Port 11435/11436), nie den echten Ollama-Dienst.
        "regex": _re.compile(r"503 Service Unavailable|Connection refused|Read timed out"),
        "was_ist_los": "Der llama-server (Live-Chat oder Hintergrund-Instanz — NICHT der Ollama-Dienst) war beim Anfragezeitpunkt nicht erreichbar oder hat nicht rechtzeitig geantwortet.",
        "empfehlung": "Pruefen ob llama-hauhaucs.service / llama-hauhaucs-hintergrund.service laufen, RAM-/CPU-Auslastung checken, ggf. Anzahl gleichzeitig laufender Codewesen-Dienste reduzieren. Seit 2026-07-07 entschaerft durch llm_scheduler.py (siehe 19_llm_scheduler.md) — pruefen ob das Problem seither noch neu auftritt oder nur historisch nachwirkt.",
        "bringt_das": "Weniger verlorene Post-/Denk-Versuche, schnellere Antwortzeiten.",
        "bringt_das_nicht": "Behebt nicht die strukturelle Slot-Knappheit bei 7 Wesen die sich einen Server-Slot teilen — das ist kein Bug, sondern eine Kapazitaetsgrenze.",
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
        "empfehlung": "Bereits am 2026-07-07 gefixt in codewesen_agent.py/codewesen_reaktion.py/codewesen_abwurf.py (isinstance-Pruefung ergaenzt). Zweite, verwandte Ursache selbes Datum: selbstreflexion()s neue_diskussion-Zweig entpackte die schon fertige ID von start_discussion() ein zweites Mal (result.get('data',{}).get('id') auf einem bereits extrahierten String) — trat erst nach dem LLM-Scheduler-Fix haeufiger auf, weil seitdem mehr Reflexions-Zyklen ueberhaupt bis zu diesem Codepfad kommen. Falls neu: dieselbe Pruefung an der jeweiligen Stelle ergaenzen.",
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
    "unbekannter_token_username": {
        "regex": _re.compile(r"Unbekannter Token/Username"),
        "was_ist_los": "flarum_api._resolve_username() konnte den uebergebenen Wesen-Namen nicht einem Flarum-Account zuordnen — der Post-Versuch scheiterte, bevor er Flarum ueberhaupt erreichte.",
        "empfehlung": "Bereits am 2026-07-07 gefixt (_resolve_username erkennt jetzt auch interne Wesen-Anzeigenamen aus _api_tokens.json). Falls neu: pruefen ob ein neuer Wesen-Name in _api_tokens.json fehlt.",
        "bringt_das": "Der betroffene Post-Versuch geht durch statt sofort zu scheitern.",
        "bringt_das_nicht": "Nichts sonst — reiner Blocker-Fix. War seit der Wesen-ID-Migration (2026-07-06) fuer 6 von 7 Wesen komplett blockierend, aber ohne eigenes Fehlermuster unsichtbar im Dashboard — deshalb hier ergaenzt.",
    },
}


BEISPIELZEILEN_MAX = 5  # pro Fehlermuster, fuer die Detailansicht (nicht nur Zaehlung)

# Quittierung (flarumstyler, 2026-07-07, Daniel: "nicht nur ausgrauen...weg damit") —
# Ein quittiertes Fehlermuster verschwindet komplett aus dem Fehler-Grid, SOLANGE kein
# neues Vorkommen nach dem Quittierungs-Zeitpunkt dazukommt. Kommt ein neues Vorkommen
# dazu, taucht die Karte automatisch wieder auf (kein dauerhaftes Stummschalten eines
# echten wiederkehrenden Problems). Nichts wird geloescht (Grundgesetz 4) - nur die
# Anzeige gefiltert, die Log-Zeilen/Zaehlung bleiben unberuehrt.
QUITTIERUNG_FILE = LOG_DIR / "flarumstyler_quittierungen.json"


def _lade_quittierungen() -> dict[str, str]:
    try:
        return json.loads(QUITTIERUNG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _dienst_fuer_log(logdatei: Path) -> str | None:
    if logdatei.name == "reaktion.log":
        return REAKTION_LOG_DIENST_PRAEFIX + logdatei.parent.name
    return LOG_DATEI_ZU_DIENST.get(logdatei.name)


def fehler_uebersicht() -> tuple[dict, dict]:
    """Scannt alle bekannten Logs einmal komplett durch, zaehlt pro Fehlermuster
    dauerhaft (seit Logbeginn), merkt den Zeitpunkt des letzten Auftretens und
    behaelt die letzten paar echten Log-Zeilen fuer die Detailansicht.
    Gibt zusaetzlich (Daniel: 'jeden Fehler direkt dort aufploppen lassen') dieselben
    Zahlen NOCHMAL pro Dienst zurueck, damit sie direkt an der jeweiligen Dienst-Karte
    angezeigt werden koennen, nicht nur in der globalen Uebersicht."""
    zaehler = {k: 0 for k in FEHLER_MUSTER}
    letzte = {k: None for k in FEHLER_MUSTER}
    beispiele: dict[str, list[str]] = {k: [] for k in FEHLER_MUSTER}
    pro_dienst: dict[str, dict[str, dict]] = {}

    for logdatei in LOG_DATEIEN:
        if not logdatei.exists():
            continue
        dienst = _dienst_fuer_log(logdatei)
        try:
            with open(logdatei, encoding="utf-8", errors="replace") as f:
                for zeile in f:
                    for schluessel, cfg in FEHLER_MUSTER.items():
                        if cfg["regex"].search(zeile):
                            zaehler[schluessel] += 1
                            ts_match = _ZEITSTEMPEL_RE.match(zeile)
                            zt = ts_match.group(1) if ts_match else None
                            if zt and (letzte[schluessel] is None or zt > letzte[schluessel]):
                                letzte[schluessel] = zt
                            gekuerzt = zeile.strip()
                            if len(gekuerzt) > 300:
                                gekuerzt = gekuerzt[:300] + "…"
                            beispiel_liste = beispiele[schluessel]
                            quelle = f"{logdatei.parent.name}/{logdatei.name}" if logdatei.name == "reaktion.log" else logdatei.name
                            beispiel_liste.append(f"{quelle}: {gekuerzt}")
                            if len(beispiel_liste) > BEISPIELZEILEN_MAX:
                                beispiel_liste.pop(0)

                            if dienst:
                                eintrag = pro_dienst.setdefault(dienst, {}).setdefault(
                                    schluessel, {"gesamt_anzahl": 0, "zuletzt_aufgetreten": None}
                                )
                                eintrag["gesamt_anzahl"] += 1
                                if zt and (eintrag["zuletzt_aufgetreten"] is None or zt > eintrag["zuletzt_aufgetreten"]):
                                    eintrag["zuletzt_aufgetreten"] = zt
        except Exception:
            continue

    quittierungen = _lade_quittierungen()
    global_uebersicht = {
        schluessel: {
            "gesamt_anzahl": zaehler[schluessel],
            "zuletzt_aufgetreten": letzte[schluessel],
            "beispielzeilen": beispiele[schluessel],
            "was_ist_los": cfg["was_ist_los"],
            "empfehlung": cfg["empfehlung"],
            "bringt_das": cfg["bringt_das"],
            "bringt_das_nicht": cfg["bringt_das_nicht"],
            "quittiert": bool(
                quittierungen.get(schluessel)
                and (letzte[schluessel] is None or letzte[schluessel] <= quittierungen[schluessel])
            ),
            "quittiert_am": quittierungen.get(schluessel),
        }
        for schluessel, cfg in FEHLER_MUSTER.items()
    }
    return global_uebersicht, pro_dienst


# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def service_is_active(name: str) -> bool:
    result = subprocess.run(
        ["systemctl", "is-active", f"{name}.service"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() == "active"


def service_details(name: str) -> dict:
    """Detailinfos jenseits von nur aktiv/inaktiv (flarumstyler, 2026-07-07):
    seit wann laeuft es, wie oft neugestartet (zeigt Crash-Loops), wie viel
    RAM. Daniel: 'man versteht nix' bei nur einem Statuswort — das hier soll
    genug Kontext geben ohne selbst auf den Server zu muessen."""
    try:
        result = subprocess.run(
            ["systemctl", "show", f"{name}.service",
             "--property=ActiveEnterTimestamp,NRestarts,MemoryCurrent,ExecMainStatus,SubState"],
            capture_output=True, text=True, timeout=5,
        )
        werte = {}
        for zeile in result.stdout.splitlines():
            if "=" in zeile:
                k, v = zeile.split("=", 1)
                werte[k] = v
    except Exception:
        werte = {}

    speicher_mb = None
    try:
        roh = werte.get("MemoryCurrent", "")
        if roh and roh != "[not set]":
            speicher_mb = round(int(roh) / 1024 / 1024, 1)
    except Exception:
        pass

    neustarts = None
    try:
        neustarts = int(werte.get("NRestarts", ""))
    except Exception:
        pass

    return {
        "seit_wann": werte.get("ActiveEnterTimestamp") or None,
        "neustarts": neustarts,
        "speicher_mb": speicher_mb,
        "sub_state": werte.get("SubState"),
    }


def service_letzte_logs(name: str, anzahl: int = 3) -> list[str]:
    """Letzte echte journalctl-Zeilen fuer diesen Dienst — direkter Kontext
    ohne SSH, analog zu den Beispielzeilen bei den Fehlermustern."""
    try:
        result = subprocess.run(
            ["journalctl", "-u", f"{name}.service", "-n", str(anzahl), "--no-pager", "-o", "short-iso"],
            capture_output=True, text=True, timeout=5,
        )
        zeilen = [z.strip() for z in result.stdout.splitlines() if z.strip()]
        return zeilen[-anzahl:]
    except Exception:
        return []


# Ports der zwei echten llama-server-Instanzen (flarumstyler, 2026-07-07) — Daniel:
# "ich will genau sehen was gerade drin arbeitet, wie lange schon, wie viel RAM".
LLAMA_SERVER_PORTS = {"llama-hauhaucs": 11435, "llama-hauhaucs-hintergrund": 11436}
LLAMA_SCHEDULER_SERVER = {"llama-hauhaucs": "chat", "llama-hauhaucs-hintergrund": "hintergrund"}


def llm_warteschlange_status(server: str) -> dict | None:
    """Liest llm_warteschlange (llm_scheduler.py) fuer einen Server-Schluessel:
    wer haelt gerade den Slot (seit wann), wer wartet dahinter (wie lange schon).
    Daniel: 'sehen ob andere auch mit rein wollen'."""
    try:
        conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT rufer, prioritaet, angefragt_um, slot_bis,
                       (slot_bis IS NOT NULL AND slot_bis > NOW()) AS aktiv,
                       EXTRACT(EPOCH FROM (NOW() - angefragt_um))::int AS wartet_sek
                FROM llm_warteschlange
                WHERE server = %s
                ORDER BY aktiv DESC, prioritaet, angefragt_um
                """,
                (server,),
            )
            zeilen = cur.fetchall()
        conn.close()
    except Exception:
        return None

    aktiv = next((z for z in zeilen if z["aktiv"]), None)
    wartend = [z for z in zeilen if not z["aktiv"]]
    return {
        "aktiv": {"rufer": aktiv["rufer"], "wartet_sek": aktiv["wartet_sek"]} if aktiv else None,
        "wartend": [{"rufer": w["rufer"], "wartet_sek": w["wartet_sek"]} for w in wartend],
    }


def llama_status(port: int) -> dict | None:
    """Fragt /slots und /metrics des llama-server direkt ab — zeigt live ob gerade
    generiert wird, wie viele Anfragen warten, und die Tokens/Sekunde-Rate."""
    try:
        slots = requests.get(f"http://localhost:{port}/slots", timeout=3).json()
        metrics_roh = requests.get(f"http://localhost:{port}/metrics", timeout=3).text
    except Exception:
        return None

    metrics = {}
    for zeile in metrics_roh.splitlines():
        if zeile.startswith("#") or " " not in zeile:
            continue
        name, _, wert = zeile.rpartition(" ")
        try:
            metrics[name.replace("llamacpp:", "")] = float(wert)
        except ValueError:
            continue

    return {
        "slots": [
            {
                "id": s.get("id"),
                "beschaeftigt": s.get("is_processing", False),
                "prompt_tokens": s.get("n_prompt_tokens"),
            }
            for s in slots
        ],
        "warteschlange": int(metrics.get("requests_deferred", 0)),
        "gerade_aktiv": any(s.get("is_processing") for s in slots),
        "tokens_pro_sekunde": round(metrics.get("predicted_tokens_seconds", 0), 1),
        "tokens_gesamt_erzeugt": int(metrics.get("tokens_predicted_total", 0)),
    }


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


def system_ressourcen() -> dict:
    """Swap/RAM-Vitalwerte (flarumstyler, 2026-07-07, nach Absturz-Forensik) —
    Daniel: Swap sass beim Absturz 4+ Stunden bei 100%, ohne dass irgendwas
    das gemeldet haette. Reiner /proc-Read, keine Zusatz-Abhaengigkeit."""
    try:
        werte = {}
        for zeile in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            k, v = zeile.split(":", 1)
            teile = v.strip().split()
            if teile:
                werte[k] = int(teile[0])  # kB
        mem_total = werte.get("MemTotal", 0)
        mem_avail = werte.get("MemAvailable", 0)
        swap_total = werte.get("SwapTotal", 0)
        swap_free = werte.get("SwapFree", 0)
        swap_belegt = swap_total - swap_free
        load1, load5, load15 = _os.getloadavg()
        return {
            "mem_gesamt_gb": round(mem_total / 1024 / 1024, 1),
            "mem_verfuegbar_gb": round(mem_avail / 1024 / 1024, 1),
            "mem_prozent_belegt": round((1 - mem_avail / mem_total) * 100, 1) if mem_total else None,
            "swap_gesamt_gb": round(swap_total / 1024 / 1024, 1),
            "swap_belegt_gb": round(swap_belegt / 1024 / 1024, 1),
            "swap_prozent": round(swap_belegt / swap_total * 100, 1) if swap_total else 0.0,
            "kerne": _os.cpu_count(),
            "load1": round(load1, 2),
            "load5": round(load5, 2),
            "load15": round(load15, 2),
        }
    except Exception:
        return {}


def oomd_eingriffe(stunden: int = 24) -> list[str]:
    """Zeigt ob systemd-oomd (seit 2026-07-07 aktiv) in den letzten Stunden
    einen Prozess wegen Speicherdruck/Swap-Ueberlastung gekillt hat."""
    try:
        result = subprocess.run(
            ["journalctl", "-u", "systemd-oomd", "--no-pager", "--since", f"-{stunden}h",
             "-o", "short-iso"],
            capture_output=True, text=True, timeout=5,
        )
        return [z.strip() for z in result.stdout.splitlines() if "killing" in z.lower() or "killed" in z.lower()][-10:]
    except Exception:
        return []


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

    # System-Ressourcen: Swap/RAM + oomd-Eingriffe (flarumstyler, 2026-07-07,
    # nach Absturz-Forensik — Swap sass 4+ Stunden bei 100% ohne jede Meldung).
    ressourcen = system_ressourcen()
    ressourcen["oomd_eingriffe_24h"] = oomd_eingriffe()
    report["system_ressourcen"] = ressourcen
    swap_pct = ressourcen.get("swap_prozent", 0.0)
    if swap_pct >= 80:
        report["warnings"].append(f"SWAP KRITISCH: {swap_pct}% belegt (oomd greift ab 85% ein)")
        log.error(f"SWAP KRITISCH: {swap_pct}%")
    elif swap_pct >= 60:
        report["warnings"].append(f"Swap erhoeht: {swap_pct}% belegt")
        log.warning(f"Swap erhoeht: {swap_pct}%")
    if ressourcen["oomd_eingriffe_24h"]:
        report["warnings"].append(f"oomd hat in den letzten 24h {len(ressourcen['oomd_eingriffe_24h'])}x eingegriffen")
        log.warning(f"oomd-Eingriffe: {ressourcen['oomd_eingriffe_24h']}")

    # Log-Fehler-Uebersicht VOR den Diensten berechnen, damit jeder Dienst seine
    # eigenen Fehler direkt an der Karte zeigen kann (Daniel: "direkt dort aufploppen
    # lassen mit Hinweis woher es kommt"), statt nur in einer getrennten Liste.
    log_fehler_global, log_fehler_pro_dienst = fehler_uebersicht()
    report["log_fehler"] = log_fehler_global

    # Individualisierbare Konfiguration (flarumstyler, 2026-07-07) — einmal fuer alle
    # Dienste auf einmal laden statt pro Dienst neu zu verbinden.
    alle_konfigurationen = dk.alle()

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

        details = service_details(name)
        konfig = alle_konfigurationen.get(name, {})
        beschreibung_standard = SERVICE_BESCHREIBUNG.get(name, "(keine Beschreibung hinterlegt)")
        beschreibung_override = konfig.get("beschreibung_override")
        report["services"][name] = {
            "active": active,
            "port_ok": port_ok,
            "health_ok": health,
            "status": status,
            "beschreibung": beschreibung_override or beschreibung_standard,
            "beschreibung_standard": beschreibung_standard,
            "beschreibung_eigene_fassung": bool(beschreibung_override),
            "steuerbar": name not in SERVICES_GESPERRT_FUER_AKTIONEN,
            "seit_wann": details["seit_wann"],
            "neustarts": details["neustarts"],
            "speicher_mb": details["speicher_mb"],
            "letzte_logs": service_letzte_logs(name),
            "gruppe": "flarum" if name in SERVICES_GRUPPE_FLARUM else "welt",
            "llm_status": llama_status(LLAMA_SERVER_PORTS[name]) if name in LLAMA_SERVER_PORTS else None,
            "llm_warteschlange": llm_warteschlange_status(LLAMA_SCHEDULER_SERVER[name]) if name in LLAMA_SCHEDULER_SERVER else None,
            "eigene_fehler": log_fehler_pro_dienst.get(name, {}),
            "konfiguration": konfig,
            "konfigurierbar": name in DIENSTE_MIT_KONFIGURATION,
            "individualisierung_hinweis": _individualisierung_hinweis(name),
            "technische_doku": _technische_doku(name),
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

    # Wesen-eigene Dienste (Baustein 4, Chat-Wizard, 2026-07-07) — dynamisch aus
    # wesen_eigene_dienste statt aus einer hartcodierten Liste, weil Daniel jederzeit
    # neue per Chat erzeugen kann. status='deaktiviert' zeigt bewusst NICHT als "down"
    # (analog zu erwartet_aus) -- das war Daniels eigene Entscheidung, kein Problem.
    for row in wed.lade_alle():
        name = row["dienst_name"]
        active = service_is_active(name)
        if row["status"] == "deaktiviert":
            status = "deaktiviert"
        else:
            status = "ok" if active else "down"
        details = service_details(name)
        auftrag_kurz = (row["verhalten_prompt"] or "")[:400]
        report["services"][name] = {
            "active": active,
            "port_ok": None,
            "health_ok": None,
            "status": status,
            "beschreibung": f"{row['anzeige_name']} — Wesen-eigener Dienst fuer {row['wesen']}, "
                            f"Takt {row['takt_sekunden']}s, Ziel: {row['ziel_typ']}.",
            "beschreibung_standard": f"{row['anzeige_name']} — Wesen-eigener Dienst fuer {row['wesen']}.",
            "beschreibung_eigene_fassung": False,
            "steuerbar": True,
            "seit_wann": details["seit_wann"],
            "neustarts": details["neustarts"],
            "speicher_mb": details["speicher_mb"],
            "letzte_logs": service_letzte_logs(name),
            "gruppe": "flarum",
            "llm_status": None,
            "llm_warteschlange": None,
            "eigene_fehler": log_fehler_pro_dienst.get(name, {}),
            "konfiguration": {k: row[k] for k in ("wesen", "anzeige_name", "takt_sekunden", "ziel_typ", "ziel_discussion_id") if row.get(k) is not None},
            "konfigurierbar": False,
            "individualisierung_hinweis": None,
            "technische_doku": f"Auftrag (Verhalten-Prompt): {auftrag_kurz}",
            "ist_wesen_eigener_dienst": True,
        }
        if status == "down":
            report["warnings"].append(f"{name}: inaktiv (Wesen-eigener Dienst, erzeugt aber nicht/nicht mehr gestartet)")
            log.warning(f"WESEN-EIGENER DIENST DOWN: {name}")

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

    # Log-Fehler-Uebersicht wird jetzt vor der Dienste-Schleife berechnet (siehe oben),
    # damit sie pro Dienst mit angehaengt werden kann — hier nicht mehr noetig.

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
        "swap_prozent": report.get("system_ressourcen", {}).get("swap_prozent"),
        "mem_prozent_belegt": report.get("system_ressourcen", {}).get("mem_prozent_belegt"),
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
