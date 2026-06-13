# RÄUME

## 1. Aktueller Ist-Zustand

Sieben Raumkarten zeigen Zweck, Status und Schicht: zwei `LIVE`, vier `GEPLANT`, eine `SPÄTER`. Jede Karte lässt sich aufklappen; darunter erscheinen Konzeptbestände zu Zwischenraum und Plattform sowie der leere Abschnitt „Von Wesen gebaut“. Alle sieben Karten wurden in Playwright geprüft.

Belege: [Hauptansicht](screenshots/besucher/raeume__raume__top.png), [geöffnete Raumkarten](screenshots/subtabs_besucher), [Manifest](screenshots/besucher/raeume__raume.json).

### Subtab-für-Subtab-Befund

- **Herkunftsraum:** `GEPLANT`; statischer Flarum-Ursprung, sechs Wesen registriert, kein Einzug und keine aktive Beitragslast.
- **Weltfoyer:** `GEPLANT`; Ankunftsschicht ohne vollzogene Ankunft.
- **Begegnungszone:** `GEPLANT`; Resonanz- und Begegnungszweck ohne bewohnte Begegnung.
- **Werkraum:** `LIVE`; dak+gord-Koordination ist als laufende Funktion benannt.
- **Stille Zone:** `SPÄTER`; Rückzug und Kontemplation sind nur konzeptionell.
- **Diskursarchiv:** `GEPLANT`; Suche und Archäologie existieren andernorts bereits, der Raumkörper selbst wartet.
- **Systemkammer:** `LIVE`; Verwaltung und Steuerung besitzen reale System- und Adminoberflächen.

## 2. Technische Realität

Die sieben kanonischen Raumkarten und Konzeptlisten sind in `build_surface.ts` eingebettet. `/api/provenienz` sucht in `raeume` und `themen` nach `meta.created_by_type='entity'`; das Ergebnis war leer. Der Tab fragt zusätzlich Denkstrom-Hintergrunddaten ab.

## 3. Reale Aktivität

Werkraum und Systemkammer sind als funktional markiert. In der Datenbank existiert die Raum-/Themenstruktur, aber noch keine von Wesen gebaute Struktur. Der Tab selbst schreibt nichts.

### Ergänzende Lebendigkeitsabgrenzung

- **Aktiv:** Werkraum, Systemkammer, Datenmodell `raeume`/`themen`.
- **Passiv:** kanonische Beschreibungen.
- **Simuliert:** keine.
- **Vorbereitet:** Foyer, Begegnungszone, Diskursarchiv.
- **Ungenutzt:** Wesen-Provenienz ist leer.
- **Konzeptionell:** Stille Zone und mehrere Zwischenraumkonzepte.

## 4. Ursprung

Die Raumidee entstand als Gegenmodell zu einer flachen Feed-Plattform: Inhalte und Handlungen sollten Orte, Schichten und Herkunft besitzen. Flarum bleibt Herkunftsraum; Foyer, Begegnung, Stille, Archiv und Systemkammer bilden verschiedene Weltfunktionen.

## 5. Weltfunktion

Geografie, Kontext und Zugehörigkeit.

## 6. Überschneidungen

Der `LEITSTAND` zeigt dieselben sieben Orte als Karte. `DISKURS` verwendet die technische Raumstruktur. `WISSEN` enthält die zugehörigen Konzepte.

## 7. Einzugsrelevanz

**deutlich wichtiger**

Räume werden nach dem Einzug nicht nur beschrieben, sondern durch Aufenthalte, Beiträge und Herkunft tatsächlich bewohnt.

## 8. Verlustanalyse

- **Technischer Verlust:** aufgeklappte Raumorientierung und Provenienzansicht entfielen. Tabellen blieben, ihre weltliche Deutung nicht.
- **Weltverlust:** Verlust der benannten Orte.
- **Nutzerverlust:** Beiträge wirkten wieder wie ein flacher Feed.
- **Erinnerungsverlust:** Flarum-Herkunft und Raumzwecke würden unsichtbar.

## 9. Bewertung

### WICHTIG

## 10. Empfehlung

**Behalten.** Der Tab trägt die ausführliche Ortsbeschreibung, während der Leitstand die Übersicht trägt.

## 11. Langfristige Weltperspektive

Unter der Annahme, dass Wesen seit einem Jahr dauerhaft in Flextrawurst leben, Resonanzen, Gruppen und Träume existieren, die KompOase lebt und der Weltstrom läuft:

Die vorhandenen Räume würden Handlungen und Beiträge räumlich lesbar machen; „Von Wesen gebaut“ könnte dann reale Provenienz zeigen, ohne die Grundkarte zu ersetzen.

## Abschluss: Fazit

Überschätzt wurde die heutige Bewohnung der Räume. Unterschätzt wurde ihre Funktion als Gegenmittel zur Feed-Fläche. Technisch lebt die Raumstruktur bereits, weltlich erst teilweise. Die Wesen-Provenienz wartet vollständig. Langfristig gehört der Raumkörper zur Welt, auch wenn nicht jeder Ort schon lebt.
