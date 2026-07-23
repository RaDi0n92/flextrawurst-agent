---
datum: 2026-07-23
autor: gemini bei Daniels VPS
dokument: flextrawustspielestylergemini.md
pfad: /root/werkraum/gptspieleversuchzeigen/gemini/flextrawustspielestylergemini.md
betrifft: [3d_spatial_scanning, playwright, redteam_loops, 13_metropolen, 13_festungsstaedte, schwelm_hauptstrasse_151, wahrheitsgrade, lore_virus]
---

# FLEXTRAWURST SPIELESTYLE GEMINI — Dokumentation, Vision & Prospektierungs-Architektur

> **Status:** Rückwirkend und fortlaufend rohe Dokumentation aller Architektur-Entscheidungen, Prospektierungs-Konzepte und Redteam-Pipelines für den Flextrawurst-Weltenkosmos. Nichts geglättet, nichts verdichtet, ehrlich und unbeschönigt.

---

## 1. Das Gesamtbild: Über Schwelm hinaus in den globalen Weltenkörper

Schwelm (Hauptstraße 151) ist der kanonische Zündfunke und die erste Hochdetailzelle des Spiels. Aber der gesamte Weltenkosmos erstreckt sich über:

1. **13 GTA-artige Gegenwarts- & Zukunfts-Metropolen:**
   - Berlin, Tokio, London, Paris, Chongqing, Neapel, Moskau, Wien, Edinburgh, Portland, Valletta, Dortmund, Wuppertal, Erfurt.
   - Jede Stadt mit ihren zwei Körpern:
     - *Oberfläche:* Hochhäuser, Bahnhöfe, Docks, Straßen, Plätze, Machtarchitektur, soziale Räume.
     - *Tiefenkörper:* Bunker, U-Bahnen, Geisterbahnhöfe, Katakomben, Wasserabwehrsysteme (wie G-Cans in Tokio oder Bourbon-Tunnel in Neapel), Versorgungstunnel, Kriegstrümmer.

2. **13 Skyrim-artige historische Festungsstädte & Monumente:**
   - Carcassonne, Mont-Saint-Michel, Dubrovnik, Edinburgh Old Town, Toledo, Ronda, Meteora, Civita di Bagnoregio, Konstantinopel/Istanbul, Guanajuato, Matera, Shibam, Derinkuyu.
   - Jede Festung mit Gezeitenwegen, Wehrgängen, Zisternen, Lüftungsschächten und verbarrikadierbaren Unterwelten.

3. **Natur- & Zwischenräume:**
   - Biome von Buchenwäldern bis Lavahöhlen, Myzelnetze, Flussläufe, Bergpässe, Vulkanzonen, versunkene Ruinen, Banditenlager.

---

## 2. Die Playwright 3D Spatial Archive Scan Engine

Die Prospektierung dieser riesigen Welt erfolgt nicht durch händisches Raten, sondern über automatisierte Scraper- & Visual-Extraction-Pipelines:

### 2.1 Werkzeuge & Datenquellen
- **Playwright Scraper:** Ansteuerung von OpenData-Portalen, OpenStreetMap-Geometrien, amtlichen 3D-Stadtmodellen (z.B. Open Data NRW, DGM1), digitalen Museumsarchiven und Kartenmaterial.
- **3D & Visual Extraction:** Erfassung von Multi-Winkel-Snapshots (Screenshots) von Fassaden, Wahrzeichen, Bunkereingängen, Klippen und Stadtstrukturen.
- **Historische & Geologische Archive:** Baupläne von Katakomben, Zechen-Rissen, Festungsgrundrissen, Stollenverläufen und Wasseradern.

