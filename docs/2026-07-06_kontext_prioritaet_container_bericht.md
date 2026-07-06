# KONTEXTGRÖSSE, CHAT-PRIORITÄT, CONTAINER-UMBAU — Bericht
**Datum:** 2026-07-06 (zweiter Arbeitsblock, direkt im Anschluss an die HauhauCS-Migration)
**Stand:** Alle vier Themen abgeschlossen und live getestet

---

## Gesamtlage

Direkter Anschluss an `docs/2026-07-06_hauhaucs_migration_bericht.md` — dort
blieben zwei Dinge offen: die Kontextgrößen-Frage (`--ctx-size`/`--parallel`)
und der eigentliche Volllasttest. Aus diesen zwei offenen Punkten wurde ein
deutlich größerer Themenblock: Kontextgröße final entschieden, eine
Chat-Prioritäts-Architektur gebaut, dabei zwei echte Bugs gefunden und
behoben, und — ausgelöst durch eine Rückfrage zu einem ganz anderen Feature —
das komplette Container-Konzept neu gebaut.

---

## TEIL 1 — Kontextgröße final entschieden

- Ausgangswert `--ctx-size 12345 --parallel 2` (6400 Token/Slot) über mehrere
  Zwischenschritte hochgesetzt: 36663 → 45678 → 88888 → letztlich **48884**
  (24576 Token/Slot)
- Unterwegs eine falsche eigene Annahme korrigiert: KV-Cache ist bei diesem
  Modell (nur 2 KV-Heads, GQA) fast kostenlos in RAM — aber **nicht** kostenlos
  in Rechenzeit. Ein Test mit `--ctx-size 88888` zeigte nur 3,2 statt der
  erwarteten 14-15 tok/s, weil eine gleichzeitig laufende, sehr lange
  Wesen-Anfrage (13958 Token) den Vergleich verfälschte
- **`--parallel 3` live getestet und wieder verworfen**: bei 3 gleichzeitig
  aktiven, unterschiedlichen Gesprächen brach die Prompt-Verarbeitung von
  ~90-115 auf ~2,5 tok/s ein (143.481 Log-Zeilen für einen einzigen Task in
  10 Minuten). Ursache: das Modell ist MoE (nur 3B von 35B Parametern aktiv
  pro Token) — sobald mehrere unterschiedliche Sequenzen zu einem
  Batch-Schritt zusammengefasst werden, wandert der Speicherbandbreiten-Bedarf
  Richtung des vollen 35B-Modells statt bei 3B zu bleiben. Mehr Slots helfen
  bei diesem Modell nicht, sie schaden
- CPU-Zuteilung nebenbei von 10 auf 12 Kerne erhöht (Daniels Wunsch),
  `--threads`/`--cpu-range`/`AllowedCPUs` im Gleichschritt angepasst
- Hardcodierte Client-Anzeigen (`NUM_CTX`/`INTERACTIVE_NUM_CTX` in
  `serve_process_camera_preview.ts`, `wesen_chat.html`, `dolphin_mischpult.html`,
  `zensi/server.py`) auf den finalen Wert (24576) nachgezogen — kein
  automatischer Sync zum Server möglich, muss von Hand mitgezogen werden

---

## TEIL 2 — Chat-Prioritäts-Architektur (id_slot)

Daniels Wunsch: kein permanent reservierter, oft leerlaufender Chat-Slot —
stattdessen soll ein Chat, egal mit welchem Wesen/GENI/Spawncharakter, immer
sofort drankommen, ohne dass Automatikbetrieb (Wesen-Ticks, Reaktionen,
GENI-Hintergrund) das blockiert.

- `id_slot` ist ein llama.cpp-Request-Feld, live verifiziert: eine Anfrage mit
  explizitem `id_slot=1` wartete nachweislich auf genau diesen (belegten) Slot,
  statt auf einen früher freien zu wechseln
