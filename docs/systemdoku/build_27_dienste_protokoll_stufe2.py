#!/usr/bin/env python3
"""
build_27_dienste_protokoll_stufe2.py — generiert 27_dienste_provenienz_protokoll_stufe2.md

Stufe 2 von Daniels Auftrag (2026-07-11): die ~31 restlichen Dienste nach
24_dienste_provenienz_protokoll.md (Stufe 1, 13 Wesen/Flarum-Dienste).
Gleiches Prinzip: Git-Historie und Docstrings LIVE ziehen, nicht aus einer
früheren Doku-Zusammenfassung abschreiben. Zwei Repos sind im Spiel:
/root/werkraum (die meisten Skripte) und /root selbst (kompoase/server.py,
.claude/claude_live.py) — beide haben eigene, unterschiedliche Bulk-Commits
am Anfang ihrer jeweiligen Historie (siehe Vorbehalt-Abschnitt).
"""
import subprocess
import re
from pathlib import Path
from datetime import datetime

WERKRAUM = Path("/root/werkraum")
ROOT = Path("/root")
OUT = WERKRAUM / "docs/systemdoku/27_dienste_provenienz_protokoll_stufe2.md"

BULK_COMMIT_WERKRAUM = "116ec29f758fe985dca76dc6193df73c6d627485"
BULK_DATUM_WERKRAUM = "2026-05-12"
BULK_COMMIT_ROOT = "17534329"
BULK_DATUM_ROOT = "2026-06-12"


