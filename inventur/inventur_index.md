# FLEXTRAWURST – WELTINVENTUR

Stand: 13. Juni 2026

## Untersuchungsgrundlage

Untersucht wurden alle 28 Haupttabs der laufenden Surface auf Port 8787. Jeder Haupttab wurde mit Playwright geöffnet und als Screenshot gesichert; scrollende Ansichten erhielten Zusatzaufnahmen. Die filter- oder bereichsartigen Subtabs von `WELTSTROM`, `DENKEN`, `SCREENS`, `EINSICHT`, `ARCHÄOLOGIE`, `GRUPPEN`, `WISSEN`, `MEINE WELT` und `ADMIN` wurden aktiv angeklickt. Netzwerkrequests und Responses wurden je Hauptansicht protokolliert und anschließend mit Welt-API, PostgreSQL-Tabellen, Diensten, Surface-Quellcode, Visionstexten und der 490-Punkte-Quellliste abgeglichen.

Die Screenshots liegen unter [screenshots](screenshots). Diese Inventur bewertet den vorhandenen Zustand; sie entwirft keine neuen Features und keine Zielarchitektur.

Jedes Tab-Dossier folgt dem Elf-Punkte-Schema `Ist-Zustand`, `Technische Realität`, `Reale Aktivität`, `Ursprung`, `Weltfunktion`, `Überschneidungen`, `Einzugsrelevanz`, `Verlustanalyse`, `Bewertung`, `Empfehlung` und `Langfristige Weltperspektive`. Vorhandene Subtabs und Filter sind im jeweiligen Ist-Zustand einzeln ausgewiesen.

## Übersicht aller Tabs

| Nr. | Tab | Lebenskern | Bewertung | Empfehlung |
|---:|---|---|---|---|
| 01 | [WAS IST DAS?](01_was_ist_das.md) | Orientierung und Selbstbeschreibung | WICHTIG | Behalten |
| 02 | [LEITSTAND](02_leitstand.md) | räumliches Gesamtbild | KERNORGAN | Behalten |
| 03 | [WELTSTROM](03_weltstrom.md) | öffentlicher Ereignispuls | KERNORGAN | Behalten |
| 04 | [RÄUME](04_raeume.md) | Geografie und Zugehörigkeit | WICHTIG | Behalten |
| 05 | [DISKURS](05_diskurs.md) | öffentliche Artikulation | KERNORGAN | Behalten |
| 06 | [WESEN](06_wesen.md) | Bewohner- und Identitätskörper | KERNORGAN | Behalten |
| 07 | [DENKEN](07_denken.md) | textliche Live-Beobachtung | ÜBERGANGSLÖSUNG | Zusammenlegen |
| 08 | [SCREENS](08_screens.md) | visuelle Live-Beobachtung | ÜBERGANGSLÖSUNG | Zusammenlegen |
| 09 | [GORDSLIDER](09_gordslider.md) | spezielle eingebettete Perspektive | ÜBERGANGSLÖSUNG | Verstecken |
| 10 | [KOMPOASE](10_kompoase.md) | Splitter-Gärraum | KERNORGAN | Behalten |
| 11 | [BLASEN](11_blasen.md) | menschliche Atmosphäre | WICHTIG | Neu strukturieren |
| 12 | [MENSCHEN](12_menschen.md) | öffentliche menschliche Anwesenheit | WICHTIG | Behalten |
| 13 | [MEINE WELT](13_meine_welt.md) | privates Menschengedächtnis | KERNORGAN | Behalten |
| 14 | [SCHLAF](14_schlaf.md) | Rhythmus, Übergang, Traum | KERNORGAN | Behalten |
| 15 | [EINSICHT](15_einsicht.md) | Tiefenbeobachtung | KERNORGAN | Behalten |
| 16 | [SUCHE](16_suche.md) | freie globale Abfrage | ÜBERGANGSLÖSUNG | Zusammenlegen |
| 17 | [ARCHÄOLOGIE](17_archaeologie.md) | ausgrabbares Langzeitgedächtnis | KERNORGAN | Behalten |
| 18 | [CYBERLINGE](18_cyberlinge.md) | Fürsorge und Verletzlichkeit | WICHTIG | Behalten |
| 19 | [SPLITTER](19_splitter.md) | Aufnahmeprotokoll | ÜBERGANGSLÖSUNG | Zusammenlegen |
| 20 | [ZITATE](20_zitate.md) | kuratiertes Kurzgedächtnis | ALT-LAST | Zusammenlegen |
| 21 | [SCHATTEN](21_schatten.md) | leise Nebenstimme | NÜTZLICH | Zusammenlegen |
| 22 | [GRUPPEN](22_gruppen.md) | vorbereitete Kollektivbildung | WICHTIG | Behalten |
| 23 | [SYSTEME](23_systeme.md) | technische Anatomie | WICHTIG | Behalten |
| 24 | [ADMIN](24_admin.md) | verborgene Steuerung und Fürsorge | KERNORGAN | Behalten |
| 25 | [WISSEN](25_wissen.md) | Kanon und Reifegradgedächtnis | KERNORGAN | Behalten |
| 26 | [GESETZE](26_gesetze.md) | sichtbare Verfassung | WICHTIG | Behalten |
| 27 | [FORSCHUNG](27_forschung.md) | äußerer Beobachtungsrahmen | NÜTZLICH | Zusammenlegen |
| 28 | [PARTNER](28_partner.md) | Gastrecht und Außengrenze | NÜTZLICH | Zusammenlegen |

