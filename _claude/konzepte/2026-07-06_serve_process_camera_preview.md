# serve_process_camera_preview.ts (dolphin)

Migriert: 2026-07-06

**Was es tut**: Der große Preview-Server (Port 8787, 3105 Zeilen) hinter
"dolphin" — Daniels Haupt-Interaktions-Oberfläche mit Codewesen/Spawner-
Charakteren (solarius/solarius2/codexium/codexium2), inkl. Session-Verwaltung,
Anhänge (Bilder/Dokumente/URL/Audio), Gedächtnis-Extraktion, Gesprächsabschlüsse,
Live-Streaming-Chat mit Abbruch-Unterstützung.

**7 Ollama-Aufrufstellen gefunden, 6 migriert, 1 bewusst nicht**:
1. Bild-Beschreibung via `VISION_MODEL` (kleines 4,5B-Modell) — **bleibt auf Ollama**,
   siehe eigener Konzept-Absatz unten.
2. Gedächtnis-Extraktion (`runAbschlussJob`-Nachbar, JSON-Antwort) → `hauhau_client.chat()`
3. Gesprächsabschluss-Text (`runAbschlussJob`) → `hauhau_client.chat()`
4. Modell-Umschalt-Endpunkt (`/dolphin/api/set-model` + `/dolphin/api/models`) — **entfernt**,
   gleiche Begründung wie bei zensi (nur noch 1 Modell, kein Dropdown mehr sinnvoll)
5. Haupt-Chat-Streaming (`/dolphin/chat`) → `hauhau_client.chatStream()`
6. Wesen-Chat-Streaming (`/{spawner}/{name}/chat`, mit Abbruch-Tracking über
   `aktiveGenerationen`-Map) → `hauhau_client.chatStream()`

**Warum VISION_MODEL nicht migriert wird**: Bewusste, dokumentierte Architektur-
Entscheidung von vor der Migration — das 35B-Hauptmodell brauchte auf reiner CPU
über 3 Minuten für ein Bild (nie zu Ende getestet), das kleine 4,5B-Modell schafft
dieselbe Beschreibung in ~14 Sekunden. Zwei-Schritt-Pipeline: kleines Modell
beschreibt das Bild als Text, das Hauptmodell bekommt nur den Text, nie die
Rohbilddaten. Bleibt unverändert auf Ollama (Port 11434) — hat nichts mit gemma4
zu tun und war schon vorher richtig gelöst.

**Wichtiger Nebenfund — entfernter toter Mechanismus**: `hauptmodellVoraussichtlichBlockiertBis`
war ein 90-Sekunden-Sperrzeitstempel, der nach jedem Bild-Upload gesetzt wurde,
weil früher Haupt- und Vision-Modell sich einen einzigen Ollama-Slot teilten
(`OLLAMA_MAX_LOADED_MODELS=1`) — Bild verarbeiten verdrängte das Hauptmodell aus
dem RAM, Neuladen dauerte ~40s. Seit das Hauptmodell auf einem eigenen
llama-server-Prozess (Port 11435) läuft, gibt es diese Verdrängung nicht mehr —
der Mechanismus wurde komplett entfernt (hätte sonst faelschlich alle 90s nach
jedem Bild-Upload "Hauptmodell lädt neu" gemeldet, obwohl das Hauptmodell nie
betroffen war).

**Bug gefunden + gefixt während des Live-Tests**: Der Wesen-Chat-Handler schickte
die SSE-Response-Header schon vor dem Streaming-Start, sein `onError`-Callback
hatte aber nur einen Fallback für "Header noch nicht gesendet" (503) — bei einem
echten Streaming-Fehler (siehe unten) blieb die Verbindung für den Client ohne
jede Antwort für immer offen hängen. Jetzt schreibt `onError` bei bereits
gesendeten Headern ein sauberes SSE-Fehlerereignis + `[DONE]` + `res.end()`.