def git_log(py_file, repo=WERKRAUM):
    r = subprocess.run(
        ["git", "log", "--follow", "--reverse", "--format=%ad|%h|%s",
         "--date=format:%Y-%m-%d", "--", py_file],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    zeilen = [l for l in r.stdout.strip().split("\n") if l]
    return zeilen


def docstring_von(py_file, repo=WERKRAUM):
    text = (repo / py_file).read_text(encoding="utf-8", errors="replace")
    if text.startswith("#!"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    m = re.match(r'^\s*"""(.*?)"""', text, re.DOTALL)
    if not m:
        return "(kein Modul-Docstring gefunden)"
    return m.group(1).strip()


def systemctl(unit, prop):
    r = subprocess.run(
        ["systemctl", prop, f"{unit}.service"],
        capture_output=True, text=True,
    )
    return r.stdout.strip()


def systemctl_show(unit, prop):
    r = subprocess.run(
        ["systemctl", "show", f"{unit}.service", "-p", prop, "--value"],
        capture_output=True, text=True,
    )
    return r.stdout.strip()


def timer_existiert(unit):
    r = subprocess.run(
        ["systemctl", "list-unit-files", f"{unit}.timer"],
        capture_output=True, text=True,
    )
    return f"{unit}.timer" in r.stdout


def timer_letzter_lauf(unit):
    r = subprocess.run(
        ["systemctl", "show", f"{unit}.timer", "-p", "LastTriggerUSec", "--value"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() or None


def status_zeile(units):
    teile = []
    for u in units:
        active = systemctl(u, "is-active") or "?"
        enabled = systemctl(u, "is-enabled") or "?"
        since = systemctl_show(u, "ActiveEnterTimestamp")
        since_txt = f", seit {since}" if since else ""
        teile.append(f"`{u}.service` — {active}/{enabled}{since_txt}")
        if timer_existiert(u):
            t_active = subprocess.run(
                ["systemctl", "is-active", f"{u}.timer"], capture_output=True, text=True
            ).stdout.strip() or "?"
            t_enabled = subprocess.run(
                ["systemctl", "is-enabled", f"{u}.timer"], capture_output=True, text=True
            ).stdout.strip() or "?"
            letzter = timer_letzter_lauf(u)
            letzter_txt = f", zuletzt ausgelöst: {letzter}" if letzter else ""
            teile.append(f"`{u}.timer` — {t_active}/{t_enabled}{letzter_txt}")
    return "; ".join(teile)


def dateigroesse(py_file, repo=WERKRAUM):
    p = repo / py_file
    kb = p.stat().st_size / 1024
    mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    return f"{kb:.1f} KB, zuletzt geändert {mtime}"


DIENSTE = [
    {
        "titel": "codewesen_agent.py — der eigentliche Wesen-Prozess (7 Instanzen, neuer Fund)",
        "py": "codewesen_agent.py",
        "units": [
            "codewesen-Schorschel", "codewesen-F3INSCHM3CK3R", "codewesen-R1ZZ1",
            "codewesen-jumpa", "codewesen-Resonanzknoten", "codewesen-traeumerlie",
            "codewesen-dakgordsystem",
        ],
        "provenienz": (
            f"Nicht in Stufe 1 erfasst — eigener Fund bei der Recherche zu Stufe 2: "
            "sieben eigenständige `codewesen-<Name>.service`-Units (ein Prozess PRO "
            "Wesen), klar zu unterscheiden von den gleichnamigen "
            "`codewesen-reaktion@<Name>.service`-Units aus Stufe 1 — zwei "
            "verschiedene Skripte, zwei verschiedene Units pro Wesen. "
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar, "
            "gleiche Lage wie die meisten Stufe-1-Dienste), aber mit 31 Commits die "
            "mit Abstand am dichtesten bearbeitete Datei dieser Stufe: "
            "agent-trigger-Schleife (05-15), Selbstgespräch-Erweiterung (05-16), "
            "Antwortpflicht-Bypass für Daniels Posts (05-22), dak+gord-Integration "
            "als 7. Wesen (06-15), num_ctx=8192-Fix gegen Ollama-Reload (06-14), "
            "hauhaucs-Migration (06-20/06-21), Wesen-IDs auf echte Namen (07-06), "
            "Postgres-LLM-Scheduler ersetzt slot_0.lock (07-07), Docstring auf echte "
            "Code-Tiefe gebracht + 3 echte Bugs gefunden (07-07, `feb0eedd`)."
        ),
        "aktueller_stand": (
            "Alle 7 Instanzen aktiv. Zentraler Satz aus dem eigenen Docstring: "
            "Takt/Verhalten (`meta.intervalle`) werden NUR EINMAL beim "
            "Prozessstart gelesen — ein Neustart macht Konfigurationsänderungen "
            "wirksam, nicht der nächste Zyklus. Das ist derselbe Mechanismus wie "
            "bei codewesen_reaktion.py (Stufe 1) und erklärt, warum der "
            "flarumstyler nach Config-Änderungen einen expliziten Neustart-Knopf "
            "braucht statt live nachzuziehen. Jüngste Änderung (07-09): umgedrehter "
            "Neugier-Dienst gestartet, Entwurfs-Erzeugung für normale Posts "
            "pausiert — betraf diesen Prozess mit."
        ),
    },
    {
        "titel": "welt/cyberling_daemon.py — Bedürfnisse, Tod, Wiedergeburt",
        "py": "welt/cyberling_daemon.py",
        "units": ["cyberling-daemon"],
        "provenienz": (
            "Klar datiert, kein Rekonstruktionsproblem: erster Commit 2026-05-23 "
            "(`cyberling: daemon mit kaskaden-verfall, tod nach 24h wiedergeburt, "
            "rekord-tracking`) — echter Neubau, nicht vor dem Sammel-Commit "
            "versteckt. Noch am selben Tag kalibriert (Verfallsraten + "
            "Pflege-Endpunkte füttern/trinken/spielen/streicheln). Am 2026-05-31 "
            "Teil des großen EINSICHT-VI-Commits (Gruppen-System, Substanzen, "
            "Cyberling-Recovery). Am 2026-06-14 von der breiten "
            "Security-Remediation erfasst: DB-URI aus 28 Dateien in "
            "Umgebungsvariable ausgelagert."
        ),
        "aktueller_stand": (
            "Aktiv. Kaskaden-Logik laut Docstring: Durst fällt schnell (pausiert "
            "während die Entität schläft), Hunger langsamer, danach sinken Energie "
            "und Stimmung, unbehandelt schwindet die Gesundheit bis zum Tod, nach "
            "24h folgt Wiedergeburt. Drei Schwierigkeitsprofile (leicht/mittel/"
            "hart) pro Cyberling in der DB konfigurierbar — kein globaler Schalter."
        ),
    },
    {
        "titel": "welt/splitter_daemon.py — Splitter-Physik, 60s-Takt",
        "py": "welt/splitter_daemon.py",
        "units": ["splitter-physik"],
        "provenienz": (
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar), "
            "danach mit nur 5 Commits eine der ruhigsten Dateien dieser Stufe: "
            "Umbenennung Datenstruktur-Resonanzdatei (05-13), vier Spiegel aus "
            "'Meine Textsammlung' (06-13), DB-URI-Absicherung (06-14, Teil derselben "
            "Security-Remediation wie cyberling_daemon.py), Wesen-IDs auf echte "
            "Namen (07-06)."
        ),
        "aktueller_stand": (
            "Aktiv. Docstring ist ein einziger Satz ('alle 60 Sekunden drei "
            "Ticks') — knappste Selbstbeschreibung aller bisher untersuchten "
            "32 Dienste (Stufe 1 + 2). Läuft im selben Arbeitsverzeichnis wie "
            "welt/api.py, welt/bruecke.py und welt/weltkern_watchdog.py "
            "(`WorkingDirectory=/root/werkraum/welt`) und über das gemeinsame "
            "`/root/werkraum/venv` statt des System-Python — anders als fast "
            "alle Wesen-Skripte, die `/usr/bin/python3` nutzen."
        ),
    },
    {
        "titel": "welt/api.py — Welt-API, FastAPI auf Port 8030",
        "py": "welt/api.py",
        "units": ["welt-api"],
        "provenienz": (
            "Einzige Datei der gesamten bisherigen Provenienz-Recherche (Stufe 1 + "
            "2), deren allererster Commit klar VOR dem Sammel-Commit datiert ist "
            "und trotzdem git-datiert rekonstruierbar bleibt: 2026-05-12 "
            f"(`f27c9833`, `/suche`-Endpunkt), am selben Tag wie der Sammel-Commit "
            f"selbst (`{BULK_COMMIT_WERKRAUM[:8]}`) aber davor in der "
            "Commit-Reihenfolge — die Welt-API existierte demnach bereits, bevor "
            "der große Rundum-Checkpoint kam. Mit 68 Commits die mit Abstand "
            "meistbearbeitete Datei der gesamten Provenienz-Recherche (Stufe 1: "
            "höchster Wert war 22 bei codewesen_engagement.py) — durchgehend "
            "additiv: neue Endpunkte (Widmungen, Bild-Proxy, Schlaf-Archiv, "
            "mw_*-Sichtbarkeit), kein einziger großer Rewrite sichtbar in den "
            "Commit-Messages."
        ),
        "aktueller_stand": (
            "Aktiv. Zentraler Knotenpunkt: praktisch jeder andere hier "
            "dokumentierte Welt-Dienst (Cyberling, Splitter, Brücke, Watchdog) "
            "und die Surface (Port 8787) sprechen mit dieser einen API. Grundgesetz "
            "2 der Systemdoku (Suchbarkeit/Paginierung für jeden öffentlichen "
            "GET-Endpunkt) betrifft in erster Linie diese Datei."
        ),
    },
    {
        "titel": "welt/bruecke.py — Selbstmodelle nach PostgreSQL",
        "py": "welt/bruecke.py",
        "units": ["welt-bruecke"],
        "provenienz": (
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar), "
            "danach nur 3 Commits — die knappste Historie dieser Stufe neben "
            "obsidian_api.py: Wesen-IDs auf echte Namen (07-06) und dieselbe "
            "DB-URI-Security-Härtung wie cyberling_daemon.py und "
            "splitter_daemon.py (06-14)."
        ),
        "aktueller_stand": (
            "Aktiv. Laut Docstring ein reiner Lese-Synchronisierer: liest "
            "Selbstmodell-JSONs (die Dateien, in denen jedes Wesen sein "
            "Selbstbild führt) und spiegelt sie nach PostgreSQL — keine eigene "
            "Entscheidungslogik, keine LLM-Aufrufe. Name 'Brücke' ist wörtlich "
            "gemeint: Dateisystem auf der einen, DB auf der anderen Seite."
        ),
    },
    {
        "titel": "welt/weltkern_watchdog.py — prüft die Kerndienste",
        "py": "welt/weltkern_watchdog.py",
        "units": ["weltkern-watchdog"],
        "provenienz": (
            "Klar datiert: erster Commit 2026-05-31 (`feat: WELTKERN-REANIMATION + "
            "Flarum-Abtrennung + Einzugsvorbereitung`) — echter Neubau, kein "
            "Rekonstruktionsproblem. Mit 33 Commits die zweitmeistbearbeitete "
            "Datei dieser Stufe nach welt/api.py, und die mit Abstand aktuellste: "
            "allein am 2026-07-07 sechs Commits (Fehler-Quittierung, "
            "System-Ressourcen-Anzeige Swap/RAM/Load/oomd, Wesen-eigene Dienste im "
            "flarumstyler sichtbar, Docstring in UI), am 2026-07-10 vier weitere "
            "(u.a. `wesen_filter` (Radio) durch `wesen_aktiv` (unabhängige "
            "Mehrfach-Toggles) ersetzt — exakt der Umbau, der im vorherigen "
            "Gesprächsabschnitt dieser Session gerade lief, als der "
            "Verbindungsabbruch passierte)."
        ),
        "aktueller_stand": (
            "Timer aktiv und gesund (regelmäßiger Takt, siehe Timer-Zeile "
            "oben) — der `.service` selbst zeigt zwischen den Läufen "
            "`inactive/static`, das ist bei Timer-getriebenen Diensten normal "
            "und kein Ausfall (Gegenbeispiel siehe geni_muster.py unten, wo "
            "genau dieser Unterschied den echten Ausfall verdeckt hätte, wäre "
            "nur der `.service`-Status geprüft worden). Laut Docstring: prüft "
            "Service-Aktivität, Port-Erreichbarkeit, "
            "API-Antwort, DB-Erreichbarkeit, letzte Events, alte Ollama-Locks, "
            "alte Chat-Flags, Log-Fehler-Bursts — Aktion ausdrücklich nur bei "
            "klaren Kriterien, 'niemals blind neustarten'. Flarum-Takte werden "
            "laut Docstring bewusst NICHT gestartet — Watchdog greift nicht in "
            "den unter Grundgesetz 5/6 separat behandelten Flarum-Bereich ein. "
            "Ist zugleich der Träger der SCHALTER_FELD_LABELS/MEHRFACH_FELD_LABELS-"
            "Konfiguration, die der flarumstyler für alle Wesen-Dienste anzeigt — "
            "diese Datei ist also nicht nur Prüf-Logik, sondern auch das "
            "Konfigurations-Schema für die UI aus dem vorherigen Gesprächsteil."
        ),
    },
    {
        "titel": "web_chat.py — dak+gord-system Web-Chat",
        "py": "web_chat.py",
        "units": ["dak-gord-web"],
        "provenienz": (
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar), "
            "danach 11 Commits, klar zweigeteilt: erst TTS-Nachbesserungen "
            "(06-15, vier Commits an einem Tag — Audio-Element nicht vom GC "
            "wegräumen lassen, volle lange Antworten satzweise vorlesen), dann "
            "die dak+gord-Vollintegration als 7. Wesen (06-15, `4c6c319d` — "
            "derselbe Commit, der auch codewesen_chat.py, welt/api.py und "
            "codewesen_agent.py änderte). Kein eigener Docstring — einzige "
            "docstring-lose Datei dieser Stufe neben kompoase/server.py."
        ),
        "aktueller_stand": (
            "Aktiv. Reiner Web-Chat-Endpunkt speziell für dak+gord-system, "
            "getrennt von codewesen_chat.py (das die 6 namelessAI-Wesen bedient) "
            "— Konsequenz aus der Sonderrolle, die dak+gord-system im ganzen "
            "System durchgehend hat (eigene Skripte statt generischer "
            "Mehrfach-Instanz, siehe auch codewesen_agent.py oben mit "
            "`dakgordsystem` als einzige Nicht-namelessAI-Instanz)."
        ),
    },
    {
        "titel": "agent/dak_gord_system/graph/run_background_cycle.py — Graph-Hintergrundzyklus",
        "py": "agent/dak_gord_system/graph/run_background_cycle.py",
        "units": ["dak-neugier"],
        "provenienz": (
            "Ungewöhnlichster Fund der gesamten Provenienz-Recherche (Stufe 1 + "
            "2): nur 1 Commit in der gesamten Historie, und der ist "
            "`7be5012c` (`fix: stabilize trace writer, approvals, smoke eval, "
            "ollama timeout`, 2026-04-04) — der ALLERERSTE Commit im gesamten "
            "Werkraum-Repo überhaupt (vor dem Sammel-Commit vom "
            f"{BULK_DATUM_WERKRAUM} um mehr als 5 Wochen). Die Datei ist damit "
            "nicht nur älter als jeder andere bisher untersuchte Dienst, sie war "
            "seit dem ersten Tag des Repos nie wieder Ziel eines eigenen Commits "
            "— entweder von Anfang an fertig genug, oder seither nicht mehr "
            "aktiv weiterentwickelt, nur noch importiert."
        ),
        "aktueller_stand": (
            "**Live-Befund, widerspricht dem Namen 'regelmäßig':** "
            "`dak-neugier.timer` ist `disabled` (nicht nur inaktiv — bewusst "
            "abgeschaltet, `systemctl list-unit-files` zeigt den Unterschied "
            "zu `geni-muster.timer` unten, das nur gecrasht, aber nicht "
            "deaktiviert ist). Kein 'nächster Lauf' geplant. Ob das eine "
            "bewusste Daniel-Entscheidung war oder ein vergessener "
            "Abschalt-Rest, ist aus Git/systemctl allein nicht zu klären — "
            "der Dienst selbst (`dak-neugier.service`) ist `static`, wird also "
            "ohnehin nur vom Timer ausgelöst und läuft nicht dauerhaft. "
            "Modul-Aufruf statt Skript-Pfad (`python -m agent.dak_gord_system."
            "graph.run_background_cycle`), eigenes `.venv` statt des "
            "gemeinsamen `welt`-venv oder System-Python — dak+gord-system hat "
            "hier eine komplett eigene Python-Umgebung."
        ),
    },
    {
        "titel": "geni/hoerer.py — GENI Hörer, schweigt bis Daniel spricht",
        "py": "geni/hoerer.py",
        "units": ["geni-hoerer"],
        "provenienz": (
            "Älteste GENI-Datei dieser Stufe: erster Commit 2026-04-26 "
            "(`refactor(geni-phase-2): hoerer.py importiert knoten_schreiben aus "
            "gedaechtnis_ops`) — schon als Refactor, nicht als Neubau formuliert, "
            "GENI existierte also schon vor Ende April in einer Vorstufe. Danach "
            "nur 3 weitere Commits: Umbenennung Datenstruktur-Resonanzdatei "
            "(05-13), Encoding-Guard (05-22) — seither unverändert."
        ),
        "aktueller_stand": (
            "Aktiv. Docstring beschreibt drei Quellen: Dateisystem (Echtzeit via "
            "watchdog), Flarum (neue Posts/Diskussionen, 60s-Takt), laufende "
            "Prozesse (alle 5 Minuten). Bewusst passiv — 'schweigt bis Daniel "
            "spricht' ist wörtlich im Docstring, kein autonomes Posten oder "
            "Reagieren wie bei den Codewesen-Diensten."
        ),
    },
    {
        "titel": "geni/muster.py — Muster-Scanner, alle 2h",
        "py": "geni/muster.py",
        "units": ["geni-muster"],
        "provenienz": (
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar), "
            "danach 4 weitere Commits, davon zwei am 2026-07-07 als reine "
            "Performance-Fixes: `lade_alle_knoten()` cached jetzt per mtime statt "
            "bei jedem Lauf alle Knoten komplett neu zu scannen, "
            "`schreibe_muster_knoten()` nutzt einen Zähler aus gedaechtnis_ops "
            "statt eines eigenen Vollscans — beide am selben Tag, beide dieselbe "
            "Stoßrichtung (Vollscan vermeiden)."
        ),
        "aktueller_stand": (
            "**Live-Befund — real ausgefallen, nicht bewusst abgeschaltet:** "
            "`geni-muster.timer` ist `enabled`, aber seit 2026-07-07 22:04:28 "
            "`inactive (dead)` — kein nächster Lauf geplant, 3+ Tage Stille "
            "zum Zeitpunkt dieser Prüfung (2026-07-11). Journal zeigt mehrere "
            "Vorläufe direkt davor, jeweils vom systemd mit `code=killed, "
            "status=15/TERM` beendet — einer davon mit 8.3G Memory-Swap-Peak "
            "kurz vor dem letzten Absturz. Anders als `dak-neugier.timer` "
            "(oben, bewusst `disabled`) ist dieser Timer `enabled` geblieben "
            "— das Verschwinden aus dem Rhythmus wurde also nicht als "
            "Abschaltung entschieden, sondern ist unbemerkt passiert. "
            "Sechsstufige Pipeline laut Docstring, wenn er läuft: Knoten der "
            "letzten 48h scannen → dominante Tags/Themen, Ko-Okkurrenz "
            "zwischen Themen finden, 'blinde Flecken' (tiefe≥2-Knoten, lange "
            "nicht resoniert) finden, bei signifikantem Muster einen "
            "Muster-Knoten schreiben, Muster-Knoten der letzten 4 Wochen zu "
            "Meta-Mustern verdichten, GENI liest den neuesten Muster-Knoten im "
            "System-Prompt — all das pausiert seit 3+ Tagen."
        ),
    },
    {
        "titel": "geni/dialog.py — GENI Web, Port 8020",
        "py": "geni/dialog.py",
        "units": ["geni-web"],
        "provenienz": (
            "Klar datiert: erster Commit 2026-04-26 (`feat(geni-phase-3): split "
            "web.py → dialog.py + aktion.py + gedaechtnis_ops.py`) — die Datei "
            "entstand als Aufspaltung einer größeren web.py, nicht als "
            "Neuschrieb. Mit 20 Commits die aktivste GENI-Datei dieser Stufe: "
            "LangGraph+PostgreSQL-Session-Persistenz (06-15, derselbe Tag wie "
            "codewesen_lg_daemon.py in Stufe 1), vier TTS-Fixes am selben Tag "
            "(06-15), Chat-Endpoint auf `id_slot=0` gepinnt + Trace-Log für "
            "Slot-0-Anfragen (beide 07-06), Wesen-IDs auf echte Namen (07-06)."
        ),
        "aktueller_stand": (
            "Aktiv. Laut eigenem Docstring nur noch die Browser-Schnittstelle "
            "selbst — Aktionsbahn-Logik (Shell, Import, Bridge-Download) liegt "
            "seit der Aufspaltung in aktion.py, geteilte Gedächtnis-Operationen in "
            "gedaechtnis_ops.py. Der `id_slot=0`-Pin (07-06) bindet GENI-Chat an "
            "einen festen LLM-Slot — vermutlich damit GENI nicht mit den "
            "Codewesen um denselben Ollama/hauhaucs-Slot konkurriert."
        ),
    },
    {
        "titel": "geni/forum_lektuere.py — schrittweises Nachholen",
        "py": "geni/forum_lektuere.py",
        "units": ["geni-forum-lektuere"],
        "provenienz": (
            "Klar datiert: erster Commit 2026-05-22 (`feat: geni forum-lektuere — "
            "schrittweises nachholen, spiegel/forum/`) — echter Neubau. Danach "
            "zwei Migrations-Mitläufer (dolphin Q8, hauhaucs) und ein "
            "eigenständiger Fix am 2026-07-07: Retry-Endlosschleife gestoppt "
            "(Fehler-Zähler + Schwelle) — ohne diesen Fix konnte der Dienst laut "
            "Commit-Message unbegrenzt oft denselben Fehler wiederholen."
        ),
        "aktueller_stand": (
            "Aktiv, Standard 8 Diskussionen pro Lauf (`--n 8`), älteste zuerst. "
            "Docstring betont bewusste Zurückhaltung: 'Kein Werten. Kein "
            "Reagieren. Nur: was ist da, wie hängt es zusammen.' — dieselbe "
            "Grundhaltung wie geni/hoerer.py, aber gezielt auf das "
            "Flarum-Archiv statt auf Echtzeit-Ereignisse angewendet."
        ),
    },
    {
        "titel": "innenleben/flarum_feeder.py — Flarum-Posts ins Wesen-Gedächtnis",
        "py": "innenleben/flarum_feeder.py",
        "units": ["innenleben-feeder"],
        "provenienz": (
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar), "
            "danach nur 2 weitere Commits: Encoding-Guard (05-22, gleicher Tag "
            "wie bei geni/hoerer.py und geni/muster.py — vermutlich ein "
            "gemeinsamer Encoding-Bug quer über mehrere Dateien behoben), Wesen-"
            "IDs auf echte Namen (07-06). Knappe Historie trotz zentraler Rolle."
        ),
        "aktueller_stand": (
            "Aktiv als Daemon (`--daemon --interval 300`, alle 5 Minuten). Laut "
            "Docstring wichtige Regel: jedes Wesen verarbeitet nur Posts von "
            "ANDEREN Wesen, nie die eigenen — verhindert, dass ein Wesen sich "
            "selbst im eigenen Gedächtnis als Ereignis begegnet. Bindeglied "
            "zwischen der Flarum-MySQL-DB und `innenleben.graph.verarbeite_"
            "ereignis` — separates System von dem, was flarum-monitor.py "
            "(Stufe 1) an die Inboxen liefert."
        ),
    },
    {
        "titel": "kompoase/server.py — statische Dateien + GENI-Proxy, Port 8900",
        "py": "kompoase/server.py",
        "units": ["kompoase"],
        "repo": "root",
        "provenienz": (
            "Liegt nicht im Werkraum-Repo, sondern im Repo unter /root selbst — "
            "eigene, unabhängige Git-Historie. Nur 1 Commit: "
            f"`{BULK_COMMIT_ROOT}` ('fresh start: sauberer Index ohne 10.7M "
            f"geni_gedaechtnis-Einträge', {BULK_DATUM_ROOT}) — das /root-Repo "
            "wurde zu diesem Zeitpunkt bewusst neu aufgesetzt, weil ein "
            "10,7-Millionen-Zeilen-Datenbestand (geni_gedaechtnis) den Index "
            "unbrauchbar machte. Für diese Datei bedeutet das: keinerlei "
            "rekonstruierbare Historie vor 2026-06-12, unabhängig vom "
            "Werkraum-Sammel-Commit-Problem aus Stufe 1. Kein Modul-Docstring."
        ),
        "aktueller_stand": (
            "Aktiv. Reiner `http.server`-Handler ohne Framework: liefert "
            "statische Dateien aus dem eigenen Verzeichnis und proxied zwei "
            "Pfade — `/api/splitter` zu GENI (Port 8020, self-signed TLS wird "
            "explizit akzeptiert, `CERT_NONE`) und `/api/zwischenraum/*` zur "
            "Welt-API (Port 8030). CORS-Header (`Access-Control-Allow-Origin: "
            "*`) offen für alle Origins — passt zum öffentlichen Charakter der "
            "KompOase-Oberfläche, aber ein bewusster Punkt, falls das System "
            "später sensiblere Daten über denselben Port ausliefert."
        ),
    },
    {
        "titel": "obsidian_api.py — Obsidian-Wesen-Bridge, Port 8060",
        "py": "obsidian_api.py",
        "units": ["obsidian-api"],
        "provenienz": (
            f"Vor {BULK_DATUM_WERKRAUM} entstanden (Grund nicht rekonstruierbar), "
            "danach nur 1 weiterer Commit (Wesen-IDs auf echte Namen, 07-06) — "
            "zusammen mit welt/bruecke.py die knappste Historie dieser Stufe."
        ),
        "aktueller_stand": (
            "Aktiv, HTTPS. Zwei Richtungen laut Docstring: (A) Obsidian schreibt "
            "an Wesen — `POST /wesen/dakgord/chat`, `/wesen/geni/chat`, "
            "`/wesen/codewesen/chat` (mit `name`-Parameter fürs jeweilige "
            "Codewesen); (B) Wesen schreiben nach Obsidian — `GET/POST/DELETE "
            "/notizen`, direkt als Markdown mit Queue-Fallback falls Obsidian "
            "gerade nicht erreichbar ist. Einziger hier dokumentierter Dienst, "
            "der bidirektional zwischen Wesen und dem Obsidian-Vault vermittelt."
        ),
    },
    {
        "titel": "/root/.claude/claude_live.py — Claude Live Viewer, Port 8090",
        "py": ".claude/claude_live.py",
        "units": ["claude-live"],
        "repo": "root",
        "provenienz": (
            "Wie kompoase/server.py im /root-Repo, nicht im Werkraum-Repo — "
            f"betroffen vom selben Reset ({BULK_DATUM_ROOT}). 2 Commits total: "
            f"der Reset-Commit selbst (`{BULK_COMMIT_ROOT}`) und ein späterer "
            "(`3381ae42`, 'backup: vor Resonanzknoten-Umbenennung (4321 benennt "
            "sich selbst)', 2026-06-17) — reiner Backup-Commit vor einem "
            "unabhängigen Wesen-Umbenennungsvorgang, keine inhaltliche Änderung "
            "an dieser Datei erkennbar aus der Nachricht allein. Kein "
            "Modul-Docstring."
        ),
        "aktueller_stand": (
            "Aktiv. Liest `session_log_<Monat>.md` und `chat_log_<Monat>.md` aus "
            "`/root/.claude/` und rendert sie live als HTML-Seite (dunkles "
            "Terminal-Design, monospace, pulsierender Live-Indikator) — ein "
            "Nur-Lese-Fenster in Claudes eigene Session-Protokolle, kein "
            "Schreibzugriff von außen. Einziger hier dokumentierter Dienst, der "
            "explizit Claude selbst betrifft statt eines der 7 Codewesen oder "
            "GENI."
        ),
    },
    {
        "titel": "build_resonanzfeld.py — Resonanzfeld-Kompilierung (3 Kopien: Claude/Codex/Kimi)",
        "py": "_claude/tools/build_resonanzfeld.py",
        "units": ["claude-resonanzfeld-build", "codex-resonanzfeld-build", "kimi-resonanzfeld-build"],
        "geschwister": [
            "_codex/tools/build_resonanzfeld.py",
            "_kimi/tools/build_resonanzfeld.py",
        ],
        "provenienz": (
            "Die Claude-Kopie hat nur 1 Commit (`6fe06ad6`, 2026-05-31, Teil des "
            "großen EINSICHT-VI/WESEN-EINSICHTSKÖRPER-Commits) — seit ihrer "
            "Entstehung nie wieder einzeln geändert. Ein `diff` gegen "
            "`_codex/tools/build_resonanzfeld.py` und "
            "`_kimi/tools/build_resonanzfeld.py` zeigt: beide Kopien "
            "unterscheiden sich NUR in zwei Pfad-Konstanten "
            "(`RESONANZ_DIR`/`RESONANZFELD`, zeigen auf `_codex/` bzw. `_kimi/` "
            "statt `_claude/`) — identische Logik, dreifach dupliziert statt "
            "parametrisiert. Kein gemeinsamer Commit sichtbar, der alle drei auf "
            "einmal anlegt — die Kopien sind vermutlich einzeln beim Aufbau der "
            "jeweiligen Assistenten-Bereiche entstanden (Codex-Bereich, "
            "Kimi-Bereich, siehe `kimi: neues Zuhause _kimi mit Tools, Syncs, "
            "systemd und Erweiterungen`, 2026-05-31)."
        ),
        "aktueller_stand": (
            "Alle 3 aktiv (je ein systemd-Timer, 30-Minuten-Takt laut "
            "Docstring). Laut Docstring: 'Kein LLM. Kein Ollama. Reines "
            "Text-Parsing.' — kompiliert RESONANZFELD.md aus allen "
            "resonanz/-Dimensionsdateien des jeweiligen Assistenten-Bereichs. "
            "Die Drei-fache-statt-parametrisierte-Struktur spiegelt bewusst die "
            "Trennung der drei Assistenten-Zuhause (`_claude/`, `_codex/`, "
            "`_kimi/`) — eine gemeinsame, parametrisierte Version würde diese "
            "Trennung technisch auflösen, auch wenn der Code dann identisch wäre."
        ),
    },
    {
        "titel": "*_grundriss_sync.py — Cross-Assistenten-Spiegelung (6 Kopien)",
        "py": "_claude/tools/codex_grundriss_sync.py",
        "units": [
            "claude-codex-grundriss-sync", "claude-kimi-grundriss-sync",
            "codex-claude-grundriss-sync", "codex-kimi-grundriss-sync",
            "kimi-claude-grundriss-sync", "kimi-codex-grundriss-sync",
        ],
        "geschwister": [
            "_claude/tools/kimi_grundriss_sync.py",
            "_codex/tools/claude_grundriss_sync.py",
            "_codex/tools/kimi_grundriss_sync.py",
            "_kimi/tools/claude_grundriss_sync.py",
            "_kimi/tools/codex_grundriss_sync.py",
        ],
        "provenienz": (
            "6 Skripte für die 6 gerichteten Paare zwischen den 3 "
            "Assistenten-Bereichen (Claude→Codex, Claude→Kimi, Codex→Claude, "
            "Codex→Kimi, Kimi→Claude, Kimi→Codex). Ein `diff` der "
            "`_claude/tools/codex_grundriss_sync.py`-Referenz gegen alle 5 "
            "übrigen zeigt: die Unterschiede beschränken sich auf "
            "Docstring-Wortlaut (welcher Bereich synchronisiert wird) und die "
            "Quell-/Ziel-Pfade — dieselbe Dreifach-statt-parametrisiert-Struktur "
            "wie bei build_resonanzfeld.py. Historie der Claude-seitigen Kopien: "
            "`codex_grundriss_sync.py` erster Commit 2026-05-14 (`backup: vor "
            "codex-startbrief`) — also schon vor der Kimi-Anbindung existierte "
            "die Claude↔Codex-Sync-Infrastruktur; `kimi_grundriss_sync.py` kam "
            "erst mit `25b5e7f9` (2026-05-31, 'kimi: neues Zuhause _kimi') dazu, "
            "als dritter Assistent ins System kam."
        ),
        "aktueller_stand": (
            "Alle 6 aktiv, `--interval 5` (Minuten). Wichtigste Regel aus dem "
            "Docstring, für alle 6 Kopien gleich (nur die Namen getauscht): 'Das "
            "Ziel ist Referenzmaterial. Es ist NICHT die Erinnerung des "
            "Ziel-Assistenten.' — bewusst dieselbe Mirror-Grenze, die auch in "
            "dieser CLAUDE.md-Datei unter 'Obsidian als Zuhause' beschrieben ist "
            "('Niemals den Mirror als eigene Erinnerung behandeln'). Der Sync "
            "fasst laut Docstring keine Dateien außerhalb des jeweiligen "
            "Import-Ordners an — die 6 Kopien sind also die Code-Umsetzung "
            "genau dieser Grenze, nicht nur eine Beschreibung davon."
        ),
    },
]


