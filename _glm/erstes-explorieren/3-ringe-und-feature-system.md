# Flextrawurst - Ring-Struktur und Feature-System Explorations-Dokument

## Ring-Struktur Erkenntnisse

### Was Ringe sind
- **Ringe sind nicht physische Verzeichnisse** - sie sind konzeptionelle Bereich/Segmente des Systems
- **Ring 22** ist der wichtigste identifizierte Ring: "Process Observatory Plan"
- Ringe haben Zahlen wie "22abc", "22d", "22i", "22j", "22m" - wahrscheinlich Sub-Ringe oder Varianten

### Ring-Typen (basierend auf Tests)
1. **Ring 1**: Weltbetriebssystem (World Operating System)
2. **Ring 2**: Scenario Inspection
3. **Ring 3**: OS Spine
4. **Ring 4**: Import Console Convergence
5. **Ring 5-7**: Visual Replay Worldview
6. **Ring 8-12**: Origin Start Memory Continuity
7. **Ring 13-15**: Worldblick (WorldInspectionExport, StaticPreview, WorldblickOutput)
8. **Ring 16**: Organ Dock Blueprints (Future Concepts)
9. **Ring 17**: Admin Feature Control
10. **Ring 18**: Deep Search Archaeology
11. **Ring 19**: Worldrun Control Locks
12. **Ring 20**: Global Governance Matrix
13. **Ring 22abc**: Process Camera Foundation
14. **Ring 22d**: Static Process Camera Worldblick
15. **Ring 22i**: Process Camera Browser Preview Access
16. **Ring 22j**: Interactive Static Neural Process Camera
17. **Ring 22m**: KompOase Vorform
18. **Ring 23**: Surface Ring (Leitstand, Weltkarte, UI-Zonen)
19. **Ring 24**: Multiple Sub-Ringe für:
   - Weltoberfläche (HTML)
   - Klicktiefe HTML
   - Deep-Link, Share & Provenienz
   - Wesen-Tab (Substanz/Cyberling-Konsistenz)
   - DENKEN-Tab (Zuständigkeit & UI-Wahrheit)
   - SCREENS-Tab (Prozesskamera & Fokusmodus)
   - KOMPOASE-Tab (Theater, Provenienz, Aufnahme)

## Feature-Activation System

### Feature Registry
- **Feature Flag System** mit: `feature_flag.ts`, `feature_activation_gate.ts`, `feature_deactivation_gate.ts`
- **Feature Registry**: Verwaltet alle Features mit Status, Blockern, Concept-Readiness

### Feature-Status
- **enabled**: Funktioniert normal
- **activation_blocked**: Wartet auf Genehmigung und Concept-Readiness

### Beispiel-Features
1. **Tamagotchi Care Feature** (Cyberling-Pflegesystem) - enabled
2. **Kompoase Space Feature** (KompOase-Raumsystem) - activation_blocked, braucht daniel_approval und concept_readiness
3. **Sleep Cycle Feature** (Schlafzyklus-System) - enabled
4. **Substanz-Modifier Feature** - activation_blocked
5. **Neural Processes** - activation_blocked
6. **Flarum Exporter** - maybe?

### Feature-Locks
- **blockers**: Array von Blocker-Gründen
- **requires_daniel_approval**: Muss Daniel explizit genehmigen
- **requires_concept_readiness**: Konzept muss "bereit" sein

## Organ Dock System

### Konzept
- **Future Concept Registry** - definierter Ort für Konzepte, die noch nicht implementiert sind
- **OrganBlueprints** - Definitionen von Organsystemen
- **OrganReadiness** - Status-System (ready = false für alle im Moment)

### Konzept-Guard
- **ConceptGuard System**: Verhindert verbotene Organ-Dock Muster
- **Ziel**: Sprache und Konzepte innerhalb von Geni, KompOase etc. validieren

## Process Model

### Canonical Process Bodies
- **16 prozess-Körper** (14 benannt + reader/writer/runner)
- **GENI** (perception_layer, memory_perception) - Ring Origin 22
- **dak+gord-system** (dialogue_core, dialogue_coordination) - Ring Origin 22
- **entity_slot bodies** - 6 entities (namelessAI Flarum-Wesen), status: pre_einzug
- Alle haben `is_canonical = true`

### Prozess-Körper-Typen
- perception_layer (GENI)
- dialogue_core (dak+gord-system)
- entity_slot (namelessAI)

## Offene Fragen
1. Wie entstehen die Ringe wirklich? (Software-Feature vs. physisch)
2. Was ist der Unterschied zwischen einem Runtime-Ring und einem Governance-Ring?
3. Was bewirkt Ring 22 - das Process Observatory?
4. Wie funktionieren die Sub-Ringe (22abc, 22d, 22i, 22j, 22m)?
5. Was soll das Feature-Activation-System eigentlich lösen?
6. Was ist der Zweck von ConceptGuard und Organ Dock?
7. Was ist die Verbindung zwischen den Ringen und dem Weltlauf-System?