- `hauhau_client.py`/`.ts`: Hintergrund-Aufrufe bekommen automatisch Slot 1
  oder 2 (`1 + pid % 2`), wenn kein `id_slot` explizit übergeben wird — kein
  Code an den ~35 Hintergrund-Aufrufstellen geändert, der sichere Default
  greift automatisch
- Explizit `id_slot=0` gesetzt an den 5 echten Live-Chat-Einstiegspunkten:
  `codewesen_chat.py`, `geni/dialog.py`, `zensi/server.py`,
  `serve_process_camera_preview.ts` (Dolphin-Chat UND Spawncharakter-Chat)
- Getestet: Chat-Latenz sank von "1,8s bis 253s Warteschlange" (Volllasttest
  ohne Priorisierung) auf durchgängig sofortige Slot-Zuteilung — verbleibende
  Verlangsamung unter Last ist normaler Mehrbenutzer-Overhead, kein
  Wartezeit-Problem mehr

### Zwei echte Chat-Hänger untersucht

Während der Arbeit meldete Daniel zweimal, Chats würden hängen:

1. **Erster Hänger**: eine einzelne, sehr lange Unterhaltung mit dem
   Spawncharakter "Mirlach" (30.879 Token Prompt, 5,3 Minuten Verarbeitung)
   blockierte den reservierten Chat-Slot für alle anderen. Kein Bug — nur die
   erwartbare Kehrseite eines einzelnen reservierten Slots bei einem
   genügend großen Gespräch
2. **Zweiter Hänger**: `progress = 3.00` (über 100%, unsinniger Wert) schon in
   der allerersten Log-Zeile, `n_tokens` blieb 3+ Minuten unverändert bei 715,
   während 62.500 identische Log-Zeilen geschrieben wurden — sieht nach einem
   echten Bug in llama-servers Prompt-Cache/Checkpoint-Mechanismus aus, nicht
   nach normaler Last. Die genaue Quelle (welcher Charakter/Dienst) konnte
   trotz gründlicher Prüfung aller 5 Chat-Endpunkte, aller Logs und aller
   Dateizeiten **nicht zweifelsfrei identifiziert werden** — llama-server
   loggt keine Client-Herkunft, und keiner der aufrufenden Dienste hinterließ
   eine Spur zur exakten Zeit. Per Neustart des Dienstes behoben (auf
   Daniels berechtigten Einwand hin: künftig erst Diagnose sichern, dann
   neu starten)

### Trace-Log als Konsequenz

Damit ein künftiger Hänger sich sofort zuordnen lässt: jede Slot-0-Anfrage
schreibt jetzt vor dem eigentlichen LLM-Call einen Eintrag nach
`_shared/chat_prioritaet_trace.jsonl` (Quelle wie
`codewesen_chat:namelessAI_1234`, Zeitpunkt, Zeichenlänge, PID) —
`trace_prioritaet()`/`tracePrioritaet()` in beiden Client-Bibliotheken, an
allen 5 Chat-Einstiegspunkten aufgerufen. Live getestet, funktioniert,
erfasste sogar einen echten parallel laufenden Chat.

### Weiterer Bugfix, dabei entdeckt: hängende Extraktions-Jobs

Bei der Suche nach dem ersten Hänger fiel auf: `memory_extraktion.json` bei
Mirlach stand seit ~15 Stunden auf `status: "laeuft"` — der Job war
vermutlich bei einem Serverneustart mitten im Lauf abgebrochen worden, die
Datei wusste das nicht und blockierte seither jeden neuen Trigger-Versuch für
immer. Gleiches Muster bei `triggerAbschlussGenerierung()`. Fix: ein
"läuft"-Status älter als 30 Minuten gilt jetzt als hinfällig statt
blockierend. Mirlachs Datei manuell zurückgesetzt.

