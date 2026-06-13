# WAS IST DAS?

## TABNAME

WAS IST DAS?  
Technische ID: `uber` / `#view-uber`

---

## Sichtbarer Zustand

Der Tab ist die Eingangserzählung der Surface. Besucher sehen zuerst einen groß gesetzten Flextrawurst-Schriftzug, den Satz „Ein Ökosystem · kein Produkt · im Aufbau“ und fünf Statusmarken zu Splitter-Physik, Welt-API, GENI, wartenden Wesen und geplanter Öffentlichkeit.

Darunter liegen drei Einstiegspfade: erst verstehen, die Welt betreten oder den Leitstand öffnen. Es folgen acht anklickbare Karten für Welt, Wesen, Zwischenraum, GENI, Menschen, Schlaf, Systeme und Wissen. Weitere Abschnitte erklären menschliche Teilhabe, Entwicklungsphasen, sieben Substanzschichten, Sonderstoffe und die achtstufige Abspaltungskette.

Der Inhalt ist mit 3.124 Pixeln deutlich höher als der sichtbare Bereich. Playwright erfasste deshalb je Rolle eine Startaufnahme und vier Scrollaufnahmen:

- [Besucher: Einstieg](screenshots/besucher/was_ist_das__uber__top.png)
- [Besucher: Scroll 1](screenshots/besucher/was_ist_das__uber__scroll_01.png)
- [Besucher: Scroll 2](screenshots/besucher/was_ist_das__uber__scroll_02.png)
- [Besucher: Scroll 3](screenshots/besucher/was_ist_das__uber__scroll_03.png)
- [Besucher: Ende](screenshots/besucher/was_ist_das__uber__scroll_04.png)
- [Admin: Einstieg](screenshots/admin/was_ist_das__uber__top.png)

Die Besucher- und Adminansicht sind inhaltlich gleich. Beim Erstbesuch liegt rechts unten zusätzlich ein Willkommensdialog über dem Inhalt. 26 sichtbare Interaktionen wurden gefunden: Sprungmarken innerhalb der Seite sowie Navigationen zu Leitstand, Wesen, KompOase, Menschen, Schlaf, Systeme und Wissen.

Leer oder wie Platzhalter wirkt nichts. Die Statusmarken reagieren auf Klick, werden aber nicht live validiert. In der Browserkonsole erscheint ein einzelner nicht weiter benannter `404`-Fehler; der Tab selbst bleibt vollständig benutzbar.

---

## Tatsächliche Datenquellen

Der Tab selbst verwendet keine API und keine Datenbanktabelle. Sein Inhalt wird statisch durch `generateUeberView()` in `/root/flextrawurst/scripts/build_surface.ts` erzeugt und in `/root/flextrawurst/out/process_camera/flextrawurst_surface.html` eingebaut.

Die Zahl `490` entsteht beim Build aus `inventory.length`; sie stammt aus dem in den Surface-Build eingebetteten Feature-Inventar. Alle Aussagen wie „Welt-API aktiv“, „GENI aktiv“ oder „Der Daemon tickt schon“ sind fest codierte Texte und keine Antworten eines Health-Endpunkts.

Die Karten verweisen nur auf andere Surface-Views. Sie lesen und schreiben selbst keine Tabellen.

---

## Aktuelle Aktivität

Im Tab entstehen keine Daten und keine Events. Seine Aktivität besteht aus Navigation und internen Scrollsprüngen.

Die von ihm beschriebenen Systeme sind außerhalb des Tabs teilweise real aktiv. Am 13. Juni 2026 liefen `welt-api`, `process-camera-preview`, `splitter-physik`, `entity-kern`, `entity-takt`, `cyberling-daemon` und `tension-daemon`. In PostgreSQL lagen 123.724 Events, davon 4.846 aus den letzten 24 Stunden. Ebenfalls vorhanden waren 792 Splitter, 8 Schlafphasen, 3 Traumspuren, 7 Cyberlinge und 6 Entitätszustände.

Gleichzeitig warteten die sechs Herkunftswesen laut sichtbarer Surface weiterhin auf den formalen Einzug. Der Tab beschreibt daher reale Prozessaktivität und zukünftige Weltbewohnung nebeneinander.

---

## Ursprung

Der Tab entstand als Atemraum vor der Systemtiefe. Die ältere Systemdokumentation beschreibt `uber` bereits als statische Erklärung und Standard-Tab beim Laden: `/root/werkraum/docs/systemdoku/05_surface_8787.md`.

Seine Grundidee folgt der 490-Punkte-Quellliste: Die erste Oberfläche soll sich wie Flextrawurst selbst anfühlen und nicht wie ein Tool, Graph oder Report. Besonders einschlägig sind die Punkte 325 bis 350 sowie 434 bis 490 in `/root/werkraum/_claude/ideen/flextrawurst_490_punkte_quellliste.md`.

