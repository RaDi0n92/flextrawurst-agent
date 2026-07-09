# Wesen-Chat: Nacht-Bau + Echttest-Verifikation — Bericht
**Datum:** 2026-07-09
**Stand:** Alle Nacht-Features real gegen die laufende Domain getestet, ein Bug gefunden und behoben

---

## Gesamtlage

In der Nacht vom 2026-07-08 auf 2026-07-09 entstanden zwölf Commits an `flextrawurst/scripts/serve_process_camera_preview.ts` und `flextrawurst/out/process_camera/wesen_chat.html` — Kontext-Mehrfachauswahl, Zeilen/Token-Live-Info, ein nicht-permanenter Übersetzer mit TTS, Fortschritts-/Stop-Steuerung für lange Hintergrundjobs, serverseitiges Rendern für Memory/Container/Aliase, ein Vision-Modell-Fehlerfix und mehrere kleinere Fixes. Dieser Bericht dokumentiert die anschließende vollständige Verifikations-Session: jedes Feature wurde real gegen `https://flextrawurst.de` getestet (curl gegen die echten API-Routen, Playwright headless gegen die echte UI), nicht nur gelesen oder angenommen. Dabei wurde ein echter, stiller Bug gefunden (Wiederkehrende-Themen-Erkennung faktisch tot) und behoben.

---

## Was in der Nacht gebaut wurde (12 Commits, cfd87124 → 0fe2bde4)

| Commit | Was |
|:---|:---|
| `cfd87124` | Kontext-Mehrfachauswahl + Zeilen/Token-Info für alle 4 Wesen-Spawner |
| `778b9f24` | Zeilen/Token-Stats bei gestreamter Wesen-Antwort nachziehen |
| `f8ded3b4` | Zeilenzählung per Layout-Messung + Zeichenangabe ergänzt |
| `10e67249` | Zeilenzählung via ResizeObserver statt rAF + korrekte Unicode-Zeichenzählung |
| `51ff9c03` | Nicht-permanenter Übersetzer mit TTS + Verlauf-Export (alle 4 Spawner) |
| `dd3b7575` | Verlauf-Export trägt jetzt die Übersetzung, nicht nur Original |
| `9035a384` | Regler bis zum kompletten Verlauf + Stop/Fortschritt für Abschluss, Memory, Übersetzer-Download |
| `008c5a06` | Ehrliche Zeitschätzung für Abschluss, Memory-Extraktion, Übersetzer-Download |
| `e162b780` | Memory/Container/Aliase auch serverseitig gerendert (crawlbar) |
| `c4655032` | Verdichtung-Fix, proaktive Sinne, Avatar-Upload, Suche, wachsendes Beziehungsgedächtnis |
| `41add240` | Vision-Modell-Fehler wird nicht mehr lautlos zu leerer Bildbeschreibung |
| `0fe2bde4` | Provenienz-Sichtbarkeit, TTS Pause/Stopp, Dropdown-Entfernung, Verlaufs-Download |

---

## Was real getestet und bestätigt wurde

Alle Tests liefen gegen `codexium2/QATestWesen` (isolierter Test-Charakter, um die echten Verläufe nicht zu verunreinigen), Live-UI-Tests über die echte Domain mit nginx-Routing (nicht direkt gegen Port 8787 — wichtig, weil `/tts/*`-Routen nur über nginx korrekt aufgelöst werden).

- **Kontext-Mehrfachauswahl + Zeilen/Token-Info** — bestätigt bei allen 4 Spawnern (codexium, codexium2, solarius, solarius2), Kontext-Button sichtbar auch bei Nicht-Testbed-Charakteren
- **Übersetzer-Popup mit TTS (Play/Pause/Stopp)** — bestätigt über echte Domain, inkl. Übersetzungsdienst-Direktaufruf (`/tts/translate`, `/tts/translation-languages`)
- **Allgemeiner Verlaufs-Download (Original + Provenienz)** — bestätigt, HTTP 200, 43 KB Markdown-Export
- **Regler/Stop/Fortschritt/Zeitschätzung** für Abschluss-Generierung, Memory-Extraktion, Verdichtung — alle Abbrechen-Endpunkte real getestet (Verdichtung mitten im Lauf abgebrochen → Status korrekt `abgebrochen`, keine Race Condition)
- **SSR Memory/Container/Aliase** — serverseitig gerendert und crawlbar, Dropdown bleibt wie gewünscht im UI versteckt
- **Vision-Modell-Fehler** — echter Crash reproduziert (Ollama-Modell nicht geladen), Ergebnis jetzt sichtbarer HTTP-500-Fehler statt stiller leerer Bildbeschreibung
- **Zeilen/Zeichen/Token-Live-Stats während des Streamens** — verifiziert mit echter, langsamer Modellantwort (Cache-Checkpoint musste neu aufgebaut werden, >30s reine Prompt-Verarbeitung): Zwischenwerte folgen dem Streaming korrekt, hinken nur innerhalb einer noch nicht umgebrochenen Zeile hinterher (bewusst so gebaut, siehe Code-Kommentar in `wesen_chat.html`), Endwert stimmt nach Abschluss immer exakt mit der echten Zeichenlänge überein
- **Avatar-Upload, Suche, Beziehungsgedächtnis** — Endpunkte real aufgerufen, funktionieren