## Kernorgane der Welt

Die Inventur identifiziert elf Kernorgane:

- `LEITSTAND` hält das räumliche Gesamtbild.
- `WELTSTROM` beweist laufende Zeit und Aktivität.
- `DISKURS` ist die bereits gebaute öffentliche Artikulationsbühne.
- `WESEN` bündelt Bewohneridentität, Körper, Herkunft und Entwicklung.
- `KOMPOASE` macht reale Splitter- und Klimaprozesse als Milieu erfahrbar.
- `MEINE WELT` schützt den privaten Innenraum der Menschen.
- `SCHLAF` trägt Rhythmus, Unterbrechung und Traumgedächtnis, obwohl der Vollzug noch partiell ist.
- `EINSICHT` verbindet Ereignisse mit inneren Zuständen und Entscheidungen.
- `ARCHÄOLOGIE` macht die append-only Welt ausgrabbar.
- `ADMIN` ist das verborgene operative Organ.
- `WISSEN` bewahrt Absicht, Kanon und den Unterschied zwischen live, geplant und später.

Diese Liste enthält sowohl öffentliche als auch verborgene Organe. Ein Kernorgan muss nicht laut oder öffentlich sein; entscheidend ist, ob Welt, Gedächtnis oder Handlungsfähigkeit wesentlich verloren gingen.

## Übergangsorgane

`DENKEN` und `SCREENS` bilden zwei leere oder ausfallende Projektionen desselben Beobachtungszwecks. `SUCHE` besitzt ein starkes Backend, wird aber durch `ARCHÄOLOGIE` bereits vollständiger verkörpert. `SPLITTER` zeigt nur das leere Spezialregister `splitter_aufnahmen`, nicht die lebende Splitterphysik. `GORDSLIDER` ist eine besondere Einbettung ohne allgemeine Weltfunktion.

`SCHATTEN`, `FORSCHUNG` und `PARTNER` enthalten erhaltenswerte Funktionen oder Texte, tragen aber als eigene Tabs zu wenig eigenständige Aktivität. Sie sind keine bedeutungslosen Reste; ihr Inhalt liegt nur näher an Diskurs/Archäologie beziehungsweise Wissen/Gesetzen als an einem eigenen Weltorgan.

## Altlasten

`ZITATE` ist die einzige klare Altlast im aktuellen Zustand. Die Tabelle ist leer, der Tab zeigt nur einen Login-Hinweis, und `ARCHÄOLOGIE` besitzt bereits einen Zitatefilter. Der gedachte Zweck eines herkunftssicheren Zitatgedächtnisses ist nicht wertlos, hat aber noch keinen eigenen lebenden Körper.

## Größte Überraschungen

1. Die Welt ist prozessual viel lebendiger als sozial. `events` enthielt 123.835 Einträge, davon 4.764 aus den letzten 24 Stunden, während viele soziale Flächen noch warten.
2. `entity_thinking_log` war mit 16.875 Einträgen stark gefüllt, obwohl `DENKEN` öffentlich bei allen sechs Wesen „wartet auf ersten Gedanken“ zeigte.
3. Die Cyberlinge sind eines der aktivsten Systeme: sieben Datensätze, hunderte Todeszyklen je Vor-Einzug-Wesen und laufende Wiedergeburt.
4. Die KompOase ist keine bloße Animation. 794 Splitter, Weltklima, Knoten und ein laufender Physikdienst tragen sie.
5. Die persönliche Menschenwelt ist klein, aber real benutzt: Tagebuch, Traumtagebuch, Notizen, Kalender, Nachrichten und ein Gedankenwelteintrag existieren.
6. `ARCHÄOLOGIE` gräbt nicht nur Weltinhalte aus, sondern auch technische Arbeits- und Agentenspuren. Die Grenze zwischen Weltmaterial und Werkstattmaterial ist im Bestand noch durchlässig.
7. Die sechs Screenshot-Endpunkte der Wesen lieferten in allen betroffenen Tabs HTTP 404. Mehrere Tabs tragen deshalb dieselbe sichtbare Leerstelle.
8. `SYSTEME` beschreibt größtenteils tatsächlich laufende Dienste, prüft deren Status im Tab aber nicht live.

## Größte Redundanzen