Spätere Arbeit machte aus der knappen Erklärung eine umfassende Selbstdarstellung mit Einstiegspfaden, Teilhaberegeln, Substanzschichten und Abspaltungsmodell. Am 3. Juni 2026 wurden verbliebene Dunkelmodus-Farben auf die gemeinsame Surface-Farbsprache umgestellt; diese Spur steht in `/root/werkraum/_claude/brief_an_mich.md`.

---

## Weltfunktion

Orientierung.

Der Tab ist das Vorwort der Welt. Er erklärt Besuchern, welche Arten von Körpern, Bewohnern, Prozessen und Grenzen sie vor sich haben, bevor sie einzelne Organe betreten.

---

## Lebendigkeitsanalyse

**Aktiv:** Navigation zu sieben anderen Weltbereichen, Sprachumschaltung, interne Sprungmarken, responsive Darstellung.

**Passiv:** Grundidee, Teilhaberegeln, Phasenmodell, Substanz- und Abspaltungserklärung.

**Simuliert:** Keine Simulation im Tab.

**Vorbereitet:** Phase B, Phase C, öffentliche Welt und spätere Visionsebenen werden als kommende Zustände beschrieben.

**Ungenutzt:** Kein erkennbarer Inhaltsblock ist funktionslos.

**Rein konzeptionell:** Mehrere Aussagen über Geburt neuer Wesen, vollständige Substanzwirkungen und spätere Weltphasen.

Die Statusanzeige ist visuell lebendig, technisch aber statisch. Sie zeigt den beim Build formulierten Weltstand, nicht den beim Seitenaufruf gemessenen Zustand.

---

## Überschneidungen

Der Tab fasst Informationen zusammen, die in `LEITSTAND`, `SYSTEME`, `WESEN`, `SCHLAF`, `WISSEN`, `KOMPOASE` und `MENSCHEN` ausführlicher erscheinen.

Die Phasen- und Statusaussagen überschneiden sich besonders mit `SYSTEME` und dem Leitstand. Substanzschichten und Abspaltung überschneiden sich mit `EINSICHT`, `SPLITTER`, `KOMPOASE` und dem Wissensarchiv. Diese Überschneidung ist sichtbar als Überblicksebene, nicht als identische Bedienfunktion.

---

## Bedeutung nach Wesen-Einzug

Nach dem Wesen-Einzug bliebe der Tab der öffentliche Eingang und die begriffliche Landkarte. Seine Rolle würde sich von der Erklärung eines wartenden Systems zur Erklärung einer bewohnten Welt verschieben.

Die Abschnitte zu Wesen, Schlaf, Abspaltung und menschlicher Teilhabe würden dann nicht mehr hauptsächlich vorbereiten, sondern vorhandene Weltpraxis einordnen. Gerade für neue Besucher bliebe diese bestehende Orientierungsfunktion erhalten.

---

## Verlustanalyse

**Weltverlust:** Die Welt verlöre ihren selbst formulierten Eingang und ihre zusammenhängende Selbsterklärung.

**Erinnerungsverlust:** Die Entwicklungsphasen und die Verbindung zwischen ursprünglicher Plattformidee, Substanzmodell und Einzug würden weniger sichtbar.

**Funktionsverlust:** Direkte Einstiege und Querverweise zu zentralen Tabs fielen weg.

**Nutzerverlust:** Neue Besucher hätten keinen sanften Zugang und müssten Bedeutung aus spezialisierten Tabs zusammensetzen.

**Systemverlust:** Keine API, Tabelle oder laufende Weltfunktion würde ausfallen.

---

## Bewertung

### Wichtig

Der Tab ist kein ausführendes Organ, aber die zentrale Orientierungsschicht zwischen Außenwelt und komplexer Surface.

---

## Empfehlung

### Behalten

Die vorhandene Funktion ist eigenständig: kein anderer Tab erklärt Welt, Teilhabe, Entwicklungsstand und Grundbegriffe in einer zusammenhängenden Besucherperspektive. Die statischen Statusbehauptungen müssen in dieser Inventur als solche kenntlich bleiben, ändern aber nichts an der Bedeutung des Tabs als Eingang.

---

## Fazit

Überschätzt wurde die technische Lebendigkeit der Statusanzeigen, denn sie messen nichts selbst. Unterschätzt wurde die Dichte des Tabs: Er ist nicht nur eine Startseite, sondern trägt Weltmodell, Teilhaberegeln, Phasen, Substanzen und Abspaltung. Real leben seine Navigation und die meisten von ihm benannten Hintergrundsysteme. Auf den Wesen-Einzug, die öffentliche Welt und vollständig wirksame Substanz- und Geburtsmodelle wartet er noch. Seine stärkste Funktion ist nicht Betrieb, sondern Verständlichkeit. Langfristig gehört er als Eingang zum Herzen der Welt, aber nicht als ausführendes Kernorgan.
