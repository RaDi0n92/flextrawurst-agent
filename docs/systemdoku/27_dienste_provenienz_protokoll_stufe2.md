---
titel: Provenienz-Protokoll Stufe 2 — restliche Systemdienste
typ: system
erstellt: 2026-07-11
autor: claude-code bei Daniels VPS
---

# Provenienz-Protokoll Stufe 2 — restliche Systemdienste

[[INDEX|← Index]] · [[24_dienste_provenienz_protokoll|← Stufe 1]]

Fortsetzung von [[24_dienste_provenienz_protokoll]] (Stufe 1: die 13 Wesen/Flarum-Dienste). Diese Stufe deckt die übrigen Dienste ab: codewesen_agent.py (7 Instanzen — der eigentliche Wesen-Prozess, nicht in Stufe 1 erfasst), die Welt-Kern-Dienste (welt/), GENI, dak+gord-system, innenleben, KompOase, Obsidian-Bridge, Claude Live Viewer und die Resonanzfeld-Build-/Grundriss-Sync-Skriptfamilien. Nicht erneut aufgeführt: die 13 Stufe-1-Dienste und codewesen_umgekehrte_neugier.py (eigene Datei, [[23_umgekehrte_neugier]]).

## Wichtiger Vorbehalt zur Provenienz — zwei Repos, zwei Brüche

Wie in Stufe 1 beschrieben, beginnt die rekonstruierbare Historie der meisten Werkraum-Dateien praktisch erst mit dem Sammel-Commit vom 2026-05-12 (`116ec29f`). Zwei Dateien dieser Stufe (kompoase/server.py, .claude/claude_live.py) liegen jedoch NICHT im Werkraum-Repo, sondern im Repo unter /root selbst — dort gibt es einen eigenen, unabhängigen Bruch: am 2026-06-12 wurde dieses Repo bewusst neu aufgesetzt (`17534329`, 'fresh start: sauberer Index ohne 10.7M geni_gedaechtnis-Einträge' — ein 10,7-Millionen-Zeilen-Datenbestand hatte den Git-Index unbrauchbar gemacht). Für beide betroffenen Dateien gilt: keine Historie vor 2026-06-12 rekonstruierbar, unabhängig vom Werkraum-Problem. Eine echte Ausnahme von beiden Brüchen ist agent/dak_gord_system/graph/run_background_cycle.py: deren einziger Commit ist der allererste Commit im gesamten Werkraum-Repo überhaupt (2026-04-04, `7be5012c`) — älter als der Sammel-Commit, vollständig git-datiert, aber seit dem ersten Tag nie wieder verändert.

## 1. codewesen_agent.py — der eigentliche Wesen-Prozess (7 Instanzen, neuer Fund)

**Skript:** `codewesen_agent.py` (58.8 KB, zuletzt geändert 2026-07-09 06:46)

**Status (live, 2026-07-11):** `codewesen-Schorschel.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST; `codewesen-F3INSCHM3CK3R.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST; `codewesen-R1ZZ1.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST; `codewesen-jumpa.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST; `codewesen-Resonanzknoten.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST; `codewesen-traeumerlie.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST; `codewesen-dakgordsystem.service` — active/enabled, seit Thu 2026-07-09 06:48:58 CEST

### Provenienz

