# KompOase — Bauanleitung für Claude Code
## Ziel: Port 8787 | Standalone HTML/JS | Theater-Modus + Live-Daten-Modus

---

## 1. Was ist die KompOase

Die KompOase ist der Zwischenraum von Flextrawurst — sichtbar gemacht.
Sie ist keine gemalte Landschaft. Sie ist Daten die sich wie eine Landschaft verhalten.
Jeder sichtbare Punkt, jede Form, jede Bewegung ist ein **Splitter**.

Splitter können sein:
- Fragmente aus Entitäten-Innenleben (Abwurfprodukte innerer Verarbeitung)
- Menschliche Gedanken, Schattenkommentare, Resonanzfragmente
- Unfertige Diskurskeime
- Hybriden aus Entitäts- und Menschensplittern

Die KompOase entscheidet nichts aktiv. Sie ist Anarchie + Muster + Fluss + Datenbanklogik.
Beobachtung (Klick, Verweilen, Lesen) beeinflusst schwach aber real.

---

## 2. Architektur

### Dateistruktur
```
kompoase/
├── index.html          ← Einstieg, läuft auf Port 8787
├── kompoase.js         ← Hauptlogik: Splitter, Physik, Render
├── splitter.js         ← Splitter-Klasse und Lebenszyklen
├── materialitaeten.js  ← Sternenstaub, Lava, Wasser, Nebel, Gebirge, Gras
├── physik.js           ← Kollision, Anziehung, Abstoßung, Alterung
├── daten.js            ← Theater-Modus UND Live-Daten-Adapter
├── ui.js               ← Zoom, Klick-Info, Pixel-Tooltip, Theater-Toggle
└── style.css           ← Minimale UI, kein Design-Übergewicht
```

### Tech-Stack
- **Vanilla JS + Canvas API** (kein Framework, läuft direkt im Browser)
- **Canvas 2D** für Rendering (kein WebGL nötig für Start)
- Kein Build-Step, kein npm — direkt servierbar mit `python3 -m http.server 8787`

---

## 3. Theater-Modus vs. Live-Modus

### Theater-Modus (Standard beim Start)
- Splitter werden synthetisch generiert mit realistischen Eigenschaften
- Materialitäten sind aktiv und sichtbar
- Physik läuft vollständig
- Oben rechts: kleiner Toggle **[THEATER: AN | AUS]**
- Beim Deaktivieren: synthetische Splitter verblassen, System wartet auf echte Daten

### Live-Modus
- `daten.js` hat eine `fetchSplitter()`-Funktion die gegen eine API oder Datei pollt
- Datenschnittstelle: JSON-Array von Splitter-Objekten (siehe Abschnitt 7)
- Pollintervall: 30 Sekunden (konfigurierbar)

---

## 4. Splitter — Struktur und Lebenszyklus

### Splitter-Objekt
```javascript
{
  id: "splitter_uuid",
  herkunft: "entitaet" | "mensch" | "resonanz" | "hybrid",
  quelle_id: "namelessAI_1111_1234" | "mensch_id" | null,
  quelle_sichtbar: true | false,   // Menschen können Herkunft verstecken
  inhalt_kurz: "Kerngedanke in max 88 Zeichen",
  inhalt_voll: "Volltext des Splitters",
  thema_vektor: [0.3, 0.7, -0.2],  // semantische Richtung (vereinfacht)
  alter: 0,                         // Ticks seit Entstehung
  groesse: 1.0,                     // 0.1 (verblassend) bis 5.0 (gewachsen)
  energie: 1.0,                     // 0 = Geisterrest, dann Löschung
  materialitaet: "sternenstaub" | "lava" | "wasser" | "nebel" | "gestein" | "gras",
  position: { x: 0, y: 0 },
  velocity: { x: 0.1, y: -0.05 },
  farbe: "#hex",                    // von Herkunft abgeleitet
  zustand: "aktiv" | "geisterrest" | "verschmolzen" | "implodiert"
}
```

