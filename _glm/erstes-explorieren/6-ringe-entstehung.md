# Flextrawurst - Ring-Entstehung und -Zweck Explorations-Dokument

## Ring-Entstehung

### Wie entstehen die Ringe?

**Antwort:** Ringe entstehen durch eine klare Entwicklungsstruktur mit spezifischem Zweck und Artefakten.

**Struktur:**
1. Jeder Ring hat eine eindeutige Nummer (Ring 1 bis Ring 21+)
2. Jeder Ring hat einen Namen (World Engine Core, Scenario Inspection, Global Governance)
3. Jeder Ring hat eine Phase (doku, implementiert, aktiv)
4. Jeder Ring hat ein Kernziel und Hauptartefakte
5. Jeder Ring hat Commit-Historie

**Entstehungsprozess:**
1. **Planung (Doku-Phase)**: Ring wird im docs/Verzeichnis als Plan dokumentiert (docs/00_ bis docs/24_)
2. **Implementierung**: Code wird im kernel/src/ oder entsprechenden Artefakten erstellt
3. **Testen**: Tests werden geschrieben und in das Test-System integriert
4. **Documentation**: Ring-Tabelle in RING_INDEX.md aktualisiert

**Aktuelles Beispiel:**
- Ring 21 ist gerade in der Doku-Phase (kein Code, nur Dokumentation)
- Ring 20 ist abgeschlossen (commit 459cf09: "feat(governance): add global governance matrix and approval workflow")

### Was ist der Unterschied zwischen einem Runtime-Ring und einem Governance-Ring?

**Antwort:** Das System hat klare Unterscheidung zwischen **Runtime** und **Kontrolle/Governance**.

**Kontrolle-Elemente:**
- Eventstream
- Governance
- Search
- WorldRun
- Admin

**Regel aus HANDOFF_CAPSULE.md:**
> "Eventstream, Governance, Search, WorldRun, Admin: Kontroll- und Prüfgrundlagen — keine Runtime-Aktivierung"

**Das bedeutet:**
- **Runtime-Ringe**: Echte Aktivierung des Systems (Ring 1: World Engine Core, Ring 13: World Inspection Export, Ring 14: Static Worldview Preview)
- **Kontrolle-Ringe**: Prüf- und Steuerungsgrundlagen ohne Runtime-Aktivierung (Governance, Gates, Locks)

**Konkret:**
- **Runtime**: Realen Welt-Tick durchführen
- **Kontrolle**: Aktivitäten überwachen, blockieren, genehmigen, nachvollziehen

### Was bewirkt Ring 22 - das Process Observatory?

**Antwort:** Ring 22 ist der Prozesskamera-Plan, der zeigt wie alle heutigen Systemwesen als sichtbare Prozesskörper aussehen.

**Ziel:**
> "Alle heutigen Systemwesen als sichtbare, zoombare Prozesskörper"

**Wesen:**
- GENI (perception_layer)
- dak+gord-system (dialogue_core)
- Systemweiser
- Sechs namelessAI-Flarum-Wesen
- Reader/Writer/Runner (später)

**Was sichtbar wird:**
- Zustand
- Letzte Aktion
- Modus (denkt/liest/schreibt/wartet/blockiert)
- Datei-/Forum-/Event-/Audit-/Search-/Governance-/WorldRun-Bezug

**Wichtig:** "Nicht als neue Bewohner — als beobachtbare laufende Prozesse."

### Was ist der eigentliche Zweck von Flextrawurst?

**Antwort:** Flextrawurst ist ein **Weltbetriebssystem** für Daniels Gedächtnis und Kontrolle.

**Zweck-Mix:**
1. **Gedächtnis-System**: Replay, Provenienz, Continuity, Memory Candidate Dossier
2. **Kontrolle-System**: Governance, Gates, Locks, Approval-Workflow
3. **Architektur-Laboratorium**: Experimentelle Architektur für komplexe Systeme
4. **Gedankenexperiment**: "Welt" als abstrakte Struktur mit Entity Slots

**Warum:**
- Daniel will sein Gedächtnis systematisieren
- Er braucht eine Kontrolle für komplexe Abläufe
- Er experimentiert mit Architekturen für kognitive Strukturen

### Wer hat Flextrawurst entwickelt und warum?

**Antwort:**
- **Entwickler:** Daniel selbst
- **Status:** Laufendes Projekt
- **Ziel:** Weltbetriebssystem mit Gedächtnis und Kontrolle
- **Plan:** Ring-basierte Entwicklung (Ring 21 ist Build Discipline als Doku-Fundament)
- **Warum:** Daniel braucht eine systematische Struktur für sein Gedächtnis und seine Kontrolle

### Wie wird das System genutzt?

**Antwort:** Daniels tägliche Verwendung:
1. **Doku-Lesen:** Bei `/clear`, Accountwechsel, neuer Session zuerst RING_INDEX.md und HANDOFF_CAPSULE.md lesen
2. **Status-Prüfen:** Ring-Index und Tests (1336/1336 grün) lesen
3. **Auftrag abwarten:** Nicht automatisch weiterbauen ohne explizite Daniel-Freigabe
4. **Testen:** Neue Tests nur für neue Verantwortung
5. **Kommunikation:** Bei Unsicherheit: Status prüfen, nicht raten

## Nächste Fragen

Jetzt gehe ich zu den technischen Fragen:
- Welche Rolle spielen GENI, dak+gord-system, entity slots?
- Was soll das Feature-Activation-System lösen?
- Was ist der Zweck von ConceptGuard und Organ Dock?
- Wie funktionieren die Sub-Ringe (22abc, 22d, 22i, 22j, 22m)?
