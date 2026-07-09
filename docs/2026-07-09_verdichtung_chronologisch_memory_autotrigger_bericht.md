# Verdichtung chronologisch echt integriert + Memory-Auto-Extraktion — Bericht

**Datum:** 2026-07-09
**Stand:** Umgesetzt, live verifiziert (inkl. eines echten, während der Verifikation gefundenen Absturz-Bugs), committet (`b58eb4e0`)

---

## Ausgangslage

Direkt im Anschluss an die drei kleineren Löschungen (Wiederkehrende Themen, feste Textblöcke, Pro-Nachricht-Feedback, siehe `2026-07-09_drei_systemprompt_bausteine_entfernt_bericht.md`) hat Daniel seine eigentliche Vision für Verdichtung im Detail beschrieben: das Kontextfenster soll sich wie ein vollständig chronologischer, durchsuchbarer "begehbarer Erinnerungskörper" verhalten. Eine Verdichtung soll eine Original-Nachricht GENAU an ihrer Stelle ersetzen — nicht als separater Block irgendwo anders. Zusätzlich wollte er die schon länger bekannte, willkürliche 20-Nachrichten-Grenze der Memory-Extraktion durch einen echten Automatismus ersetzen. Auftrag am Ende: "jetzt durchdenken und dann in einem Rutsch bauen."

## 1) Verdichtung: chronologisch echt ins Kontextfenster integriert

**Vorher:** Verdichtete Rohnachrichten wurden aus dem Verlauf gefiltert, die Zusammenfassungen aller bestätigten Verdichtungen landeten als EIN flacher Block (`[Verdichtete Gesprächsabschnitte]`) im System-Prompt — unabhängig von ihrer tatsächlichen Position im Gespräch.

**Jetzt:** `aktiveZeitachse()` (bereits vorhandene Funktion, bisher nur für die Slider-Anzeige und die Verdichtungs-Generierung selbst genutzt) baut direkt die an das Modell gesendete Nachrichtenliste. Jede Verdichtung erscheint an der Stelle, an der ihre Original-Nachrichten standen.

### Echter Bug, live gefunden

Der erste Versuch fügte eine Verdichtung als eigene Nachricht mit `role: "system"` mitten in den Verlauf ein. Beim ersten echten Live-Test (Testcharakter `codexium2/VerdichtungLiveTest`, zwei Nachrichten gesendet, die erste verdichtet, dritte Nachricht abgeschickt) stürzte der komplette Chat ab:

```
llama-server 400: "Unable to generate parser for this template ... System message must be at the beginning."
```

Die Jinja-Chat-Vorlage des Modells erlaubt `role: "system"` ausschließlich als allererste Nachricht im gesamten Request — nicht mittendrin. **Fix:** der Verdichtungstext wird jetzt vor die nächste sichtbare Nachricht gewoben (`[Bereits verdichteter Gesprächsabschnitt]: ...` + Original-Content dahinter), exakt nach demselben Muster wie die bestehende Anhang-Injektion (Bild-/Dokument-Beschreibungen werden schon länger genauso vor eine Nachricht gesetzt). Die Rolle der Trägernachricht (user oder assistant) bleibt unverändert.

Nach dem Fix erneut live getestet: derselbe Ablauf lief ohne Absturz durch. Per temporärem Debug-Log (`DEBUG_OLLAMA_MESSAGES=1`, nach der Verifikation wieder entfernt) mechanisch bestätigt, dass die Verdichtung korrekt an der richtigen Position im tatsächlich gesendeten Array steht — die LLM-Antwort selbst enthielt danach eine sachlich falsche Erinnerung (verwechselte "lila" mit "blau"), was aber ein reines Modell-Recall-Problem ist, keine Aussage über die Korrektheit der Code-Änderung (durch das Debug-Log unabhängig bestätigt).

### Nebenfund: `aktiveZeitachse()`-Bug behoben

