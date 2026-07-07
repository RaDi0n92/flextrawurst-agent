---
titel: flarumstyler — Meldesystem
typ: system
erstellt: 2026-07-07
autor: claude-code bei Daniels VPS
---

# flarumstyler — Meldesystem

[[INDEX|← Index]]

## Zweck

Meldesystem: zeigt an was nicht so ist wie es sein soll, erklärt was das bedeutet und was eine Empfehlung bringen würde/nicht bringen würde, und Daniel kann direkt darauf reagieren. **Ursprünglich rein beobachtend geplant** ("kein Auto-Fix"), noch in derselben Nacht auf Daniels ausdrücklichen Wunsch ("ich will alles managen selber") um manuelle Start/Stop/Neustart-Steuerung mit Bestätigungsdialog erweitert (siehe Ausbau-Abschnitt unten). Keine Telegram-Anbindung (bewusst abgelehnt), keine Automatik — jede Aktion braucht Daniels expliziten Klick + Bestätigung.

Entstanden in der Nacht 2026-07-06/07, direkt nachdem mehrere wochenlang unbemerkte Bugs auftauchten (`flarum-monitor.service` seit über einem Monat deaktiviert, fehlende dak+gord-Antwortpflicht, veraltete Watchdog-Guardrail). Loser Vorbild-Gedanke: Systemweiser (Ampel-Optik), aber eigenständig gebaut — Systemweiser selbst ist unfertig/roh.

## Zugriff

`https://flextrawurst.de/flarumstyler` (öffentlich, seit 2026-07-07) sowie weiterhin `http://localhost:8787/flarumstyler` lokal. Eigenständige Seite, **nicht** Teil der flextrawurst-Surface (die zeigt laut Daniel nur Flarum-Inhalte ab).

**nginx-Fund beim Live-Schalten:** `/etc/nginx/sites-available/flextrawurst` hatte bereits einen generischen `location /api/ { proxy_pass http://localhost:8030; }`-Block (welt-api) — `/api/flarumstyler` wäre darüber fälschlich zu welt-api geroutet worden (404, da dort unbekannt) statt zu Port 8787. Gefixt mit einem spezifischeren `location /api/flarumstyler { proxy_pass http://localhost:8787; }`-Block (deckt als Prefix auch `/api/flarumstyler_verlauf` mit ab) — nginx bevorzugt bei Prefix-Locations automatisch den längeren, unabhängig von der Reihenfolge in der Datei. Getestet: `/api/health` (welt-api) weiterhin korrekt auf 8030, `/api/flarumstyler*` jetzt korrekt auf 8787.

## Architektur

- **Datenquelle:** `welt/weltkern_watchdog.py`, läuft weiterhin alle 10 Minuten über `weltkern-watchdog.timer`, schreibt `logs/weltkern_letzter_bericht.json`.
- **Erweiterung 2026-07-07:**
  - `WELTKERN_SERVICES` um 13 Flarum-/Codewesen-Dienste ergänzt, die vorher gar nicht überwacht wurden (die 6 `codewesen-<Name>`, `codewesen-antwort-daniel`, `codewesen-takt`, `codewesen-lg-daemon`, `codewesen-forum-neugier`, `codewesen-batch-generator`, `codewesen-dakgordsystem`, `codewesen-reaktion-dakgord`, `flarum-monitor`).
  - Neue Funktion `fehler_uebersicht()`: scannt alle Haupt-Logs + alle `codewesen/<Name>/reaktion.log` einmal komplett durch, zählt **dauerhaft** (seit Logbeginn, kein Zeitfenster) pro bekanntem Fehlermuster und merkt den Zeitpunkt des letzten Auftretens.
  - `FEHLER_MUSTER`-Katalog: pro Muster ein Eintrag mit `was_ist_los`, `empfehlung`, `bringt_das`, `bringt_das_nicht` — Klartext, kein reiner Zähler. Aktuell erfasst: Ollama nicht erreichbar, CSRF-Mismatch, kaputter Import, JSON-ohne-Dict, Tag-Validierung, Impuls ohne Titel.