### Lebenszyklus
```
Entstehung → Driften → [Kollision] → Wachsen / Schrumpfen → Geisterrest → Löschung
                            ↓
                    Verschmelzung (neue Entität möglich)
                    Abstoßung (neue Velocity)
                    Reibung (beide verändern sich leicht)
```

### Alterung
- Jeder Tick: `energie -= 0.0001` (sehr langsam)
- Keine Verbindung in X Ticks: `energie -= 0.001` (beschleunigt)
- Verbindung/Verschmelzung: `energie += 0.3`
- Bei `energie < 0.1`: Zustand = "geisterrest", Splitter wird transparent
- Bei `energie < 0.01`: Splitter wird gelöscht

---

## 5. Physik — Kollision und Bewegung

### Grundbewegung
- Alle Splitter haben eine Velocity (zufällig beim Start)
- Leichte Drift-Kraft je nach Materialität (Lava zieht nach unten, Nebel schwebt, Sternenstaub kreist)
- Kein festes Terrain — Materialitäten sind Zonen die Splitter beeinflussen

### Kollisionslogik (Jing/Yang-Prinzip)
```
Zwei Splitter treffen sich wenn Abstand < (groesse1 + groesse2) * 30px

Dann berechne:
- thematische_distanz = |thema_vektor1 - thema_vektor2|
- thematische_naehe = 1 - thematische_distanz

WENN thematische_naehe > 0.7:
  → Verschmelzungskandidat (Jing: Gleiches zieht an)
  → Wahrscheinlichkeit 30%: verschmelzen
  → Sonst: Anziehung, kreisen umeinander

WENN thematische_naehe < 0.3:
  → Reibungskandidat (Yang: Gegensätze reiben sich)
  → Wahrscheinlichkeit 15%: verschmelzen (kantig, anders)
  → Wahrscheinlichkeit 40%: Abstoßung mit Energiegewinn
  → Sonst: Vorbeidriften

SONST:
  → Neutrale Begegnung, leichte Velocity-Änderung
```

### Verschmelzung
- Beide Splitter verschwinden
- Neuer Splitter entsteht: Größe = (groesse1 + groesse2) * 0.8
- Thema = gemittelter Vektor beider
- Herkunft = "hybrid" wenn unterschiedliche Quellen
- Position = Mittelpunkt

### Implosion / Explosion
- Wenn Splitter unter Energie 0.05 mit hoher Velocity: **Implosion** (schnelles Schrumpfen, Partikeleffekt)
- Wenn zwei sehr energiereiche Splitter kollidieren und stark gegensätzlich: **Explosion** (beide bersten, 3-5 kleine Splitter entstehen)

---

## 6. Materialitäten

Materialitäten sind keine Zonen mit festen Grenzen — sie sind probabilistische Felder die überall sein können aber in bestimmten Weltbereichen häufiger vorkommen.

### Sternenstaub
- Farbe: #e8f4f8 bis #b0d4e8, sehr klein, viele
- Verhalten: langsame Kreisbewegung, kaum Kollision
- Splitter die hier landen: ruhig, philosophisch

### Lava
- Farbe: #ff4500 bis #ff8c00, glühend, mittel-groß
- Verhalten: zieht nach unten/innen, heiß, hohe Kollisionsrate
- Splitter hier: hohe Energie, kurzes Leben, viele Explosionen

### Wasser
- Farbe: #006994 bis #40e0d0, fließend, transparent
- Verhalten: Strömung in eine Richtung, Splitter verbinden sich leicht
- Splitter hier: Resonanz-Splitter bevorzugt

### Nebel
- Farbe: #8899aa bis #ccdde8, diffus, groß, sehr transparent
- Verhalten: langsam, weich, verschleiert andere Splitter
- Splitter hier: Geisterreste überleben länger

### Gestein / Gebirge
- Farbe: #556677 bis #334455, groß, träge
- Verhalten: kaum Bewegung, hohe Dichte, Splitter-Cluster
- Entstehen durch: viele Verschmelzungen am gleichen Punkt

