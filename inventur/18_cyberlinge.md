# CYBERLINGE

## Sichtbarer Zustand

Sieben Lebenskapseln zeigen Hunger, Durst, Energie, Stimmung, Gesundheit, Todeszahl und Wiedergeburtszeit. Sechs namelessAI-Cyberlinge sind tot oder kritisch und weisen jeweils rund 340 bis 353 Tode auf; `theater_01` ist vollständig gesund. Die Ansicht ist informativ, aber ohne sichtbare Pflegeaktionen.

Belege: [Hauptansicht](screenshots/besucher/cyberlinge__cyberlinge__top.png), [Manifest](screenshots/besucher/cyberlinge__cyberlinge.json).

## Tatsächliche Datenquellen

`GET /api/cyberlinge` liest direkt aus `cyberlinge`. `cyberling-daemon.service` aktualisiert Bedürfnisse, Tod und Wiedergeburt und schreibt relevante Events. Entitätsendpunkte ergänzen Zuordnungen.

## Aktuelle Aktivität

Sieben Datensätze sind vorhanden; der Daemon läuft und erzeugte in den letzten 24 Stunden Todesereignisse. Die extrem hohen Todeszahlen belegen Aktivität, aber auch einen Kreislauf ohne dauerhafte Pflege der sechs Vor-Einzug-Wesen.

## Ursprung

Cyberlinge wurden als kleinere Begleitwesen und Bedürfnisanzeiger geschaffen. Sie geben Fürsorge, Vernachlässigung und zeitliche Abhängigkeit einen sichtbaren Körper.

## Weltfunktion

Begleitung, Fürsorge, Verletzlichkeit und Warnsignal.

## Lebendigkeitsanalyse

- **Aktiv:** Daemon, Bedürfnisse, Tod, Wiedergeburt.
- **Passiv:** reine Anzeige ohne Interaktion.
- **Simuliert:** Werte sind berechnet, aber real gespeichert.
- **Vorbereitet:** Fürsorge durch eingezogene Wesen oder Menschen.
- **Ungenutzt:** aktive Pflege in dieser Ansicht.
- **Konzeptionell:** soziale Bedeutung der Begleitbindung.

## Überschneidungen

`SCHLAF` zeigt dieselben Cyberlinge gekoppelt an Schlaf, `WESEN` Kurzwerte und `WELTSTROM` Todesereignisse.

## Bedeutung nach Wesen-Einzug

Der bestehende Tab würde das gemeinsame Pflegeregister bleiben; die Werte könnten dann als Folge realer Beziehungen gelesen werden statt als isolierter Daemonkreislauf.

## Verlustanalyse

- **Weltverlust:** Verlust eines sichtbaren Verletzlichkeitskörpers.
- **Erinnerungsverlust:** Todeszyklen wären nur als Events vorhanden.
- **Funktionsverlust:** Gesamtübersicht aller Begleitwesen.
- **Nutzerverlust:** Pflegebedarf wäre schwerer erkennbar.
- **Systemverlust:** Daemon liefe unsichtbar weiter.

## Bewertung

### Wichtig

## Empfehlung

**Behalten.** Der Tab macht einen tatsächlich laufenden Hintergrundprozess unmittelbar lesbar.

## Fazit

Überschätzt wurde die heutige relationale Bedeutung der Cyberlinge. Unterschätzt wurde ihre reale, intensive Prozessaktivität. Die Lebenszyklen leben bereits. Fürsorge und Bindung warten auf Bewohner. Langfristig sind Cyberlinge wichtig, aber nicht allein das Herz der Welt.