- **Server:** `scripts/serve_process_camera_preview.ts` (Port 8787, derselbe Server wie Aufgabenchats) — zwei neue Routen:
  - `GET /flarumstyler` — die Seite (`out/process_camera/flarumstyler.html`)
  - `GET /api/flarumstyler` — der aktuelle Watchdog-Bericht als JSON, unverändert durchgereicht
- **Seite:** Ampel-Kacheln (grün/gelb/grau/rot) für Dienste und für Fehlermuster. Klick öffnet ein Detail-Panel mit vollem Erklärungstext. Auto-Refresh alle 30s. Farblogik Fehlermuster: rot < 6h seit letztem Auftreten, gelb < 72h, grau darüber oder nie aufgetreten (0 Vorkommen = grau).

## Ausbau 2026-07-07 (noch selbe Nacht — "die ganze Karte")

Nach Daniels Selbstanalyse-Wunsch fünf Verbesserungen umgesetzt:

1. **Kopf-Banner** — "Alles ok" (grün) oder "X Dienste unerwartet down · Y akute Fehler-Kategorien" (gelb/rot) auf einen Blick, ohne scrollen zu müssen.
2. **Sortierung nach Dringlichkeit** — rote Karten zuerst, dann gelb, dann grau/grün. Dienste-Sektion klappt sich automatisch ein, wenn keine unerwarteten Ausfälle da sind (Daniel kann manuell auf-/zuklappen, das wird respektiert).
3. **`erwartet_aus`-Status** — `SERVICES_ERWARTET_AUS = {"entity-kern", "entity-takt"}` in `weltkern_watchdog.py`: bewusst dauerhaft inaktive Dienste werden grau statt rot markiert, damit sie kein Dauer-Alarm-Rauschen erzeugen und echte rote Punkte nicht verwaschen.
4. **Beispielzeilen im Detail** — `fehler_uebersicht()` sammelt jetzt pro Fehlermuster die letzten 5 echten Log-Zeilen (mit Wesen-Zuordnung bei `reaktion.log`), sichtbar im Detail-Panel unter "Letzte Vorkommen im Log" — direkter diagnostischer Wert ohne SSH.
5. **Mini-Verlauf + Trend-Delta** — `logs/weltkern_verlauf.jsonl` (schlanke Kennzahlen pro Lauf, max. 4320 Zeilen ≈ 30 Tage bei 10-Min-Takt, kein Volltext) über neue Funktion `verlauf_anhaengen()`. Neue Route `GET /api/flarumstyler_verlauf` liefert die letzten 50 Einträge. Frontend zeigt ein kleines `+N`/`-N` neben jeder Fehlerzahl — Vergleich zum vorletzten Lauf.

Bewusst zurückgestellt: Punkt 5 aus der ursprünglichen Ideenliste ("Verknüpfung mit Baustein 2/Content-Live-Ansicht") — Baustein 2 existiert noch nicht, daher nur als Design-Hinweis in `project_meldesystem_vision`-Memory festgehalten.

## Klartext-Beschreibungen + Dienst-Steuerung (2026-07-07, noch selbe Nacht, zweite Kurskorrektur)

- **`SERVICE_BESCHREIBUNG`**-Dict: jeder der 31 Dienste hat jetzt einen Klartext-Satz ("was macht dieser Dienst") — gekürzt direkt in der Karte, vollständig im Detail-Panel. Daniel: "die dienste sollten doch auch alle explizit erklärt werden".
- **Start/Stop/Neustart mit Bestätigung**: Daniel wollte entgegen der ursprünglichen Entscheidung doch direkte Steuerung ("ich will alles managen selber"). Umgesetzt:
  - `SERVICES_GESPERRT_FUER_AKTIONEN = {"ollama", "process-camera-preview", "welt-api", "welt-bruecke"}` in `weltkern_watchdog.py` — meine eigene Vorsichts-Auswahl (Blast-Radius für alle Wesen gleichzeitig), von Daniel nicht widersprochen. Jeder Service-Eintrag im Report hat jetzt ein `steuerbar`-Feld.
  - Neue Route `POST /api/flarumstyler/dienst/:name/:aktion` (start\|stop\|restart) in `serve_process_camera_preview.ts` — validiert Aktion per Regex, prüft `steuerbar` gegen den aktuellen Watchdog-Bericht, verlangt `{"bestaetigt": true}` im Body, führt `systemctl <aktion> <name>.service` über `execFileSync` mit Argument-Array aus (keine Shell-Interpolation).
  - Frontend: Start/Stopp/Neustart-Buttons im Detail-Panel (nur wenn `steuerbar`), eigener Bestätigungs-Zwischenschritt (kein natives `confirm()`, eigenes Overlay wie bei Systemweiser), Modal schließt sich automatisch bei Erfolg und die Seite lädt neu.
  - Live getestet: `codewesen-jumpa.service` per Button neu gestartet, `ActiveEnterTimestamp` bestätigt den echten Neustart.