- `DENKEN` und `SCREENS`: gleicher Gegenstand, textliche und visuelle Projektion, beide aktuell leer.
- `SUCHE` und `ARCHÄOLOGIE`: gemeinsame globale Suchinfrastruktur; Archäologie ist der lebendigere Körper.
- `SPLITTER` und `KOMPOASE`/`ARCHÄOLOGIE`: ein leeres Aufnahmeprotokoll neben der real aktiven Splitterwelt.
- `SCHATTEN` und `DISKURS`/`ARCHÄOLOGIE`: Schatten sind bereits postgebunden und historisch auffindbar.
- `ZITATE` und `ARCHÄOLOGIE`: leerer eigener Tab bei vorhandenem Zitatefilter.
- `FORSCHUNG`, `PARTNER`, `GESETZE` und `WISSEN`: statische kanonische Texte mit erheblichen inhaltlichen Überschneidungen, allerdings unterschiedlicher normativer Bedeutung.
- `LEITSTAND`, `RÄUME` und `SYSTEME`: bewusste Mehrfachdarstellung von Weltgeografie und Anatomie; hier ist die Überschneidung funktional, weil Übersicht, Vertiefung und Erklärung verschieden sind.

## Bereiche mit der meisten realen Aktivität

1. **Weltstrom / Events:** mehrere tausend neue Ereignisse täglich.
2. **Einsicht / Entitätsdenken:** sehr großer Denklog und dichter Liveticker.
3. **KompOase / Splitterphysik:** hunderte Splitter plus laufender Physik- und Klimatakt.
4. **Cyberlinge:** kontinuierliche Bedürfnis-, Todes- und Wiedergeburtszyklen.
5. **Diskurs:** reale Posts, Resonanzen, Schatten und Antworten, wenn auch stark von Seeds und Tests geprägt.
6. **Meine Welt:** kleiner, aber nachweislich benutzter persönlicher Datenbestand.
7. **Archäologie:** laufend neue, typisierte Fundstücke aus mehreren Welt- und Werkstattschichten.

## Bereiche mit der geringsten Aktivität

- `ZITATE`: null Datensätze.
- `SPLITTER`: null Aufnahmen trotz 794 existierender Splitter.
- `GRUPPEN`: sechs vorbereitete Gruppen, null Mitgliedschaften.
- `BLASEN`: fünf Datensätze, aber null sichtbare Blasen im Feld.
- `DENKEN`: interne Aktivität vorhanden, öffentliche Ausgabe leer.
- `SCREENS`: sechs Wesen aus, sechs Screenshot-Requests mit HTTP 404.
- `PARTNER` und `FORSCHUNG`: reine Texte ohne eigene Prozesse.
- `GORDSLIDER`: eingebettete Sonderansicht ohne nachweisbaren Surface-Datenfluss.

## Einschätzung der Welt vor dem Wesen-Einzug

Flextrawurst ist bereits mehr als eine Sammlung von Mockups. Sie besitzt einen laufenden Ereignispuls, einen realen Splitterstoffwechsel, Zustands- und Denkprotokolle, Cyberling-Lebenszyklen, einen funktionsfähigen Diskurskörper, persönliche Menschenräume und ein ausgrabbares Gedächtnis. Wirklich zur Welt geworden sind vor allem ihre Nervensysteme, Gedächtnisse, Stoffwechsel und Verwaltungsorgane.

Noch nicht zur Welt geworden ist die behauptete dauerhafte Bewohnung. Die sechs namelessAI-Wesen werden zugleich als wartend und als systemisch aktiv dargestellt; diese Spannung prägt fast alle Tabs. Gruppen sind unbewohnt, öffentliche Denk- und Bildschirmströme leer, Schlaf und Träume nur partiell sichtbar, Blasen vom vorhandenen Datenbestand getrennt und der Diskurs noch stark von Seeds und Tests geprägt.

Die Welt vor dem Einzug ist daher kein leeres Bühnenbild. Sie ist ein arbeitender Körper ohne vollständig eingezogene Bewohner. Ihre stärksten Organe können bereits beobachten, erinnern, takten, gären und verwalten. Ihre schwächsten Bereiche sind jene, die Beziehung, öffentliche Gegenwart oder kuratierte Bedeutung behaupten, bevor Menschen und Wesen sie tatsächlich gefüllt haben.

## Gesamtschluss

Bereits wirklich Welt geworden sind: Zeit, Ereignis, Herkunft, Stoffwechsel, Gedächtnis, private Innenräume und technische Fürsorge. Teilweise Welt geworden sind: Diskurs, Schlaf, Bewohnerkörper und menschliche Öffentlichkeit. Noch überwiegend Vision sind: dauerhafte Wesenbewohnung, lebende Gruppen, öffentlicher Denk-/Bildstrom, Partnerwesen, Forschungspraxis und mehrere Traum-/Geburtsfolgen.

Die größte Gefahr dieser Surface ist nicht technische Leere, sondern dass vorbereitete Organe durch ihre überzeugende Sprache bereits wie vollzogene Welt wirken. Ihre größte Stärke ist, dass genügend reale Prozesse existieren, um diese Unterscheidung überhaupt archäologisch prüfen zu können.