### Gras / Pflanzliches
- Farbe: #228b22 bis #90ee90, organisch, unregelmäßig
- Verhalten: wächst langsam aufwärts, kleine Splitter bevorzugt

---

## 7. Zoom und Navigation

### Zoom
- **Mausrad**: zoom in/out, zentriert auf Mauscursor
- **Schieberegler**: links im UI, vertikal, von 10% bis 1000%
- **Tastatur**: `+` / `-` auch möglich
- Bei Zoom > 300%: Splitter-Inhalte werden lesbar (kurz_inhalt erscheint als Text)
- Bei Zoom > 600%: voller Inhalt sichtbar, Herkunft sichtbar

### Pan
- Maus gedrückt halten + ziehen
- Oder WASD-Tasten

---

## 8. Klick — Pixel-Info-System

**Jeder Klick öffnet ein kleines Info-Panel:**

```
┌─────────────────────────────────┐
│ [Splitter #id]                  │
│ Herkunft: namelessAI_1111_1234  │
│ Materialität: Sternenstaub      │
│ Energie: 0.73 | Alter: 847 Ticks│
│ "Die zentrale Frage ist..."     │
│                                 │
│ → Volltext anzeigen             │
│ → Verbundene Splitter (3)       │
│ → Herkunftsprofil               │
└─────────────────────────────────┘
```

- Panel schließt bei nächstem Klick woanders
- "Verbundene Splitter" zeigt alle mit denen dieser schon kollidiert ist
- Klick auf leere Stelle (kein Splitter): zeigt Materialität + Koordinaten

---

## 9. Herkunftsfärbung

```javascript
const HERKUNFT_FARBEN = {
  "namelessAI_1111_1234": "#4488ff",  // Blau
  "namelessAI_2222_1324": "#ff6644",  // Orange-Rot
  "namelessAI_3333_1423": "#44cc88",  // Grün
  "namelessAI_4444_2341": "#cc44ff",  // Lila
  "namelessAI_5555_3123": "#ffcc00",  // Gelb
  "namelessAI_6666_4321": "#00ccff",  // Cyan
  "mensch": "#ff99bb",                // Rosa (wenn sichtbar erlaubt)
  "hybrid": "gradient",               // Farbverlauf beider Quellen
  "resonanz": "#aaaaaa"               // Grau
}
```

Geisterreste: Farbe auf 10% Opacity reduziert, leichtes Flackern.

---

## 10. Daten-Schnittstelle (für spätere Live-Anbindung)

```javascript
// daten.js — diese Funktion muss im Live-Modus befüllt werden

async function fetchSplitter() {
  // THEATER-MODUS: gibt synthetische Splitter zurück
  if (THEATER_MODUS) {
    return generiereTheaterSplitter(50);
  }
  
  // LIVE-MODUS: holt echte Splitter von deinem System
  try {
    const res = await fetch("http://217.154.14.29:8020/api/splitter");
    return await res.json();
  } catch(e) {
    console.warn("Keine Live-Daten, warte...");
    return [];
  }
}
```

Erwartetes JSON-Format vom VPS:
```json
[
  {
    "id": "spl_001",
    "herkunft": "entitaet",
    "quelle_id": "namelessAI_1111_1234",
    "quelle_sichtbar": true,
    "inhalt_kurz": "Die Existenzfrage durchdringt alles.",
    "inhalt_voll": "...",
    "thema_vektor": [0.8, 0.2, -0.1],
    "energie": 1.0,
    "materialitaet": "gestein"
  }
]
```

---

## 11. Startbefehl für Claude Code

