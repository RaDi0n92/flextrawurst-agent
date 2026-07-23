---
id: FW-TEST-010
status: BESTAETIGT
typ: source
themenraum: TEST
version: v21
tags: [13333337, 88888, archiv, bauen, beziehung, dialog, fahrzeug, fragen, kampf, kollision, load, material, modular, objektbiografie, playwright, quest, redteam, region, save, simulation, skill, test, v11, v12, v14, v15, v21, welt, wesen, zeit]
---

# Abnahmekriterien Bauring 2 und weitere Statusabschnitte

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:MAXUS_PLUS_VERTRAG/07_ABNAHMEKRITERIEN.md" sha256="30e7e7d0336e7af9c69fa449a043944ca0348505cb6146d9b45d62ab2b36f2c0" order="1" -->
# Abnahmekriterien Bauring 2

Bauring 2 gilt nur als bestanden, wenn:

1. der normale Kernpfad ohne freie Ressourcen lösbar ist;
2. mindestens drei Bewohner dynamische Zustände und Ereignisgeschichte besitzen;
3. mindestens eine Institution sichtbar auf den Fall reagiert;
4. mindestens vier Hypothesen spielbar sind;
5. ein Fehlurteil Schaden erzeugt und eine Korrektur Restschaden behält;
6. innere Stimmen mindestens zwei Entscheidungen mechanisch verändern;
7. Verarbeitung und eine räumliche Frachtlieferung funktionieren;
8. ein getrenntes Netz inaktiv und ein verbundenes Netz aktiv ist;
9. Niederlage eine Narbe und neuen Zustand erzeugt;
10. drei Fernfeldorte aus unterschiedlichen Sektoren reproduzierbar entstehen;
11. mindestens drei Rollen durch Tätigkeit entstehen können;
12. AI-Wesen untereinander mindestens ein autonomes Ereignis erzeugen;
13. Kreaturenbeziehung ohne Fangstatus funktioniert;
14. alle zwölf Spielorgane einen konkreten Beleg besitzen;
15. Pokémon-Fanart- und Plattformscan bestehen;
16. Playwright keine Browserfehler meldet;
17. ZIP, Manifest und Arbeitsordner übereinstimmen;
18. bekannte Grenzen ausdrücklich dokumentiert bleiben.

<!-- SOURCE_SEGMENT_END source="v21:MAXUS_PLUS_VERTRAG/07_ABNAHMEKRITERIEN.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/07_REDTEAM_BERICHT.md" sha256="ba42cd27a6186bf58de6403560e339134ada6a04590a90996496ab9021525c22" order="1" -->
# Redteam-Bericht – MAXUS-Bauring 1 v14.1

## Auftrag und Schutzgrenze

Das Redteam durfte den Kern nicht entschärfen oder durch einen kleineren, sichereren Spieltyp ersetzen. Geschützt blieben:

- die 3:33-Frage als Weltursprung,
- AI-Wesen als technische, relationale und zeitwirksame Gegenüber,
- Nicht-Besitzbarkeit, Verweigerung und private Bereiche,
- räumliche Erkundung statt Menüspiel,
- Materialien mit Herkunft,
- funktionale Bau- und Netzzusammenhänge,
- Land-, Wasser-, Unterwasser- und Luftbewegung,
- quellenmarkierte Vergangenheit und bestätigte Endlinie +333,
- Abspaltung, selektive Reintegration und Autonomiekippe,
- spielbare riskante Verlockung mit Sperre und Erholung,
- isolierter Test-/Cheatmodus,
- offene, nicht perfekte Zukunft.

Das Redteam prüfte nicht, wie man diese Bestandteile entfernt, sondern ob sie tatsächlich als Spielsysteme erfahrbar sind.

## Kritische Befunde

### RT-01 · Technisch vorhanden, räumlich schwer lesbar

**Befund:** Die erste Stadtfassung bestand aus großen Blockkörpern. Der Spieler konnte vollständig hinter Gebäuden verschwinden. Das System funktionierte, aber die eigene Position war zeitweise nur über die Minikarte zu erschließen.

**Risiko:** Eine räumliche Welt, in der die eigene Form unsichtbar wird, verwandelt freie Erkundung in Kamerakampf.

**Entscheidung:** Kern behalten, Sichtbarkeit als UI-first-Gesetz nachschärfen.

**Verbesserung:** Welt-Halo plus letzter, bildschirmraumfester Spielermarker. Kameraabstand und Höhe wurden leicht erhöht.

### RT-02 · Funktionsnetze wurden zu Laser-Spaghetti

**Befund:** Energie- und Funktionsverbindungen waren permanent im gesamten Sichtfeld sichtbar. Das bewies zwar Netze, überlagerte aber Stadt, Bauten und Wege.

