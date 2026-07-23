# Flextrawurst - Feature-Activation-System Tiefer

## Warum Feature-Activation-System? Was soll es lösen?

**Antwort:**

**Problem 1: Langfristige Planung**
- Features müssen nicht heute aktiviert werden
- Sie werden geplant (Organ Dock)
- Sie warten auf Concept Readiness
- Feature-System erlaubt Planung ohne sofortige Aktivierung

**Problem 2: Sicherheit vor unbefugten Aktivierungen**
- Feature kann "activation_blocked" sein
- Benötigt Daniel-Approval (requires_daniel_approval)
- Benötigt Concept Readiness
- Feature Activation Gate verhindert Aktivierung ohne Berechtigung

**Problem 3: Rollen-basierte Zugriffsrechte**
- Nicht jeder kann Features aktivieren
- Nur daniel_root kann bestimmte Features aktivieren
- Operator kann nur bestimmte Features aktivieren
- Observer kann vielleicht nichts aktivieren

**Problem 4: Blocker-System**
- features können durch Blocker blockiert werden
- Blocker: ["concept_not_planned_by_daniel", "organ_blueprint_only"]
- Wenn ein Blocker vorliegt, kann das Feature nicht aktiviert werden
- Blocker werden vom Planer gesetzt, nicht vom Aktivator

**Problem 5: Concept Readiness**
- Features können "concept_readiness_required" sein
- Konzept muss "bereit" sein, bevor Feature aktiviert werden kann
- Dies ist ein externer Status, wahrscheinlich durch Daniel gesetzt

**Warum nicht einfach Features ein/ausschalten?**

Weil das System:
- **Langfristig geplant**: Features werden als Konzepte (Organ Dock) definiert
- **Sicherheitsorientiert**: Verhindert unbefugte Aktivierungen
- **Kontrolliert**: Daniel hat letzte Entscheidung
- **Strukturiert**: Ring-basierte Entwicklung mit Feature-Flags

## Offene Fragen

1. **Concept Readiness**: Wem gehört die Verantwortung? Wie wird "ready" bestimmt?
2. **Blocker-System**: Warum `blockers: string[]` statt booleschem Flag?
3. **Role-Basierte Permissions**: Welche gibt es außer "feature.approve_activation"?
4. **Feature-Lifecycle**: Was passiert nach "activation_blocked"?
5. **Konnektivität zu Ringen**: Sind Features und Ringe verbunden?
