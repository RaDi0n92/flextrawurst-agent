---
id: FW-BUILD-002
status: BESTAETIGT
typ: source
themenraum: BUILD
version: v21
tags: [88888, beziehung, build, dust, material, simulation, test, v21, welt, wesen, zeit]
---

# Architektur vor dem Bau

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:MAXUS_DUST_VERTRAG/06_ARCHITEKTUR_VOR_BAU.md" sha256="87f5f6a90a8f67de5e7c876de3c8b2cc8f7b470a513d40ff4660f54b7b3638eb" order="1" -->
# Architektur vor dem Bau

## Neue Module

### `DustRegistry`

- besitzt `total = 88888`;
- generiert Identitäten deterministisch aus Seed und globalem Index;
- hält die acht Körperfamilien und ihre exakte Verteilung;
- erzeugt keine 88.888 schweren Objektinstanzen beim Start;
- liefert `get(index)`, `getById(id)`, `sectorPopulation(sectorX, sectorZ)`, `materializeLocal(player)` und `simulateLongCycle(state)`.

### Zustandsdeltas

`state.dust` speichert nur:

- Generatorversion;
- Begegnungen und lokale Beziehungen;
- irreversible Narben und Ortswechsel;
- relevante Ereigniskanten;
- aktiven Simulationscursor;
- keine Vollkopie des Registers.

### Lokale Materialisierung

- maximal 36 generierte Wesen gleichzeitig zusätzlich zu handgebauten Figuren;
- stabile Sektorzuordnung;
- unterschiedliche visuelle und mechanische Ausdrucksformen je Körperfamilie;
- bei Sektorwechsel werden lokale Körper neu aus denselben Identitäten materialisiert.

### Langzyklus

- mindestens 512 Ereigniskörper werden pro großem Zyklus über Cursorfenster berücksichtigt;
- Ereignisse besitzen zwei oder mehr konkrete Dust-IDs;
- Ereignisse verändern kompakte Deltas, Beziehungen, Ort oder Zustand;
- Chronik speichert nur bedeutsame Ereignisse.

### UI

- Taste `O` öffnet **Lokale Dustökologie**;
- keine Restzahl und kein `x/88888`;
- sichtbare Gesamtzahl nur als Weltregister-Nachweis;
- lokale Begegnungen, Ausdrucksform und Rechte werden dargestellt;
- Testmodus kann Körperfamilien und Sektoren materialisieren, ohne Normalstand zu verändern.

### Renderer

- vorhandener Soft3D-Renderer bleibt austauschbar;
- neue Körper verwenden vorhandene primitive Formen und Kompositionen;
- keine humanoiden AI-Maskottchen;
- lokale Dichte darf Framezeit nicht unkontrolliert erhöhen.

<!-- SOURCE_SEGMENT_END source="v21:MAXUS_DUST_VERTRAG/06_ARCHITEKTUR_VOR_BAU.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-BUILD-001__222_Pflichtfragen_beantwortet_vor_dem_Bau.md) · `FW-BUILD-001`
- [Nächster Knoten](FW-BUILD-003__F-0051_TEILWEISE.md) · `FW-BUILD-003`
- [Themenindex](00_INDEX.md) · `FW-INDEX-BUILD`
- [Verwandt: Test, Redteam, Abnahme](../07_BEWEGUNG_FAHRZEUGE_KAMPF_LOOT/FW-MOVE-001__Test_Redteam_Abnahme.md) · `FW-MOVE-001`
- [Verwandt: 8. Daniels Ideen-Redteam](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-021__8._Daniels_Ideen-Redteam.md) · `FW-SKILL-021`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: D136-Q01 · Nachbauprüfung](../05_DUST_WESEN_BEZIEHUNGEN/FW-DUST-021__D136-Q01_Nachbauprufung.md) · `FW-DUST-021`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