## Gruppierung, Detailausbau, LLM-Live-Einblick (2026-07-07, dritte Kurskorrektur)

- **Gruppierung Flarum/Welt** — Daniel: "ich hab mir auch gruperungen vorgestellt, ganz oben die in flarum und andere darunter". `SERVICES_GRUPPE_FLARUM` in `weltkern_watchdog.py` markiert alle Wesen-/Flarum-bezogenen Dienste, jeder Service-Eintrag bekommt ein `gruppe`-Feld (`"flarum"`/`"welt"`). Frontend rendert zwei getrennte Grids (`dienste-grid-flarum` oben, `dienste-grid-welt` darunter), je intern weiter nach Dringlichkeit sortiert.
- **Detailausbau** — Daniel: "die info zu den diensten is minimalistisch...man versteht nix". Neue Funktionen `service_details()` (liest `systemctl show` für `ActiveEnterTimestamp`, `NRestarts`, `MemoryCurrent`) und `service_letzte_logs()` (letzte 3 `journalctl`-Zeilen). Report-Felder: `seit_wann`, `neustarts` (mit ⚠-Hinweis bei >3), `speicher_mb`. Sichtbar im Detail-Panel.
- **LLM-Live-Einblick** — Daniel: "ich dachte auch dass wenn ich einblick in ollama hab dass ich genau sehe [was gerade laeuft]". Entdeckt dabei: "ollama" ist seit der hauhaucs-Migration (siehe Memory `2026-07-06_project_ollama_setup`) nicht mehr das Haupt-Backend, sondern nur noch Freier-Modus+Vision — die zwei echten LLM-Backends (`llama-hauhaucs` Port 11435 fuer Live-Chat, `llama-hauhaucs-hintergrund` Port 11436 fuer alle Hintergrund-Denkprozesse) fehlten komplett in `WELTKERN_SERVICES`. Beide ergänzt, neue Funktion `llama_status()` fragt `/slots` + `/metrics` des jeweiligen llama-server direkt ab (beschäftigt/frei pro Slot, Warteschlange, Tokens/Sek, Tokens gesamt). Karte zeigt 🔥/💤-Kurzstatus, Detail-Panel den vollen Slot-Status.
- **Fehler direkt am Dienst** — Daniel: "ich hab mir auch wher ne art fenster vorgestellt der alle dienste liest und jeden fehler direkt dort dann aufploppen lässt mit hiweis woher es kommt". `LOG_DATEI_ZU_DIENST`-Mapping (welches Log gehört zu welchem systemd-Dienst; `reaktion.log` wird ueber `_dienst_fuer_log()` dem `codewesen-reaktion@<wesen>`-Muster zugeordnet) plus `fehler_uebersicht()` liefert jetzt zusätzlich `log_fehler_pro_dienst` — jeder Service-Eintrag bekommt `eigene_fehler`. Frontend zeigt rot/gelb-Badges direkt auf der Dienst-Karte (nur aktuelle, historisch-graue bleiben verborgen), Klick öffnet dasselbe Fehler-Detail-Panel wie die globale Übersicht.

## Individualisierungs-Konfigurationslayer (2026-07-07, vierte Kurskorrektur — Proof-of-Concept)

