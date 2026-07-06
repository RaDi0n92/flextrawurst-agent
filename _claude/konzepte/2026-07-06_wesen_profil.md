# wesen_profil.html

Neu dokumentiert: 2026-07-06 (Datei existierte vorher schon, war aber noch nicht
in den Konzept-Dokumenten erfasst — Anlass war der Container-Umbau)

**Was es tut**: Profilseite pro Charakter (alle 4 Spawner), erreichbar über
`/{spawner}/{name}/profil` — Identität (`wesen.md`), Aliase, alle weiteren
MD-Felder (Weltlore, Beispiel-Dialoge etc., je nach Spawner unterschiedliche
Feldliste), Memory, Container, Löschen (Papierkorb, kein echtes Löschen).

**Wozu**: Der einzige Ort, an dem strukturierte Daten (nicht nur der laufende
Chat) direkt bearbeitbar sind — Textfelder, Memory-Kategorien, Container.

## Nachtrag 2026-07-06 — Container-Umbau auf Mehrfach-Container-Sammlung

Der komplette Container-Abschnitt wurde neu gebaut (siehe Konzept-Nachtrag in
`serve_process_camera_preview.md` für die volle Begründung/Datenstruktur).
Vorher: eine feste Liste (`contData.eintraege`), unterschiedliches Anzeigeformat
je nachdem ob Testbed-Spawner (Pin-Format) oder nicht (Key/Val-Format mit eigenem
Eingabeformular `#cont-key`/`#cont-val`).

Jetzt: `contData = { container: [...] }`, eine Karte pro Container mit:
- Name-Eingabefeld (Umbenennen bei `change`-Event, `PUT .../container/:id/name`)
- Aktiv-Checkbox (`PATCH .../container/:id/aktiv`)
- "Container löschen"-Button (mit Bestätigungsdialog, `DELETE .../container/:id`)
- Liste der Einträge (Text + optionaler Kommentar + Quelle + Zeitstempel, `✕
  entfernen`-Button pro Eintrag → `DELETE .../container/:id/eintrag/:eintragId`)
- Eigenes "+ Eintrag hinzufügen"-Eingabefeld pro Container (`POST
  .../container/:id/pin`)

Neuer Container: einfaches Namensfeld unten im Abschnitt + "+ Container anlegen"-
Button (`POST .../container/neu`) — auf Daniels Wunsch "einfach hinzufügbar", an
der Stelle wo die alte Container-Verwaltung schon lebte.

Budget-Anzeige (`CONTAINER_BUDGET` = 5555) summiert jetzt über ALLE Container
zusammen, nicht mehr pro Container getrennt — passend zum geteilten Gesamtbudget
im Backend.

Die alte `IS_TESTBED`-Unterscheidung für Container ist komplett weg — Container
gelten jetzt einheitlich für alle 4 Spawner (Daniels ausdrücklicher Wunsch).
Memory bleibt unverändert testbed-spezifisch (nicht angefasst).

**Getestet**: Container anlegen/pinnen/löschen live gegen `solarius/KrEaPPy`
(regulärer, nicht-Testbed-Charakter) durchgespielt — funktioniert, Testdaten
danach wieder entfernt.