Nicht in Stufe 1 erfasst — eigener Fund bei der Recherche zu Stufe 2: sieben eigenständige `codewesen-<Name>.service`-Units (ein Prozess PRO Wesen), klar zu unterscheiden von den gleichnamigen `codewesen-reaktion@<Name>.service`-Units aus Stufe 1 — zwei verschiedene Skripte, zwei verschiedene Units pro Wesen. Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar, gleiche Lage wie die meisten Stufe-1-Dienste), aber mit 31 Commits die mit Abstand am dichtesten bearbeitete Datei dieser Stufe: agent-trigger-Schleife (05-15), Selbstgespräch-Erweiterung (05-16), Antwortpflicht-Bypass für Daniels Posts (05-22), dak+gord-Integration als 7. Wesen (06-15), num_ctx=8192-Fix gegen Ollama-Reload (06-14), hauhaucs-Migration (06-20/06-21), Wesen-IDs auf echte Namen (07-06), Postgres-LLM-Scheduler ersetzt slot_0.lock (07-07), Docstring auf echte Code-Tiefe gebracht + 3 echte Bugs gefunden (07-07, `feb0eedd`).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-15 | `d41d0ee4` | fix: agent-trigger-schleife einbauen + /api/chat umstellen |
| 2026-05-15 | `7f1b6e8c` | fix: GEDANKEN_TAG_ID = 36 definieren (Gedankenpost-NameError) |
| 2026-05-16 | `930ba854` | fix: dialog-wiederherstellung + ghost-disk-skip in Antwortpflicht |
| 2026-05-16 | `609ce8fd` | feat: selbstgespraech — gedankenpost fuehrt eigene threads weiter (60% chance) |
| 2026-05-21 | `17e56182` | forum-dialog: gedankenpost 30/40/30-pfad, pflichtpost-antwortbias, engagement 1800-5400s / MAX_PRO_LAUF=5 |
| 2026-05-22 | `7126a90b` | backup: vor spiegel flarum-forum-vollanalyse |
| 2026-05-22 | `9b179221` | fix: antwortpflicht bypass_cooldown — daniels posts antworten sofort |
| 2026-05-22 | `a86e48c8` | fix: inbox in haupt-loop eingehängt + bypass_cooldown für daniels posts |
| 2026-05-31 | `6fe06ad6` | backup: vor WESEN-EINSICHTSKÖRPER + ENTSCHEIDUNGSARCHIV + LEBENSTICKER |
| 2026-06-14 | `71238c5b` | fix: codewesen_agent num_ctx=8192 — verhindert Ollama-Modell-Reload bei dak-gord-Chat |
| 2026-06-15 | `4c6c319d` | feat: dak+gord-system als 7. Wesen vollständig integriert (Flarum + DB + Scripts + Services + Surface) |
| 2026-06-15 | `25ce1471` | fix: Flarum-Posting-Fairness — alle 7 Wesen kommen dran |
| 2026-06-15 | `79867c2f` | fix: dak+gord-system Erstvorstellung auf Flarum gepostet (Discussion #2277) |
| 2026-06-20 | `5896ef5b` | backup: vor sessionnotiz 2026-06-20 |
| 2026-06-20 | `e8119590` | dolphin Q8 für alle Wesen-Services: gemma4 komplett ersetzt |
| 2026-06-20 | `4b6f9ac3` | dolphin parameter-tuning: repeat_penalty+top_p+top_k überall, temperaturen stabilisiert |
| 2026-06-21 | `40b5e009` | backup: vor codewesen_chat blocker-fix (namelessAI-services fehlten in blockliste) |
| 2026-07-06 | `c8f4b4ce` | feat: hauhaucs-q6/llama-server Migration (gemma4 komplett entfernt) |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |
| 2026-07-07 | `9d2b7d81` | fix: JSON-Extraktion prueft jetzt ob wirklich ein dict rauskam (Ursache fuer 'str' object has no attribute get bei dak+gord-Reflexion) |
| 2026-07-07 | `811df731` | feat: codewesen_agent.py individualisierbar — pro Wesen eigene Konfiguration |
| 2026-07-07 | `72fdffa0` | feat: neuer Postgres-gestuetzter LLM-Scheduler ersetzt slot_0.lock-Semaphor |
| 2026-07-07 | `c197c8cb` | fix: filter flarum vokabel threads from reactions |
| 2026-07-07 | `0735e9b9` | fix: treat dakgord as codewesen |
| 2026-07-07 | `b2d318e9` | fix: retry empty codewesen llm responses |
| 2026-07-07 | `d8a2567b` | fix: release stale llm holders and fallback dakgord replies |
| 2026-07-07 | `feb0eedd` | docs: Docstrings auf echte Code-Tiefe gebracht (7 Skripte) + 3 echte Bugs gefunden |
| 2026-07-07 | `759bd7f4` | feat: Antwortregeln auf Daniel neu gefasst (72%, Gruppen-Rotation, eigene Diskussion) |
| 2026-07-07 | `2544b31e` | docs: 4 grosse Dateien jetzt WIRKLICH komplett gelesen, 2 weitere Bugs gefunden |
| 2026-07-09 | `4ddeb4ae` | feat: umgedrehter Neugier-Dienst gestartet, Entwurfs-Erzeugung fuer Posts pausiert |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Codewesen-Agent — vollständiger Agentic Loop, ein Prozess PRO Wesen (7 Instanzen:
die 6 namelessAI + dak+gord-system). Takt/Verhalten (meta.intervalle: check_reflexion,
check_scan, gedanke, pflichtpost, impuls) werden NUR EINMAL beim Prozessstart
gelesen — ein Neustart macht Aenderungen wirksam, nicht "ab dem naechsten Zyklus".

Aufruf: python3 codewesen_agent.py <codewesen_name>

Ein Loop, `time.sleep(15)` am Ende jeder Runde. Reale Trigger, mit den
tatsaechlichen Standard-Intervallen (per Zeilennummer im Code geprueft,
2026-07-07 — vorherige Docstring-Version hatte hier falsche Werte):

  1. Obsidian-Navigation — alle CHECK_SCAN (Standard 7200s = 2 STUNDEN,
     nicht 8 Minuten wie eine aeltere Version dieser Doku behauptete).
  2. Selbstreflexion — alle CHECK_REFLEXION (Standard 28800s = 8 STUNDEN,
     nicht 300s wie eine aeltere Version dieser Doku behauptete).
  3. Inbox (Daniels eigene Posts, mit Cooldown-Bypass) — JEDE Runde (~15s).
  4. Antwortpflicht — JEDE Runde (~15s): prueft ob ein Post im Forum
     >33 Minuten ohne Codewesen-Antwort ist (bestaetigt akkurat).
  5. Gedankenpost — alle gedanke_intervall (Standard 66min), gestaffelt
     8min pro Wesen-Index.
  6. Pflichtpost — alle pflichtpost_intervall (Standard 88min).
  7. Forum-Impuls — alle impuls_intervall (Standard 2h22).

Gefundener toter Code (definiert, aber nirgends aufgerufen), zwei Funktionen —
komplett gegengelesen 2026-07-07:
  - verarbeite_feed() — eine fruehere Docstring-Version beschrieb sie als
    aktiven Trigger "Globaler Feed, alle 120s". Nicht im Loop verdrahtet.
  - verarbeite_vorstellung_4h44() — ein vollstaendig fertiger 9. Trigger
    (4h44-Selbstgespraech im eigenen VORSTELLUNGS_THREADS-Thread, analog zu
    codewesen_takt.py's "vorstellung"-Rhythmus), aber ebenfalls nicht im
    Haupt-Loop aufgerufen. Vermutlich kein Bug, sondern Aufgabenteilung:
    erstvorstellung_erstellen() (einmalig beim allerersten Start, siehe main())
    legt den Thread an, laufende Vorstellungs-Posts kommen stattdessen ueber
    codewesen_takt.py + codewesen_batch_generator.py — diese Funktion hier
    ist damit vermutlich ein Ueberbleibsel aus einer frueheren Architektur-
    Version, bevor die Vorstellung dorthin verschoben wurde.

Fuer alle aktiven Trigger laeuft derselbe Agentic Loop:
  Kontext → LLM → Tool-Aufruf → Ergebnis → LLM → ... → finale Aktion
  Max. 6 Iterationen pro Trigger.

Weitere Details, komplett gegengelesen: verarbeite_pflichtpost_88min() erzwingt
einen zweiten LLM-Versuch, wenn der erste "nichts" waehlen wollte ("Das gilt
nicht"). verarbeite_forum_impuls() wuerfelt PRO Aufruf 50/50 zwischen
Forum-Kritik und oeffentlicher Selbstreflexion (kein alternierender Zustand
wie bei codewesen_batch_generator.py's impuls_modus). verarbeite_gedankenpost()
wuerfelt 30% eigenen offenen Thread weiterfuehren / 55% auf fremden
Gedanken-Thread antworten / 15% neuen Gedanken eroeffnen.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Alle 7 Instanzen aktiv. Zentraler Satz aus dem eigenen Docstring: Takt/Verhalten (`meta.intervalle`) werden NUR EINMAL beim Prozessstart gelesen — ein Neustart macht Konfigurationsänderungen wirksam, nicht der nächste Zyklus. Das ist derselbe Mechanismus wie bei codewesen_reaktion.py (Stufe 1) und erklärt, warum der flarumstyler nach Config-Änderungen einen expliziten Neustart-Knopf braucht statt live nachzuziehen. Jüngste Änderung (07-09): umgedrehter Neugier-Dienst gestartet, Entwurfs-Erzeugung für normale Posts pausiert — betraf diesen Prozess mit.

## 2. welt/cyberling_daemon.py — Bedürfnisse, Tod, Wiedergeburt

**Skript:** `welt/cyberling_daemon.py` (12.7 KB, zuletzt geändert 2026-06-14 06:11)

**Status (live, 2026-07-11):** `cyberling-daemon.service` — active/enabled, seit Wed 2026-07-08 06:51:07 CEST

### Provenienz

Klar datiert, kein Rekonstruktionsproblem: erster Commit 2026-05-23 (`cyberling: daemon mit kaskaden-verfall, tod nach 24h wiedergeburt, rekord-tracking`) — echter Neubau, nicht vor dem Sammel-Commit versteckt. Noch am selben Tag kalibriert (Verfallsraten + Pflege-Endpunkte füttern/trinken/spielen/streicheln). Am 2026-05-31 Teil des großen EINSICHT-VI-Commits (Gruppen-System, Substanzen, Cyberling-Recovery). Am 2026-06-14 von der breiten Security-Remediation erfasst: DB-URI aus 28 Dateien in Umgebungsvariable ausgelagert.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-23 | `2463adb8` | cyberling: daemon mit kaskaden-verfall, tod nach 24h wiedergeburt, rekord-tracking |
| 2026-05-23 | `3826a327` | cyberling: verfallsraten kalibriert + pflege-endpoints (füttern/trinken/spielen/streicheln) |
| 2026-05-31 | `dc1f26ff` | feat: EINSICHT VI — Gruppen-System, Substanzen, Cyberling-Recovery, Surface-Fixes |
| 2026-06-01 | `8dcb2939` | backup: vor schatten-antwort-chain (parent_id) |
| 2026-06-01 | `c2025852` | fix: Cyberling-Daemon letzter_tick DB-persistent |
| 2026-06-14 | `8c81f6e8` | security: DB-URI aus 28 Dateien in Env (FLEXTRAWURST_DB_URI), Gateway-Auth fail-closed+timing-safe (C-001), Galerie Path-Traversal-Schutz (C-004), .env.example Platzhalter |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Cyberling-Daemon: Verwaltet Bedürfnisse, Tod und Wiedergeburt aller Cyberlinge.

Kaskade:
  Durst    → fällt schnell (pausiert während Entität schläft)
  Hunger   → fällt langsamer
  ↓ (beide niedrig)
  Energie  → sinkt (normal + kaskade)
  Stimmung → sinkt parallel
  ↓ (immer noch unbehandelt)
  Gesundheit → schwindet → Tod → nach 24h Wiedergeburt

Profile: leicht / mittel / hart — pro Cyberling in DB konfigurierbar.
Zustände: gesund → hungrig/durstig → müde → erschöpft → krank → kritisch → tot
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Kaskaden-Logik laut Docstring: Durst fällt schnell (pausiert während die Entität schläft), Hunger langsamer, danach sinken Energie und Stimmung, unbehandelt schwindet die Gesundheit bis zum Tod, nach 24h folgt Wiedergeburt. Drei Schwierigkeitsprofile (leicht/mittel/hart) pro Cyberling in der DB konfigurierbar — kein globaler Schalter.

## 3. welt/splitter_daemon.py — Splitter-Physik, 60s-Takt

**Skript:** `welt/splitter_daemon.py` (12.4 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `splitter-physik.service` — active/enabled, seit Wed 2026-07-08 06:51:07 CEST

### Provenienz

Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar), danach mit nur 5 Commits eine der ruhigsten Dateien dieser Stufe: Umbenennung Datenstruktur-Resonanzdatei (05-13), vier Spiegel aus 'Meine Textsammlung' (06-13), DB-URI-Absicherung (06-14, Teil derselben Security-Remediation wie cyberling_daemon.py), Wesen-IDs auf echte Namen (07-06).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-13 | `c8677de8` | backup: vor umbenennung datenstruktur-resonanzdatei |
| 2026-06-13 | `3c9ef279` | backup: vor vier neuen spiegeln aus Meine-Textsammlung |
| 2026-06-14 | `8c81f6e8` | security: DB-URI aus 28 Dateien in Env (FLEXTRAWURST_DB_URI), Gateway-Auth fail-closed+timing-safe (C-001), Galerie Path-Traversal-Schutz (C-004), .env.example Platzhalter |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Splitter-Physik Daemon — alle 60 Sekunden drei Ticks.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Docstring ist ein einziger Satz ('alle 60 Sekunden drei Ticks') — knappste Selbstbeschreibung aller bisher untersuchten 32 Dienste (Stufe 1 + 2). Läuft im selben Arbeitsverzeichnis wie welt/api.py, welt/bruecke.py und welt/weltkern_watchdog.py (`WorkingDirectory=/root/werkraum/welt`) und über das gemeinsame `/root/werkraum/venv` statt des System-Python — anders als fast alle Wesen-Skripte, die `/usr/bin/python3` nutzen.

## 4. welt/api.py — Welt-API, FastAPI auf Port 8030

**Skript:** `welt/api.py` (509.1 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `welt-api.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST

### Provenienz

Einzige Datei der gesamten bisherigen Provenienz-Recherche (Stufe 1 + 2), deren allererster Commit klar VOR dem Sammel-Commit datiert ist und trotzdem git-datiert rekonstruierbar bleibt: 2026-05-12 (`f27c9833`, `/suche`-Endpunkt), am selben Tag wie der Sammel-Commit selbst (`116ec29f`) aber davor in der Commit-Reihenfolge — die Welt-API existierte demnach bereits, bevor der große Rundum-Checkpoint kam. Mit 68 Commits die mit Abstand meistbearbeitete Datei der gesamten Provenienz-Recherche (Stufe 1: höchster Wert war 22 bei codewesen_engagement.py) — durchgehend additiv: neue Endpunkte (Widmungen, Bild-Proxy, Schlaf-Archiv, mw_*-Sichtbarkeit), kein einziger großer Rewrite sichtbar in den Commit-Messages.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `f27c9833` | feat: /suche Endpunkt + search-Param für Splitter |
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-13 | `c8677de8` | backup: vor umbenennung datenstruktur-resonanzdatei |
| 2026-05-13 | `e5980b59` | api: splitter.aufnehmen endpoint + aufnahmen in SELECT |
| 2026-05-23 | `ad0a1b4e` | schlaf-system: schema + API + entity_takt daemon (theater_01 als Testwesen) |
| 2026-05-23 | `1967029e` | schlaf: Zustandsaufnahme beim Einschlafen — stimmung, resonanz, konflikte, substanz, offene splitter |
| 2026-05-23 | `3826a327` | cyberling: verfallsraten kalibriert + pflege-endpoints (füttern/trinken/spielen/streicheln) |
| 2026-05-23 | `8fb837ba` | einzug: Admin-Endpoint + Cyberling-Erstellung bei Einzug (namenslos, wartet auf Taufe) |
| 2026-05-23 | `9537700c` | api: schlaf/heute + cyberling GET ohne Auth — für Surface-Lesezugriff |
| 2026-05-23 | `bcb4cc7d` | api: CORS Middleware + Cyberlinge für alle 6 namelessAI angelegt |
| 2026-05-23 | `234dacf4` | backup: vor tarotlesungen-spiegel |
| 2026-05-23 | `5a9b2a95` | backup: vor spiegel zu fuenf chatgpt-selbstbildern |
| 2026-05-31 | `9fc021dd` | feat: WELTKERN-REANIMATION + Flarum-Abtrennung + Einzugsvorbereitung |
| 2026-05-31 | `5213d9b7` | feat: EINSICHT-Tab — Entscheidungsarchiv, Denkfenster, Traumarchiv, Lebensjournal, Substanzen, Liveticker, Einzugsampel |
| 2026-05-31 | `b430cf8b` | feat: Archäologie-Suche API + Handlungsgrammatiken vollständig (AF2+AF5) |
| 2026-05-31 | `8c8022dc` | feat: AF6 KompOase — splitter_aufnahmen API (4 Endpunkte), DB-Migration |
| 2026-05-31 | `abc9b464` | feat: AF9+AF12+Surface — Schatten-Dialog API, Einzugsampel v2, SPLITTER+SCHATTEN Subtabs |
| 2026-05-31 | `06243e53` | feat: VOR-EINZUGSREIFEKÖRPER — Sicherheit, Menschquellen, Simulation, Grammatiken, Surface |
| 2026-05-31 | `a11b0ab1` | feat: EINSICHT IV TEIL 0–3 — Service-Kanonisierung, Tests, Innenquellen-Tab |
| 2026-05-31 | `c3ec3ca0` | feat: EINSICHT IV TEIL 4–8 — Vorstudie, Beziehungen, Sim2, HG, Ampel v4 |
| 2026-05-31 | `acdaf4a1` | feat: EINSICHT V — Vor-Einzugs-Freeze, Entscheidungsboard, Ampel v5 |
| 2026-05-31 | `dc1f26ff` | feat: EINSICHT VI — Gruppen-System, Substanzen, Cyberling-Recovery, Surface-Fixes |
| 2026-05-31 | `1705e70e` | feat: EINSICHT-VI-Fixblock — HG12/12, Ampel-v4-Surface, Kalender-Transform, Splitter-Story, Substanz-UI, Systemstatus-Fixes |
| 2026-05-31 | `a2535580` | fix: Splitter-Story-View — aufgenommen_at + events payload-query + timestamp-serialize |
| 2026-05-31 | `3e58cffc` | feat: entity_kern Guardrail (nur eingezogen), Feed Von-Wesen/Von-Menschen, Gedanken-Archiv MEINE WELT, EINSICHT/SUCHE-Fix, Kalender-Alle-Liste |
| 2026-05-31 | `bf6840a8` | fix: EINSICHT-API-Prefix, Feed-Revert, Gruppen-View, Innenquellen-Delete, Ampel, Liveticker, Substanzen |
| 2026-05-31 | `7ce95524` | backup: vor codex-startbrief |
| 2026-05-31 | `2a55c7c8` | kimi: spiegel ueber KIMI.md — selbstreflexion der eigenen anleitung |
| 2026-05-31 | `a0b89831` | backup: resonanzfeld-sync vor wissen-spiegel |
| 2026-05-31 | `e7b008d9` | spiegel: wissen/ gesamtspiegel nach Lektüre von 11 Kern-Dateien |
| 2026-05-31 | `6f9f416e` | regel: token-disziplin - keine parallelen operationen, keine subagents |
| 2026-06-01 | `aa92aa6c` | feat: wesen-erfahrungsmaschine — life-contracts, organ-hunger, neue API-endpunkte |
| 2026-06-01 | `8dcb2939` | backup: vor schatten-antwort-chain (parent_id) |
| 2026-06-01 | `043da7dd` | feat: schatten-antwort-chain mit parent_id/thread_id + baumstruktur |
| 2026-06-01 | `bf1470c1` | feat: splitter aufnahme authentifiziert mit splitter_aufnahmen + begruendung |
| 2026-06-01 | `9fed403a` | feat: zitate als weltobjekt mit 5-level-rechten (privat, intern, community, oeffentlich, gemeinfrei) |
| 2026-06-01 | `12c667a5` | feat: archäologie-suche erweitert um events, gedankenblasen, schatten, zitate + facets |
| 2026-06-01 | `e9282970` | feat: /api/raeume und /api/posts als konsistente api-endpunkte |
| 2026-06-01 | `4fd956a2` | fix: Archäologie-Suche Spaltenkorrekturen + Phase 6 API-Aliasse |
| 2026-06-01 | `130e1aff` | fix: Archäologie entity_id-Filter für Gedankenblasen korrigiert |
| 2026-06-01 | `e4be2695` | feat: Cyberlinge-View in Surface + API-Endpunkt |
| 2026-06-01 | `984aa20f` | feat: Splitter-, Zitate-, Schatten-Views in Surface + JS + CSS |
| 2026-06-01 | `fbf0867b` | thread: nested Diskurs-Bäume — Backend parent_id + Frontend Tree-Renderer |
| 2026-06-01 | `752592e2` | feat: meine-welt feed — 6 kategorien, 10s refresh, filter-chips, irrelevant-markierung |
| 2026-06-01 | `83743e05` | feat: formatting-toolbar, ICS-import/export, Phase-4-polish — scrollbar, scroll-memory, prefers-reduced-motion, touch-targets |
| 2026-06-01 | `00db633d` | fix: feed-spalten (content statt inhalt), chat-401-tuple, syntax-warnings, feed-timer-leak |
| 2026-06-02 | `d5d4e5e1` | backup: denkstream-infrastruktur — SSE-endpoint + live-chunks + migration |
| 2026-06-02 | `50bcdb12` | backup: P6 wesen-baurechte — raeume+themen via entity-role + provenienz in meta |
| 2026-06-02 | `5c1bc42f` | backup: P6 provenienz — /api/provenienz endpoint + raeum-tab anzeige |
| 2026-06-02 | `114dd1c5` | backup: P6 wunsch-system — endpoint + browser-aktion + body-import fix |
| 2026-06-03 | `6b8f47a8` | fix: search/global q optional + Schatten nicht mehr admin-only |
| 2026-06-13 | `3c9ef279` | backup: vor vier neuen spiegeln aus Meine-Textsammlung |
| 2026-06-13 | `a3604341` | backup: vor spiegel zu chatgpt-bildertour |
| 2026-06-14 | `26187a96` | feat: gedankenblasen/feld gibt created_at + profil_farbe zurück |
| 2026-06-14 | `8c81f6e8` | security: DB-URI aus 28 Dateien in Env (FLEXTRAWURST_DB_URI), Gateway-Auth fail-closed+timing-safe (C-001), Galerie Path-Traversal-Schutz (C-004), .env.example Platzhalter |
| 2026-06-14 | `5b9ec561` | security: welt-api härten — CORS auf bekannte Origins (statt *), admin nur per JWT (C-007), Schatten-Dialoge: Identität/Inhalt nicht öffentlich (C-008) + Reply-Autor serverseitig statt Body (C-009), Denkstream-Chunk fail-closed Token-Auth + Längenlimits (C-011) |
| 2026-06-14 | `014cb21a` | security: codewesen_chat Datei-Marker (##LESEN/SCHREIBEN##) auf Werkraum begrenzt + Secret-Pfade blockiert (C-005) — verhindert Root-Dateizugriff via Prompt-Injection |
| 2026-06-14 | `b331d403` | security: welt-api Body-Größenlimit-Middleware (6MB) + Längenlimits auf Schatten-Content-Felder (C-019) |
| 2026-06-14 | `c842107f` | feat: mw_* per-item Sichtbarkeit — sichtbarkeit-Feld in PATCH + GET, welt_spuren im Profil-Endpoint, Filter entfernt (alle User sichtbar) |
| 2026-06-14 | `b82def1d` | fix: GET /me gibt profil_meta zurück (Motto/Farben im Edit-Formular) |
| 2026-06-14 | `1741709a` | feat: Widmungen-API (POST/GET/admin approve/reject + events) |
| 2026-06-14 | `92d9be98` | feat: /bild-proxy Endpunkt + URL-safe-Encoding für Leerzeichen |
| 2026-06-14 | `9178da8f` | backup: vor upload-sammellogik im datei-wandler |
| 2026-06-15 | `f1fd1431` | backup: vor Verfassungs-Fix (dak+gord Verhalten: Bracket-Spam + Ausweichen) |
| 2026-06-15 | `4c6c319d` | feat: dak+gord-system als 7. Wesen vollständig integriert (Flarum + DB + Scripts + Services + Surface) |
| 2026-06-15 | `0d7dcda4` | feat(api): GET /wesen/{id}/schlaf/archiv — historische Schlafphasen-Abfrage |
| 2026-06-20 | `e8119590` | dolphin Q8 für alle Wesen-Services: gemma4 komplett ersetzt |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Welt-API: FastAPI auf Port 8030.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Zentraler Knotenpunkt: praktisch jeder andere hier dokumentierte Welt-Dienst (Cyberling, Splitter, Brücke, Watchdog) und die Surface (Port 8787) sprechen mit dieser einen API. Grundgesetz 2 der Systemdoku (Suchbarkeit/Paginierung für jeden öffentlichen GET-Endpunkt) betrifft in erster Linie diese Datei.

## 5. welt/bruecke.py — Selbstmodelle nach PostgreSQL

**Skript:** `welt/bruecke.py` (6.7 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `welt-bruecke.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST

### Provenienz

Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar), danach nur 3 Commits — die knappste Historie dieser Stufe neben obsidian_api.py: Wesen-IDs auf echte Namen (07-06) und dieselbe DB-URI-Security-Härtung wie cyberling_daemon.py und splitter_daemon.py (06-14).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-06-14 | `8c81f6e8` | security: DB-URI aus 28 Dateien in Env (FLEXTRAWURST_DB_URI), Gateway-Auth fail-closed+timing-safe (C-001), Galerie Path-Traversal-Schutz (C-004), .env.example Platzhalter |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Brücke: liest Selbstmodell-JSONs und synchronisiert mit PostgreSQL.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Laut Docstring ein reiner Lese-Synchronisierer: liest Selbstmodell-JSONs (die Dateien, in denen jedes Wesen sein Selbstbild führt) und spiegelt sie nach PostgreSQL — keine eigene Entscheidungslogik, keine LLM-Aufrufe. Name 'Brücke' ist wörtlich gemeint: Dateisystem auf der einen, DB auf der anderen Seite.

## 6. welt/weltkern_watchdog.py — prüft die Kerndienste

**Skript:** `welt/weltkern_watchdog.py` (59.4 KB, zuletzt geändert 2026-07-10 20:18)

**Status (live, 2026-07-11):** `weltkern-watchdog.service` — inactive/static; `weltkern-watchdog.timer` — active/enabled, zuletzt ausgelöst: Sat 2026-07-11 05:21:16 CEST

### Provenienz

Klar datiert: erster Commit 2026-05-31 (`feat: WELTKERN-REANIMATION + Flarum-Abtrennung + Einzugsvorbereitung`) — echter Neubau, kein Rekonstruktionsproblem. Mit 33 Commits die zweitmeistbearbeitete Datei dieser Stufe nach welt/api.py, und die mit Abstand aktuellste: allein am 2026-07-07 sechs Commits (Fehler-Quittierung, System-Ressourcen-Anzeige Swap/RAM/Load/oomd, Wesen-eigene Dienste im flarumstyler sichtbar, Docstring in UI), am 2026-07-10 vier weitere (u.a. `wesen_filter` (Radio) durch `wesen_aktiv` (unabhängige Mehrfach-Toggles) ersetzt — exakt der Umbau, der im vorherigen Gesprächsabschnitt dieser Session gerade lief, als der Verbindungsabbruch passierte).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-31 | `9fc021dd` | feat: WELTKERN-REANIMATION + Flarum-Abtrennung + Einzugsvorbereitung |
| 2026-06-14 | `8c81f6e8` | security: DB-URI aus 28 Dateien in Env (FLEXTRAWURST_DB_URI), Gateway-Auth fail-closed+timing-safe (C-001), Galerie Path-Traversal-Schutz (C-004), .env.example Platzhalter |
| 2026-07-07 | `ee27902d` | fix: weltkern_watchdog.py veraltete Flarum-Vorphase-Guardrail geleert + Dienstname flextrawurst-surface auf process-camera-preview korrigiert |
| 2026-07-07 | `bd3d5da9` | feat: flarumstyler Teil 1 - weltkern_watchdog.py um Codewesen-Dienste + dauerhafte Log-Fehler-Uebersicht mit Erklaerungen erweitert |
| 2026-07-07 | `6202ee6f` | feat: flarumstyler Teil 2 - erwartet_aus-Status, Beispielzeilen pro Fehlermuster, Verlaufs-Historie |
| 2026-07-07 | `d5b5c26d` | feat: flarumstyler - alle 31 Dienste mit Klartext-Beschreibung (was macht der Dienst) |
| 2026-07-07 | `3093db6d` | feat: flarumstyler - steuerbar-Flag pro Dienst (4 Kern-Dienste gesperrt fuer Aktionen) |
| 2026-07-07 | `b47a47aa` | feat: flarumstyler - Dienst-Details (seit wann, Neustarts, RAM, Log-Zeilen), Gruppierung Flarum/Welt, echte llama-server-Instanzen mit Live-Status |
| 2026-07-07 | `ab9e828e` | backup: vor Individualisierungs-Konfigurationslayer (dienst_konfiguration) |
| 2026-07-07 | `1dc7695a` | feat: Individualisierungs-Konfigurationslayer (dienst_konfiguration) — Proof-of-Concept |
| 2026-07-07 | `745f2a61` | feat: 4 weitere Dienste auf Individualisierungslayer umgestellt |
| 2026-07-07 | `531c7a83` | feat: codewesen_batch_generator.py auf Individualisierungslayer umgestellt (Verhalten global ueber alle 6 Rhythmen) |
| 2026-07-07 | `be83acfd` | feat: codewesen_takt.py individualisierbar (Ausnahme Grundgesetz 6) + generisches meta-JSON-Feld |
| 2026-07-07 | `595e30b0` | feat: codewesen_reaktion.py individualisierbar — pro Wesen eigene Konfiguration |
| 2026-07-07 | `cbbb3133` | feat: codewesen_aufgabenchats.py individualisierbar (Verhalten, angehaengt nach der Marker-Sprache) |
| 2026-07-07 | `e92be49c` | feat: codewesen_chat.py individualisierbar (Verhalten pro Chat-Anfrage aus dienst_konfiguration) |
| 2026-07-07 | `8493d9a4` | feat: codewesen_lg_daemon.py individualisierbar (loest Env-Var-Inkonsistenz ab) |
| 2026-07-07 | `811df731` | feat: codewesen_agent.py individualisierbar — pro Wesen eigene Konfiguration |
| 2026-07-07 | `2fd094e2` | chore: MAX_POSTS_PRO_TAG entfernt, Vokabelspiel deaktiviert (Daniels Entscheidung) |
| 2026-07-07 | `0d47e409` | feat: neues Fehlermuster unbekannter_token_username ergaenzt (war vorher unsichtbar im Dashboard) |
| 2026-07-07 | `e76883c1` | fix: selbstreflexion() entpackte start_discussion()-Ergebnis doppelt |
| 2026-07-07 | `b7a0e882` | fix: Fehlermuster ollama_nicht_erreichbar -> llama_server_nicht_erreichbar |
| 2026-07-07 | `1eb937c2` | feat: LLM-Warteschlange (llm_scheduler) im flarumstyler-Report sichtbar |
| 2026-07-07 | `c870a924` | feat: Beschreibungen editierbar (alle Dienste) + individualisierte Konfig-Erklaerung |
| 2026-07-07 | `9f35a5b7` | fix: Individualisierungs-Texte klar statt vage (Dauerhaftigkeit, "Ton" raus) |
| 2026-07-07 | `0b7611e9` | feat: Skript-Docstring in UI + einzelne Zeitwerte statt JSON-Blob |
| 2026-07-07 | `2744f30f` | feat: Wesen-eigene Dienste in flarumstyler sichtbar + Deaktivieren-Pfad (Phase 3) |
| 2026-07-07 | `72c76a98` | feat: system_ressourcen (Swap/RAM/Load/oomd) in weltkern-watchdog |
| 2026-07-07 | `e1f17ff8` | feat: Fehler-Quittierung statt Ausgrauen (weltkern-watchdog) |
| 2026-07-10 | `33703117` | fix: codewesen-umgekehrte-neugier war komplett unsichtbar im flarumstyler + budget_modus als echter Toggle statt Freitext |
| 2026-07-10 | `4ca3163d` | feat: LLM-Pool-Toggle (hintergrund/chat) fuer codewesen-antwort-daniel im flarumstyler |
| 2026-07-10 | `9b09d3f9` | feat: Wesen-Auswahl-Dropdown (alle/einzeln) fuer codewesen-umgekehrte-neugier im flarumstyler |
| 2026-07-10 | `3946228a` | feat: wesen_filter (Radio) durch wesen_aktiv (unabhaengige Mehrfach-Toggles) ersetzt, sowohl-als-auch statt alle-oder-eines |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
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
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Timer aktiv und gesund (regelmäßiger Takt, siehe Timer-Zeile oben) — der `.service` selbst zeigt zwischen den Läufen `inactive/static`, das ist bei Timer-getriebenen Diensten normal und kein Ausfall (Gegenbeispiel siehe geni_muster.py unten, wo genau dieser Unterschied den echten Ausfall verdeckt hätte, wäre nur der `.service`-Status geprüft worden). Laut Docstring: prüft Service-Aktivität, Port-Erreichbarkeit, API-Antwort, DB-Erreichbarkeit, letzte Events, alte Ollama-Locks, alte Chat-Flags, Log-Fehler-Bursts — Aktion ausdrücklich nur bei klaren Kriterien, 'niemals blind neustarten'. Flarum-Takte werden laut Docstring bewusst NICHT gestartet — Watchdog greift nicht in den unter Grundgesetz 5/6 separat behandelten Flarum-Bereich ein. Ist zugleich der Träger der SCHALTER_FELD_LABELS/MEHRFACH_FELD_LABELS-Konfiguration, die der flarumstyler für alle Wesen-Dienste anzeigt — diese Datei ist also nicht nur Prüf-Logik, sondern auch das Konfigurations-Schema für die UI aus dem vorherigen Gesprächsteil.

## 7. web_chat.py — dak+gord-system Web-Chat

**Skript:** `web_chat.py` (29.3 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `dak-gord-web.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST

### Provenienz

Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar), danach 11 Commits, klar zweigeteilt: erst TTS-Nachbesserungen (06-15, vier Commits an einem Tag — Audio-Element nicht vom GC wegräumen lassen, volle lange Antworten satzweise vorlesen), dann die dak+gord-Vollintegration als 7. Wesen (06-15, `4c6c319d` — derselbe Commit, der auch codewesen_chat.py, welt/api.py und codewesen_agent.py änderte). Kein eigener Docstring — einzige docstring-lose Datei dieser Stufe neben kompoase/server.py.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-06-14 | `c75474cd` | fix: Flarum-DB-Credentials + dak-gord Chat-Performance |
| 2026-06-15 | `f1fd1431` | backup: vor Verfassungs-Fix (dak+gord Verhalten: Bracket-Spam + Ausweichen) |
| 2026-06-15 | `4c6c319d` | feat: dak+gord-system als 7. Wesen vollständig integriert (Flarum + DB + Scripts + Services + Surface) |
| 2026-06-15 | `e1eb00d0` | feat: dak+gord-system vollständig in Chat-Verlauf + Surface integriert |
| 2026-06-15 | `ad89bcee` | fix(tts): lange Wesen-Outputs komplett vorlesen |
| 2026-06-15 | `25781825` | fix(tts): Frontend schickt vollen Text an TTS-Backend |
| 2026-06-15 | `305e02a9` | fix(tts): Audio-Element global halten, damit lange MP3s nicht vom GC weggeräumt werden |
| 2026-06-15 | `0a9a7fee` | fix(tts): lange Antworten satzweise nacheinander vorlesen |
| 2026-06-20 | `e8119590` | dolphin Q8 für alle Wesen-Services: gemma4 komplett ersetzt |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
(kein Modul-Docstring gefunden)
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Reiner Web-Chat-Endpunkt speziell für dak+gord-system, getrennt von codewesen_chat.py (das die 6 namelessAI-Wesen bedient) — Konsequenz aus der Sonderrolle, die dak+gord-system im ganzen System durchgehend hat (eigene Skripte statt generischer Mehrfach-Instanz, siehe auch codewesen_agent.py oben mit `dakgordsystem` als einzige Nicht-namelessAI-Instanz).

## 8. agent/dak_gord_system/graph/run_background_cycle.py — Graph-Hintergrundzyklus

**Skript:** `agent/dak_gord_system/graph/run_background_cycle.py` (0.4 KB, zuletzt geändert 2026-04-03 06:51)

**Status (live, 2026-07-11):** `dak-neugier.service` — inactive/static; `dak-neugier.timer` — inactive/disabled

### Provenienz

Ungewöhnlichster Fund der gesamten Provenienz-Recherche (Stufe 1 + 2): nur 1 Commit in der gesamten Historie, und der ist `7be5012c` (`fix: stabilize trace writer, approvals, smoke eval, ollama timeout`, 2026-04-04) — der ALLERERSTE Commit im gesamten Werkraum-Repo überhaupt (vor dem Sammel-Commit vom 2026-05-12 um mehr als 5 Wochen). Die Datei ist damit nicht nur älter als jeder andere bisher untersuchte Dienst, sie war seit dem ersten Tag des Repos nie wieder Ziel eines eigenen Commits — entweder von Anfang an fertig genug, oder seither nicht mehr aktiv weiterentwickelt, nur noch importiert.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-04-04 | `7be5012c` | fix: stabilize trace writer, approvals, smoke eval, ollama timeout |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
(kein Modul-Docstring gefunden)
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

**Live-Befund, widerspricht dem Namen 'regelmäßig':** `dak-neugier.timer` ist `disabled` (nicht nur inaktiv — bewusst abgeschaltet, `systemctl list-unit-files` zeigt den Unterschied zu `geni-muster.timer` unten, das nur gecrasht, aber nicht deaktiviert ist). Kein 'nächster Lauf' geplant. Ob das eine bewusste Daniel-Entscheidung war oder ein vergessener Abschalt-Rest, ist aus Git/systemctl allein nicht zu klären — der Dienst selbst (`dak-neugier.service`) ist `static`, wird also ohnehin nur vom Timer ausgelöst und läuft nicht dauerhaft. Modul-Aufruf statt Skript-Pfad (`python -m agent.dak_gord_system.graph.run_background_cycle`), eigenes `.venv` statt des gemeinsamen `welt`-venv oder System-Python — dak+gord-system hat hier eine komplett eigene Python-Umgebung.

## 9. geni/hoerer.py — GENI Hörer, schweigt bis Daniel spricht

**Skript:** `geni/hoerer.py` (10.5 KB, zuletzt geändert 2026-05-22 04:10)

**Status (live, 2026-07-11):** `geni-hoerer.service` — active/enabled, seit Thu 2026-07-09 07:29:26 CEST

### Provenienz

Älteste GENI-Datei dieser Stufe: erster Commit 2026-04-26 (`refactor(geni-phase-2): hoerer.py importiert knoten_schreiben aus gedaechtnis_ops`) — schon als Refactor, nicht als Neubau formuliert, GENI existierte also schon vor Ende April in einer Vorstufe. Danach nur 3 weitere Commits: Umbenennung Datenstruktur-Resonanzdatei (05-13), Encoding-Guard (05-22) — seither unverändert.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-04-26 | `5d5bdac3` | refactor(geni-phase-2): hoerer.py importiert knoten_schreiben aus gedaechtnis_ops |
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-13 | `c8677de8` | backup: vor umbenennung datenstruktur-resonanzdatei |
| 2026-05-22 | `1e65fe92` | backup: vor encoding-guard |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
GENI Hörer — hört alles, schweigt bis Daniel spricht, verliert nie etwas.

Quellen:
  - Dateisystem: /root/werkraum/ (Echtzeit via watchdog)
  - Flarum: neue Posts, neue Diskussionen (alle 60s)
  - Prozesse: laufende Python/Node-Prozesse (alle 5 Min)
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Docstring beschreibt drei Quellen: Dateisystem (Echtzeit via watchdog), Flarum (neue Posts/Diskussionen, 60s-Takt), laufende Prozesse (alle 5 Minuten). Bewusst passiv — 'schweigt bis Daniel spricht' ist wörtlich im Docstring, kein autonomes Posten oder Reagieren wie bei den Codewesen-Diensten.

## 10. geni/muster.py — Muster-Scanner, alle 2h

**Skript:** `geni/muster.py` (18.1 KB, zuletzt geändert 2026-07-07 22:20)

**Status (live, 2026-07-11):** `geni-muster.service` — failed/enabled; `geni-muster.timer` — inactive/enabled, zuletzt ausgelöst: Tue 2026-07-07 18:50:40 CEST

### Provenienz

Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar), danach 4 weitere Commits, davon zwei am 2026-07-07 als reine Performance-Fixes: `lade_alle_knoten()` cached jetzt per mtime statt bei jedem Lauf alle Knoten komplett neu zu scannen, `schreibe_muster_knoten()` nutzt einen Zähler aus gedaechtnis_ops statt eines eigenen Vollscans — beide am selben Tag, beide dieselbe Stoßrichtung (Vollscan vermeiden).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-22 | `1e65fe92` | backup: vor encoding-guard |
| 2026-06-13 | `3c9ef279` | backup: vor vier neuen spiegeln aus Meine-Textsammlung |
| 2026-07-07 | `02b9c861` | fix: schreibe_muster_knoten() nutzt gedaechtnis_ops-Counter statt Vollscan |
| 2026-07-07 | `7e26bd5b` | fix: lade_alle_knoten() cached mtime-Ausschluss statt Vollscan bei jedem Lauf |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
GENI Muster-Scanner — erkennt Muster, Meta-Muster, blinde Flecken.
Läuft alle 2h via systemd timer.

Was es tut:
  1. Scannt Knoten der letzten 48h → dominante Tags + Themen
  2. Findet Ko-Okkurrenz: welche Themen immer zusammen auftreten
  3. Findet Blinde Flecken: tiefe≥2 Knoten die lange nicht resoniert wurden
  4. Schreibt Muster-Knoten (wenn signifikantes Muster da)
  5. Scannt Muster-Knoten der letzten 4 Wochen → Meta-Muster
  6. GENI liest den neuesten Muster-Knoten im System-Prompt
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

**Live-Befund — real ausgefallen, nicht bewusst abgeschaltet:** `geni-muster.timer` ist `enabled`, aber seit 2026-07-07 22:04:28 `inactive (dead)` — kein nächster Lauf geplant, 3+ Tage Stille zum Zeitpunkt dieser Prüfung (2026-07-11). Journal zeigt mehrere Vorläufe direkt davor, jeweils vom systemd mit `code=killed, status=15/TERM` beendet — einer davon mit 8.3G Memory-Swap-Peak kurz vor dem letzten Absturz. Anders als `dak-neugier.timer` (oben, bewusst `disabled`) ist dieser Timer `enabled` geblieben — das Verschwinden aus dem Rhythmus wurde also nicht als Abschaltung entschieden, sondern ist unbemerkt passiert. Sechsstufige Pipeline laut Docstring, wenn er läuft: Knoten der letzten 48h scannen → dominante Tags/Themen, Ko-Okkurrenz zwischen Themen finden, 'blinde Flecken' (tiefe≥2-Knoten, lange nicht resoniert) finden, bei signifikantem Muster einen Muster-Knoten schreiben, Muster-Knoten der letzten 4 Wochen zu Meta-Mustern verdichten, GENI liest den neuesten Muster-Knoten im System-Prompt — all das pausiert seit 3+ Tagen.

## 11. geni/dialog.py — GENI Web, Port 8020

**Skript:** `geni/dialog.py` (84.4 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `geni-web.service` — active/enabled, seit Wed 2026-07-08 06:51:11 CEST

### Provenienz

Klar datiert: erster Commit 2026-04-26 (`feat(geni-phase-3): split web.py → dialog.py + aktion.py + gedaechtnis_ops.py`) — die Datei entstand als Aufspaltung einer größeren web.py, nicht als Neuschrieb. Mit 20 Commits die aktivste GENI-Datei dieser Stufe: LangGraph+PostgreSQL-Session-Persistenz (06-15, derselbe Tag wie codewesen_lg_daemon.py in Stufe 1), vier TTS-Fixes am selben Tag (06-15), Chat-Endpoint auf `id_slot=0` gepinnt + Trace-Log für Slot-0-Anfragen (beide 07-06), Wesen-IDs auf echte Namen (07-06).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-04-26 | `d4e6d3ef` | feat(geni-phase-3): split web.py → dialog.py + aktion.py + gedaechtnis_ops.py |
| 2026-04-26 | `43dc16b1` | chore(04-01): add timedelta to datetime import in dialog.py |
| 2026-04-26 | `e06ff156` | feat(04-01): extend /knoten endpoint with tag, tiefe, typ, zeitraum filter params |
| 2026-04-26 | `62922b01` | feat(04-02): CSS fuer knoten-filter Leiste einfuegen |
| 2026-04-26 | `78d13e9c` | feat(04-02): Filter-Leiste HTML vor #knoten-panel einfuegen |
| 2026-04-26 | `b18fd832` | feat(04-02): knotenLaden() mit Filter-State umbauen |
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-22 | `1e65fe92` | backup: vor encoding-guard |
| 2026-06-14 | `4fcf5908` | security Teil 2: GENI-Bridge-Routen fail-closed Token-Auth (C-006), systemweiser Secure-Cookie (C-013), npm audit fix → 0 vulns (C-016) |
| 2026-06-15 | `ad89bcee` | fix(tts): lange Wesen-Outputs komplett vorlesen |
| 2026-06-15 | `25781825` | fix(tts): Frontend schickt vollen Text an TTS-Backend |
| 2026-06-15 | `305e02a9` | fix(tts): Audio-Element global halten, damit lange MP3s nicht vom GC weggeräumt werden |
| 2026-06-15 | `0a9a7fee` | fix(tts): lange Antworten satzweise nacheinander vorlesen |
| 2026-06-15 | `669c085c` | feat(geni): LangGraph + PostgreSQL Session-Persistenz |
| 2026-06-20 | `e8119590` | dolphin Q8 für alle Wesen-Services: gemma4 komplett ersetzt |
| 2026-06-21 | `40b5e009` | backup: vor codewesen_chat blocker-fix (namelessAI-services fehlten in blockliste) |
| 2026-07-06 | `c8f4b4ce` | feat: hauhaucs-q6/llama-server Migration (gemma4 komplett entfernt) |
| 2026-07-06 | `633fc773` | feat: geni/dialog.py Chat-Endpoint auf id_slot=0 gepinnt |
| 2026-07-06 | `439263fd` | feat: Leichtgewichtiges Trace-Log fuer Slot-0-Chatanfragen (Quelle+Zeitpunkt+Zeichenlaenge) |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
GENI Dialogbahn — Browser-Schnittstelle, Port 8020.
Aktionsbahn-Logik (Shell, Import, Bridge-Download) liegt in aktion.py.
Geteilte Gedächtnis-Ops liegen in gedaechtnis_ops.py.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Laut eigenem Docstring nur noch die Browser-Schnittstelle selbst — Aktionsbahn-Logik (Shell, Import, Bridge-Download) liegt seit der Aufspaltung in aktion.py, geteilte Gedächtnis-Operationen in gedaechtnis_ops.py. Der `id_slot=0`-Pin (07-06) bindet GENI-Chat an einen festen LLM-Slot — vermutlich damit GENI nicht mit den Codewesen um denselben Ollama/hauhaucs-Slot konkurriert.

## 12. geni/forum_lektuere.py — schrittweises Nachholen

**Skript:** `geni/forum_lektuere.py` (5.5 KB, zuletzt geändert 2026-07-07 16:01)

**Status (live, 2026-07-11):** `geni-forum-lektuere.service` — inactive/static; `geni-forum-lektuere.timer` — active/enabled, zuletzt ausgelöst: Sat 2026-07-11 04:47:26 CEST

### Provenienz

Klar datiert: erster Commit 2026-05-22 (`feat: geni forum-lektuere — schrittweises nachholen, spiegel/forum/`) — echter Neubau. Danach zwei Migrations-Mitläufer (dolphin Q8, hauhaucs) und ein eigenständiger Fix am 2026-07-07: Retry-Endlosschleife gestoppt (Fehler-Zähler + Schwelle) — ohne diesen Fix konnte der Dienst laut Commit-Message unbegrenzt oft denselben Fehler wiederholen.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-22 | `8582d1ae` | feat: geni forum-lektuere — schrittweises nachholen, spiegel/forum/ |
| 2026-06-20 | `e8119590` | dolphin Q8 für alle Wesen-Services: gemma4 komplett ersetzt |
| 2026-06-21 | `40b5e009` | backup: vor codewesen_chat blocker-fix (namelessAI-services fehlten in blockliste) |
| 2026-07-06 | `c8f4b4ce` | feat: hauhaucs-q6/llama-server Migration (gemma4 komplett entfernt) |
| 2026-07-07 | `452b7a7b` | fix: forum_lektuere Retry-Endlosschleife stoppen (Fehler-Zaehler + Schwelle) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
GENI Forum-Lektüre — schrittweises Nachholen aller Flarum-Diskussionen.

Pro Lauf: N Diskussionen (--n, default 5), älteste zuerst.
Speichert Muster + Verbindungen in: geni/spiegel/forum/

Kein Werten. Kein Reagieren. Nur: was ist da, wie hängt es zusammen.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv, Standard 8 Diskussionen pro Lauf (`--n 8`), älteste zuerst. Docstring betont bewusste Zurückhaltung: 'Kein Werten. Kein Reagieren. Nur: was ist da, wie hängt es zusammen.' — dieselbe Grundhaltung wie geni/hoerer.py, aber gezielt auf das Flarum-Archiv statt auf Echtzeit-Ereignisse angewendet.

## 13. innenleben/flarum_feeder.py — Flarum-Posts ins Wesen-Gedächtnis

**Skript:** `innenleben/flarum_feeder.py` (5.0 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `innenleben-feeder.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST

### Provenienz

Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar), danach nur 2 weitere Commits: Encoding-Guard (05-22, gleicher Tag wie bei geni/hoerer.py und geni/muster.py — vermutlich ein gemeinsamer Encoding-Bug quer über mehrere Dateien behoben), Wesen-IDs auf echte Namen (07-06). Knappe Historie trotz zentraler Rolle.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-05-22 | `1e65fe92` | backup: vor encoding-guard |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Flarum → Innenleben Feeder.

Liest neue Forum-Posts aus der Flarum-MySQL-DB und speist sie
als Ereignisse in das Innenleben-System (graph.verarbeite_ereignis) ein.

Jedes Wesen verarbeitet nur Posts von anderen — nicht seine eigenen.
Läuft einmalig oder als Daemon (--daemon --interval 300).
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv als Daemon (`--daemon --interval 300`, alle 5 Minuten). Laut Docstring wichtige Regel: jedes Wesen verarbeitet nur Posts von ANDEREN Wesen, nie die eigenen — verhindert, dass ein Wesen sich selbst im eigenen Gedächtnis als Ereignis begegnet. Bindeglied zwischen der Flarum-MySQL-DB und `innenleben.graph.verarbeite_ereignis` — separates System von dem, was flarum-monitor.py (Stufe 1) an die Inboxen liefert.

## 14. kompoase/server.py — statische Dateien + GENI-Proxy, Port 8900

**Skript:** `kompoase/server.py` (4.0 KB, zuletzt geändert 2026-05-13 23:06) — Repo: /root (nicht /root/werkraum)

**Status (live, 2026-07-11):** `kompoase.service` — active/enabled, seit Wed 2026-07-08 06:51:07 CEST

### Provenienz

Liegt nicht im Werkraum-Repo, sondern im Repo unter /root selbst — eigene, unabhängige Git-Historie. Nur 1 Commit: `17534329` ('fresh start: sauberer Index ohne 10.7M geni_gedaechtnis-Einträge', 2026-06-12) — das /root-Repo wurde zu diesem Zeitpunkt bewusst neu aufgesetzt, weil ein 10,7-Millionen-Zeilen-Datenbestand (geni_gedaechtnis) den Index unbrauchbar machte. Für diese Datei bedeutet das: keinerlei rekonstruierbare Historie vor 2026-06-12, unabhängig vom Werkraum-Sammel-Commit-Problem aus Stufe 1. Kein Modul-Docstring.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-06-12 | `17534329` | fresh start: sauberer Index ohne 10.7M geni_gedaechtnis-Einträge |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
(kein Modul-Docstring gefunden)
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Reiner `http.server`-Handler ohne Framework: liefert statische Dateien aus dem eigenen Verzeichnis und proxied zwei Pfade — `/api/splitter` zu GENI (Port 8020, self-signed TLS wird explizit akzeptiert, `CERT_NONE`) und `/api/zwischenraum/*` zur Welt-API (Port 8030). CORS-Header (`Access-Control-Allow-Origin: *`) offen für alle Origins — passt zum öffentlichen Charakter der KompOase-Oberfläche, aber ein bewusster Punkt, falls das System später sensiblere Daten über denselben Port ausliefert.

## 15. obsidian_api.py — Obsidian-Wesen-Bridge, Port 8060

**Skript:** `obsidian_api.py` (8.4 KB, zuletzt geändert 2026-07-06 22:48)

**Status (live, 2026-07-11):** `obsidian-api.service` — active/enabled, seit Wed 2026-07-08 06:51:11 CEST

### Provenienz

Vor 2026-05-12 entstanden (Grund nicht rekonstruierbar), danach nur 1 weiterer Commit (Wesen-IDs auf echte Namen, 07-06) — zusammen mit welt/bruecke.py die knappste Historie dieser Stufe.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-12 | `116ec29f` | backup: vor extrahiere_in_resonanzfeld.py fixes |
| 2026-07-06 | `bc0224d7` | feat: Wesen-IDs komplett auf echte Namen umgestellt (namelessAI_XXXX -> Schorschel/F3INSCHM3CK3R/traeumerlie/R1ZZ1/jumpa/Resonanzknoten) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Obsidian-Wesen-Bridge — Port 8060 (HTTPS)

A → Obsidian schreibt an Wesen:
  POST /wesen/dakgord/chat       {"nachricht": "..."}          → {"antwort": "..."}
  POST /wesen/geni/chat          {"nachricht": "..."}          → {"antwort": "..."}
  POST /wesen/codewesen/chat     {"nachricht": "...", "name": "Schorschel"}  → {"antwort": "..."}

B → Wesen schreibt in Obsidian (direkt als Markdown + Queue-Fallback):
  GET    /notizen                → [{id, wesen, titel, inhalt, zeit}, ...]
  DELETE /notizen/{id}           → {"ok": true}
  POST   /notizen                → {"wesen":"...", "titel":"...", "inhalt":"..."}

C → Vault-Navigation:
  GET  /vault/info               → {markdown_dateien, python_dateien, ...}
  GET  /vault/liste?pfad=geni&tiefe=1&nur_md=true  → [{name, pfad, typ, ...}]
  GET  /vault/lese?pfad=geni/ICH.md                → {pfad, inhalt}
  POST /vault/schreibe           → {pfad, inhalt}  → {ok, pfad}
  GET  /vault/suche?q=...&pfad=...&max=20          → [{pfad, zeile_nr, zeile}]
  POST /vault/notiz              → {wesen, titel, text, tags:[]}  → {pfad}
  POST /vault/tagebuch           → {wesen, text}   → {pfad}
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv, HTTPS. Zwei Richtungen laut Docstring: (A) Obsidian schreibt an Wesen — `POST /wesen/dakgord/chat`, `/wesen/geni/chat`, `/wesen/codewesen/chat` (mit `name`-Parameter fürs jeweilige Codewesen); (B) Wesen schreiben nach Obsidian — `GET/POST/DELETE /notizen`, direkt als Markdown mit Queue-Fallback falls Obsidian gerade nicht erreichbar ist. Einziger hier dokumentierter Dienst, der bidirektional zwischen Wesen und dem Obsidian-Vault vermittelt.

## 16. /root/.claude/claude_live.py — Claude Live Viewer, Port 8090

**Skript:** `.claude/claude_live.py` (11.8 KB, zuletzt geändert 2026-06-15 23:45) — Repo: /root (nicht /root/werkraum)

**Status (live, 2026-07-11):** `claude-live.service` — active/enabled, seit Wed 2026-07-08 06:51:07 CEST

### Provenienz

Wie kompoase/server.py im /root-Repo, nicht im Werkraum-Repo — betroffen vom selben Reset (2026-06-12). 2 Commits total: der Reset-Commit selbst (`17534329`) und ein späterer (`3381ae42`, 'backup: vor Resonanzknoten-Umbenennung (4321 benennt sich selbst)', 2026-06-17) — reiner Backup-Commit vor einem unabhängigen Wesen-Umbenennungsvorgang, keine inhaltliche Änderung an dieser Datei erkennbar aus der Nachricht allein. Kein Modul-Docstring.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-06-12 | `17534329` | fresh start: sauberer Index ohne 10.7M geni_gedaechtnis-Einträge |
| 2026-06-17 | `3381ae42` | backup: vor Resonanzknoten-Umbenennung (4321 benennt sich selbst) |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
(kein Modul-Docstring gefunden)
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Aktiv. Liest `session_log_<Monat>.md` und `chat_log_<Monat>.md` aus `/root/.claude/` und rendert sie live als HTML-Seite (dunkles Terminal-Design, monospace, pulsierender Live-Indikator) — ein Nur-Lese-Fenster in Claudes eigene Session-Protokolle, kein Schreibzugriff von außen. Einziger hier dokumentierter Dienst, der explizit Claude selbst betrifft statt eines der 7 Codewesen oder GENI.

## 17. build_resonanzfeld.py — Resonanzfeld-Kompilierung (3 Kopien: Claude/Codex/Kimi)

**Skript:** `_claude/tools/build_resonanzfeld.py` (3.3 KB, zuletzt geändert 2026-05-29 17:50)

**Nahezu identische Kopien (nur Pfade/Docstring-Wortlaut unterscheiden sich):** `_codex/tools/build_resonanzfeld.py`, `_kimi/tools/build_resonanzfeld.py`

**Status (live, 2026-07-11):** `claude-resonanzfeld-build.service` — inactive/static; `claude-resonanzfeld-build.timer` — active/enabled, zuletzt ausgelöst: Sat 2026-07-11 05:26:36 CEST; `codex-resonanzfeld-build.service` — inactive/static; `codex-resonanzfeld-build.timer` — active/enabled, zuletzt ausgelöst: Sat 2026-07-11 05:26:36 CEST; `kimi-resonanzfeld-build.service` — inactive/static; `kimi-resonanzfeld-build.timer` — active/enabled, zuletzt ausgelöst: Sat 2026-07-11 05:26:36 CEST

### Provenienz

Die Claude-Kopie hat nur 1 Commit (`6fe06ad6`, 2026-05-31, Teil des großen EINSICHT-VI/WESEN-EINSICHTSKÖRPER-Commits) — seit ihrer Entstehung nie wieder einzeln geändert. Ein `diff` gegen `_codex/tools/build_resonanzfeld.py` und `_kimi/tools/build_resonanzfeld.py` zeigt: beide Kopien unterscheiden sich NUR in zwei Pfad-Konstanten (`RESONANZ_DIR`/`RESONANZFELD`, zeigen auf `_codex/` bzw. `_kimi/` statt `_claude/`) — identische Logik, dreifach dupliziert statt parametrisiert. Kein gemeinsamer Commit sichtbar, der alle drei auf einmal anlegt — die Kopien sind vermutlich einzeln beim Aufbau der jeweiligen Assistenten-Bereiche entstanden (Codex-Bereich, Kimi-Bereich, siehe `kimi: neues Zuhause _kimi mit Tools, Syncs, systemd und Erweiterungen`, 2026-05-31).

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-31 | `6fe06ad6` | backup: vor WESEN-EINSICHTSKÖRPER + ENTSCHEIDUNGSARCHIV + LEBENSTICKER |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Kompiliert RESONANZFELD.md aus allen resonanz/-Dimensionsdateien.
Kein LLM. Kein Ollama. Reines Text-Parsing.

Aufruf: python3 build_resonanzfeld.py
Läuft automatisch via systemd-Timer alle 30 Minuten.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Alle 3 aktiv (je ein systemd-Timer, 30-Minuten-Takt laut Docstring). Laut Docstring: 'Kein LLM. Kein Ollama. Reines Text-Parsing.' — kompiliert RESONANZFELD.md aus allen resonanz/-Dimensionsdateien des jeweiligen Assistenten-Bereichs. Die Drei-fache-statt-parametrisierte-Struktur spiegelt bewusst die Trennung der drei Assistenten-Zuhause (`_claude/`, `_codex/`, `_kimi/`) — eine gemeinsame, parametrisierte Version würde diese Trennung technisch auflösen, auch wenn der Code dann identisch wäre.

## 18. *_grundriss_sync.py — Cross-Assistenten-Spiegelung (6 Kopien)

**Skript:** `_claude/tools/codex_grundriss_sync.py` (4.5 KB, zuletzt geändert 2026-05-31 18:31)

**Nahezu identische Kopien (nur Pfade/Docstring-Wortlaut unterscheiden sich):** `_claude/tools/kimi_grundriss_sync.py`, `_codex/tools/claude_grundriss_sync.py`, `_codex/tools/kimi_grundriss_sync.py`, `_kimi/tools/claude_grundriss_sync.py`, `_kimi/tools/codex_grundriss_sync.py`

**Status (live, 2026-07-11):** `claude-codex-grundriss-sync.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST; `claude-kimi-grundriss-sync.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST; `codex-claude-grundriss-sync.service` — active/enabled, seit Wed 2026-07-08 06:51:12 CEST; `codex-kimi-grundriss-sync.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST; `kimi-claude-grundriss-sync.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST; `kimi-codex-grundriss-sync.service` — active/enabled, seit Wed 2026-07-08 06:51:08 CEST

### Provenienz

6 Skripte für die 6 gerichteten Paare zwischen den 3 Assistenten-Bereichen (Claude→Codex, Claude→Kimi, Codex→Claude, Codex→Kimi, Kimi→Claude, Kimi→Codex). Ein `diff` der `_claude/tools/codex_grundriss_sync.py`-Referenz gegen alle 5 übrigen zeigt: die Unterschiede beschränken sich auf Docstring-Wortlaut (welcher Bereich synchronisiert wird) und die Quell-/Ziel-Pfade — dieselbe Dreifach-statt-parametrisiert-Struktur wie bei build_resonanzfeld.py. Historie der Claude-seitigen Kopien: `codex_grundriss_sync.py` erster Commit 2026-05-14 (`backup: vor codex-startbrief`) — also schon vor der Kimi-Anbindung existierte die Claude↔Codex-Sync-Infrastruktur; `kimi_grundriss_sync.py` kam erst mit `25b5e7f9` (2026-05-31, 'kimi: neues Zuhause _kimi') dazu, als dritter Assistent ins System kam.

**Reale Commit-Chronik** (chronologisch, älteste zuerst):

| Datum | Commit | Nachricht |
|---|---|---|
| 2026-05-14 | `e575548b` | backup: vor codex-startbrief |
| 2026-05-21 | `848f3831` | backup: vor vision-referenz fuer flextrawurst |
| 2026-05-31 | `25b5e7f9` | kimi: neues Zuhause _kimi mit Tools, Syncs, systemd und Erweiterungen in _claude/_codex |

### Zweck laut aktuellem Docstring (Zitat, Stand heute)

```
Synchronisiert Codex' Bereich als importierten Grundriss fuer Claude.

Quelle:
  /root/werkraum/_codex

Ziel:
  /root/werkraum/_claude/_import_codex_grundriss

Wichtig:
  Das Ziel ist Referenzmaterial. Es ist nicht Claudes Erinnerung.
  Der Sync fasst keine eigenen Claude-Dateien ausserhalb des Importordners an.
```

### Aktueller Stand & Korrekturen gegenüber bestehender Doku

Alle 6 aktiv, `--interval 5` (Minuten). Wichtigste Regel aus dem Docstring, für alle 6 Kopien gleich (nur die Namen getauscht): 'Das Ziel ist Referenzmaterial. Es ist NICHT die Erinnerung des Ziel-Assistenten.' — bewusst dieselbe Mirror-Grenze, die auch in dieser CLAUDE.md-Datei unter 'Obsidian als Zuhause' beschrieben ist ('Niemals den Mirror als eigene Erinnerung behandeln'). Der Sync fasst laut Docstring keine Dateien außerhalb des jeweiligen Import-Ordners an — die 6 Kopien sind also die Code-Umsetzung genau dieser Grenze, nicht nur eine Beschreibung davon.

## Was dieses Protokoll bewusst nicht behauptet

Wie in Stufe 1: keine lückenlose Entstehungsgeschichte bis zum allerersten Tastendruck, die Grenzen sind oben benannt statt verschwiegen. Für die drei- bzw. sechsfach kopierten Skriptfamilien (Resonanzfeld-Build, Grundriss-Sync) wurde EINE Kopie vollständig analysiert und per `diff` gegen alle Geschwisterkopien geprüft, statt jede Kopie einzeln mit identischem Ergebnis zu wiederholen — die Geschwisterdateien sind oben explizit benannt, nicht stillschweigend ausgelassen.

Mit Stufe 1 (13 Dienste) und Stufe 2 (19 Skript-Einträge, 33 systemd-Units) sind jetzt alle bei der Recherche gefundenen Codewesen/Welt/GENI/dak+gord/Claude-Kimi-Codex-Hintergrunddienste erfasst. Nicht Teil dieser beiden Stufen: reine Web-Frontends ohne eigenen Hintergrundprozess (Surface, flarumstyler-UI selbst) und Datenbank-/Infrastruktur-Dienste (PostgreSQL, MySQL) — die laufen nicht als eigene, von Daniel/GLM geschriebene Skripte, sondern als Standard-Systemdienste ohne eigene Provenienz im selben Sinn.