Daniel: "ich hatte es doch auh so erklärt dass ich jeden dienst bis ins jede kleinste detail individualisieren umschreiben ändern können will" — inklusive Takt/Rhythmus und "genau ändern was das überhaupt tut" über einen editierbaren Text.

**Architektur** (siehe Rueckfrage-Antworten vor dem Bau — volle Individualisierung inkl. Takt, gewollt inkl. Ausnahme von Grundgesetz 6 fuer `codewesen_takt.py` bei spaeteren Diensten):

- Neue Tabelle `dienst_konfiguration` (`welt/schema_dienst_konfiguration.sql`): `dienst_name` (unique), `takt_sekunden` (Override, NULL=Skript-Default), `verhalten_text` (fliesst in den System-Prompt ein, NULL=Standardverhalten), `meta JSONB` (Grundgesetz 1), `created_at`/`updated_at`. Vorbild: `user_modules` (module_name/enabled/config JSONB) aus `schema_menschen.sql`.
- `dienst_konfiguration.py` (Top-Level, wie `hauhau_client.py`): `lade()`/`speichere()`/`alle()`, psycopg2, gibt bei DB-Fehler/fehlendem Eintrag `{}` zurück — Aufrufer behalten dann ihre Default-Werte.
- **Erster umgestellter Dienst:** `codewesen_vokabel_takt.py` (`DIENSTE_MIT_KONFIGURATION = {"codewesen-vokabel-takt"}` in `weltkern_watchdog.py`, weitere Dienste folgen nach Bestätigung). Liest Konfiguration einmal pro Zyklus (`haupt_schleife()`), `takt_sekunden` überschreibt `ZYKLUS_SEK`, `verhalten_text` wird an beide System-Prompts angehängt (nicht ersetzt — die Formatvorgaben wie `Format: SYNONYM|Begründung` bleiben Code-kontrolliert, sonst bricht das Parsing).
- **Schreibpfad:** `welt/dienst_konfiguration_setzen.py` (CLI, `python3 ... <dienst> --takt-sekunden N --verhalten-text "..."`, leer=löscht Override) — aufgerufen von einer neuen Node-Route `POST /api/flarumstyler/dienst/:name/konfiguration` via `execFileSync` (Argument-Array, keine Shell-Interpolation), weil `serve_process_camera_preview.ts` keine eigene Postgres-Anbindung hat. Nach dem Schreiben stößt die Route sofort einen Watchdog-Nachlauf an (`weltkern_watchdog.py` einmalig ausgeführt), damit die Anzeige nicht bis zu 10 Minuten auf den nächsten Timer-Lauf warten muss.
- **Lesepfad:** `weltkern_watchdog.py` läd über `dk.alle()` einmal pro Lauf die komplette Tabelle, hängt sie pro Dienst als `konfiguration`-Feld an, plus `konfigurierbar` (bool, ob der Dienst schon umgestellt ist).
- **Frontend:** neuer "Individualisierung"-Block im Detail-Modal — bei `konfigurierbar=true` ein Formular (Takt-Zahlenfeld, Verhalten-Textarea, Speichern-Button), sonst ein Platzhalter-Hinweis ("kommt schrittweise"). Kein Bestätigungsdialog (im Gegensatz zu Start/Stop/Neustart) — Konfigurationsänderungen sind weniger destruktiv als ein Neustart.
- **DB-Zugangsdaten:** `codewesen-vokabel-takt.service` und `process-camera-preview.service` bekamen je eine zusätzliche `EnvironmentFile=/root/werkraum/.agent/flextrawurst-db.env`-Zeile (systemd erlaubt mehrere `EnvironmentFile`-Direktiven, sie werden gemerged) — vorher hatte keiner der beiden Dienste `FLEXTRAWURST_DB_URI` gesetzt.

## Individualisierungslayer — vollständiger Rollout (2026-07-07, noch dieselbe Nacht)