**Ctx-size/parallel-Frage (später am selben Tag geklärt)**: der oben beschriebene
Fund (`exceed_context_size_error` bei langen Verläufen) führte zu einer längeren
Testreihe — Ergebnis: `--ctx-size 48884 --parallel 2` (24576 Token/Slot), mit
`--parallel 3` bewusst verworfen (MoE-Modell wird bei 3 gleichzeitigen
unterschiedlichen Gesprächen durch mehr Experten-Speicherzugriffe drastisch
langsamer). Volle Herleitung in `docs/systemdoku/12_ollama_gemma4.md`.
`INTERACTIVE_NUM_CTX` (Konstante hier, unbenutzt/vestigial) und die hardcodierten
Ctx-Meter-Anzeigen in `wesen_chat.html`/`dolphin_mischpult.html` wurden auf den
aktuellen Wert (24576) nachgezogen.

**Zusammenhang**: `process-camera-preview.service`, neu gestartet, mehrere
Live-Tests erfolgreich (Haupt-Chat mit Token-Zählern, Wesen-Chat mit und ohne
Kontext-Überschreitung).

---

## Nachtrag 2026-07-06 (später) — id_slot-Priorisierung + Trace-Log

Beide Chat-Streams (`/dolphin/chat` und `/{spawner}/{name}/chat`) bekamen
`extra: {id_slot: 0}` — Chat bekommt garantiert einen der 2 Slots, unabhängig
davon wie viel Automatikbetrieb (Wesen-Ticks etc.) gerade läuft. Direkt davor:
`hauhauClient.tracePrioritaet(quelle, zeichenlaenge)` — Reaktion auf zwei nicht
zurückverfolgbare Chat-Hänger, schreibt Quelle+Zeitpunkt+Zeichenlänge nach
`_shared/chat_prioritaet_trace.jsonl`, getrennt von den schweren Chat-Verläufen.

## Nachtrag 2026-07-06 (später) — Container-Budgets erhöht

`CONTAINER_BUDGET_ZEICHEN` 2222→5555, `MEMORY_BUDGET_ZEICHEN` 3333→5555,
`ABSCHLUSS_MAX_ZEICHEN` 2345→4444 (Daniels Zahlen). Gilt seither für alle 4
Spawner, nicht nur codexium2/solarius2 (siehe Container-Umbau unten).

## Nachtrag 2026-07-06 (später) — Container-Feature: mehrere benennbare Behälter

**Ausgangspunkt**: Daniel erinnerte sich, Container seien "so gedacht, dass ich
selbst immer neue anlegen und benennen kann, egal was und wie viele" — nachgeschaut
statt geraten: das stimmte nicht, Container war von Anfang an eine einzige feste
Liste pro Charakter (siehe `_claude/ideen/codexium2_solarius2/memory_container.md`,
dort auch die vollständige Entscheidungs-Historie inkl. der 5 mit Daniel geklärten
Architekturfragen). Keine Wiederherstellung, sondern eine neue, bewusste Entscheidung.

**Neue Datenstruktur** (`container.json`, alle 4 Spawner):
```typescript
interface ContainerBox {
  id: string; name: string; aktiv: boolean; erstellt_am: string;
  eintraege: ContainerEintrag[]; // unveraendertes Pin-Format: text/kommentar/quelle/hinzugefuegt_am
}
interface ContainerSammlung { container: ContainerBox[]; }
```
Ersetzt die alte `{ eintraege: [...] }`-Liste komplett (Daniels Entscheidung: kein
Nebeneinander zweier Formate).

**Migration alter Daten** (`ladeContainerSammlung()`): liest sowohl das alte
Pin-Format (codexium2/solarius2) als auch das noch ältere Key/Val-Format
(codexium/solarius, `{key, val}` → wird zu `"key: val"` zusammengeführt) und
schreibt sofort die neue Struktur zurück (ein Container namens "Container" mit
den migrierten Einträgen). Kein Datenverlust, keine manuelle Migration nötig —
passiert transparent beim ersten Lesen.

