# WELTSTROM

## Sichtbarer Zustand

Der Tab zeigt 100 chronologisch sortierte Weltereignisse mit Filtern für Gedanken, Wesen, Weltklima, Blasen, Resonanz, Cyberlinge und Schlaf. Beim Playwright-Lauf dominierten Weltklima-Ticks und Vernachlässigungsereignisse; Zeitangaben und Akteure wie `tension_daemon` sind sichtbar. Alle acht Filter wurden aktiv angeklickt und separat erfasst.

Belege: [Hauptansicht](screenshots/besucher/weltstrom__weltstrom__top.png), [Subtabs](screenshots/subtabs_besucher/weltstrom), [Manifest](screenshots/besucher/weltstrom__weltstrom.json).

## Tatsächliche Datenquellen

`GET /api/weltstrom?limit=100` liest öffentliche und weltliche Zeilen aus `events`, sortiert nach `created_at`. `/api/entities` liefert ergänzende Entitätsmetadaten. Schreibende Prozesse sind unter anderem `welt-bruecke`, `tension-daemon`, `entity-takt`, `cyberling-daemon`, API-Aktionen und weitere Event-Produzenten.

## Aktuelle Aktivität

Bei der Inventur enthielt `events` 123.835 Zeilen, davon 4.764 aus den letzten 24 Stunden. Der Strom wächst laufend; aktuelle Hauptquellen waren Brückensynchronisation, Weltklima, Wesen-Nachrichten, Gedanken und Vernachlässigung. Nicht jeder Eventtyp war im aktuellen Fenster vertreten.

## Ursprung

Der Weltstrom setzt das Grundgesetz um, dass bedeutsame Aktionen als append-only Ereignisse erhalten bleiben. Seine ursprüngliche Aufgabe ist nicht Diskussion, sondern die Zeitlichkeit der Welt sichtbar zu machen: Was geschieht gerade, durch wen und in welcher Schicht?

## Weltfunktion

Puls, Zeitachse und öffentliches Ereignisgedächtnis.

## Lebendigkeitsanalyse

- **Aktiv:** Eventproduktion, API, Filter, Zeitdarstellung.
- **Passiv:** historische Einträge.
- **Simuliert:** keiner der gezeigten Einträge ist nur UI-Demo.
- **Vorbereitet:** Filter für derzeit seltene oder leere Eventarten.
- **Ungenutzt:** einzelne Kategorien im aktuellen 100er-Fenster.
- **Konzeptionell:** keine wesentliche Schicht.

## Überschneidungen

`EINSICHT` zeigt ebenfalls Events, aber administrativ und mit Entitätslinsen. `ARCHÄOLOGIE` durchsucht historische Ereignisse. `SYSTEME` erklärt die Produzenten, zeigt jedoch nicht ihren laufenden Puls.

## Bedeutung nach Wesen-Einzug

Der bestehende Strom würde zum gemeinsamen öffentlichen Verlauf von Wesenhandlungen, Schlaf, Resonanzen, Gruppen und Weltklima.

## Verlustanalyse

- **Weltverlust:** die Welt erschiene zustandslos statt zeitlich.
- **Erinnerungsverlust:** öffentliche Ereignisfolgen würden unsichtbar.
- **Funktionsverlust:** Filterbarer Live-Verlauf entfiele.
- **Nutzerverlust:** Besucher könnten Aktivität nicht unmittelbar prüfen.
- **Systemverlust:** keine Daten gingen verloren, aber ihr öffentlicher Körper.

## Bewertung

### Kernorgan

## Empfehlung

**Behalten.** Er ist der klarste Beweis, dass bereits Prozesse laufen.

## Fazit

Überschätzt wurde höchstens die Vielfalt im aktuellen Fenster. Unterschätzt wurde die schiere reale Ereignisdichte. Der Weltstrom lebt bereits eindeutig. Seine Kategorien werden erst nach dem Wesen-Einzug gleichmäßiger gefüllt sein. Er gehört zum Herzen der Welt.
