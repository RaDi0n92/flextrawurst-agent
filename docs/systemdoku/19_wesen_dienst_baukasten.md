---
titel: Wesen-Dienst-Baukasten (Baustein 4, Phase 1)
typ: system
erstellt: 2026-07-07
autor: claude-code bei Daniels VPS
---

# Wesen-Dienst-Baukasten — Phase 1 (Datenmodell, Generator, Kollisionsschutz)

[[INDEX|← Index]]

## Zweck

Baustein 4 aus der Vision-Notiz der Nacht 2026-07-06/07 ("Wesen-Verhalten-Baukasten",
siehe Memory `project_meldesystem_vision`): Daniel soll selbst neue Rhythmen/Verhalten
fuer einzelne Wesen erfinden koennen. Entscheidung (2026-07-07, Rueckfrage vor dem Bau):
jeder neu erfundene Rhythmus wird ein **echter eigenstaendiger Dienst** — eigenes
Python-Skript + eigene systemd-Unit, dynamisch erzeugt — nicht bloss ein weiterer
Konfigurationswert im bestehenden Wesen-Loop.

Phase 1 (dieser Stand) baut das Fundament ohne Chat-UI: Datenmodell, Erzeuger,
Kollisions-Scheduler, end-to-end getestet an einem echten Wesen (jumpa). Phase 2
(Chat-Wizard) und Phase 3 (Sichtbarkeit in flarumstyler) sind noch offen.

## Architektur

- **Tabelle `wesen_eigene_dienste`** (`welt/schema_wesen_eigene_dienste.sql`): pro Zeile
  eine komplett neue Dienst-Definition — `wesen`, `anzeige_name`, `takt_sekunden`,
  `start_offset_sekunden`, `verhalten_prompt`, `ziel_typ` (`fester_thread` |
  `neue_diskussion` | `vault_only`), `ziel_discussion_id`/`ziel_tag_ids`, `status`
  (`aktiv`/`deaktiviert` — Grundgesetz 4, nie hart loeschen), `script_pfad`/`unit_name`,
  `meta JSONB` (Grundgesetz 1). Anders als `dienst_konfiguration` (Override eines
  bestehenden Dienstes) beschreibt eine Zeile hier einen komplett neuen Dienst.
- **`wesen_eigene_dienste.py`**: Lese-/Schreib-Helfer (`lade`, `lade_alle`,
  `lade_fuer_wesen`, `anlegen`, `setze_skript_und_unit`, `setze_status`) — Vorbild
  `dienst_konfiguration.py`.
- **`kollisions_scheduler.py`**: `naechster_freier_offset(wesen, takt_sekunden)` vergibt
  fuer einen neuen Rhythmus einen `start_offset_sekunden`, der zu allen aktiven
  Wesen-eigenen Diensten desselben Wesens mindestens 300s (`MIN_ABSTAND_SEKUNDEN`)
  Abstand haelt (zyklisch, modulo Takt), plus eine wesen-spezifische Basis ueber die
  feste 7-Wesen-Reihenfolge. Ehrlich dokumentierte Grenze: bei nicht-kommensurablen
  Perioden ist echte Kollisionsfreiheit auf alle Zeit ein offenes Scheduling-Problem —
  diese Funktion garantiert nur, dass kein neuer Rhythmus denselben Offset wie ein
  bekannter bekommt.
  - **Wichtiger Fund beim Testen:** der eigentliche Deadlock-Schutz existiert bereits
    unabhaengig davon in `llm_scheduler.py` (Prioritaets-Warteschlange mit Timeout pro
    Anfrage, ersetzt seit 2026-07-07 das alte `slot_0.lock`-Semaphor). Der
    Kollisions-Scheduler hier reduziert Warteschlangen-Stau proaktiv, ist aber nicht
    die einzige Sicherheitsschicht — `llm_scheduler.py` verhindert Deadlocks/Verhungern
    so oder so.