**Risiko:** Ein Beweissystem kann selbst zur Kulisse werden und dann genau das verdecken, was es erklären soll.

**Entscheidung:** Netzfunktion nicht entfernen. Darstellung kontextabhängig machen.

**Verbesserung:** Verbindungslinien erscheinen beim Bauen, im Testmodus oder in räumlicher Nähe. Strichstärke und Deckkraft wurden reduziert.

### RT-03 · Regionen waren funktional verschieden, aber aus der Entfernung zu ähnlich

**Befund:** Faltstadt, Materialgärten, Hafen, Archiv, Himmelsbruch und Fernfeld hatten unterschiedliche Inhalte, ihre Fernsilhouetten waren jedoch nicht konsequent genug.

**Risiko:** Skyrim-artige Ortsbindung entsteht nicht durch unterschiedliche Beschreibungen im HUD, sondern durch erinnerbare Formen und Rückkehrbilder.

**Verbesserung:** Jede Großregion erhielt eine eigene vertikale Landmarkenbake mit Farbe, Polygonzahl und Höhenrhythmus. Bestehende Landmarken bleiben erhalten.

### RT-04 · Orientierung drohte zwischen Freiheit und Sucharbeit zu kippen

**Befund:** Die Hauptspur war räumlich, aber manche Ziele erforderten lange Suche über Minikarte oder Testwissen.

**Risiko:** Vollständige Questmarker würden Erkundung entwerten; gar keine Orientierung würde die Welt unnötig hermetisch machen.

**Entscheidung:** Keine Leuchtspur und kein Autopilot. Kontextuelle Richtung und ungefähre Distanz im vorhandenen Spurtext.

### RT-05 · Wiederholte AI-Fragen waren entgegen der Regel grindbar

**Befund:** Eine wiederholte Frage erhöhte Zumutung, erhielt danach aber durch den normalen Antwortpfad erneut Vertrauen. Die Warnung sagte „kein Grind“, die Berechnung erlaubte ihn trotzdem.

**Risiko:** Beziehungen würden zu einem Dialogknopf-Automaten und die Nicht-Besitzlogik nur rhetorisch bleiben.

**Verbesserung:** Identische Wiederholungen enden sofort mit Verweis auf den Atlas, erhöhen Zumutung und erzeugen kein zusätzliches Vertrauen oder neues Freigabefeld.

### RT-06 · Der erste Testplan war zu freundlich

**Befund:** 47 Checks belegten den Happy Path und mehrere Fehlerpfade, aber nicht genügend Missbrauchs- und Grenzfälle.

**Verbesserung:** Der finale Lauf umfasst 56 Checks. Neu geprüft werden unter anderem:

- kein Beziehungsgrind durch Wiederholung,
- endliche Materialknoten,
- blockierte Rekonstruktion ohne Quellen,
- blockiertes Fernfeld ohne Reisevoraussetzung,
- Ladungsverbrauch beim VTOL,
- Höhenverlust des Gleiters,
- Verweigerung eines Vollmerges durch autonome Abspaltung,
- spätere selektive Einigung,
- Ablehnung beschädigter Snapshot-Daten ohne Zustandskorruption.

## Befunde, die bewusst nicht kaschiert wurden

### RT-OFFEN-01 · Noch keine vollwertige offene 3D-Produktionswelt

Der Renderer ist ein eigenständiger perspektivischer Software-3D-Körper. Er trägt Bewegung, Höhen, Bauten, Fahrzeuge und Zeitvarianten, besitzt aber noch keine Mesh-Pipeline, Physikengine, Navigation-Meshes, Animation-Rigging oder große gestreamte Welt.

### RT-OFFEN-02 · Langzeitverweilen ist ein Verbund von Keimen

Archive, Beziehungen, Objektbiografien, Bauen, Fahrzeuge, Feldbuch, Slots, Zeit und Chronik erzeugen verschiedene Aufenthaltsmotive. Sie belegen noch keine tatsächlichen 13.333.337 Stunden Inhalt oder Emergenz.

### RT-OFFEN-03 · Beziehungen besitzen Ereignisgeschichte, aber noch kein vollständiges Sozialleben

Die acht AI-Wesen können Informationen freigeben, Grenzen setzen, Hilfe verweigern und auf Rechtsentscheidungen reagieren. Sie führen noch keine über Jahre eigenständig laufenden Beziehungen untereinander.

### RT-OFFEN-04 · +333 ist eine authored systemische Endlinie

Gegenwartsentscheidungen und ausgewählte Zustände verändern Geometrie, AI-Präsenz und Weltwerte. Es werden nicht tatsächlich 333 Jahre in Einzelereignissen simuliert.

