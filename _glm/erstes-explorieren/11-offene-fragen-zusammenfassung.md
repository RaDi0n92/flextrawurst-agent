# Flextrawurst - Offene Fragen Zusammenfassung

## Beantwortete Fragen

1. ✅ **Wie entstehen die Ringe?** - Ring-basierte Entwicklung: Planung (docs/XX_) → Implementierung (kernel/src/) → Testen → Documentation (RING_INDEX.md)
2. ✅ **Unterschied Runtime-Ring und Governance-Ring?** - Runtime = echte Aktivierung (Ring 1, 13, 14), Governance = Kontrolle/Gates/Locks
3. ✅ **Ring 22 Process Observatory?** - Plan für Prozesskamera zur Beobachtung aller Systemwesen als Prozesskörper (GENI, dak+gord-system, Entity Slots, Reader/Writer/Runner)
4. ✅ **Was ist der eigentliche Zweck von Flextrawurst?** - Weltbetriebssystem für Gedächtnis und Kontrolle (Gedächtnis-System, Kontrolle-System, Architektur-Laboratorium, Gedankenexperiment)
5. ✅ **Wer hat Flextrawurst entwickelt?** - Daniel selbst, Laufendes Projekt, Ring-basierte Entwicklung
6. ✅ **Wie wird das System genutzt?** - Doku-Lesen (RING_INDEX.md, HANDOFF_CAPSULE.md), Status-Prüfen, Auftrag abwarten, Testen, Kommunikation

### Technische Fragen

7. ✅ **Rolle von GENI?** - perception_layer, memory_perception, ist ein canonical process body im Ring 22
8. ✅ **Rolle von dak+gord-system?** - dialogue_core, dialogue_coordination, ist ein canonical process body im Ring 22
9. ✅ **Rolle von entity slots?** - 6 entities (namelessAI Flarum-Wesen), status: pre_einzug, sind Träger ohne Bewohner
10. ✅ **Was soll Feature-Activation-System lösen?** - Langfristige Planung (Organ Dock), Sicherheit vor unbefugten Aktivierungen, Rollen-basierte Zugriffsrechte, Blocker-System, Concept Readiness
11. ✅ **Was ist der Zweck von ConceptGuard?** - Validiert Sprache und Konzepte, verhindert verbotene Muster wie "Wesen leben", "Flarum ist Flextrawurst", konsequente Terminologie
12. ✅ **Was ist der Zweck von Organ Dock?** - Future Concept Registry für geplante Konzepte, Concept Readiness System, Blueprint-System, Sicherheit vor ungeplanten Aktivierungen
13. ✅ **Wie funktionieren Sub-Ringe (22abc, 22d, 22i, 22j, 22m)?** - Alle sind Teil von Ring 22 (Process Observatory) mit spezifischen Zwecken: Foundation, Static Preview, Browser Access, Interactive, KompOase Vorform
14. ✅ **Wie entstehen die Ringe wirklich?** - Konzeptionelle Bereiche, nicht physische Verzeichnisse, durch Ring-Index dokumentiert

### Offene Fragen (noch nicht beantwortet)

15. **Concept Readiness:** Wem gehört die Verantwortung? Wie wird "ready" bestimmt?
16. **Blocker-System:** Warum `blockers: string[]` statt booleschem Flag?
17. **Role-Basierte Permissions:** Welche gibt es außer "feature.approve_activation"?
18. **Feature-Lifecycle:** Was passiert nach "activation_blocked"? Kann ein Feature deaktiviert werden?
19. **Konnektivität zu Ringen:** Sind Features und Ringe verbunden? Welche Ringe haben welche Features?
20. **Ring 21:** Ring 21 ist Build Discipline, aber was genau ist das?
21. **Ring 23:** Was ist Ring 23 (Surface Ring)?
22. **Ring 24:** Was ist Ring 24 (Multiple Sub-Ringe für UI)?

## Offene Fragen von den anderen Dokumenten

1. **Genau wie die fragen bei...** (dies ist nicht spezifiziert)
2. **Wo sind die Ursprungsdokumente (RING_INDEX.md, HANDOFF_CAPSULE.md)?** - gefunden
3. **Wie wird das System gebaut?** - unbekannt
4. **Wie wird das System betrieben?** - unbekannt
5. **Wie funktionieren die anderen Ringe?** - unbekannt

## Zusammenfassung

**Beantwortet:**
- Ring-Entstehung und -Zweck
- Runtime vs Governance-Ring
- Ring 22 Process Observatory
- Zweck von Flextrawurst
- GENI, dak+gord-system, entity slots
- Feature-Activation-System
- ConceptGuard und Organ Dock
- Sub-Ringe (22abc bis 22m)

**Offen:**
- Concept Readiness Verantwortung
- Blocker-System-Details
- Role-Basierte Permissions
- Feature-Lifecycle
- Konnektivität Features-Ringe
- Build/Operational-Details
- Weitere Ringe (23, 24)