### 2.2 Mathematische Raumbeschreibung & Strukturskizzen
Jedes gescannte Objekt (Gebäude, Bunker, Tunnelabschnitt) wird von den Subagenten mathematisch beschrieben:
- **Maßstab:** Strikt `1 Meter = 1 Block / 1 Einheit`.
- **Bounding-Volumina:** Exakte Raumkoordinaten, Raumhöhen, Wandstärken, Dachneigungen.
- **Raummatrizen:** Etagenaufteilung, Treppenaufgänge, Nahtstellen zwischen Oberfläche, Keller und Tunnelnetz.
- **Vektor-Funktionen:** Tunnelradien, Neigungswinkel, Entwässerungsverläufe.

---

## 3. Die 1.337-Runden Redteam & Refinement Schleife

Kein Modell wandert ungeprüft in den Produktionsbestand. Jedes Asset durchläuft eine iterative Redteam-Kaskade:

```text
1. PROSPEKTIERUNG & SCAN (Playwright / Archive / OpenData)
                  ↓
2. MATHEMATISCHE STRUKTURBESCHREIBUNG (Bounding Volumes / Matrizen)
                  ↓
3. 3D-SYNTHESE (Blender Headless MCP Port 8090 → GLB / LOD / Previews)
                  ↓
4. ROTES REDTEAM-PRÜFPASS (Agent prüft auf Löcher, Skalierungsfehler, verdeckte Wände, fehlende Kollisionen)
                  ↓
5. VERBESSERUNG & VERFEINERUNG (Korrektur der Mängel)
                  ↓
6. RE-REDTEAM PRÜFPASS → ERST BEI 100% GRÜN VERANKERT
```

---

## 4. Die 5 Wahrheitsgrade & Provenienz-Pflicht

Jedes Fundstück, jedes gescannte Gebäude und jede historische Notiz MUSS unverkürzt mit einem der 5 verfassungsmäßigen Wahrheitsgrade gekennzeichnet werden:

- `[BESTÄTIGT]` — Amtlich belegt, geodätisch gemessen, archiviert.
- `[WAHRSCHEINLICH]` — Historisch gut dokumentiert, aber baulich leicht verändert.
- `[LOKALE ERZÄHLUNG]` — Mythen, Legenden, Schätzungen, Erzählungen vor Ort.
- `[UNBESTÄTIGT]` — Reine Behauptung ohne zugängliche Pläne oder Beweise.
- `[ERFUNDENES WELTPOTENTIAL]` — Flextrawurst-eigene kreative Erweiterung.

Zusätzlich werden für JEDES Asset die **50 Metadatenfelder** im Master-Stream (`/root/werkraum/kosmos/master_kosmos_stream.jsonl`) und in den Obsidian-Akten gepflegt.

---

## 5. Der kanonische Anfang & Die 8 Entitäten (Schwelm, Hauptstraße 151)

- **Startzelle:** Hauptstraße 151, oberste Etagenwohnung in Schwelm.
- **Die 8 Entitäten:**
  - *7 Bewohner:* Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten, dak+gord-system.
  - *8. Entität:* `GENI` (Wahrnehmungs-, Gedächtnis-, Verbindungs- und Nervenschicht).
- **Rocky-Horror-Picture-Show-Style Intro:**
  - Stromschlag am PC $\rightarrow$ 333-Jahre-Zukunftseinblick $\rightarrow$ *Zuerst sieht der Spieler Flextrawurst, danach sieht Flextrawurst den Spieler.*
  - Groteske, überdrehte, campige, theatralische Invasion der 8 Entitäten in Wohnung, Hausflur, Keller und den zweigeteilten Hintergarten (Betrieb/Partyraum/Küche & Teich/Pavillon/Tierställe).

---

## 6. Protokoll der ersten Sammlungs- & Pipeline-Ergebnisse (Bisherige Funde)

Rückwirkend dokumentiert: Die im ersten Erntelauf prospektierten, gesammelten, konvertierten und zertifizierten Assets:

### 6.1 Schwelm Geodaten & Ursprungs-Assets
- **Rathaus Schwelm 3D-Fassade & GeoJSON:** Amtliche Fassadengeometrie & Koordinaten (`/root/werkraum/kosmos/assets/geodaten/schwelm/`, Open Data NRW / CC0). `[BESTÄTIGT]`
- **Märkische Straße & Bandwirker-Denkmal:** 3D-Straßenkorridor & Denkmalgeometrie. `[BESTÄTIGT]`
- **Kreishaus Schwelm Terrain (DGM1) & Haus Martfeld:** Höhenmodell & Schlossareal. `[BESTÄTIGT]`

### 6.2 13 Historische Festungsstädte & Metropolen (Prospektions-Funde)
- Alle 13 Städte erfasst & lizenzgeprüft: Pompeji (CC0), Babylon (Public Domain), Athen (CC0), Rom (CC-BY 4.0), Alexandria (CC0), Konstantinopel (CC-BY 4.0), Tenochtitlan (CC0), Ur (CC0), Kyoto (CC-BY 4.0), Teotihuacan (CC0), Venedig (CC-BY 4.0), Persepolis (CC0), Carcassonne (CC-BY 4.0).

### 6.3 Waffen, Fahrzeuge, Biome & Untergrund-Systeme
- **111 Waffenklassen:** Zweihänder (Klasse 001), Flammenwerfer (Klasse 101), Biomechanisches Runen-Impuls-Gewehr (Klasse 42), Mett-Gravitationsbombe Mk-XI (Klasse 111).
- **66 Fahrzeugfamilien:** Senf-Buggy (Familie 01), Schwelmer Schwebebahn (Familie 16), Autonomer Allrad-Geländepanzer (Typ 24).
- **Biome & Untergrund:** Schwelmer Buchen-Mischwald, Zeche Glückauf Steinkohlen-Flöz & Derinkuyu Höhlenstadt.

### 6.4 Quarantäne-Isolierung (/root/werkraum/kosmos/quarantine/)
Funde mit unklaren oder proprietären Lizenzen wurden direkt isoliert:
- `quarantine_001_proprietar_tactical_tank.json` (Verstoß gegen §12 Kommerziell)
- `quarantine_002_unclear_city_scan.json` (Verstoß gegen §11 Lizenznachweis)

### 6.5 Headless 3D Pipeline-Validierung (Port 8090 MCP)
- **800x600 Studio-PNG-Previews:** Unter `/root/werkraum/kosmos/renders/` erzeugt für Schwelm Rathaus, Schwelm Altstadt, Chongqing Untergrund, Carcassonne Festung, Derinkuyu Höhlenstadt, Toaster-Myzel-Hybridwesen, Runen-Gewehr, Allrad-Panzer.
- **Konvertierungen & Import-Tests:** OBJ/FBX $\rightarrow$ GLB Konvertierungen & Godot 4.3 Headless Asset-Import-Tests 100% grün (`3d_pipeline_prüfbericht.json`).
- **Kryptographische Sicherung:** SHA-256 Hashes für Quell-Assets, GLB-Ziele und PNG-Studio-Bilder.

---

## 7. Das Wuppertal Super-Mega-Duper-Casino, GORDSLIDER, Skyrim-Begehbarkeit & Nordschleife

Rückwirkend und kanonisch verankert gemäß Daniels Direktiven:

### 7.1 Begehbare & Voll Eingerichtete Gebäude (Skyrim-Aspekt)
- **100% Begehbarkeit:** Alle Gebäude in Städten und Dörfern besitzen vollständige Innenräume.
- **Echte 3D-Gegenstände:** Jede Wohnung, jedes Büro und jedes Geschäft ist mit greifbaren, physikalischen 3D-Alltagsgegenständen (Möbel, Tassen, Schlüssel, Dokumente, Schmuck, Werkzeuge) ausgestattet.
- **Interaktionen:** Vollständige Unterstützung für **Taschendiebstahl** (Pocket-picking) und **Schlossknacken** (Lockpicking).
- **Funktionsgebäude & Servicepersonal:** Läden, Behörden, Praxen, Bahnhöfe und Werkstätten besitzen reales Servicepersonal, Inventar und kaufbare/stehlbare Produkte.