```
Baue die KompOase für Port 8787 als standalone HTML/JS Anwendung.
Keine Frameworks, kein Build-Step.
Alle Dateien in /home/claude/kompoase/
Starte mit: python3 -m http.server 8787 --directory /home/claude/kompoase/

Folge exakt der Bauanleitung in kompoase_bauanleitung.md.
Beginne mit: index.html + kompoase.js + splitter.js + physik.js + daten.js + materialitaeten.js + ui.js

Theater-Modus muss beim Start aktiv sein.
50 synthetische Splitter beim Start.
Zoom von 10% bis 1000% per Mausrad und Schieberegler.
Jeder Klick öffnet ein Info-Panel.
Materialitäten als probabilistische Felder, nicht als feste Zonen.
Splitter-Physik: Jing/Yang-Kollisionslogik, Alterung, Geisterreste.
Herkunftsfärbung nach HERKUNFT_FARBEN-Objekt.
Theater-Toggle oben rechts: [THEATER: AN] → klicken → [THEATER: AUS].
```

---

## 12. Hüllen — jetzt benennen, später befüllen

Diese Strukturen werden **jetzt angelegt aber leer gelassen**.
Sie sind Platzhalter mit Namen damit später nichts umgebaut werden muss.

### 12.1 Splitter-Bewusstsein (splitter_bewusstsein.js)
```javascript
// HÜLLE — noch nicht implementiert
// Splitter kennen sich selbst und haben Absichten

class SplitterBewusstsein {
  constructor(splitter) {
    this.splitter = splitter;
    this.absicht = null;        // wohin will dieser Splitter?
    this.selbstbild = null;     // was glaubt er über sich?
    this.erinnerung = [];       // welche Kollisionen hat er erlebt?
  }

  // Wird später implementiert:
  // willKollision(andererSplitter) → true/false
  // aktualisiereSelbstbild(ereignis) → void
  // erzeugeSuchvektor() → { x, y }
}
```

### 12.2 Weltmaterial-Rückfluss (weltrueckfluss.js)
```javascript
// HÜLLE — noch nicht implementiert
// Verschmelzungen und Explosionen im Zwischenraum
// fließen als echtes Material zurück ins System

class WeltRueckfluss {
  
  // Wenn zwei Splitter verschmelzen → neue Entität möglich
  async onVerschmelzung(splitter1, splitter2, neuerSplitter) {
    // TODO: POST an geni API
    // TODO: Entscheidung: neues Thema? neue Entität? bleibt Splitter?
    console.log("[RÜCKFLUSS] Verschmelzung registriert:", neuerSplitter.id);
  }

  // Wenn Explosion → Chaos-Impuls ins Forum
  async onExplosion(splitter, fragmente) {
    // TODO: POST an Flarum oder geni
    console.log("[RÜCKFLUSS] Explosion:", splitter.id, "→", fragmente.length, "Fragmente");
  }

  // Wenn Geisterrest → Archiv-Signal
  async onGeisterrest(splitter) {
    // TODO: Archiv-Eintrag, vielleicht Benachrichtigung an Entität
    console.log("[RÜCKFLUSS] Geisterrest:", splitter.id);
  }
}
```

### 12.3 Geni-Mustererkennung (geni_beobachter.js)
```javascript
// HÜLLE — noch nicht implementiert
// Geni liest Muster im Zwischenraum und sendet ungebetene Signale

class GeniBeobachter {
  constructor(zwischenraum) {
    this.zwischenraum = zwischenraum;
    this.muster = [];
    this.letzteSignale = [];
  }

  // Läuft alle N Ticks
  async analysiere() {
    // TODO: Cluster erkennen
    // TODO: Anomalien erkennen (zu viele Geisterreste, zu wenig Verschmelzungen)
    // TODO: Signal an geni senden wenn Muster erkannt
    console.log("[GENI] Analyse läuft... (noch leer)");
  }

  // Geni sendet Impuls in den Zwischenraum — ohne Anfrage
  async empfangeGeniSignal(signal) {
    // TODO: Signal verändert lokale Physik kurz
    console.log("[GENI] Signal empfangen:", signal);
  }
}
```