Ebenfalls untersucht (auf Daniels Verdacht hin, der Kontext-Ausschluss
"belaste trotzdem weiter"): ein Live-Debug-Test zeigte, dass die
Kontext-Ausschluss-Funktion (`wendeKontextAusschlussAn`) tatsächlich korrekt
funktioniert (56.674 Zeichen unfiltriert → 14.597 Zeichen nach Filter bei 50
aktiven Ausschlüssen) — kein Bug in diesem Mechanismus gefunden.

---

## TEIL 3 — Container-Feature: von einer Liste zu mehreren benennbaren Behältern

Ausgangspunkt war eine Erinnerungsfrage Daniels: Container seien "so gedacht,
dass ich selbst immer neue anlegen und benennen kann, egal was und wie viele."
Nachgeschaut statt geraten: das stimmte nicht — weder im aktuellen
Codexium2/Solarius2-Konzept noch im älteren Zwischenwesen-Vorläufer war das je
so gebaut oder auch nur entworfen. Container war von Anfang an eine einzige
feste Liste pro Charakter. Keine Wiederherstellung also, sondern eine neue,
bewusste Entscheidung — vollständig dokumentiert in
`_claude/ideen/codexium2_solarius2/memory_container.md`.

**5 Architekturfragen mit Daniel geklärt**, dann gebaut:
1. Ersetzt komplett (kein Nebeneinander alt/neu)
2. Gesamtbudget bleibt geteilt über alle Container einer Figur
3. Einzeln an-/ausschaltbar (`aktiv`-Flag) — nicht immer alle im Kontext
4. Verwaltung im Profil, "einfach hinzufügbar"
5. Gilt für alle 4 Spawner, nicht nur die Testbed-Varianten

**Migration ohne Datenverlust**: `ladeContainerSammlung()` erkennt sowohl das
alte Pin-Format (Codexium2/Solarius2) als auch das noch ältere Key/Val-Format
(Codexium/Solarius) beim ersten Lesen und überführt es automatisch in die neue
Struktur — keine manuelle Migration, kein Datenverlust.

**Volle Transparenz** (Daniels Wunsch: "alles muss komplett offen sein"): jede
Container-Aktion (anlegen, umbenennen, löschen, pinnen, entfernen) erscheint
als lesbares Ereignis im sichtbaren Chat-Verlauf — gleicher Mechanismus wie
alle anderen Provenienz-Events im System, nicht nur eine stille Log-Zeile.

**Betroffene Dateien** (Details je in eigenem Konzept-Dokument unter
`_claude/konzepte/2026-07-06_*.md`): `serve_process_camera_preview.ts`
(Datenmodell, Migration, 6 neue/geänderte Endpunkte, System-Prompt-Aufbau),
`wesen_profil.html` (Verwaltungs-UI), `wesen_chat.html` (Pin-Modal +
Container-Popup).

**Live getestet** gegen `solarius/KrEaPPy` (regulärer, nicht-Testbed-Charakter,
bestätigt dass die Ausweitung auf alle 4 Spawner tatsächlich funktioniert) —
Container anlegen, pinnen, löschen durchgespielt, Testdaten danach entfernt.

---

## Was noch offen ist

- Das neue, separat besprochene Slider-Feature (letzte N Ein-/Ausgaben auf
  Wunsch zusammenfassen lassen, gegen unbegrenztes Kontextwachstum) ist erst
  besprochen, noch nicht gebaut — auf Daniels Wunsch wurde zuerst der
  Container-Umbau fertiggestellt
- Die genaue Ursache des zweiten Chat-Hängers (progress=3.00-Bug) bleibt
  ungeklärt — das neue Trace-Log sollte das nächste Mal die Zuordnung
  ermöglichen
- Der ursprünglich angefragte volle 8-Wesen-Volllasttest (aus dem allerersten
  Auftrag der Session) wurde durch die Chat-Prioritäts-Arbeit funktional
  ersetzt (echte Latenzmessungen unter Last liegen vor), aber nie als
  eigenständiger, isolierter Test wiederholt seit dem `id_slot`-Rollout
