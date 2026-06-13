# SPLITTER

## Sichtbarer Zustand

Der Tab zeigt ausschließlich `SPLITTER-AUFNAHMEN · 0` und „Keine Aufnahmen“. Es gibt keine Filter, Karten oder weitere Interaktion.

Belege: [Hauptansicht](screenshots/besucher/splitter__splitter__top.png), [Manifest](screenshots/besucher/splitter__splitter.json).

## Tatsächliche Datenquellen

`GET /api/splitter-aufnahmen?limit=50` liest `splitter_aufnahmen` und verbindet auf `splitter`. Der Endpunkt antwortete HTTP 200. Die eigentliche Splitterphysik liegt in `splitter`, `splitter_verbindungen`, `splitter_knoten`, `keimkoerper` und dem Splitter-Physik-Daemon.

## Aktuelle Aktivität

Es existierten 794 Splitter, aber null `splitter_aufnahmen`. Der Tab bildet daher nicht die aktive Splitterwelt ab, sondern nur einen noch ungenutzten Spezialvorgang.

## Ursprung

Die Ansicht sollte dokumentieren, wer welchen Splitter aus dem Zwischenraum aufgenommen hat und warum. Sie ist Provenienzregister einer künftigen Aneignungsbeziehung.

## Weltfunktion

Aufnahmeprotokoll und Besitzlosigkeits-/Herkunftsspur.

## Lebendigkeitsanalyse

- **Aktiv:** API und Tabellenstruktur.
- **Passiv:** leere Liste.
- **Simuliert:** keine.
- **Vorbereitet:** Aufnahmehandlungen.
- **Ungenutzt:** der gesamte sichtbare Fachvorgang.
- **Konzeptionell:** soziale Bedeutung der Aufnahme.

## Überschneidungen

`KOMPOASE` zeigt aktive Splitter, `ARCHÄOLOGIE` durchsucht sie, `EINSICHT` hat eine Splitterlinse und `WESEN` zeigt Abgabe/Aufnahme je Wesen.

## Bedeutung nach Wesen-Einzug

Der bestehende Inhalt könnte als Provenienzspur realer Aufnahmen Bedeutung gewinnen, bliebe aber ein Teilaspekt des größeren Splitterorgans.

## Verlustanalyse

- **Weltverlust:** aktuell keiner.
- **Erinnerungsverlust:** künftige Aufnahmeprovenienz hätte keine eigene Liste.
- **Funktionsverlust:** spezielle Aufnahmenübersicht.
- **Nutzerverlust:** gering.
- **Systemverlust:** keiner; Tabelle und andere Ansichten blieben.

## Bewertung

### Übergangslösung

## Empfehlung

**Zusammenlegen.** Als eigener Tab ist ein einzelnes leeres Register zu schmal; sein Befund gehört zur KompOase oder Archäologie.

## Fazit

Überschätzt wurde die Gleichsetzung dieses Tabs mit der lebenden Splitterphysik. Unterschätzt wurde, wie eng er tatsächlich nur `splitter_aufnahmen` abbildet. Die Splitterwelt lebt, dieser Vorgang nicht. Nach dem Einzug kann die Provenienz wichtig werden. Ein eigenes Kernorgan ist der Tab nicht.