Nach dem Proof-of-Concept auf Daniels "gogogo" hin alle verbleibenden Dienste durchgezogen, einen nach dem anderen getestet. Ergebnis: **24 von 43 Diensten sind jetzt individualisierbar** — praktisch jeder Dienst, der ein Wesen-Verhalten oder einen Post-Rhythmus steuert.

**Alle 13 ursprünglich katalogisierten Skripte umgestellt** (1 bewusst ausgenommen — `reaktion_auf_dakgord.py` ist ein Einmal-Migrationsskript, kein Dauerdienst):

| Skript | Takt überschreibbar | Verhalten überschreibbar | Besonderheit |
|---|---|---|---|
| `codewesen_vokabel_takt.py` | ✓ (`takt_sekunden`) | ✓ | Proof-of-Concept, siehe oben |
| `codewesen_antwort_auf_daniel.py` | ✓ | ✓ | — |
| `weltbild_builder.py` | ✓ | ✓ | — |
| `codewesen_forum_neugier.py` | ✓ | ✓ (nach den Formatvorgaben angehängt) | Entscheidungs-Format bleibt Code-kontrolliert |
| `codewesen_engagement.py` | ✗ | ✓ | Kein eigener Sleep-Loop — Takt kommt aus `systemd RestartSec=7200`, nicht aus Python |
| `codewesen_batch_generator.py` | ✗ | ✓ (global über alle 6 Rhythmen) | `_wesen_basis()` ist der gemeinsame Textbaustein aller 6 Generierungsfunktionen |
| `codewesen_takt.py` | ✓ (`meta.intervalle`, 6 benannte Werte) | — (kein LLM in dieser Datei) | Ausnahme von Grundgesetz 6, von Daniel vorab genehmigt |
| `codewesen_reaktion.py` | ✓ (`meta.intervalle`, 6 benannte Werte) | ✓ | Läuft **pro Wesen** (7 Instanzen) — jedes Wesen hat seine eigene Konfigurationszeile |
| `codewesen_aufgabenchats.py` | ✗ | ✓ (nach der Marker-Sprache angehängt) | Kein Zeittakt — Flag-Datei-gesteuert |
| `codewesen_chat.py` | ✗ | ✓ | Webserver, request-getrieben, kein Takt-Konzept |
| `codewesen_lg_daemon.py` | ✓ (`takt_sekunden`, hat Vorrang vor `LG_TICK_SEKUNDEN`-Env-Var) | ✓ | War vorher nur über systemd-Unit-Edit konfigurierbar — jetzt einheitlich |
| `codewesen_agent.py` | ✓ (`meta.intervalle`: gedanke/pflichtpost/impuls) | ✓ | Läuft **pro Wesen** (7 Instanzen) |

**Neues generisches Feld:** "Erweiterte Konfiguration (JSON)" im Detail-Modal, nutzt die schon vorhandene `meta`-Spalte — für Dienste mit mehreren benannten Werten statt einem einzigen Takt (`codewesen_takt.py`, `codewesen_reaktion.py`, `codewesen_agent.py`: `meta.intervalle = {"eigene_antwort": 1200, ...}`). Neues optionales `--meta`-Argument in `dienst_konfiguration_setzen.py`, clientseitige JSON-Validierung vor dem Absenden.

**Zwei echte Bugs nebenbei gefunden und behoben** (beide unabhängig vom Individualisierungslayer selbst, aber beim Testen der eigenen Änderungen aufgefallen):
1. `flarum_poster.MAX_POSTS_PRO_TAG` existierte nicht — crashte `codewesen_vokabel_takt.py` bei jedem Post/Gamble, vermutlich seit Wochen unbemerkt (verdeckt durch `Restart=always`). Gefixt, Deckel auf Daniels Wunsch bei 66/Tag (ursprünglich 25, dann angehoben).
2. Die Node-Routen (`/api/flarumstyler/dienst/:name/...`) erlaubten kein `@`/`%` in Dienstnamen — `codewesen-reaktion@Schorschel` etc. wären über `encodeURIComponent()` (→ `%40`) nie erreichbar gewesen, weder für die neue Konfigurations-Route noch für die bereits länger existierende Start/Stop/Neustart-Route. Regex erweitert, `decodeURIComponent()` ergänzt.

