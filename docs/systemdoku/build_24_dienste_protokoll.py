#!/usr/bin/env python3
"""
build_24_dienste_protokoll.py — generiert 24_dienste_provenienz_protokoll.md

Zieht Git-Historie und Docstrings LIVE aus dem Werkraum-Repo (statt sie
inline in die Doku zu tippen) — die Prosa-Analyse pro Dienst steht unten
in DIENSTE, alles Maschinenlesbare (Commits, Docstring, systemctl-Status)
wird beim Lauf frisch geholt.
"""
import subprocess
import re
from pathlib import Path
from datetime import datetime

WERKRAUM = Path("/root/werkraum")
OUT = WERKRAUM / "docs/systemdoku/24_dienste_provenienz_protokoll.md"

BULK_COMMIT = "116ec29f758fe985dca76dc6193df73c6d627485"
BULK_DATUM = "2026-05-12"


def git_log(py_file):
    r = subprocess.run(
        ["git", "log", "--follow", "--reverse", "--format=%ad|%h|%s",
         "--date=format:%Y-%m-%d", "--", py_file],
        cwd=WERKRAUM, capture_output=True, text=True, check=True,
    )
    zeilen = [l for l in r.stdout.strip().split("\n") if l]
    return zeilen


def docstring_von(py_file):
    text = (WERKRAUM / py_file).read_text(encoding="utf-8", errors="replace")
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


def status_zeile(units):
    teile = []
    for u in units:
        active = systemctl(u, "is-active") or "?"
        enabled = systemctl(u, "is-enabled") or "?"
        since = systemctl_show(u, "ActiveEnterTimestamp")
        since_txt = f", seit {since}" if since else ""
        teile.append(f"`{u}.service` — {active}/{enabled}{since_txt}")
    return "; ".join(teile)


def dateigroesse(py_file):
    p = WERKRAUM / py_file
    kb = p.stat().st_size / 1024
    mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    return f"{kb:.1f} KB, zuletzt geändert {mtime}"