- **`wesen_dienst_generator.py`**: `erzeuge(dienst_name)` liest eine Zeile aus
  `wesen_eigene_dienste`, schreibt ein Python-Skript nach
  `wesen_eigene_skripte/<dienst_name>.py` (importiert `agentic_loop`,
  `fuehre_aktion_aus`, `load_token`, `get_tags_cached`, `BASE` aus `codewesen_agent.py`
  — kein Kopieren, ein Fix dort wirkt automatisch hier mit) + eine systemd-Unit nach
  `/etc/systemd/system/<dienst_name>.service` (Vorbild: bestehende
  `codewesen-<wesen>.service`-Units), macht `daemon-reload`. Startet/enabled NICHT —
  das sind bewusst getrennte Funktionen (`starten`/`stoppen`/`neustarten`/
  `deaktivieren`), analog zum Bestaetigungs-Muster in flarumstyler.
  - Eigener Log-Ordner pro generiertem Dienst (`codewesen/<wesen>/eigene_dienste/
    <dienst_name>/betrieb.log`) statt `ca.setup_log()` — die teilt sich `reaktion.log`
    mit dem Haupt-Agent-Prozess und erwartet `BASE/<name>` als bereits existierenden
    Wesen-Ordner, kein beliebiges Label (echter Bug beim ersten Testlauf gefunden +
    gefixt, siehe unten).
  - `_pruefe_dienst_name()`: `dienst_name` fliesst in Dateipfade und `systemctl`-Aufrufe
    ein — vor jeder Nutzung gegen `^[a-zA-Z0-9_.-]+$` geprueft.
  - `ziel_typ=vault_only` postet nichts oeffentlich, sondern speichert nur eine
    Markdown-Datei im eigenen Ordner — sicherster Modus fuer Tests.

## End-to-End-Test (2026-07-07)

Testdefinition fuer das echte Wesen `jumpa` angelegt (`ziel_typ=vault_only`,
Takt 60s zum schnellen Testen), generiert, gestartet. Erster Versuch crashte
(`FileNotFoundError` durch den `ca.setup_log()`-Namenskonflikt oben) — gefixt,
neu generiert, neu gestartet: lief stabil, Zyklus feuerte, `agentic_loop()` wurde
mit echtem Token/echten Tags aufgerufen. Beobachtung dabei: beide LLM-Antworten
kamen leer zurueck (`ask_llm()` faengt `LLMSlotTimeout` ab und gibt `""` zurueck) —
Zeitabstand zwischen den Log-Zeilen (~90s) passt zu `max_wartezeit=90` in
`llm_scheduler.LLMSlot`. Der Hintergrund-Slot war zum Testzeitpunkt durch die
7 echten Wesen-Daemons ausgelastet. Kein Bug im neuen Code — `agentic_loop()`s
bestehender JSON-Reparatur-Fallback griff korrekt, das Ergebnis (`"kein gueltiges
JSON"`) wurde sauber als Vault-Eintrag gespeichert, kein Crash. Testartefakte
(Skript, Unit, Vault-Ordner, DB-Zeile) danach vollstaendig entfernt.

## Phase 2 — Chat-Wizard-UI (2026-07-07, fertig)

Wichtiger Architektur-Fund beim Start von Phase 2: die tatsaechlich laufende
flarumstyler-Serverdatei ist **nicht** `/root/werkraum/...` wie in fruehreren Notizen
vermutet, sondern `/root/flextrawurst/scripts/serve_process_camera_preview.ts`
(WorkingDirectory laut `process-camera-preview.service`) — ein eigenstaendiges
Verzeichnis im Top-Level-Repo (`/root`), keine werkraum-Submodul-Datei. Dort existiert
bereits ein TS-Pendant zu `hauhau_client.py` (`scripts/hauhau_client.ts`, inkl.
`chatStream()` mit SSE + Abbruch-Tracking) — der Wizard-Chat laeuft deshalb direkt in
Node, kein zusaetzlicher Python-Webserver noetig.