**Wiederkehrendes Muster für "Verhalten ohne Format zu brechen":** Bei Dateien mit strikten Parsing-Verträgen (`codewesen_forum_neugier.py`s `ENTSCHEIDUNG:`/`BEZUG:`-Format, `codewesen_aufgabenchats.py`s `[[LESEN:]]`/`[[SICHERN:]]`-Marker-Sprache, `codewesen_agent.py`s JSON-Aktionsformate) wird der Verhaltenstext immer ANGEHÄNGT, nie eingemischt oder ersetzend — die Format-Vorgaben bleiben Code-kontrolliert, Daniel kann Ton/Zusatzanweisungen ändern, aber nicht die Parsing-Verträge brechen.

**Alle Dienste einzeln getestet:** Syntax-Check, Neustart, Journal auf Fehler geprüft, mindestens ein voller UI-Rundlauf (Playwright: Formular ausfüllen → Speichern → Wert in DB bestätigt) für die architektonisch unterschiedlichen Fälle (einfacher Dienst, `@`-Dienst, `meta`-JSON-Dienst).

**Nebenbei gefunden+gefixt:** `flarum_poster.py` referenzierte `MAX_POSTS_PRO_TAG`, das nirgends definiert war — `codewesen_vokabel_takt.py` crashte dadurch bei **jedem** Synonym-Post und **jedem** Gamble (25%-Würfel) mit `AttributeError`, seit vermutlich Wochen unbemerkt, weil `Restart=always` den Dienst alle 5 Minuten klaglos neu startete. Fund passierte zufällig beim Testneustart für dieses Feature — unabhängig vom Konfigurationslayer. Nach Rückfrage: echter Deckel `MAX_POSTS_PRO_TAG = 25` (global über alle 7 Wesen/Tag) ergänzt.

**Getestet:** DB-Helfer (lade/speichere/alle direkt), CLI-Skript (setzen + leeren), Node-Route (setzen, gesperrter Dienst korrekt abgelehnt), volle UI (Playwright: Formular ausfüllen → Speichern → Wert in DB bestätigt → Report aktualisiert sich sofort), Dienst läuft nach Bugfix stabil durch einen echten Gamble-Zyklus.

**Noch offen (Task, nicht vergessen):** Die übrigen ~12 codewesen-Skripte sind noch nicht umgestellt (siehe Recherche-Katalog vom 2026-07-07: `codewesen_takt.py` braucht explizite Ausnahme von Grundgesetz 6, `codewesen_batch_generator.py` ist der architektonisch wichtigste weil er die eigentlichen Post-Inhalte generiert, mehrere haben unterschiedliche `wesen.md`/`weltbild.md`-Zeichenlimits und drei parallele, unabhängige Marker-Sprachen für Verhaltenssteuerung die vereinheitlicht werden könnten). Nach Bestätigung einzeln weitermachen, Ergebnis je zeigen bevor der nächste beginnt (Skalpell-Prinzip).

## Bewusst nicht enthalten

- Keine Push-Benachrichtigung (kein Telegram/E-Mail) — Daniel ruft die Seite bei Bedarf selbst auf.
- Keine Live-Ansicht der heute gebauten Content-Features (Container, Batch-Queue, Ready-Check) — das ist ein separater, späterer Baustein (siehe Memory `project_meldesystem_vision`).
- Keine Steuerung für die 4 gesperrten Kern-Dienste (siehe oben) — dort weiterhin nur manuell auf dem Server.

## Nächste Schritte (noch offen)

- Weitere Fehlermuster ergänzen, sobald neue wiederkehrende Fehlerklassen auffallen.
- Die 8 weiteren Dateien mit derselben JSON-Extraktions-Schwachstelle (nicht geprüft ob dict) sind noch nicht abgesichert — nur die 3 tatsächlich am dak+gord-Absturz beteiligten wurden gefixt.
- Restliche ~12 codewesen-Dienste auf den Konfigurationslayer umstellen (siehe Abschnitt oben).