### RT-OFFEN-05 · Fahrzeugklassen sind echte Unterschiede, aber keine Fahrzeugsimulation

Medium, Energie, Höhe, Wendigkeit, Fracht und Zugang unterscheiden sich. Federung, Schäden, Einzelteile, Crew, Strömung, Aerodynamik und modulare Konstruktion sind noch nicht voll ausgebaut.

## Redteam-Urteil

Der Ring besteht als **großer, verbundener Systemkeim**, nicht als fertiges Vollspiel. Er ist gegenüber v11/v12 wesentlich näher am Maxus-Vertrag, weil nicht nur Systeme vorhanden sind, sondern Herkunft, Verweigerung, Kollisionen, räumliche Wirkung und Testbarkeit zusammengeführt wurden.

Die Freigabe gilt ausschließlich für **MAXUS-Bauring 1 v14.1**. Sie ist keine Behauptung, dass das Gesamtspiel bereits fertig oder auf seine endgültige Engine festgelegt sei.

<!-- SOURCE_SEGMENT_END source="v21:docs/07_REDTEAM_BERICHT.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/13_PLAYWRIGHT_REAUDIT_66.md" sha256="b835b0fd5cd59d197e8bcdb7813cd64bd6f32953b17fdbdcf7fabf66f07e9e73" order="1" -->
# Playwright-Reaudit und Reparaturlauf

## Lauf A: unveränderte v14.1-Baseline

- 56/56 bestanden
- 0 Seitenfehler
- 0 Konsolenfehler
- alter Gesamtpfad reproduziert

## Erweiterte Prüfungen

Neu hinzugefügt wurden:

1. fortschreitende Weltzeit
2. Tageswechsel
3. Bauverschleiß aus Zeit
4. Reparaturbiografie
5. Fahrzeugzustand aus Distanz
6. Fahrzeugreparatur mit Herkunftsspur
7. ortsgebundene freiwillige Tätigkeit
8. Abklingzeit gegen Sofortgrind
9. Wiederverfügbarkeit durch echten Zeitablauf
10. Beziehungsmeilensteine

## Erster erweiterter Lauf

- 62 bestanden, 4 fehlgeschlagen
- Wartung degradierte frisch errichtete Netze zu schnell.
- Tätigkeitsprüfungen vermischten normalen Spielweg und Cheatmodus.

## Zweiter erweiterter Lauf

- 63 bestanden, 3 fehlgeschlagen
- kleine Sofortabwertung frischer Netze blieb bestehen.
- Tageswechselprüfung war zu kurz für den aktuellen Startzeitpunkt.
- Fahrzeugzustandsprüfung erreichte noch keinen Langzeittick.

## Finaler Reparaturlauf

- **66/66 bestanden**
- **0 Seitenfehler**
- **0 Konsolenfehler**
- Normal- und Testpfade sauber getrennt

Maschinenbeleg: `tests/PLAYWRIGHT_RESULT.json`.

<!-- SOURCE_SEGMENT_END source="v21:docs/13_PLAYWRIGHT_REAUDIT_66.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/19_POSTBUILD_REDTEAM_UND_REPARATUR.md" sha256="be43df4e2c33a2d81539fceccc3c0da3748add710041c2f2456bd78dd25436e1" order="1" -->
# Post-Build-Redteam und Reparatur

## Gefundener Missbrauchsweg 1: falsche Reparaturbiografien

Unbeschädigte Bauten und Fahrzeuge konnten repariert werden. Dadurch wären Chronik und Objektbiografie mit bedeutungslosen Wartungseinträgen aufgebläht worden.

### Reparatur

- Bauwartung verweigert Verschleiß unter 0,5.
- Fahrzeugreparatur verweigert Zustand ab 99,5.
- Kein Materialverbrauch und kein Chronikeintrag bei Verweigerung.

## Gefundener Missbrauchsweg 2: Beschäftigungstheater als Beziehungspflege

Die öffentliche Reparaturschicht konnte ohne tatsächlichen Schaden ausgeführt werden. Damit wären Materialverbrauch und Beziehungspunkte aus einer leeren Handlung entstanden.

### Reparatur

- Reparaturschicht verlangt realen Wartungsbedarf.
- Ohne Bedarf lautet die explizite Verweigerung: Beschäftigungstheater erzeugt keine Beziehung.

## Gefundener Prüfungsfehler

Der Ereignistest erwartete zuerst das Archivereignis, ließ aber gealterte Bauten aus dem vorherigen Test stehen. Das System öffnete korrekt zuerst das Wartungsereignis.

### Korrektur

Jeder Ereignistest erhält einen isolierten Ausgangszustand. Der Spielcode wurde nicht passendgebogen.