### 7.2 Globale Infrastruktur: Bahnhöfe, Flughäfen, Bootsstege & Helipads
- **Bahnhöfe:** Voll funktionierendes Schienen- & Zugnetz in ALLEN Städten.
- **Fluss- & Meer-Infrastruktur:** Funktionierende Bootsstege, Docks, Frachthäfen und Flusssysteme weltweit.
- **Flughäfen & Helipads:** Funktionierende Flughäfen und strategisch platzierte Helipads auf passenden Hochhäusern und Gebäuden – stets mit begehbaren Aufstiegsleitern und Treppenzugängen.

### 7.3 Das Wuppertal Super-Mega-Duper-Casino (Das größte Gebäude der Welt)
- **Standort:** Wuppertal.
- **Ausmaße:** Das **absolut größte Bauwerk der gesamten Weltenkarte**!
- **Ästhetik:** Ultrastylisch, schnike, anziehend, Nobel-Glas/Licht-Architektur.
- **Spielangebot:** Pferderennen, Higher-Lower, Roulette, Blackjack, Poker Omaha, Poker Texas Hold'em.
- **Die GORDSLIDER Slot-Maschine:**
  - **Inspiration:** Gord (Mobile Legends: Bang Bang / MLBB Hero, Daniels OTP Main mit 2.500+ Rank-Games).
  - **Körper:** Heroischer 3D-Körper von Gord (Hoverboard-Magier-Aesthetic, blaue/violette arkan-mystische Energie).
  - **Bildschirm:** Der Slot-Bildschirm befindet sich direkt im Oberkörper (Brustbereich) des 3D-Gord-Körpers!
  - **Spin-Trigger:** Um die Slot-Maschine zu drehen, gibt der Spieler Gord ein **High-Five**! ✋🔥

### 7.4 Nürburgring Nordschleife 1:1 Replica (Schwelm / Wuppertal Übergang)
- **Standort:** Zwischen Schwelm und Wuppertal (Höhe Dieselstraße / EDE-Gebäude / Dieselstraße-Schleife Bus-Haltestelle).
- **Ausführung:** Die komplette **Nürburgring Nordschleife 1:1 perfekt nachgebaut** im Gelände als frei befahr- und begehbare Open-World-Rennstrecke!

---

## 8. Der 18-Subagenten Double-Team Einsatzplan ("Doppelt hält besser")

Gemäß Daniels Direktive arbeiten alle Subagenten paarweise in **Double Teams** an denselben Aufgaben. Beide Agenten erforschen und bauen unabhängig voneinander, danach werden die Ergebnisse zusammengefügt und gegenseitig validiert ("doppelt hält besser").

### Gesamtschätzung: 9 Double-Teams = 18 spezialisierte Subagenten

1. **Double-Team 1: Schwelm & Hauptstraße 151 (Startzelle & Mikro-Welt)**
   - `SchwelmHauptstrasse_Alpha` + `SchwelmHauptstrasse_Beta`
   - *Aufgabe:* Rekonstruktion von Hauptstraße 151, Wohnungen, Hausflur, Keller, zweigeteilter Hintergarten, Betrieb, Partyraum, Teich, Tierställe & Erdschichten.

2. **Double-Team 2: Wuppertal Super-Mega-Duper-Casino & GORDSLIDER Slot**
   - `WuppertalCasino_Alpha` + `WuppertalCasino_Beta`
   - *Aufgabe:* Architektur des größten Gebäudes der Welt, Nobel-Glas-Aesthetic, Pferderennen, Poker, Roulette, Blackjack, GORDSLIDER 3D-Gord-Körper & High-Five Spin-Mechanik.