**Budget bleibt geteilt** (Daniels Entscheidung): alle Container einer Figur
teilen sich weiterhin ein Gesamtbudget (`CONTAINER_BUDGET_ZEICHEN`), nicht pro
Container einzeln — mehr Container bedeutet nicht automatisch mehr Kapazität.

**Aktiv-Schalter**: jeder Container hat `aktiv: boolean` — nur aktive Container
fließen in den System-Prompt ein (`buildSystemPrompt()`, ein Block pro aktivem
Container mit `[Container: <Name>]`-Überschrift). Daniels Entscheidung: einzeln
an-/ausschaltbar statt immer alle aktiv, damit nicht relevante Container das
Kontextfenster nicht unnötig belasten.

**Neue Endpunkte** (ersetzen `POST/DELETE .../container/pin`, jetzt Container-
spezifisch):
- `POST .../container/neu` `{name}` → neuen leeren Container anlegen
- `PUT .../container/:id/name` `{name}` → umbenennen
- `PATCH .../container/:id/aktiv` `{aktiv}` → an/ausschalten
- `POST .../container/:id/pin` `{text, kommentar?, quelle}` → Eintrag in DIESEN Container
- `DELETE .../container/:id/eintrag/:eintragId` → einzelnen Eintrag entfernen
- `DELETE .../container/:id` → ganzen Container löschen

Alle ohne `isTestbedSpawner`-Gate mehr — gilt jetzt für alle 4 Spawner (vorher
nur codexium2/solarius2), auf Daniels ausdrücklichen Wunsch.

**Vollständige Provenienz** (Daniels Wunsch: "alles muss komplett offen sein"):
neue Ereignis-Typen `container_angelegt`/`container_umbenannt`/`container_geloescht`
in `EREIGNIS_LABEL`/`formatiereEreignisDetails` ergänzt (Server + Client
`wesen_chat.html` synchron gehalten) — erscheinen automatisch im sichtbaren
Verlauf, gleicher Mechanismus wie alle anderen Provenienz-Events (Feedback,
Memory-Änderungen, Profil-Edits). `pin_hinzugefuegt` zeigt jetzt zusätzlich den
Ziel-Container-Namen an.

**UI-Änderungen**: `wesen_profil.html` (Container anlegen/umbenennen/löschen/
Aktiv-Schalter) und `wesen_chat.html` (Pin-Modal fragt Ziel-Container ab inkl.
"+ Neuer Container…"-Option, Container-Popup zeigt gruppiert nach Container) —
siehe eigene Konzept-Dokumente. Der "📌 Container"/"📍 Pinnen"-Button ist jetzt
für alle 4 Spawner sichtbar (vorher nur `IS_TESTBED`), Memory/Sessions/Abschluss
bleiben bewusst weiterhin testbed-exklusiv.

## Nachtrag 2026-07-06 (später) — Stale-Lock-Fix bei Memory-Extraktion/Abschluss

`triggerMemoryExtraktion()`/`triggerAbschlussGenerierung()` prüften bisher nur
`status === "laeuft"`, ohne Alter — wenn der Server während eines laufenden Jobs
neu startet/abstürzt, bleibt die Datei für immer auf "läuft" stehen und blockiert
jeden künftigen Trigger-Versuch dauerhaft. Beobachtet bei `codexium2/Mirlach`:
Job stand seit ~15 Stunden auf "läuft". Fix: ein "läuft"-Status älter als
`EXTRAKTION_STALE_MS` (30 Minuten) gilt jetzt als hinfällig, nicht mehr als
blockierend. Mirlachs `memory_extraktion.json` manuell zurückgesetzt (Datei
gelöscht, Endpunkt behandelt fehlende Datei korrekt als `nie_gelaufen`).

