# dak+gord-system – Architektur heute

## 1. Einstieg
Der zentrale Einstieg ist:
- `starte_dak_gord_system.py`

Er übernimmt aktuell:
- Chatloop
- Dateibefehle
- Fokus-/Anschlusslogik
- Modellaufrufe
- periodische Status-/Neugierprüfung

## 2. Dateiarbeit
Der Agent kann aktuell:
- Dateinamen auflösen
- Dateien lesen
- Fokus auf eine Datei legen
- Anschlussfragen auf diese Datei beziehen

## 3. Gedächtnis
Pro gelesener Datei entsteht eine `.agent.md`.

Diese enthält:
- stabilen Gesamtstand
- aktuellen Fokus
- Verlauf älterer Lesespuren und Anschlussantworten

## 4. Verdichtung
`verdichtung.py` erzeugt strukturierte Verdichtungen aus Dateiauszügen.

## 5. Anschlusskontext
`anschlusskontext.py` hält fest:
- zuletzt relevante Datei
- Textstück
- Offset
- Nachfrage-Tiefe
- Fokuskontext

## 6. Agentdateien
`agentdateien.py` baut und pflegt das Dateigedächtnis:
- Dossierkopf
- stabiler Gesamtstand
- aktueller Fokus
- Verlauf

## 7. Neugier
`neugierkern.py` erzeugt:
- Werkraum-Neugier
- Vision-Zyklus

`neugier_ticker.py` führt diese Logik entkoppelt vom Chat aus.

## 8. Hintergrundbetrieb
Systemd-Timer:
- `dak-neugier.timer`
- `dak-neugier.service`

Zweck:
- periodische Neugierläufe unabhängig vom Chat

## 9. Spuren und Logs
Wichtige Spuren:
- Wochenlog
- `neugier_ticker.log`
- Verdichtungsspuren
- Agentdateien

## 10. Modellschicht
Antwort- und Verdichtungslogik läuft aktuell über lokale Modellaufrufe.

## 11. Aktueller Reifegrad
Das System ist heute:
- lokaler Single-Agent-Kern
- mit Dateigedächtnis
- mit Hintergrundneugier
- mit Spuren und Dossiers
- aber noch ohne saubere Task-Engine, Approval-Schicht und Eval-System
