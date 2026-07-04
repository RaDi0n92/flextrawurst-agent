---
name: codexium2-solarius2-sessions-kontextmeter
description: Session-Konzept (neue Session, alte Sessions lesbar) + Kontextfenster-Anzeige für Codexium2/Solarius2
metadata:
  type: project
tags: [codexium2, solarius2, sessions, kontextfenster, testbed]
status: in-diskussion
datum: 2026-07-04
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

## Scope

Gilt NUR für Codexium2/Solarius2. Codexium/Solarius bleiben bei der aktuellen flachen `chat_history.jsonl` ohne Sessions — siehe `project_codexium2_testbed` in Claudes Memory.

## Was ich verstehe

Aktuell (auch bei Codexium/Solarius): keine Sessions. Nur eine einzige, endlos wachsende History-Datei pro Wesen. Kein Marker, keine Session-ID, kein "neue Session"-Knopf, keine Liste alter Sessions.

Vorbild: Dolphin Mischpult hat ein Session-System (eigene `.jsonl` pro Session unter `/root/werkraum/dolphin_mischpult/sessions/`, Index-Datei, Marker-Zeile `"— Neue Session · <Datum> · <Modell> · <UA> —"` als erste Zeile). Für Codexium2/Solarius2 reicht ein schlankerer Ausschnitt davon — kein Umbenennen/Archivieren/Ghost-Sessions/Papierkorb wie im Mischpult, nur:

**Kontextfenster-Anzeige:** Text-Label wie im Mischpult ("ctx ~X/8192"), geschätzt clientseitig (Zeichen/4 ≈ Token), keine Ampel-Farben (Mischpult hat auch keine).

**Session-Konzept:**
1. Button "Neue Session starten" im Chat-Header.
2. **Vor der Ausführung: Bestätigungsdialog** — muss klar sagen, dass die aktuelle Session danach nur noch lesbar ist, nichts mehr gesendet werden kann. Erst nach Bestätigung wird gewechselt.
3. Beim Wechsel:
   - Marker-Zeile in `chat_history.jsonl` (analog zum Mischpult-Vorbild), die den Sessionwechsel markiert.
   - Automatischer Trigger der (bereits gebauten) Memory-Extraktion auf die gerade beendete Session — das ist die "Geschichte fürs System schreiben, für zukünftige Einsichten".
   - Container wird geleert (passt zum Konzept: Container = was in *diesem* Gespräch akut ist).
4. Alte Sessions bleiben lesbar über eine einfache Liste/Popup — kein Weiterschreiben in ihnen möglich, nur Ansicht.

## Entschieden (2026-07-04)

**Marker-Format:** `{"type":"session_start","ts":"<iso>"}` als eigene Zeile in `chat_history.jsonl`, analog zum Mischpult-Eventformat.

**Aktive Session** = alle Nachrichten NACH dem letzten `session_start`-Marker (bzw. alles seit Anfang, falls noch kein Marker existiert — erste Session). Frühere Abschnitte = alte Sessions.

**Durchsetzung "nur lesbar":** rein client-seitig, kein Server-Lock nötig — `appendHistory()` hängt Nachrichten immer ans Dateiende an, das ist per Definition immer die aktuelle/letzte Session. Es gibt serverseitig keinen Mechanismus "in eine bestimmte Session schreiben", also auch keine Angriffsfläche. Beim Ansehen einer alten Session in der UI wird einfach kein Eingabefeld/Senden-Button angezeigt (nur Lesen), bei der aktuellen Session normal wie gehabt.

