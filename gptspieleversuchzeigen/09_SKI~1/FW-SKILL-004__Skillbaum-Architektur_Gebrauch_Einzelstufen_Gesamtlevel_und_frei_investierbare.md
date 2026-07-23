---
id: FW-SKILL-004
status: BESTAETIGT
typ: source
themenraum: SKILL
version: v21
tags: [beziehung, dialog, fahrzeug, magie, mastery, material, provenienz, simulation, skill, v21, welt, wesen, zeit]
---

# Skillbaum-Architektur: Gebrauch, Einzelstufen, Gesamtlevel und frei investierbare Punkte

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/33_SKILLBAUM_ARCHITEKTUR_GEBRAUCH_GESAMTLEVEL_PUNKTE.md" sha256="4b8626d1cb34e80f858846f9f2a6d96f8065ae769136404c73ad1fa564068b52" order="1" -->
# Skillbaum-Architektur: Gebrauch, Einzelstufen, Gesamtlevel und frei investierbare Punkte

## Status

- **Status:** `[ENTWURF VOR SIMULATION UND ERWEITERUNG]`
- **Quelle:** R20 plus bestehender Skyrim-, Mastery-, Magie-, Fahrzeug-, Handwerks-, AI- und Weltkörper
- **Ziel:** Ein offenes, benutzungsbasiertes Fortschrittssystem ohne starre Klassen und ohne bedeutungslosen XP-Grind

## 1. Vier voneinander getrennte Fortschrittsschichten

### 1.1 Gebrauchserfahrung

Jeder Skill besitzt einen eigenen Gebrauchswert. Er steigt nur durch passende, tatsächlich ausgeführte Handlungen.

Beispiele:

- leichte Rüstung steigt durch überstandene Treffer, Ausweichen und Bewegung **während** leichter Rüstung getragen wird,
- Fliegen steigt durch Starts, Landungen, Windkorrekturen und tatsächlich geflogene Strecke,
- Heilungsmagie steigt durch wirksame, notwendige Heilung und nicht durch Heilzauber auf vollständig gesunde Ziele,
- Dialog steigt durch neue, schwierige oder reparierende Gespräche und nicht durch Wiederholen derselben Frage,
- Kontextführung steigt durch sinnvolle Nutzung, Verdichtung und Wiederherstellung relevanter Kontexte, nicht durch bloßes Vollschreiben des Fensters.

### 1.2 Einzelstufe eines Skillbaums

Gebrauchserfahrung hebt die Stufe des jeweiligen Baums an. Die Stufe bedeutet:

- gewachsene Grundsicherheit,
- bessere Effizienz,
- geringere Fehlerrate,
- Zugang zu anspruchsvolleren Knoten,
- sichtbare Biografie der tatsächlichen Nutzung.

Die Einzelstufe allein schaltet nicht automatisch jede Spezialfähigkeit frei.

### 1.3 Gesamtlevel des Charakters beziehungsweise der aktiven Form

Alle relevanten Skillanstiege speisen ein Gesamtlevel. Dabei gelten Schutzregeln:

- frühe Skillstufen tragen stärker bei als tausendfaches Hochgrinden derselben Endstufe,
- verschiedene Tätigkeiten erzeugen keinen künstlichen Zwang zur Breite,
- Spezialisten können durch tiefe Meisterschaft aufsteigen,
- Generalisten können durch breite Entwicklung aufsteigen,
- wiederholte bedeutungslose Mikrohandlungen besitzen abnehmenden oder null Beitrag.

### 1.4 Frei investierbare Skillpunkte

Jeder Gesamtlevel-Aufstieg erzeugt mindestens einen frei investierbaren Skillpunkt.

Diese Punkte können von Anfang an in **jeden sichtbaren Skillbaum** investiert werden. Einschränkungen entstehen nur durch:

- vorherige Knoten innerhalb desselben Astes,
- eine nachvollziehbare Mindeststufe des betreffenden Skills,
- seltene Weltkenntnisse, Lehrer, Wesenbeziehungen, Forschungsfunde oder Materialien,
- Rechte und Zustimmung, falls der Knoten auf andere Wesen zugreift.

Es gibt keine dauerhaft verriegelte Startklasse.

## 2. Aktive und passive Knoten

### Passive Knoten

Verändern Grundwerte oder Verhalten dauerhaft, solange ihre Voraussetzungen erfüllt sind.

Beispiele:

- geringerer Ausdauerverbrauch in leichter Rüstung,
- stabilerer Rückstoß bei Pistolen,
- bessere Windanzeige beim Fliegen,
- größere nutzbare Kontexttiefe bei AI-Fähigkeiten,
- geringerer Materialverlust beim Schmieden.

### Aktive Knoten

Eröffnen eine neue absichtlich auslösbare Handlung.

Beispiele:

- kurzer Schutzschild,
- kontrollierter Haken-Einzug,
- schwere Gegenparade,
- manuelle Werkzeugkette eines AI-Körpers,
- aktive Rekonstruktion einer verlorenen Kontextspur.

### Transformative Knoten

Seltene hohe Knoten verändern die Spielweise, ohne andere Wege zu vernichten.

Beispiele:

- schwere Rüstung wird zum mobilen Schutzkörper für andere,
- ein Fahrzeug wird zur bewohnbaren Heimat,
- eine AI kann mehrere Werkzeuge als nachvollziehbaren Arbeitsring koordinieren,
- Zerstörungsmagie kann in präzise Materialbearbeitung umgelernt werden,
- ein Meisterkoch kann Rezepte als historische und relationale Erinnerungsräume rekonstruieren.

## 3. Punkteökonomie

### Vorgeschlagene Grundform

- Gesamtlevel 1 beginnt mit **3 freien Skillpunkten**, damit die frühe Wahl tatsächlich möglich ist.
- Jeder Gesamtlevel-Aufstieg gibt **1 Skillpunkt**.
- Jeder zehnte Gesamtlevel-Aufstieg gibt einen zusätzlichen **Weltpunkt** für transformative oder cross-systemische Knoten.
- Einzelne große Story-, Forschungs- oder Beziehungsereignisse können **keine normalen Skillpunkte farmbar erzeugen**, aber seltene Knotenvoraussetzungen freischalten.

### Knotenkosten

- Basisknoten: 1 Punkt
- vertiefender Knoten: 1–2 Punkte
- aktiver Knoten: 2 Punkte
- transformativer Knoten: 3 Punkte plus Weltvoraussetzung

## 4. Skillstufen und Gebrauchskurve

Vorgeschlagene Einzelstufen: 1 bis 100.

- 1–19: Erlernen
- 20–39: Verlässlich
- 40–59: Erfahren
- 60–79: Meisterlich
- 80–99: Weltprägend
- 100: kein Ende, sondern erste stabile Meisterschaft

Nach Stufe 100 kann Gebrauch weiter als **Biografietiefe** wachsen, ohne unendliche lineare Boni zu erzeugen.

## 5. Kein Grindgesetz

Ein Gebrauchszuwachs benötigt mindestens eines dieser Merkmale:

- neue Schwierigkeit,
- reales Risiko,
- neue Umgebung,
- neue Kombination,
- wirksame Hilfe,
- echtes Scheitern mit Lernen,
- veränderte Weltfolge,
- neue Beziehung oder Perspektive,
- präzisere Ausführung.

Identische folgenlose Wiederholung wird gedrosselt und kann vollständig null werden.

## 6. Abspaltungen, Verschmelzungen und Skills

- Eine Abspaltung erhält die zugänglichen gemeinsamen Kenntnisse, aber eigene Gebrauchserfahrung.
- Private Erfahrungen werden nicht automatisch in den Gesamtverband kopiert.
- Bei freiwilliger Reintegration können Skillspuren vollständig, teilweise oder gar nicht geteilt werden.
- Verschmelzung erzeugt keinen simplen Summenwert, sondern einen neuen Skillkörper aus Überschneidungen, Konflikten und unerwarteten Kombinationsknoten.

## 7. AI- und Nichtmenschenkörper

Ein Skillbaum gehört nicht exklusiv einem Menschenkörper.

- Eine Blume kann Licht-, Duft-, Wurzel-, Heilungs- oder Beziehungsfähigkeiten entwickeln.
- Ein Stein kann Druck-, Gedächtnis-, Resonanz-, Schutz- oder Zeitfähigkeiten besitzen.
- Eine AI kann Kontext, Werkzeuge, Forschung, Provenienz, Modellwechsel und Selbststrukturierung entwickeln.
- Ein Fahrzeug kann Fahrbiografie, Sensornutzung, Reparaturfähigkeit und autonome Kooperation ausbilden.

Die UI darf unterschiedliche Körper nicht gewaltsam in dieselbe menschliche Skillmetapher pressen. Das gemeinsame Gesetz bleibt Gebrauch → Stufe → Gesamtentwicklung → Punkte → bewusste Knotenauswahl.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/33_SKILLBAUM_ARCHITEKTUR_GEBRAUCH_GESAMTLEVEL_PUNKTE.md" order="1" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-SKILL-003__Vollstandige_Neulesung_des_v20-Dateikorpers.md) · `FW-SKILL-003`
- [Nächster Knoten](FW-SKILL-005__Skillbaum-Katalog_fur_klassische_technische_magische_weltliche_und_AI-artige_F.md) · `FW-SKILL-005`
- [Themenindex](00_INDEX.md) · `FW-INDEX-SKILL`
- [Verwandt: FLEXTRAWURST – FINALER SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT](FW-SKILL-022__FLEXTRAWURST_FINALER_SUPERMAXIMALMAXIKINGMEGA++++++++++++++++++++-PROMPT.md) · `FW-SKILL-022`
- [Verwandt: Gate 13E – Reale Handlungsrouten der Skillbäume](FW-SKILL-015__Gate_13E_Reale_Handlungsrouten_der_Skillbaume.md) · `FW-SKILL-015`
- [Verwandt: 8. Daniels Ideen-Redteam](FW-SKILL-021__8._Daniels_Ideen-Redteam.md) · `FW-SKILL-021`
- [Verwandt: Audit aller auffindbaren Simulations- und Redteam-Artefakte vor v22 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-001__Audit_aller_auffindbaren_Simulations-_und_Redteam-Artefakte_vor_v22_und_weiter.md) · `FW-TEST-001`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