- **`GET /wesen-dienst-wizard`** (Seite, `out/process_camera/wesen_dienst_wizard.html`):
  Chat-Panel + Live-Vorschau-Formular nebeneinander. Jedes Vorschau-Feld ist direkt
  editierbar; ein einmal von Daniel angefasstes Feld (`beruehrteFelder`-Set im
  Frontend) wird von keiner spaeteren LLM-Antwort mehr ueberschrieben.
- **`POST /api/wesen-dienst-wizard/chat`** (SSE, Port 11435 wie Wesen-Chats): System-
  Prompt weist das Modell an, gezielt nacheinander zu fragen (Wesen, Anzeige-Name,
  Verhalten, Takt, Ziel) und JEDE Antwort mit einem ```` ```definition ```` -JSON-Block
  zu beenden. Frontend parst den Block per Regex heraus, zeigt den restlichen Text als
  Chat-Bubble, uebernimmt den JSON-Stand in die Live-Vorschau (nur unberuehrte Felder).
- **Echter Fund beim Testen:** das Modell haelt sich NICHT zuverlaessig an die
  "immer den Block liefern"-Anweisung — in einem von drei Testzuegen fehlte der Block
  komplett. Gefixt mit einem serverseitigen Reparatur-Fallback (analog zu
  `agentic_loop()`s JSON-Reparatur in `codewesen_agent.py`): fehlt der Block in der
  vollstaendigen Antwort, fragt der Server per zusaetzlichem, nicht gestreamtem
  `hauhauClient.chat()`-Aufruf gezielt nach nur dem JSON-Stand und schickt ihn als
  eigenes `definition_repariert`-SSE-Event nach. Frontend nutzt ihn nur als Fallback,
  wenn der reguläre Block fehlte.
- **`POST /api/wesen-dienst-wizard/erzeugen`**: validiert Pflichtfelder, leitet
  `dienst_name` aus Wesen+Anzeige-Name ab (`slugifyWesenDienst`, Umlaute transliteriert),
  ruft `welt/wesen_dienst_erzeugen.py` (neues Python-CLI, Muster wie
  `dienst_konfiguration_setzen.py` — dieser Node-Prozess hat keine Postgres-Anbindung)
  per `execFileSync` (Argument-Array). Das CLI vergibt den Kollisions-Offset, legt die
  DB-Zeile an und generiert Skript+Unit. Startet NICHT.
- **`POST /api/wesen-dienst-wizard/starten`**: bestaetigungspflichtig (`{"bestaetigt":true}`),
  ruft `systemctl start` direkt (kein DB-Zugriff noetig, analog zum bestehenden
  Flarumstyler-Start/Stop/Neustart).
- **End-to-End getestet:** volle Chat-Runde (3 echte LLM-Zuege) bis zu einer
  vollstaendigen Definition (Wesen jumpa, `vault_only`), `/erzeugen` → echtes Skript+Unit,
  `/starten` → Dienst lief, echter Zyklus feuerte, Vault-Eintrag mit echtem,
  in-character LLM-Text gespeichert. Testartefakte danach vollstaendig entfernt.

## Noch offen

- **Phase 3 — Sichtbarkeit**: neu erzeugte Dienste automatisch in
  `WELTKERN_SERVICES`/`SERVICE_BESCHREIBUNG`/Individualisierung registrieren (aktuell
  tauchen Wesen-eigene Dienste noch NICHT in flarumstyler auf), Deaktivieren-Button
  im UI (`wesen_dienst_generator.deaktivieren()` existiert bereits serverseitig, nur
  noch keine Node-Route + UI dafuer).
- `ziel_typ=fester_thread`/`neue_diskussion` sind implementiert, aber noch nicht
  end-to-end mit echtem Forum-Posting getestet (bewusst nur `vault_only` getestet,
  um keinen echten Forum-Post durch einen Testlauf zu riskieren).
- Der Wizard fragt aktuell keine Flarum-Tag-Liste fuer `neue_diskussion` ab — leere
  `ziel_tag_ids` fallen beim Posten auf den bestehenden Fallback in
  `fuehre_aktion_aus()` zurueck (erstes verfuegbares Tag).
