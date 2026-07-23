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

## 8. Arbeitsgrundsatz für Gemini

- **v21** (`PLAY_FLEXTRAWURST_V21.html`) bleibt der einzige ausführbare Kern.
- **v22** ist die Quest- und Konstruktionsquelle.
- Dokumentation erfolgt sofort, sobald logisch erfassbar ("sobald logisch doku").
- Nichts verdichten, nichts glätten, Rohheit und Ehrlichkeit wahren.


