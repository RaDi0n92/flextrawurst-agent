---
id: FW-MOVE-023
status: BESTAETIGT
typ: source
themenraum: MOVE
version: v21
tags: [bauen, beziehung, fahrzeug, fragen, kampf, kollision, load, loot, move, playwright, provenienz, quest, redteam, save, test, v21, welt, wesen, zeit]
---

# K045-Q5 · K045 · Fehlurteil × Beziehungen

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_09_FRAGEN_VORHER_NACHHER.md" sha256="2de5b0fdf0248753b5824045428a6ce095944e20e9d3dc59b54aa98bb5c4bdb0" order="2" -->
### K045-Q5 · K045 · Fehlurteil × Beziehungen

**Frage:** Wie wird **Fehlurteil × Beziehungen** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K045-Q6 · K045 · Fehlurteil × Beziehungen

**Frage:** Wie versucht das Redteam, **Fehlurteil × Beziehungen** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Vorbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

### K066-Q1 · K066 · UI/Erklärung × Testmodus

**Frage:** Welche Zustände von **UI/Erklärung** verändern **Testmodus**, und welche Rückwirkung entsteht?

**Vorbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K066-Q2 · K066 · UI/Erklärung × Testmodus

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **UI/Erklärung** und **Testmodus** in Konflikt?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K066-Q3 · K066 · UI/Erklärung × Testmodus

**Frage:** Bei **UI/Erklärung × Testmodus**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K066-Q4 · K066 · UI/Erklärung × Testmodus

**Frage:** Bei **UI/Erklärung × Testmodus**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K066-Q5 · K066 · UI/Erklärung × Testmodus

**Frage:** Wie wird **UI/Erklärung × Testmodus** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K066-Q6 · K066 · UI/Erklärung × Testmodus

**Frage:** Wie versucht das Redteam, **UI/Erklärung × Testmodus** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Vorbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

### K099-Q1 · K099 · Recht × Bauen

**Frage:** Welche Zustände von **Recht** verändern **Bauen**, und welche Rückwirkung entsteht?

**Vorbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K099-Q2 · K099 · Recht × Bauen

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Recht** und **Bauen** in Konflikt?

**Vorbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

### K099-Q3 · K099 · Recht × Bauen

**Frage:** Bei **Recht × Bauen**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Vorbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

### K099-Q4 · K099 · Recht × Bauen

**Frage:** Bei **Recht × Bauen**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Vorbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K099-Q5 · K099 · Recht × Bauen

**Frage:** Wie wird **Recht × Bauen** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K099-Q6 · K099 · Recht × Bauen

**Frage:** Wie versucht das Redteam, **Recht × Bauen** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Vorbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

### K115-Q1 · K115 · Landfahrzeuge × Körper

**Frage:** Welche Zustände von **Landfahrzeuge** verändern **Körper**, und welche Rückwirkung entsteht?

**Vorbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K115-Q2 · K115 · Landfahrzeuge × Körper

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Landfahrzeuge** und **Körper** in Konflikt?

**Vorbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

### K115-Q3 · K115 · Landfahrzeuge × Körper

**Frage:** Bei **Landfahrzeuge × Körper**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Vorbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

### K115-Q4 · K115 · Landfahrzeuge × Körper

**Frage:** Bei **Landfahrzeuge × Körper**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Vorbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K115-Q5 · K115 · Landfahrzeuge × Körper

**Frage:** Wie wird **Landfahrzeuge × Körper** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K115-Q6 · K115 · Landfahrzeuge × Körper

**Frage:** Wie versucht das Redteam, **Landfahrzeuge × Körper** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Vorbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

### K120-Q1 · K120 · Luftfahrzeuge × Körper

**Frage:** Welche Zustände von **Luftfahrzeuge** verändern **Körper**, und welche Rückwirkung entsteht?

**Vorbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K120-Q2 · K120 · Luftfahrzeuge × Körper

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Luftfahrzeuge** und **Körper** in Konflikt?

**Vorbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

### K120-Q3 · K120 · Luftfahrzeuge × Körper

**Frage:** Bei **Luftfahrzeuge × Körper**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Vorbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

### K120-Q4 · K120 · Luftfahrzeuge × Körper

**Frage:** Bei **Luftfahrzeuge × Körper**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Vorbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K120-Q5 · K120 · Luftfahrzeuge × Körper