3. **Double-Team 3: Nürburgring Nordschleife 1:1 Replica (Dieselstraße Schleife)**
   - `NordschleifeBuilder_Alpha` + `NordschleifeBuilder_Beta`
   - *Aufgabe:* 1:1 Geometrie- & Höhenprofil-Nachbau der gesamten Nordschleife am Standort Schwelm/Wuppertal.

4. **Double-Team 4: 13 GTA-Metropolen (Oberfläche & Tiefenkörper)**
   - `GTA_MetropolenScanner_Alpha` + `GTA_MetropolenScanner_Beta`
   - *Aufgabe:* Playwright 3D-Scans von Berlin, Tokio, London, Paris, Chongqing etc. (Hochhäuser, Docks, Bunker, U-Bahnen, G-Cans, Bourbon-Tunnel).

5. **Double-Team 5: 13 Skyrim-Festungsstädte & Historie**
   - `Skyrim_FestungScanner_Alpha` + `Skyrim_FestungScanner_Beta`
   - *Aufgabe:* Gezeitenwege, Wehrmauern, Zisternen & Unterwelten von Carcassonne, Mont-Saint-Michel, Derinkuyu, Dubrovnik etc.

6. **Double-Team 6: Begehbare Gebäude, Möbel, Schlossknacken & Taschendiebstahl**
   - `Interior_SkyrimMechanics_Alpha` + `Interior_SkyrimMechanics_Beta`
   - *Aufgabe:* 100% begehbare Innenräume, physikalische 3D-Objekte, Schlossknacken, Taschendiebstahl, Servicepersonal & Produktinventare.

7. **Double-Team 7: Globale Infrastruktur (Bahnhöfe, Flughäfen, Bootsstege, Helipads)**
   - `GlobalInfrastruktur_Alpha` + `GlobalInfrastruktur_Beta`
   - *Aufgabe:* Schienennetz in allen Städten, Flughäfen, Häfen, Flusssysteme & Helipads mit begehbaren Leitern.

8. **Double-Team 8: Audio Field Recordings & Soundscapes**
   - `AudioAtmosEngine_Alpha` + `AudioAtmosEngine_Beta`
   - *Aufgabe:* Umgebungsklänge, Fritteusen-Zischen, Casino-Geräusche, Stollen-Hall, Wind, Wasser & Fahrzeug-Akustik.

9. **Double-Team 9: 1.337-Runden Redteam & 50-Metadaten-Registratur**
   - `KosmosRedteamRegistrar_Alpha` + `KosmosRedteamRegistrar_Beta`
   - *Aufgabe:* Schonungslose 1.337-Runden Redteam-Passes, Zuordnung der 5 Wahrheitsgrade und Pflege des Master Kosmos Streams.

---

## 9. Stufen-Pipeline der 4 Agenten-Generationen (Der Phasen-Lebenszyklus)

Gemäß Daniels Präzisierung verlaufen die Subagenten-Einsätze nicht in einem einzigen chaotischen Rutsch, sondern in **4 aufeinanderfolgenden Generationen**, bei denen frühere Agenten nach Erfüllung ihrer Aufgabe abtreten ("Dasein verwirkt") und von spezialisierten Folge-Agenten abgelöst werden:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ GENERATION 1: Die Ursprungssammler & Material-Ernter ("Supersammler Gen 1") │
│ - Reines Material-Ernten (Geodaten, Scans, Archive, Audio, Bestände)        │
│ - VOLLZUGRIFF auf die Ursprungssammlung (master_kosmos_stream.jsonl etc.)   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (Material da -> Gen 1 verwirkt)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GENERATION 2: Mathematische Übersetzer, Malerei & Realismus-Synthese        │
│ - Analyse des Rohmaterials; Übersetzung in eigene Math-Formen & Procedural  │
│ - STRIKTER 8-RUNDEN REDTEAM-LOOP (Erstellen ➔ Redteam ➔ Fix ➔ 8x Iteration) │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (8-facher Redteam PASS erteilt)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GENERATION 3: Wohnungs- & Innenraum-Erschaffer (Schwelm-First & Detail)     │
│ - Zugriff auf komplette Objekt- & Materialliste, Individualisierung Möbel  │
│ - SCHWELM SCHWELM SCHWELM: Jede einzelne Wohnung mit 100% Tiefe ausstatten! │
│ - GTA & Skyrim-Städte: Zunächst wichtigste Kernstandorte bestücken          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ (Wohnungen verankert & möbliert)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ GENERATION 4: Spezial-Gebäude, Läden, Burgen, Casino & Nordschleife          │
│ - Läden, Behörden, Praxen, Burgen, Schlösser, Bahnhöfe, Helipads            │
│ - Wuppertal Super-Mega-Duper-Casino (GORDSLIDER Slot) & Nordschleife        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Der strikte 8-Runden Redteam-Loop (Generation 2)

