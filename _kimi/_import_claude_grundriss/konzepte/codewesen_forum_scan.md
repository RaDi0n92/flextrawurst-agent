# codewesen_forum_scan.py

Migriert: 2026-07-06

**Was es tut**: Alle 8 Minuten: komplettes Forum analysieren, eigene Gedanken
der Wesen in individuelle, verknüpfte Dateien schreiben (`gedanken/`, `ideen/`,
`meinungen/`, `beitraege/`, mit lebendigem `INDEX.md`).

**Wozu**: Ein strukturiertes, durchsuchbares Gedächtnis-Archiv pro Wesen, getrennt
nach Art des Gedankens — nicht nur ein Forum-Post-Verlauf.

**Migration**: War Streaming (`stream=True`, alle Tokens akkumuliert, kein
Live-Callback nötig) — vereinfacht zu `hauhau_client.chat()` (nicht-streamend),
da das Ergebnis ohnehin erst komplett gebraucht wird.
