# Flextrawurst - ConceptGuard und Organ Dock Explorations-Dokument

## ConceptGuard - Zweck

**Was macht ConceptGuard?**

ConceptGuard validiert Sprache und Konzepte innerhalb von Flextrawurst und verhindert verbotene Muster.

**Beispiele für verbotene Muster:**
1. /eingezogene\w* Wesen/i → Slots sind keine Wesen, sondern kanonische Entitätsslots
2. /lebende Wesen/i → Presence Pulse erzeugt kein Leben
3. /Wesen leben/i → Slots leben nicht
4. /Bewohner eingezogen/i → Seed ≠ Einzug
5. /presence_pulse bedeutet Leben/i → Presence Pulse ist ein Weltpuls, kein Lebenszeichen
6. /Seed bedeutet Einzug/i → Seed registriert einen Slot, erzeugt aber keinen Einzug
7. /Import bedeutet Einzug/i → Import ≠ Einzug
8. /Flarum-Post ist Live-Handlung/i → Importierte Posts sind keine Live-Handlungen
9. /Account ist Bewohner/i → Forum-Account ≠ eingezogener Bewohner
10. /Slot ist Wesen/i → Slot ≠ Wesen
11. /Console ist UI/i → Read-only Console Model ≠ UI
12. /CameraModel ist Renderer/i → CameraModel ≠ Renderer
13. /Visualisierung ist Deko/i → Keine dekorativen Visuals
14. /Graph ist Hintergrund/i → Graph ≠ Hintergrunddekoration
15. /Flarum ist Flextrawurst/i → Flarum ≠ Flextrawurst

**Zweck:**
- Konsequente Terminologie
- Klare Abgrenzung zwischen Konzepten
- Vermeidung von fälschlicherweise "lebendigen" Wesen
- Klare Herkunftsnachweise (Provenienz)

**Welche Bereiche sind betroffen?**
- Geni
- KompOase
- Andere Prozess-Körper
- Dokumentationen
- UI-Elemente

## Organ Dock - Zweck

**Was macht Organ Dock?**

Organ Dock ist ein **Future Concept Registry** - ein definierter Ort für Konzepte, die noch nicht implementiert sind.

**Ziele:**
1. **Blueprint-System**: Definitionen von Organsystemen
2. **Future Concepts**: Konzepte, die geplant sind, aber noch nicht "bereit"
3. **Concept Readiness**: Konzepte müssen "ready" sein, bevor sie aktiviert werden können
4. **Prevention**: Verhindert unbefugtes Aktivieren von nicht bereiten Features

**Status-System:**
- Organ Readiness: ready = false für alle im Moment
- OrganBlueprint: implementation_forbidden für viele

**Verbindung zu Feature-System:**
- Feature Activation braucht Concept Readiness
- Organ Dock ist die Quelle für Concept Readiness
- Feature Flags verweisen auf source_blueprint_id

**Zweck:**
- Langfristige Planung
- Sicherheit vor ungeplanten Aktivierungen
- Klare Zuständigkeiten (Concept Readiness liegt bei Daniel)

## Offene Fragen

1. **ConceptGuard**: Wer validiert ConceptGuard-Regeln? Wann werden sie aktualisiert?
2. **Organ Dock**: Wie wird "Concept Readiness" bestimmt? Wer besitzt diese Zuständigkeit?
3. **Language Discipline**: Wie wird konsequent durchgesetzt? Ist das Teil eines Ringes?
4. **Integration**: Wie hängen ConceptGuard und Organ Dock in den World-Engine ein?