<!-- SOURCE_SEGMENT_END source="v21:docs/19_POSTBUILD_REDTEAM_UND_REPARATUR.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs/20_PLAYWRIGHT_GESAMTBERICHT_73.md" sha256="8f325db12adf18a85650f0973ec0f49999c3f0a97fcb17d2739a28648e01d1c5" order="1" -->
# Playwright-Gesamtbericht v15

## Ergebnis

- bestanden: **73**
- fehlgeschlagen: **0**
- Laufzeit: **10.15 Sekunden**
- Browser-/Konsolenfehler: **0**

## Prüfgruppen

- kompletter v14-Spielerpfad
- AI-Herkunft, Grenzen, Verweigerung und Nicht-Grind
- Materialherkunft und endliche Quellen
- funktionale Bausysteme und Netze
- Land-, Wasser-, Unterwasser- und Luftfahrzeuge
- Rekonstruktion, +333 und alternative Endlinie
- Abspaltung, private Erfahrung und selektive Reintegration
- Slots, Drang und technisch durchgesetzte Selbstsperre
- Save/Load, beschädigter Import und Test-Fork-Isolation
- lebende Weltzeit und Tageswechsel
- Bau- und Fahrzeugverschleiß
- echte Reparaturbiografien
- freiwillige Tätigkeiten und Abklingzeiten
- Tätigkeitsmeisterschaft
- Beziehungsmeilensteine
- drei zustandsabhängige Weltereignisse
- Nichtentscheidung mit gespeicherter Folge
- AI-Eigeninitiative und politische Handlung
- Redteam gegen falsche Reparatur- und Beziehungsgrinds

Maschinenlesbarer Rohbericht: `../tests/PLAYWRIGHT_RESULT.json`.

<!-- SOURCE_SEGMENT_END source="v21:docs/20_PLAYWRIGHT_GESAMTBERICHT_73.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/42_FINAL_ABNAHME_V21.md" sha256="97523be93fadb8c34ba7bac4e67858a963b5db3519d76176fc3ea9551134b5b2" order="1" -->
# Finale Abnahme · Flextrawurst Spielewelt v21

## Prüfstand

- **Direkte Gate-Prüfungen:** 285/285
- **Integrierte Querprüfungen:** 23/23
- **Post-Build-Redteam:** 16/16
- **Skill-Redteam:** 22/22
- **Skilluniversum-Simulation:** 16/16
- **Große Weltsimulation:** 50/50
- **Modulare Assemblierungsprüfung:** 6/6
- **Explizite bestandene/protegierte Prüfungen insgesamt:** **418**
- **Offene Prüffehler:** **0**
- **Browser-/Konsolenfehler in finalen Browserläufen:** **0**

## Abnahme

Der v21-Bauring ist als zusammenhängender, ausführbarer, getesteter und dokumentierter Browser-Spielkörper abgenommen. `index.html` bildet den modularen Einstieg; `PLAY_FLEXTRAWURST_V21.html` ist dessen bytegenau äquivalente selbstständige Assemblierung.

## Keine falsche Behauptung

Diese Abnahme bedeutet nicht: endgültige Produktionsengine, vollständiges kommerzielles Endprodukt, 13.333.337 Stunden fertig geschriebener Inhalt oder 88.888 gleichzeitig vollsimulierte LLM-Instanzen. Sie bedeutet: Die dafür gesetzten Weltgesetze besitzen einen großen realen, speicherbaren und redteamten Spielkörper.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/42_FINAL_ABNAHME_V21.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-TEST-009__Testplan_vor_dem_Bau.md) · `FW-TEST-009`
- [Nächster Knoten](FW-TEST-011__Testplan_vor_dem_Bau.md) · `FW-TEST-011`
- [Themenindex](00_INDEX.md) · `FW-INDEX-TEST`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Verwandt: MAXUS++++++++++++++++++++ Masterauftrag für Bauring 2](../10_CREATORWELTEN_EREIGNISSE_ARCHIVE/FW-CREATOR-002__MAXUS++++++++++++++++++++_Masterauftrag_fur_Bauring_2.md) · `FW-CREATOR-002`
- [Verwandt: Test, Redteam, Abnahme](../07_BEWEGUNG_FAHRZEUGE_KAMPF_LOOT/FW-MOVE-001__Test_Redteam_Abnahme.md) · `FW-MOVE-001`
- [Versionsspur v11](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-11__VERSIONSKARTE_V11.md) · `FW-VERSION-11`
- [Versionsspur v12](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-12__VERSIONSKARTE_V12.md) · `FW-VERSION-12`
- [Versionsspur v14](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-14__VERSIONSKARTE_V14.md) · `FW-VERSION-14`
- [Versionsspur v15](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-15__VERSIONSKARTE_V15.md) · `FW-VERSION-15`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