**Frage:** Wie wird **Luftfahrzeuge × Körper** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K120-Q6 · K120 · Luftfahrzeuge × Körper

**Frage:** Wie versucht das Redteam, **Luftfahrzeuge × Körper** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Vorbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

### K156-Q1 · K156 · Aufgaben × Testmodus

**Frage:** Welche Zustände von **Aufgaben** verändern **Testmodus**, und welche Rückwirkung entsteht?

**Vorbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Gameplay muss für ruhige Organisation, Heilung, Waffen-, Rüstungs- und Zauberwechsel anhaltbar sein; Kampf und Loot brauchen Grenzen und Herkunft.

### K156-Q2 · K156 · Aufgaben × Testmodus

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Aufgaben** und **Testmodus** in Konflikt?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K156-Q3 · K156 · Aufgaben × Testmodus

**Frage:** Bei **Aufgaben × Testmodus**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K156-Q4 · K156 · Aufgaben × Testmodus

**Frage:** Bei **Aufgaben × Testmodus**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K156-Q5 · K156 · Aufgaben × Testmodus

**Frage:** Wie wird **Aufgaben × Testmodus** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Vorbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

### K156-Q6 · K156 · Aufgaben × Testmodus

**Frage:** Wie versucht das Redteam, **Aufgaben × Testmodus** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Vorbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

## Nachbau-Gegenprüfung

Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

### D049-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Woher kommt jeder zentrale Baustoff, Energieträger und Verbrauchsstoff?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Ressourcenherkunft“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Ressourcenherkunft“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Ressourcenherkunft“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Ressourcenherkunft“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Ressourcenherkunft“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Ressourcenherkunft“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D049-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Ressourcenherkunft“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie unterscheiden Materialien Bau, Fahrzeug, Körper und Zeitwirkung?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Materialeigenschaften“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Materialeigenschaften“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Materialeigenschaften“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Materialeigenschaften“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Materialeigenschaften“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Materialeigenschaften“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D050-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Materialeigenschaften“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche Maschinen, Berufe, Abfälle und Qualitätsstufen entstehen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Verarbeitung“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Verarbeitung“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Verarbeitung“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Verarbeitung“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Verarbeitung“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Verarbeitung“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D052-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Verarbeitung“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie entstehen, verändern und heilen körperliche Zustände?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Verletzung und Krankheit“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Verletzung und Krankheit“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Verletzung und Krankheit“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Verletzung und Krankheit“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Verletzung und Krankheit“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Verletzung und Krankheit“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D071-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Verletzung und Krankheit“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche biologischen, technischen und hybriden Erweiterungen existieren?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Prothesen und Modifikationen“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Prothesen und Modifikationen“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Prothesen und Modifikationen“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Prothesen und Modifikationen“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Prothesen und Modifikationen“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Prothesen und Modifikationen“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D072-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Prothesen und Modifikationen“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche Konfliktformen reichen von Gespräch bis Gewalt und warum?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Konflikt und Kampf“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Konflikt und Kampf“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Konflikt und Kampf“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Konflikt und Kampf“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Konflikt und Kampf“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Konflikt und Kampf“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D073-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Konflikt und Kampf“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie verändert Können Handlung, Wahrnehmung und Weltzugang?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Meisterschaft“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Meisterschaft“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Meisterschaft“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Meisterschaft“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Meisterschaft“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Meisterschaft“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D090-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Meisterschaft“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`


<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_09_FRAGEN_VORHER_NACHHER.md" order="2" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-MOVE-022__Gate_09_Taktische_Pause_Ausrustung_Kampf_Loot_und_dialogreiche_Nebenquests.md) · `FW-MOVE-022`
- [Nächster Knoten](FW-MOVE-024__Cross-System-Kollisionsmatrix_200_Paare.md) · `FW-MOVE-024`
- [Themenindex](00_INDEX.md) · `FW-INDEX-MOVE`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: Abnahmekriterien Bauring 2 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-010__Abnahmekriterien_Bauring_2_und_weitere_Statusabschnitte.md) · `FW-TEST-010`
- [Verwandt: D134-Q05 · D134 · Testmodus](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-020__D134-Q05_D134_Testmodus.md) · `FW-BUILD-020`
- [Verwandt: D136-Q05 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-021__D136-Q05_Nachbauprufung.md) · `FW-BUILD-021`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
