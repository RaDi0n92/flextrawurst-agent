---
id: FW-NET-001
status: BESTAETIGT
typ: source
themenraum: NET
version: v21
tags: [88888, beziehung, creator, dialog, dungeon, dust, fahrzeug, fragen, konzert, magie, modular, net, playwright, redteam, simulation, skill, test, untergrund, v21, welt, wesen, zeit]
---

# Changelog · v21 final und weitere Statusabschnitte

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:CHANGELOG.md" sha256="cc3cab924b45cad4d5d7cf33e8a0a9b7758c489e399c379e15bbdc519600e869" order="1" -->
# Changelog · v21 final

## 2026-07-22

### Gebaut

- zwölf große Bau-Gates plus Gates 13A bis 13H
- 69 Skillbäume, 276 individuelle Knoten und einheitliche globale Skillpunkteökonomie
- filmische Spieleröffnung, Dust-/Wesenswelt, Zeitatlas, Untergrund, Creatorwelten, Magie, Handwerk, Modularität, Fahrzeuge und Traversal
- begehbare Erfahrungs- und Testzone

### Repariert

- identisches Konzertfarming
- Testzonen-Fahrzeugduplikation
- unvollständiger Laborreset
- nicht sichtbarer Laserstrahl
- fehlende passive Heilwirkung
- parallele alte Skillpunktewährung
- wirkungslose beziehungsweise generische Skillknoten
- veraltete Gate- und Simulationsannahmen
- Kontextwiederherstellung gegen falsches Datenfeld

### Geprüft

- 418 explizite Prüfungen bestanden oder geschützt
- 10.000 Charakterentwicklungen
- 88.888 Identitäten, 2.048 Dialoge, 128 Beziehungspfade, 256 Forschungszyklen, 4.096 Vergangenheiten, 333 Zukunftsschritte und 500 Traversalläufe

### Dokumentiert

- Rohinput R20
- sämtliche Gate-Fragenakten
- 2.607 einzeln zugeordnete Fragen
- finale Regression, Redteams, Simulationen, bekannte Grenzen
- `OUTRO.md` als Dateiresonanzfeld

<!-- SOURCE_SEGMENT_END source="v21:CHANGELOG.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:LINKPRUEFUNG.md" sha256="45b1d684b73188f1aa2d70985a3fcf9dd5cd32365115bcc8f5060641000cf64a" order="1" -->
# Link- und Referenzprüfung v21 final

- Markdown-Links geprüft: **0**
- Gebrochene Markdown-Links: **0**
- Modulare CSS-/JS-Referenzen: **32**
- Fehlende modulare Referenzen: **0**
- OUTRO-Dateieinträge: **296/296**
- `__pycache__`/`.pyc`: **0**

## Ergebnis

**BESTANDEN**

<!-- SOURCE_SEGMENT_END source="v21:LINKPRUEFUNG.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:MANIFEST.md" sha256="b8ad9595ae505884c4b601b2297e3975fe191460880b1e5b787857d1078feb5a" order="1" -->
# Manifest · v21 final

- **Erzeugt:** 2026-07-22
- **Gehaschte Dateien:** 292


<!-- SOURCE_SEGMENT_END source="v21:MANIFEST.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:README.md" sha256="2ca1d1ca91e920706a01f324ab944ac3cb97d485791776a11f0cff8728f35099" order="1" -->
# Flextrawurst Spielewelt · Supermaximal-Bauring 4 · v21 final

## Direkt spielen

Öffne **`PLAY_FLEXTRAWURST_V21.html`** in einem aktuellen Desktopbrowser. Diese Datei enthält CSS und JavaScript vollständig eingebettet.

`index.html` ist der modulare Entwicklungs- und Quellen-Einstieg. Er referenziert `assets/` und `src/` und wird mit `python tools/build_v21.py` deterministisch zum identischen Ein-Datei-Körper zusammengesetzt.

## Kern dieses Baurings

- filmische Eingangsfrage, katastrophale Endzukunft und Flextrawurst-Kontaktbruch
- Dust-Welt mit 88.888 stabilen Mischwesenidentitäten
- 69 gebrauchsgesteuerte Skillbäume und 276 individuelle Knoten
- echte Magie, Handwerk, Schmieden, Verzaubern, Waffen, Kleidung und Rüstungen
- Krallenhaken/Fallschirm-Traversal mit physikgekoppeltem Schwung
- Höhlen, Dungeons, Erze, Tiefenbau und Lebendgestein-Zustimmung
- Land-, Wasser-, Rail- und Luftfahrzeugfamilien
- 4.096 Vergangenheit-Adressen und 333 rückwärts gelesene Zukunftsschritte
- Creatorwelten, Konzerte, Versionen und rekonstruierbare Ereignisse
- vollständig begehbare, isolierte Erfahrungs- und Testzone

## Finaler Prüfstand

- **285/285** direkte Gate-Prüfungen
- **23/23** integrierte Querprüfungen
- **16/16** Post-Build-Redteam-Angriffe geschützt
- **22/22** Skill-Redteam-Angriffe geschützt
- **16/16** Skilluniversum-Simulation
- **50/50** große Welt-Simulationsprüfungen
- **6/6** Assemblierungsprüfungen
- **418** explizite bestandene oder geschützte Prüfungen insgesamt
- offene Prüffehler: **0**

## Dokumentation

Beginne mit:

1. `docs_v21/42_FINAL_ABNAHME_V21.md`
2. `docs_v21/43_BEKANNTE_GRENZEN_V21.md`
3. `OUTRO.md`
4. `MANIFEST.md`
5. `PACKAGE_AUDIT.json`

`OUTRO.md` erklärt jede einzelne Datei als Teil des Gesamtresonanzfelds.

<!-- SOURCE_SEGMENT_END source="v21:README.md" order="1" -->

<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/45_MODULARER_UND_EIN_DATEI_EINSTIEG.md" sha256="cc560aa464cde92963683cee32610fc658c4559f08392d7c36085a728df9f5ad" order="1" -->
# Modularer Einstieg und selbstständiger Ein-Datei-Körper

## Ergebnis

`index.html` referenziert die getrennten CSS- und JavaScript-Schichten. `tools/build_v21.py` fügt exakt diese Dateien in derselben Reihenfolge zusammen. Das Ergebnis ist bytegenau identisch mit `PLAY_FLEXTRAWURST_V21.html`.

- **Assemblierungsprüfung:** 6/6
- **SHA-256 des geprüften Ein-Datei-Körpers:** `7b15da11e4d2eee2d087f73cbaf7528642396a23f7b6f7af9fc3bf49604c021c`
- **Integrierter Playwright-Lauf desselben Körpers:** 23/23

Der direkte URL-Aufruf lokaler Dateien war in der abgeschotteten Testumgebung administrativ blockiert. Deshalb wurde nicht behauptet, dieser Navigationsweg sei dort ausgeführt worden. Stattdessen wurde die deterministische Assemblierung gegen den vollständig Playwright-geprüften Ein-Datei-Körper bytegenau verifiziert.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/45_MODULARER_UND_EIN_DATEI_EINSTIEG.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](00_INDEX.md) · `FW-INDEX-NET`
- [Nächster Knoten](FW-NET-002__Manifest_und_weitere_Statusabschnitte.md) · `FW-NET-002`
- [Verwandt: 8. Daniels Ideen-Redteam](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-021__8._Daniels_Ideen-Redteam.md) · `FW-SKILL-021`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