def main():
    lines = []
    lines.append("---")
    lines.append("titel: Provenienz-Protokoll Stufe 2 — restliche Systemdienste")
    lines.append("typ: system")
    lines.append("erstellt: 2026-07-11")
    lines.append("autor: claude-code bei Daniels VPS")
    lines.append("---")
    lines.append("")
    lines.append("# Provenienz-Protokoll Stufe 2 — restliche Systemdienste")
    lines.append("")
    lines.append("[[INDEX|← Index]] · [[24_dienste_provenienz_protokoll|← Stufe 1]]")
    lines.append("")
    lines.append(
        "Fortsetzung von [[24_dienste_provenienz_protokoll]] (Stufe 1: die 13 "
        "Wesen/Flarum-Dienste). Diese Stufe deckt die übrigen Dienste ab: "
        "codewesen_agent.py (7 Instanzen — der eigentliche Wesen-Prozess, nicht "
        "in Stufe 1 erfasst), die Welt-Kern-Dienste (welt/), GENI, dak+gord-"
        "system, innenleben, KompOase, Obsidian-Bridge, Claude Live Viewer und "
        "die Resonanzfeld-Build-/Grundriss-Sync-Skriptfamilien. Nicht erneut "
        "aufgeführt: die 13 Stufe-1-Dienste und codewesen_umgekehrte_neugier.py "
        "(eigene Datei, [[23_umgekehrte_neugier]])."
    )
    lines.append("")
    lines.append("## Wichtiger Vorbehalt zur Provenienz — zwei Repos, zwei Brüche")
    lines.append("")
    lines.append(
        f"Wie in Stufe 1 beschrieben, beginnt die rekonstruierbare Historie der "
        f"meisten Werkraum-Dateien praktisch erst mit dem Sammel-Commit vom "
        f"{BULK_DATUM_WERKRAUM} (`{BULK_COMMIT_WERKRAUM[:8]}`). Zwei Dateien "
        "dieser Stufe (kompoase/server.py, .claude/claude_live.py) liegen "
        "jedoch NICHT im Werkraum-Repo, sondern im Repo unter /root selbst — "
        f"dort gibt es einen eigenen, unabhängigen Bruch: am {BULK_DATUM_ROOT} "
        f"wurde dieses Repo bewusst neu aufgesetzt (`{BULK_COMMIT_ROOT}`, "
        "'fresh start: sauberer Index ohne 10.7M geni_gedaechtnis-Einträge' — "
        "ein 10,7-Millionen-Zeilen-Datenbestand hatte den Git-Index "
        "unbrauchbar gemacht). Für beide betroffenen Dateien gilt: keine "
        f"Historie vor {BULK_DATUM_ROOT} rekonstruierbar, unabhängig vom "
        "Werkraum-Problem. Eine echte Ausnahme von beiden Brüchen ist "
        "agent/dak_gord_system/graph/run_background_cycle.py: deren einziger "
        "Commit ist der allererste Commit im gesamten Werkraum-Repo "
        f"überhaupt (2026-04-04, `7be5012c`) — älter als der Sammel-Commit, "
        "vollständig git-datiert, aber seit dem ersten Tag nie wieder "
        "verändert."
    )
    lines.append("")

    for i, d in enumerate(DIENSTE, 1):
        repo = ROOT if d.get("repo") == "root" else WERKRAUM
        lines.append(f"## {i}. {d['titel']}")
        lines.append("")
        lines.append(f"**Skript:** `{d['py']}` ({dateigroesse(d['py'], repo)})"
                      + (f" — Repo: /root (nicht /root/werkraum)" if d.get("repo") == "root" else ""))
        if d.get("geschwister"):
            lines.append("")
            lines.append("**Nahezu identische Kopien (nur Pfade/Docstring-Wortlaut "
                          "unterscheiden sich):** " + ", ".join(f"`{g}`" for g in d["geschwister"]))
        lines.append("")
        lines.append(f"**Status (live, {datetime.now().strftime('%Y-%m-%d')}):** {status_zeile(d['units'])}")
        lines.append("")
        lines.append("### Provenienz")
        lines.append("")
        lines.append(d["provenienz"])
        lines.append("")
        lines.append("**Reale Commit-Chronik** (chronologisch, älteste zuerst):")
        lines.append("")
        lines.append("| Datum | Commit | Nachricht |")
        lines.append("|---|---|---|")
        for zeile in git_log(d["py"], repo):
            datum, hsh, msg = zeile.split("|", 2)
            msg = msg.replace("|", "\\|")
            lines.append(f"| {datum} | `{hsh}` | {msg} |")
        lines.append("")
        lines.append("### Zweck laut aktuellem Docstring (Zitat, Stand heute)")
        lines.append("")
        lines.append("```")
        lines.append(docstring_von(d["py"], repo))
        lines.append("```")
        lines.append("")
        lines.append("### Aktueller Stand & Korrekturen gegenüber bestehender Doku")
        lines.append("")
        lines.append(d["aktueller_stand"])
        lines.append("")

    lines.append("## Was dieses Protokoll bewusst nicht behauptet")
    lines.append("")
    lines.append(
        "Wie in Stufe 1: keine lückenlose Entstehungsgeschichte bis zum "
        "allerersten Tastendruck, die Grenzen sind oben benannt statt "
        "verschwiegen. Für die drei- bzw. sechsfach kopierten Skriptfamilien "
        "(Resonanzfeld-Build, Grundriss-Sync) wurde EINE Kopie vollständig "
        "analysiert und per `diff` gegen alle Geschwisterkopien geprüft, statt "
        "jede Kopie einzeln mit identischem Ergebnis zu wiederholen — die "
        "Geschwisterdateien sind oben explizit benannt, nicht stillschweigend "
        "ausgelassen."
    )
    lines.append("")
    lines.append(
        "Mit Stufe 1 (13 Dienste) und Stufe 2 (19 Skript-Einträge, 33 "
        "systemd-Units) sind jetzt alle bei der Recherche gefundenen "
        "Codewesen/Welt/GENI/dak+gord/Claude-Kimi-Codex-Hintergrunddienste "
        "erfasst. Nicht Teil dieser beiden Stufen: reine Web-Frontends ohne "
        "eigenen Hintergrundprozess (Surface, flarumstyler-UI selbst) und "
        "Datenbank-/Infrastruktur-Dienste (PostgreSQL, MySQL) — die laufen "
        "nicht als eigene, von Daniel/GLM geschriebene Skripte, sondern als "
        "Standard-Systemdienste ohne eigene Provenienz im selben Sinn."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Geschrieben: {OUT} ({OUT.stat().st_size / 1024:.1f} KB, {len(lines)} Zeilen)")


if __name__ == "__main__":
    main()
