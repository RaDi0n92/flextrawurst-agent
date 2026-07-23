---
id: FW-WORLD-008
status: BESTAETIGT
typ: source
themenraum: WORLD
version: v21
tags: [bauen, dungeon, fragen, kollision, load, playwright, provenienz, redteam, save, test, v21, welt, wesen, world, zeit]
---

# K066-Q3 · Nachbauprüfung

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_04_FRAGEN_VORHER_NACHHER.md" sha256="2c9a85cf54594d6c19221b079a0e03593044591fcbd7349b8a765ed39b0c3b60" order="3" -->
### K066-Q3 · Nachbauprüfung

**Frage:** Bei **UI/Erklärung × Testmodus**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K066-Q4 · Nachbauprüfung

**Frage:** Bei **UI/Erklärung × Testmodus**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K066-Q5 · Nachbauprüfung

**Frage:** Wie wird **UI/Erklärung × Testmodus** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K066-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **UI/Erklärung × Testmodus** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K099-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Recht** verändern **Bauen**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Drei Tiefen, erschöpfbare Adern, fünf Storyräume, Lebendgestein-Zustimmung und Tiefenbau bestehen 14/14 Tests.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K099-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Recht** und **Bauen** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K099-Q3 · Nachbauprüfung

**Frage:** Bei **Recht × Bauen**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K099-Q4 · Nachbauprüfung

**Frage:** Bei **Recht × Bauen**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Drei Tiefen, erschöpfbare Adern, fünf Storyräume, Lebendgestein-Zustimmung und Tiefenbau bestehen 14/14 Tests.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K099-Q5 · Nachbauprüfung

**Frage:** Wie wird **Recht × Bauen** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K099-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Recht × Bauen** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K102-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Ökologie** verändern **Produktion**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Drei Tiefen, erschöpfbare Adern, fünf Storyräume, Lebendgestein-Zustimmung und Tiefenbau bestehen 14/14 Tests.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K102-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Ökologie** und **Produktion** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K102-Q3 · Nachbauprüfung

**Frage:** Bei **Ökologie × Produktion**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K102-Q4 · Nachbauprüfung

**Frage:** Bei **Ökologie × Produktion**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Drei Tiefen, erschöpfbare Adern, fünf Storyräume, Lebendgestein-Zustimmung und Tiefenbau bestehen 14/14 Tests.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K102-Q5 · Nachbauprüfung

**Frage:** Wie wird **Ökologie × Produktion** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

### K102-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Ökologie × Produktion** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_04_RESULT.json · screenshots_v21/gate04_underworld_dungeon.png`

## Gate-Entscheidung

Alle 102 relevanten Fragen wurden vor und nach dem Bau beantwortet. Der unmittelbare Playwright-Lauf ist bestanden.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_04_FRAGEN_VORHER_NACHHER.md" order="3" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-WORLD-007__Gate_04_Untergrund_Hohlen_Dungeons_Erze_und_Tiefenbau.md) · `FW-WORLD-007`
- [Nächster Knoten](FW-WORLD-009__D137-Q02_Nachbauprufung.md) · `FW-WORLD-009`
- [Themenindex](00_INDEX.md) · `FW-INDEX-WORLD`
- [Verwandt: D134-Q05 · D134 · Testmodus](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-020__D134-Q05_D134_Testmodus.md) · `FW-BUILD-020`
- [Verwandt: D136-Q05 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-021__D136-Q05_Nachbauprufung.md) · `FW-BUILD-021`
- [Verwandt: K045-Q5 · K045 · Fehlurteil × Beziehungen](../07_BEWEGUNG_FAHRZEUGE_KAMPF_LOOT/FW-MOVE-023__K045-Q5_K045_Fehlurteil_Beziehungen.md) · `FW-MOVE-023`
- [Verwandt: K024-Q1 · K024 · Bauen × Ressourcen](../09_SKILLS_MASTERIES_MAGIE_AI/FW-SKILL-010__K024-Q1_K024_Bauen_Ressourcen.md) · `FW-SKILL-010`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