## Nachtrag 2026-07-06 (noch später) — Verdichtungs-Feature gebaut

Auslöser: MoE-Speedprobleme + Daniels Wunsch, "quasi endlos" chatten zu können
durch echte Verdichtung statt nur Kontext-Ausschluss. Volle Herleitung in
`_claude/ideen/codexium2_solarius2/verdichtung.md`.

**Datenmodell** (`verdichtungen.json` pro Charakter, testbed-exklusiv):
```typescript
interface Verdichtung {
  id: string;
  ersetztIds: string[]; // Nachrichten-IDs UND/ODER IDs anderer Verdichtungen
  zusammenfassung: string;
  kommentare: Array<{ text: string; ts: string }>;
  bestaetigt: boolean;
  erstellt_am: string; aktualisiert_am: string;
}
```

**`aktiveZeitachse()`**: baut die Nachrichtenliste, aber jede von einer
bestätigten Verdichtung abgedeckte Spanne erscheint als EINE Einheit.
`findeAeusserstenTraeger()` löst beliebig tiefe Verschachtelung rekursiv auf —
eine Verdichtung kann selbst wieder Teil einer neueren Verdichtung werden,
transitiv, ohne explizites Tracking der Tiefe. Live getestet: 18 Rohnachrichten
→ 3 davon zu 1 Verdichtung (16 Einheiten) → diese + 2 weitere zu 1 äußerer
Verdichtung (14 Einheiten) — korrekt kollabiert.

**Ablauf** (Button 🗜️ unter jeder Nachricht, testbed-exklusiv wie Memory/Kontext):
Slider (0-11) wählt Einheiten ab der geklickten Nachricht rückwärts → Entwurf
(Hintergrund-Job, gleiches Email-Prinzip wie Abschluss/Memory-Extraktion) →
Mensch kann kommentieren (löst Neugenerierung aus, wiederholbar) → erst nach
aktivem "Übernehmen" wird die Verdichtung bestätigt.

**Prompt-Integration wie Container/Erinnerungen**: bestätigte (nicht selbst
absorbierte) Verdichtungen erscheinen als `[Verdichtete Gesprächsabschnitte]`-
Block im System-Prompt (`buildSystemPrompt`), die abgedeckten Rohnachrichten
werden aus der `messages`-Liste gefiltert statt doppelt gesendet. Bewusst NICHT
als synthetische Chat-Nachricht in die messages-Liste gespleisst — konsistent
mit dem bestehenden Muster (Container, Erinnerungen, `kontext_automatisch_gefunden`
landen alle im System-Prompt, nicht in der Nachrichtenliste).

**Race-Condition gefunden + gefixt beim Live-Test**: Ein verworfener
Entwurfsversuch (falsche IDs) lief im Hintergrund weiter, obwohl der Mensch ihn
per "Verwerfen" abgebrochen hatte — `verwerfen` löscht nur die Statusdatei,
bricht den async-Job selbst nicht ab. Als der alte Job Minuten später fertig
wurde, überschrieb er das inzwischen korrekt bestätigte Ergebnis eines neueren
Versuchs mit seinem (falschen) Stand. Fix: jeder Job bekommt einen zufälligen
`jobToken`, der in der Statusdatei mitgeführt wird — vor dem Schreiben des
Ergebnisses prüft der Job, ob sein Token noch mit dem aktuellen Dateiinhalt
übereinstimmt. Verworfene/überholte Jobs erkennen das und schreiben ihr
Ergebnis nicht mehr. Nach dem Fix im Live-Test bestätigt: kein erneutes
Überschreiben mehr aufgetreten.

Neue Endpunkte: `GET .../verdichtung/zeitachse`, `GET/POST
.../verdichtung/entwurf/{status,generieren,kommentar,verwerfen,uebernehmen}`.
Neues Provenienz-Event `verdichtung_uebernommen` (Server+Client synchron).