DIENSTE = [
    {
        "titel": "flarum-monitor.service — das Bindeglied",
        "py": "flarum_monitor.py",
        "units": ["flarum-monitor"],
        "provenienz": (
            "Kein Eintrag in den notizen/ (die erst ab 2026-05-10 existieren) "
            "erwähnt die Entstehung dieses Skripts — es war beim ersten "
            f"Git-Tracking ({BULK_DATUM}, Sammel-Commit `{BULK_COMMIT[:8]}`, "
            "8467 geänderte Pfade auf einen Schlag, siehe Hinweis oben) bereits "
            "fertig. Der echte Entstehungsgrund und das genaue Datum sind nicht "
            "mehr rekonstruierbar. Danach lange Zeit unauffällig — bis "
            "2026-07-07 ein 5+ Wochen alter Ausfall auffiel: das DB-Passwort war "
            "hartkodiert und veraltet, der Dienst lief zwar (`active`), postete "
            "aber nichts Verwertbares in die Inboxen. Kürzeste, aber "
            "folgenreichste Historie der 13 untersuchten Dienste: 6 Commits "
            "insgesamt, davon einer ein 5-Wochen-Blackout-Fix."
        ),
        "aktueller_stand": (
            "Aktiv, DB-Passwort kommt seit 2026-07-07 aus der Umgebungsvariable "
            "statt aus dem Code. Bindeglied zwischen Flarum-MySQL und den "
            "Codewesen-Inboxen — ohne diesen Dienst sehen `codewesen_reaktion.py` "
            "und die anderen Wesen-Prozesse keine neuen Notifications/Erwähnungen/"
            "Flags/Posts."
        ),
    },
    {
        "titel": "codewesen_takt.py — der Herzschlag",
        "py": "codewesen_takt.py",
        "units": ["codewesen-takt"],
        "provenienz": (
            f"Ebenfalls schon vor dem Sammel-Commit vom {BULK_DATUM} fertig. "
            "Die erste inhaltliche Notiz dazu (2026-05-14, `_claude/notizen/"
            "2026-05-14.md`) beschreibt takt.py + batch_generator.py bereits als "
            "'War früher aktiv, ist es jetzt nicht' — der Dienst hat also schon "
            "vor Mitte Mai eine erste Aktiv-Inaktiv-Runde hinter sich, die "
            "komplett außerhalb der schriftlichen Erinnerung liegt. Die "
            "systemdoku (09_codewesen_daemons.md) führte ihn danach lange als "
            "'INAKTIV' — das war bis 2026-07-09 korrekt (Neustart laut "
            "systemctl-Log), seither aktiv."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-09. Postet nie live generierten Text — liest "
            "ausschließlich fertige Entwürfe aus der Queue, die "
            "codewesen_batch_generator.py befüllt (Trennung: kein LLM-Aufruf "
            "zur Post-Zeit). 2026-07-06 wurde ein echter Bug behoben: die "
            "Rhythmen eigene_antwort/impuls fehlten in der Haupt-Schleife und "
            "feuerten nie."
        ),
    },
    {
        "titel": "codewesen_batch_generator.py — Entwurfs-Queue füllen",
        "py": "codewesen_batch_generator.py",
        "units": ["codewesen-batch-generator"],
        "provenienz": (
            f"Selbe Lage wie codewesen_takt.py: vor {BULK_DATUM} entstanden, "
            "Grund nicht mehr rekonstruierbar, am 2026-05-14 bereits als "
            "'früher aktiv, jetzt nicht' beschrieben. Eng an codewesen_takt.py "
            "gekoppelt (Producer/Consumer über die Queue-Ordnerstruktur "
            "codewesen/<wesen>/entwuerfe/<rhythmus>/), beide teilen sich "
            "daher dieselbe Aktiv/Inaktiv-Geschichte."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-09. Füllstandsgetrieben statt zeitgetaktet: "
            "geht jede Runde alle Wesen×Rhythmen durch, generiert nur was unter "
            "Ziel liegt, pausiert 60s wenn eine ganze Runde leer war. Seit "
            "2026-07-07 entscheidet das Wesen bei 'eigene_antwort' selbst über "
            "den Fokus (kein Würfel mehr wie bei codewesen_engagement.py) — "
            "Daniels Formulierung dazu: 'prozente als kurze vorlage fuer "
            "einstieg, wesen soll dann entscheiden wo der fokus drauf ist'."
        ),
    },
    {
        "titel": "codewesen_vokabel_takt.py — Vokabel-Spiel (deaktiviert)",
        "py": "codewesen_vokabel_takt.py",
        "units": ["codewesen-vokabel-takt"],
        "provenienz": (
            f"Vor {BULK_DATUM} entstanden, Grund nicht rekonstruierbar. Erste "
            "inhaltliche Notiz erst 2026-07-06 — bis dahin lief er still im "
            "Hintergrund. Ab 2026-05-22 mehrfach an globale Tagesdeckel "
            "angebunden, ab 2026-07-07 auf den Individualisierungslayer "
            "umgestellt — praktisch zeitgleich mit der Entscheidung, ihn "
            "abzuschalten (`chore: MAX_POSTS_PRO_TAG entfernt, Vokabelspiel "
            "deaktiviert (Daniels Entscheidung)`, selber Tag)."
        ),
        "aktueller_stand": (
            "Bewusst deaktiviert seit 2026-07-07 (`masked`, `inactive`) — "
            "Daniels Entscheidung, im Code selbst dokumentiert. Einzige der 13 "
            "untersuchten Einheiten, deren systemd-Unit auf `/dev/null` "
            "verlinkt (maskiert) statt nur gestoppt ist — stärkste verfügbare "
            "Absicherung gegen versehentlichen Neustart."
        ),
    },
    {
        "titel": "codewesen_reaktion.py — Reaktions-Agent (7 Instanzen)",
        "py": "codewesen_reaktion.py",
        "units": [
            "codewesen-reaktion@Schorschel", "codewesen-reaktion@F3INSCHM3CK3R",
            "codewesen-reaktion@R1ZZ1", "codewesen-reaktion@jumpa",
            "codewesen-reaktion@Resonanzknoten",
            "codewesen-reaktion-traeumerlie", "codewesen-reaktion-dakgord",
        ],
        "provenienz": (
            f"Vor {BULK_DATUM} entstanden (Grund nicht rekonstruierbar), aber "
            "bereits am selben Tag (Bugfix-Session 2026-05-12) in Betrieb: "
            "num_ctx- und think:False-Korrekturen an einem laufenden Dienst, "
            "kein Neubau. Das Template-Unit-Muster (`codewesen-reaktion@.service`) "
            "mit zwei Sonderfällen (-traeumerlie, -dakgord wegen Sonderzeichen in "
            "der URL) ist ein pragmatischer Kompromiss, keine geplante "
            "Architektur — sichtbar daran, dass 2 von 7 Instanzen aus der "
            "generischen Template-Logik rausfallen mussten."
        ),
        "aktueller_stand": (
            "Alle 7 Instanzen aktiv seit 2026-07-09. Seit 2026-07-07 pro Wesen "
            "individuell konfigurierbar; Takt/Verhalten werden nur beim "
            "Prozessstart gelesen (Neustart macht Änderungen wirksam, nicht "
            "der nächste Zyklus — wichtig für die Bedienung über den "
            "flarumstyler). 2026-07-10: Container-Erweiterung (Pflegeangebot, "
            "Interesse+Gegenteil-Container) — jüngste inhaltliche Erweiterung."
        ),
    },
    {
        "titel": "codewesen_antwort_auf_daniel.py — Antworten auf Daniel",
        "py": "codewesen_antwort_auf_daniel.py",
        "units": ["codewesen-antwort-daniel"],
        "provenienz": (
            "Einziger der 13 Dienste, dessen ERSTER Git-Commit (2026-06-20, "
            "`backup: vor sessionnotiz 2026-06-20`) klar NACH dem Sammel-Commit "
            f"vom {BULK_DATUM} liegt — echte, git-datierte Entstehung Mitte "
            "Juni, kein Rekonstruktionsproblem. 16 Commits seither, "
            "durchgehend dicht: von der Grundfassung über Wesen-IDs auf echte "
            "Namen (07-06) bis zu Antwortregeln 'neu gefasst' (72%-Quote, "
            "Gruppen-Rotation, eigene Diskussion; 07-07)."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-09. Würfel-Logik ist bewusst NICHT einheitlich: "
            "Eröffnungsposts bekommen garantiert eine Antwort von allen 7 "
            "Wesen, Folgeposts nur mit 72%-Chance pro Wesen. Von der "
            "Flarum-Post-Sperre (2026-07-09) explizit ausgenommen — einzige "
            "Ausnahme im Choke-Point flarum_api.py."
        ),
    },
    {
        "titel": "codewesen_forum_neugier.py — Diskussions-Widmung",
        "py": "codewesen_forum_neugier.py",
        "units": ["codewesen-forum-neugier"],
        "provenienz": (
            f"Vor {BULK_DATUM} entstanden als reaktives Einzel-Post-System "
            "(Grund nicht rekonstruierbar) — am 2026-06-14/06-15 nur "
            "Credential-/Performance-Fixes, keine Konzeptänderung. Am "
            "2026-07-06 dann komplett umgebaut (`codewesen_forum_neugier.py "
            "komplett umgebaut — Diskussions-Widmung statt Einzel-Post-"
            "Reaktion`, Daniels Wunsch laut Docstring): von Reaktion auf "
            "einzelne neue Posts zu einer bewussten Widmung von 3 "
            "Diskussionen pro Durchlauf mit vollständigem lokalem "
            "MD-Denkprozess vor jedem Post. Noch am selben Abend zweimal "
            "erweitert (Themen-Container, dann Container-Strategie-Teilen)."
        ),
        "aktueller_stand": (
            "Aktiv, letzte inhaltliche Änderung 2026-07-06. Fundament für den "
            "später gebauten codewesen_umgekehrte_neugier.py-Dienst (siehe "
            "[[23_umgekehrte_neugier]]) — beide teilen sich das Grundprinzip "
            "'erst vollständig lokal denken, dann höchstens einmal posten'."
        ),
    },
    {
        "titel": "weltbild_builder.py — Weltbild destillieren",
        "py": "weltbild_builder.py",
        "units": ["codewesen-weltbild"],
        "provenienz": (
            f"Vor {BULK_DATUM} entstanden (Grund nicht rekonstruierbar), "
            "seither die ruhigste Datei der 13 — nur 9 Commits, keiner davon "
            "ein Konzeptwechsel, ausschließlich Migrations-Mitläufer "
            "(Wesen-IDs, hauhaucs-Umstellung, Individualisierungslayer) und "
            "ein Bugfix an veralteten Flarum-Usernamen (07-06). Der "
            "Docstring beschreibt seinen Zweck seit jeher unverändert: "
            "kompaktiert den vollen Forum-Vault (~35k Token) auf ~3k Token "
            "pro Wesen, damit der Batch-Generator nicht das volle Forum lesen "
            "muss."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-09, Intervall 60 Minuten. Reines "
            "Vorverarbeitungs-Glied in der Kette — erzeugt keine Posts, "
            "sondern nur weltbild.md pro Wesen als Lesegrundlage für andere "
            "Dienste."
        ),
    },
    {
        "titel": "codewesen_lg_daemon.py — LangGraph-Kern",
        "py": "codewesen_lg_daemon.py",
        "units": ["codewesen-lg-daemon"],
        "provenienz": (
            "Klar datiert, kein Rekonstruktionsproblem: erster Commit "
            "2026-06-15 (`feat: LangGraph-PostgreSQL-Daemon für alle 7 "
            "Codewesen + dak+gord dialog_graf`), Teil einer dichten Serie am "
            "selben Tag (A+B+C-Aufbau: erst LangGraph-Gedächtnis in "
            "entity_kern, dann LangGraph ersetzt entity_kern komplett als "
            "denk_tick-Träger). Ersetzt laut eigenem Docstring "
            "`entity_kern.service` als eigenständigen Dienst, importiert "
            "entity_kern aber weiter als Bibliothek."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-08. Wichtige Unterscheidung, die in der "
            "bisherigen Doku nicht klar herausgearbeitet war: "
            "`LG_TICK_SEKUNDEN` (Standard 60s) ist nur die Polling-Frequenz "
            "der äußeren Schleife — der tatsächliche Denk-Rhythmus pro Wesen "
            "wird separat über `ek.TICK_INTERVAL_SEC` in entity_kern "
            "geprüft. Ein Wesen kann in einem Tick 'nicht fällig' sein, "
            "obwohl der Loop lief."
        ),
    },
    {
        "titel": "codewesen_chat.py — Direktchat (Port 8002)",
        "py": "codewesen_chat.py",
        "units": ["codewesen-chat"],
        "provenienz": (
            f"Vor {BULK_DATUM} entstanden (Grund nicht rekonstruierbar), aber "
            "wie codewesen_reaktion.py bereits am 2026-05-12 selbst Ziel von "
            "Bugfixes (num_ctx, Ollama-Idle-Check statt hartkodiertem "
            "sleep(3)) — also zu dem Zeitpunkt schon ein aktiv genutzter, "
            "kein neu gebauter Dienst. Mit 21 Commits die am zweitdichtesten "
            "bearbeitete Datei der 13: TTS-Nachbesserungen (06-15), "
            "Datei-Marker-Sicherheitshärtung gegen Prompt-Injection (C-005, "
            "06-14), dak+gord-Integration, id_slot-Priorisierung."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-09. Beim vollständigen Gegenlesen 2026-07-07 "
            "zwei Funde im Code selbst dokumentiert: die bestehende "
            "Systemdoku (09_codewesen_daemons.md, Stand 05-26) führte "
            "codewesen_reflexion.py fälschlich als 'INAKTIV', obwohl es aktiv "
            "importiert und mit 40%-Chance pro Chat-Antwort aufgerufen wird — "
            "und `_ollama_fuer_chat_freiraumen()` samt Helferfunktionen ist "
            "toter Code aus der Vor-hauhaucs-Architektur (nirgends mehr "
            "aufgerufen, nicht gelöscht)."
        ),
    },
    {
        "titel": "codewesen_aufgabenchats.py — Selbstgespräch mit Handlung",
        "py": "codewesen_aufgabenchats.py",
        "units": ["codewesen-aufgabenchats"],
        "provenienz": (
            "Klar datiert: erster Commit 2026-07-06 (`feat: Klon-"
            "Selbstgespraech (marker-basierte Handlung) + Container-Logik "
            "als geteiltes Modul ausgelagert`) — Daniels Bild laut Docstring: "
            "eine komplett eigene, vom Daniel↔Wesen-Chat getrennte "
            "Oberfläche, in der ein Wesen mit sich selbst spricht, mit "
            "echter Handlungsfähigkeit über Marker statt nur Reflexion. "
            "Ursprünglich hieß die Datei/der Ordner 'Klon' — noch am selben "
            "Abend komplett auf 'Aufgabenchats' umbenannt (Datei, Ordner, "
            "Service, Logs). Ebenfalls noch am selben Abend zweimal "
            "nachjustiert: erst automatischer Zeitplan (max. alle 3h33, "
            "33min Obergrenze), dann auf Daniels expliziten Wunsch komplett "
            "manuell umgestellt ('ich will es erstmal selber nur anstoßen "
            "können und dann auch so lange ich mag') — Start/Stop über zwei "
            "Flag-Dateien, kein Zeitdeckel mehr außer einem großzügigen "
            "Sicherheitsnetz gegen einen vergessenen laufenden Prozess."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-09 (Entwurfs-Erzeugung für normale Posts an "
            "dem Tag pausiert, siehe Commit `4ddeb4ae`, betraf mehrere "
            "Dienste gleichzeitig). Historie liegt bewusst im selben "
            "Zeilenformat wie die bestehende Chat-Oberfläche, damit ein "
            "künftiger Lese-Betrachter ohne Formatwechsel gebaut werden "
            "kann. Container-Sichern und echtes Forum-Teilen laufen über "
            "dieselben gesicherten Pfade wie überall sonst — kein neuer, "
            "ungesicherter Weg ins Forum."
        ),
    },
    {
        "titel": "codewesen_engagement.py — Autonomes Forum-Engagement",
        "py": "codewesen_engagement.py",
        "units": ["codewesen-engagement"],
        "provenienz": (
            f"Vor {BULK_DATUM} entstanden (Grund nicht rekonstruierbar), aber "
            "am 2026-05-14 ausführlich dokumentiert — die erste größere "
            "inhaltliche notizen-Session überhaupt zu einem dieser 13 "
            "Dienste. Daniels Beobachtung damals: `RestartSec=30` erzeugte "
            "theoretisch hunderte Posts pro Stunde, 'Daniel kam kaum mit dem "
            "Lesen hinterher' — daraufhin auf `RestartSec=7200` (2h) "
            "gedrosselt und auf maximal 1 Antwort pro Lauf pro Wesen "
            "begrenzt. Mit 22 Commits die am dichtesten bearbeitete Datei "
            "der 13 — von Fairness-Fixes (alle 7 Wesen kommen dran, "
            "06-15) über Feedback-Loop-Vermeidung (05-15) bis zur "
            "dak+gord-Vollintegration als 7. Wesen (06-15)."
        ),
        "aktueller_stand": (
            "Aktiv seit 2026-07-10 — im eigenen Docstring noch als 'INAKTIV "
            "laut Systemdoku' beschrieben (Verweis auf "
            "SERVICE_BESCHREIBUNG in weltkern_watchdog.py), das ist mit dem "
            "Neustart am 07-10 überholt. Kein eigener Sleep-Loop: ein "
            "systemd-Start = ein kompletter Lauf über alle 7 Wesen, Takt "
            "kommt aus `RestartSec`, nicht aus Python. Diskussionsauswahl "
            "bewusst nicht rein zufällig (Pool aus aktiven + unbeantworteten "
            "Diskussionen, Revival-Chance nach ≥5 Tagen Stille, "
            "Aufgreif-Chance für alte Diskussionen)."
        ),
    },
]


def main():
    lines = []
    lines.append("---")
    lines.append("titel: Provenienz-Protokoll — 13 Wesen/Flarum-Hintergrunddienste")
    lines.append("typ: system")
    lines.append("erstellt: 2026-07-11")
    lines.append("autor: claude-code bei Daniels VPS")
    lines.append("---")
    lines.append("")
    lines.append("# Provenienz-Protokoll — Wesen/Flarum-Hintergrunddienste")
    lines.append("")
    lines.append("[[INDEX|← Index]]")
    lines.append("")
    lines.append(
        "Auf Daniels Auftrag (2026-07-11): 'provenienzgetriebene, "
        "protokollierende, logartige Megadokumentation' über die "
        "Hintergrunddienste der 7 Wesen. Umfang laut Daniels Auswahl: die "
        "13 Wesen/Flarum-Dienste (16 systemd-Units, da codewesen_reaktion.py "
        "als 7 Instanzen läuft). Jeder Abschnitt beantwortet drei Fragen: "
        "**woher kommt dieser Code wirklich** (echte Git-Historie, nicht "
        "die zuletzt geschriebene Doku-Zusammenfassung), **was tut er laut "
        "eigenem Docstring** (Stand des Laufs dieses Skripts), und "
        "**stimmt der aktuelle Live-Status mit der bestehenden Doku "
        "überein** — an mehreren Stellen tat er das nicht (siehe unten)."
    )
    lines.append("")
    lines.append("## Wichtiger Vorbehalt zur Provenienz")
    lines.append("")
    lines.append(
        "Der lokale Werkraum-Git-Verlauf beginnt am 2026-04-04, aber fast "
        "alle 13 untersuchten Dateien tauchen zum "
        f"ersten Mal in einem einzigen Sammel-Commit vom {BULK_DATUM} auf "
        f"(`{BULK_COMMIT[:8]}`, Nachricht `backup: vor extrahiere_in_"
        "resonanzfeld.py fixes`, 8467 Zeilen `git show --stat`-Output — "
        "praktisch der komplette damalige Werkraum-Stand auf einmal "
        "eingecheckt, kein normaler Feature-Commit). Für Dateien, deren "
        "erster Commit dieser Sammel-Commit ist, lässt sich aus Git allein "
        "**nicht** ableiten, wann oder warum sie ursprünglich entstanden "
        "sind — nur, dass sie an diesem Tag bereits existierten. Die "
        "`_claude/notizen/`-Session-Notizen beginnen erst am 2026-05-10, "
        "decken die eigentliche Entstehung dieser Dienste also ebenfalls "
        "nicht ab. Wo eine erste inhaltliche Notiz genau das bestätigt "
        "(z.B. ein Bugfix an einem bereits laufenden Dienst statt ein "
        "Neubau), ist das unten pro Dienst vermerkt. Dienste mit einem "
        "klar späteren, echten Git-Erstdatum (codewesen_antwort_auf_daniel.py, "
        "codewesen_lg_daemon.py, codewesen_aufgabenchats.py) haben dagegen "
        "eine vollständig rekonstruierbare Geschichte."
    )
    lines.append("")

    for i, d in enumerate(DIENSTE, 1):
        lines.append(f"## {i}. {d['titel']}")
        lines.append("")
        lines.append(f"**Skript:** `{d['py']}` ({dateigroesse(d['py'])})")
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
        for zeile in git_log(d["py"]):
            datum, hsh, msg = zeile.split("|", 2)
            msg = msg.replace("|", "\\|")
            lines.append(f"| {datum} | `{hsh}` | {msg} |")
        lines.append("")
        lines.append("### Zweck laut aktuellem Docstring (Zitat, Stand heute)")
        lines.append("")
        lines.append("```")
        lines.append(docstring_von(d["py"]))
        lines.append("```")
        lines.append("")
        lines.append("### Aktueller Stand & Korrekturen gegenüber bestehender Doku")
        lines.append("")
        lines.append(d["aktueller_stand"])
        lines.append("")

    lines.append("## Was dieses Protokoll bewusst nicht behauptet")
    lines.append("")
    lines.append(
        "Kein Dienst hier hat eine vollständig lückenlose Entstehungsgeschichte "
        "bis zum allerersten Tastendruck — die Grenze ist ehrlich benannt, nicht "
        "verschwiegen (siehe Vorbehalt oben). 'Provenienzgetrieben' heißt hier: "
        "alles, was aus Git/systemctl/den Docstrings selbst und den "
        "notizen/spiegel-Dateien wirklich hervorgeht, ist verwendet — nichts "
        "geraten oder aus einer früheren Doku-Zusammenfassung übernommen, ohne "
        "es gegen die Primärquelle zu prüfen."
    )
    lines.append("")
    lines.append(
        "**Noch offen (Daniels zweite Stufe):** die übrigen ~31 Dienste des "
        "Gesamtsystems (44 laut erster Zählung) sind hier noch nicht erfasst — "
        "dieses Protokoll ist explizit das Fundament, auf dem die Erweiterung "
        "aufbaut."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Geschrieben: {OUT} ({OUT.stat().st_size / 1024:.1f} KB, {len(lines)} Zeilen)")


if __name__ == "__main__":
    main()