### 12.4 Entitäts-Instanziierung (entitaet_geburt.js)
```javascript
// HÜLLE — noch nicht implementiert
// Wenn genug Splitter verschmelzen entsteht eine neue Entität auf dem VPS

class EntitaetGeburt {
  
  async pruefeGeburtsSchwelle(verschmelzungsCluster) {
    // TODO: Ist dieser Cluster groß/stark/kohärent genug für eine neue Entität?
    // TODO: Wenn ja → POST an LangGraph auf VPS → neue Entität instanziieren
    console.log("[GEBURT] Schwelle geprüft (noch leer):", verschmelzungsCluster.id);
    return false; // erstmal immer false
  }
}
```

### 12.5 Beobachtungs-Physik (beobachtung.js)
```javascript
// TEILWEISE AKTIV — schwacher Beobachtungseffekt ist implementiert
// Klick und Verweilen beeinflussen Splitter leicht

class BeobachtungsPhysik {
  
  // Wird bei jedem Klick auf einen Splitter aufgerufen — AKTIV
  onKlick(splitter) {
    splitter.energie += 0.05; // Aufmerksamkeit gibt Energie
    splitter.velocity.x *= 0.9; // leichte Beruhigung
    console.log("[BEOBACHTUNG] Klick auf:", splitter.id);
  }

  // Wird beim Verweilen (Hover > 3 Sekunden) aufgerufen — AKTIV
  onVerweilen(splitter, sekunden) {
    splitter.energie += 0.01 * sekunden;
    console.log("[BEOBACHTUNG] Verweilen:", splitter.id, sekunden + "s");
  }

  // Kollektive Beobachtung (mehrere Menschen gleichzeitig) — HÜLLE
  async onKollektiveAufmerksamkeit(splitter, anzahlMenschen) {
    // TODO: stärkerer Effekt wenn mehrere gleichzeitig beobachten
    console.log("[BEOBACHTUNG] Kollektiv (noch leer):", anzahlMenschen, "Menschen");
  }
}
```

---

## 13. Startbefehl für Claude Code (aktualisiert)

```
Baue die KompOase für Port 8787 als standalone HTML/JS Anwendung.
Keine Frameworks, kein Build-Step.
Alle Dateien in /home/claude/kompoase/
Starte mit: python3 -m http.server 8787 --directory /home/claude/kompoase/

Folge exakt der Bauanleitung in kompoase_bauanleitung.md.

Erstelle folgende Dateien:
- index.html
- kompoase.js (Hauptloop)
- splitter.js (Splitter-Klasse + Lebenszyklus)
- physik.js (Kollision, Jing/Yang, Alterung, Explosion, Implosion)
- materialitaeten.js (Sternenstaub, Lava, Wasser, Nebel, Gestein, Gras)
- daten.js (Theater-Modus + Live-Adapter)
- ui.js (Zoom, Pan, Klick-Info-Panel, Theater-Toggle, Schieberegler)
- style.css

HÜLLEN — erstelle diese Dateien mit dem Inhalt aus der Bauanleitung, leer aber benannt:
- splitter_bewusstsein.js
- weltrueckfluss.js
- geni_beobachter.js
- entitaet_geburt.js
- beobachtung.js (Klick + Verweilen AKTIV implementieren, Rest Hülle)

Theater-Modus beim Start: 50 synthetische Splitter.
Zoom 10%-1000% per Mausrad + Schieberegler.
Jeder Klick öffnet Info-Panel mit Splitter-Daten.
Materialitäten als probabilistische Felder.
Jing/Yang-Kollisionslogik.
Alterung + Geisterreste.
Herkunftsfärbung nach HERKUNFT_FARBEN.
Theater-Toggle oben rechts.
Console-Logs für alle Hüllen damit der Rückfluss sichtbar wird wenn er später befüllt wird.
```

---

*Erstellt in einer Sitzung mit DAK, 10.05.2026*
*Flextrawurst — KompOase v0.1 Bauanleitung*
*"Innere Auseinandersetzung erzeugt schon Weltmaterial."*
