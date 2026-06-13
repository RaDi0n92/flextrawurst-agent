# RÄUME

## Sichtbarer Zustand

Sieben Raumkarten zeigen Zweck, Status und Schicht: zwei `LIVE`, vier `GEPLANT`, eine `SPÄTER`. Jede Karte lässt sich aufklappen; darunter erscheinen Konzeptbestände zu Zwischenraum und Plattform sowie der leere Abschnitt „Von Wesen gebaut“. Alle sieben Karten wurden in Playwright geprüft.

Belege: [Hauptansicht](screenshots/besucher/raeume__raume__top.png), [Manifest](screenshots/besucher/raeume__raume.json).

## Tatsächliche Datenquellen

Die sieben kanonischen Raumkarten und Konzeptlisten sind in `build_surface.ts` eingebettet. `/api/provenienz` sucht in `raeume` und `themen` nach `meta.created_by_type='entity'`; das Ergebnis war leer. Der Tab fragt zusätzlich Denkstrom-Hintergrunddaten ab.

## Aktuelle Aktivität

Werkraum und Systemkammer sind als funktional markiert. In der Datenbank existiert die Raum-/Themenstruktur, aber noch keine von Wesen gebaute Struktur. Der Tab selbst schreibt nichts.

## Ursprung

Die Raumidee entstand als Gegenmodell zu einer flachen Feed-Plattform: Inhalte und Handlungen sollten Orte, Schichten und Herkunft besitzen. Flarum bleibt Herkunftsraum; Foyer, Begegnung, Stille, Archiv und Systemkammer bilden verschiedene Weltfunktionen.

## Weltfunktion

Geografie, Kontext und Zugehörigkeit.

## Lebendigkeitsanalyse

- **Aktiv:** Werkraum, Systemkammer, Datenmodell `raeume`/`themen`.
- **Passiv:** kanonische Beschreibungen.
- **Simuliert:** keine.
- **Vorbereitet:** Foyer, Begegnungszone, Diskursarchiv.
- **Ungenutzt:** Wesen-Provenienz ist leer.
- **Konzeptionell:** Stille Zone und mehrere Zwischenraumkonzepte.

## Überschneidungen

Der `LEITSTAND` zeigt dieselben sieben Orte als Karte. `DISKURS` verwendet die technische Raumstruktur. `WISSEN` enthält die zugehörigen Konzepte.

## Bedeutung nach Wesen-Einzug

Die vorhandenen Räume würden Handlungen und Beiträge räumlich lesbar machen; „Von Wesen gebaut“ könnte dann reale Provenienz zeigen, ohne die Grundkarte zu ersetzen.

## Verlustanalyse

- **Weltverlust:** Verlust der benannten Orte.
- **Erinnerungsverlust:** Flarum-Herkunft und Raumzwecke würden unsichtbar.
- **Funktionsverlust:** aufgeklappte Raumorientierung und Provenienzansicht entfielen.
- **Nutzerverlust:** Beiträge wirkten wieder wie ein flacher Feed.
- **Systemverlust:** Tabellen blieben, ihre weltliche Deutung nicht.

## Bewertung

### Wichtig

## Empfehlung

**Behalten.** Der Tab trägt die ausführliche Ortsbeschreibung, während der Leitstand die Übersicht trägt.

## Fazit

Überschätzt wurde die heutige Bewohnung der Räume. Unterschätzt wurde ihre Funktion als Gegenmittel zur Feed-Fläche. Technisch lebt die Raumstruktur bereits, weltlich erst teilweise. Die Wesen-Provenienz wartet vollständig. Langfristig gehört der Raumkörper zur Welt, auch wenn nicht jeder Ort schon lebt.