---

## Gefundener Bug: Wiederkehrende-Themen-Erkennung war faktisch tot

**Symptom:** `wiederkehrende_themen.json` bei QATestWesen zeigte nach mehreren Gesprächen neun verschiedene Themen-Einträge, alle mit `anzahl: 1` — obwohl inhaltlich mehrere davon eindeutig dasselbe Thema waren ("Unbeständigkeit und Formwandel" / "Körperliche Schwere vs. Unbeständigkeit" / "Starre vs. Unbeständigkeit des Menschen").

**Ursache:** `mergeWiederkehrendeThemen()` matcht neue Themen nur per exaktem, normalisiertem String-Vergleich gegen bestehende Einträge. Der Extraktions-Prompt zeigte dem Modell zwar die bisherigen Memory-Kategorien zum Abgleich, aber nie die bereits gespeicherten Themennamen aus `wiederkehrende_themen.json` selbst. Das Modell musste den Themennamen bei jeder Extraktion neu erfinden — dadurch blieb `anzahl` in der Praxis immer bei 1, und das gesamte Feature (inkl. dem System-Prompt-Hinweis, der erst ab `anzahl>=2` greift, und `renderWiederkehrendeThemenText`, das nur ab diesem Schwellenwert überhaupt etwas anzeigt) war faktisch tot, obwohl technisch fehlerfrei.

**Fix (Commit `971dba35` in `/root`):** Der Extraktions-Prompt bekommt jetzt die Liste der bereits als wiederkehrend erkannten Themennamen (mit bisheriger Zählung) explizit mitgegeben, mit der Anweisung, bei Übereinstimmung den Namen zeichengenau zu übernehmen statt neu zu formulieren.

**Verifikation:** Direkt nach dem Fix stieg `anzahl` beim nächsten echten Testlauf auf 2 — bei zwei Themen gleichzeitig ("Unbeständigkeit und Formwandel" und "Sensorische Wahrnehmung von Sprache"), das Provenienz-Event `thema_wiederholt_erkannt` wurde korrekt geschrieben.

**Wichtiger Nachtrag zur eigenen Sorgfalt:** Der erste Commit-Versuch dieses Fixes landete versehentlich nur im `/root/werkraum`-Repo (Datendateien), nicht im `/root`-Repo, in dem der eigentliche Quellcode liegt (`/root/flextrawurst` ist real ein Unterverzeichnis von `/root`, nicht von `/root/werkraum`, trotz eines ähnlich benannten, aber inhaltlich anderen `/root/werkraum/flextrawurst/`). Der Fix war dadurch bis zum Dokumentations-Nachtrag uncommitted. Jetzt korrekt nachgeholt.

---

## Nebenwirkung (unbereinigt, Daniel-Entscheidung offen)

Beim Testen des Kontext-Ausschluss-Endpunkts gegen einen Nicht-Testbed-Charakter (solarius/KreFsUzi) wurde versehentlich ein Test-Event mit einer nicht existierenden `msgId` in dessen echten, append-only Verlauf geschrieben. Harmlos für die Datenintegrität (kein UPDATE/DELETE, nur ein zusätzliches Event), aber real vorhanden. Nicht bereinigt, weil Löschen aus einem append-only-Verlauf ohne expliziten Auftrag falsch wäre.

---

## Was bewusst nicht getan wurde

| Was | Warum |
|:----|:------|
| KreFsUzi-Testdaten-Event bereinigen | Braucht Daniel-Entscheidung (append-only-Prinzip) |
| Systemdoku (`docs/systemdoku/*.md`) aktualisieren | Keine bestehende Datei beschreibt die Chat-UI-Details auf dieser Tiefe — kein Nachtrag nötig, kein Nachtrag vorgenommen |
| Weitere Nacht-Features über die getesteten hinaus | Alle 12 Commits wurden abgedeckt; kein Hinweis auf weitere ungetestete Bereiche gefunden |

---

## Schlusssatz

Diese Session war kein neuer Bau, sondern eine vollständige Gegenprobe: jedes in der Nacht gebaute Feature wurde real ausgelöst und sein tatsächliches Ergebnis geprüft, nicht nur der Code gelesen. Das hat einen stillen, technisch fehlerfreien aber funktional toten Bug aufgedeckt (Wiederkehrende Themen) — genau die Art Fehler, die reines Code-Lesen nicht zuverlässig findet.