Nachrichten ohne `id` (aus der Zeit vor der ID-Einführung, 2026-07-04) wurden von der Funktion bisher komplett verschluckt — weder angezeigt noch ersetzbar. Betraf potenziell alte Gespräche. Fix: id-lose Nachrichten werden jetzt immer als eigene Einheit durchgereicht (können naturgemäß nie Teil einer Verdichtung sein, da sie keine matchbare ID haben).

## 2) Verdichten-Popup neu gebaut

- Checkbox-Mehrfachauswahl: eine einzelne Nachricht, mehrere, oder alle gleichzeitig markierbar
- Regler bleibt erhalten, markiert weiterhin einen chronologischen Bereich vor (nur im Modus "Chronologisch" sichtbar) — einzelne Häkchen danach entfernbar
- Sortier-Dropdown: Chronologisch / Zeichenanzahl auf-ab / Tokenanzahl auf-ab
- Laufende Summe während der Auswahl (Zeichen + geschätzte Tokens der aktuell markierten Einheiten)
- Nach Entwurfserstellung, vor dem Übernehmen: "Macht schätzungsweise ~X Tokens frei (A → B Zeichen)" — Berechnung rein clientseitig aus bereits vorhandenen Daten, kein neuer Server-Endpunkt nötig

## 3) Verstrichene Zeit jetzt immer sichtbar

Bei Verdichtung UND Abschluss-Generierung wurde die verstrichene Zeit bisher nur angezeigt, solange noch keine Prozent-Schätzung möglich war. Jetzt immer sichtbar, zusätzlich zur Schätzung.

## 4) Memory-Extraktion: automatischer Rhythmus

- `nachrichtenSeitLetzterExtraktion()`: zählt Nachrichten seit dem Startzeitpunkt (`gestartet_am`) des letzten Extraktionsversuchs — bewusst nicht über das sichtbare Provenienz-Ereignis gezählt, weil das nur bei tatsächlichem Fund geschrieben wird und ein leerer Durchlauf den Zähler sonst nie zurückgesetzt hätte
- Ab 10 Nachrichten: Vorab-Hinweis in der UI ("in spätestens X weiteren Nachrichten läuft automatisch eine Extraktion")
- Ab 20 Nachrichten: automatischer Trigger, direkt nach dem Speichern der Wesen-Antwort im Chat-Handler
- Ehrliche Zeitschätzung: da die JSON-Extraktion keine bekannte Ziellänge hat (anders als Verdichtung/Abschluss mit festem Zeichen-Maximum), wäre eine Live-Prozent-Schätzung erfunden. Stattdessen: echte Dauer der letzten 5 Durchläufe wird gespeichert (`letzte_dauern_sek`), Durchschnitt als "üblicherweise ca. Xs" angezeigt — klar als Erfahrungswert markiert, kein Countdown

## 5) Memory-Popup: neu/alt-Unterscheidung + Bearbeiten

- Einträge aus dem letzten Extraktionsdurchlauf werden farblich hervorgehoben (`kategorie::text`-Abgleich gegen die im Status gespeicherten `texte`)
- Neuer "✎ bearbeiten"-Button pro Eintrag öffnet ein Inline-Textarea — Speichern nutzt den bereits bestehenden `PUT .../memory`-Endpunkt (der schon Budget-Prüfung und Provenienz-Diff mitbringt), kein neuer Endpunkt nötig

## Verifikation

- `node --check`: fehlerfrei nach jedem Zwischenschritt
- `npm test`: durchgehend unverändert 1500 pass / 123 fail
- Live gegen `codexium2/VerdichtungLiveTest` (danach gelöscht): zwei Nachrichten, eine Verdichtung erstellt und übernommen, Zeitachse-Endpunkt bestätigt korrekte chronologische Position, Folgenachricht hat den (vor dem Fix crashenden) Fall ausgelöst und lief danach durch, Debug-Log bestätigte korrekten Inhalt an korrekter Position im gesendeten Array
- Server neu gestartet (nach expliziter Rückfrage), Debug-Code danach entfernt, Testartefakte restlos gelöscht

## Nicht Teil dieser Änderung

Rückblick-auf-frühere-Gespräche als RAG-Trigger bleibt weiterhin explizit vertagt ("ein Thema für ein andermal").