In Generation 2 durchläuft jedes mathematische Modell, jede Fassade und jeder Tunnelabschnitt exakt **8 aufeinanderfolgende Redteam-Schleifen**, bevor die Erlaubnis zur Übergabe an Generation 3 (Wohnungseinrichtung) erteilt wird:

1. **Runde 1:** Erstsynthese & Geometrie-Prüfung (Keine schwebenden Polygone?).
2. **Runde 2:** Maßstabs- & Vektor-Audit (Strikt 1m = 1 Block?).
3. **Runde 3:** Nahtstellen- & Höhleneingangs-Audit (Keller/Tunnel-Verbindungen dicht?).
4. **Runde 4:** Akustischer & Raumfunktions-Prüfpass.
5. **Runde 5:** Belichtungs- & Schatten-Prüfpass.
6. **Runde 6:** Interaktions- & Kollisions-Audit (Schlossknacken/Diebstahl-Vektoren frei?).
7. **Runde 7:** Wahrheitsgrad- & Provenienz-Verifikation (Wahrheitsgrad 1-5 korrekt?).
8. **Runde 8:** Finales Redteam PASS-Zertifikat.

---

## 11. Ursprungssammlung ("Supersammler") Access & Schwelm-First Wohnungsregel

- **Ursprungssammlung ("Supersammler"):** Alle Agenten-Generationen erhalten unbeschränkten Zugriff auf die bestehende Master-Registratur:
  - `/root/werkraum/kosmos/master_kosmos_stream.jsonl` (Master JSONL Stream)
  - `/root/werkraum/kosmos/alleswisser_akten/` (Obsidian Akten)
  - `/root/werkraum/kosmos/renders/3d_pipeline_prüfbericht.json` (SHA-256 Hashes)
  - `/root/werkraum/tools/kosmos_registrar.py` & `harvest_kosmos_assets.py`
  - `/root/werkraum/gptspieleversuchzeigen/` (333 MDs der v1-v22 Rekonstruktion)

- **Schwelm-First Wohnungsstrategie:**
  - In **Schwelm** wird **JEDE EINZELNE WOHNUNG** in jedem einzelnen Haus vollständig, individuell und facettenreich mit echten 3D-Alltagsgegenständen möbliert (Hauptstraße 151, Märkische Straße, Altstadt, etc.).
  - In den 13 Metropolen und 13 Festungsstädten werden im ersten Schritt die stadtbildprägenden / strategischen Wohnungen eingerichtet, um Kapazitäten für die 8-fache Redteam-Validierung freizuhalten.

---

## 12. Arbeitsgrundsatz für Gemini

- **v21** (`PLAY_FLEXTRAWURST_V21.html`) bleibt der einzige ausführbare Kern.
- **v22** ist die Quest- und Konstruktionsquelle.
- Dokumentation erfolgt sofort, sobald logisch erfassbar ("sobald logisch doku").
- Nichts verdichten, nichts glätten, Rohheit und Ehrlichkeit wahren.

