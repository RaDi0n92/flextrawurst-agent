---
id: FW-MOVE-021
status: BESTAETIGT
typ: source
themenraum: MOVE
version: v21
tags: [dungeon, fragen, kampf, load, loot, move, playwright, quest, redteam, save, test, v20, v21, welt, wesen, zeit]
---

# D130-Q01 · Nachbauprüfung

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_09_FRAGEN_VORHER_NACHHER.md" sha256="2de5b0fdf0248753b5824045428a6ce095944e20e9d3dc59b54aa98bb5c4bdb0" order="3" -->
### D130-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche Zustände, Ereignisse und privaten Schichten werden wie gespeichert?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Speichern“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Speichern“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Speichern“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Speichern“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Speichern“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Speichern“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D130-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Speichern“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie werden alle Systeme frei erzeugt, verändert, verglichen und zurückgesetzt?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Testmodus“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Testmodus“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Testmodus“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Testmodus“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Testmodus“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Testmodus“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D134-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Testmodus“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie bleiben Testwelten strikt getrennt?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Testisolierung“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Testisolierung“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Testisolierung“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Testisolierung“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Testisolierung“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Testisolierung“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D135-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Testisolierung“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche echten Spielerpfade werden vollständig automatisiert?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Playwright/Automation“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Playwright/Automation“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Playwright/Automation“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Playwright/Automation“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Playwright/Automation“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Playwright/Automation“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### D136-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Playwright/Automation“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K024-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Bauen** verändern **Ressourcen**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K024-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Bauen** und **Ressourcen** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K024-Q3 · Nachbauprüfung

**Frage:** Bei **Bauen × Ressourcen**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K024-Q4 · Nachbauprüfung

**Frage:** Bei **Bauen × Ressourcen**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K024-Q5 · Nachbauprüfung

**Frage:** Wie wird **Bauen × Ressourcen** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K024-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Bauen × Ressourcen** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K045-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Fehlurteil** verändern **Beziehungen**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K045-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Fehlurteil** und **Beziehungen** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K045-Q3 · Nachbauprüfung

**Frage:** Bei **Fehlurteil × Beziehungen**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K045-Q4 · Nachbauprüfung

**Frage:** Bei **Fehlurteil × Beziehungen**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K045-Q5 · Nachbauprüfung

**Frage:** Wie wird **Fehlurteil × Beziehungen** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K045-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Fehlurteil × Beziehungen** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K066-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **UI/Erklärung** verändern **Testmodus**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K066-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **UI/Erklärung** und **Testmodus** in Konflikt?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K066-Q3 · Nachbauprüfung

**Frage:** Bei **UI/Erklärung × Testmodus**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K066-Q4 · Nachbauprüfung

**Frage:** Bei **UI/Erklärung × Testmodus**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K066-Q5 · Nachbauprüfung

**Frage:** Wie wird **UI/Erklärung × Testmodus** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K066-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **UI/Erklärung × Testmodus** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K099-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Recht** verändern **Bauen**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K099-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Recht** und **Bauen** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K099-Q3 · Nachbauprüfung

**Frage:** Bei **Recht × Bauen**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K099-Q4 · Nachbauprüfung

**Frage:** Bei **Recht × Bauen**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K099-Q5 · Nachbauprüfung

**Frage:** Wie wird **Recht × Bauen** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K099-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Recht × Bauen** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K115-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Landfahrzeuge** verändern **Körper**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K115-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Landfahrzeuge** und **Körper** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K115-Q3 · Nachbauprüfung

**Frage:** Bei **Landfahrzeuge × Körper**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K115-Q4 · Nachbauprüfung

**Frage:** Bei **Landfahrzeuge × Körper**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K115-Q5 · Nachbauprüfung

**Frage:** Wie wird **Landfahrzeuge × Körper** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K115-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Landfahrzeuge × Körper** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K120-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Luftfahrzeuge** verändern **Körper**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K120-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Luftfahrzeuge** und **Körper** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K120-Q3 · Nachbauprüfung

**Frage:** Bei **Luftfahrzeuge × Körper**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K120-Q4 · Nachbauprüfung

**Frage:** Bei **Luftfahrzeuge × Körper**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K120-Q5 · Nachbauprüfung

**Frage:** Wie wird **Luftfahrzeuge × Körper** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K120-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Luftfahrzeuge × Körper** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K156-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Aufgaben** verändern **Testmodus**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Zeitstopp, Ausrüstung, Heilung, Kampfzustimmung, endlicher Loot und mehrstufige Dungeon-Nebenquests bestehen 17/17.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K156-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Aufgaben** und **Testmodus** in Konflikt?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K156-Q3 · Nachbauprüfung

**Frage:** Bei **Aufgaben × Testmodus**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K156-Q4 · Nachbauprüfung

**Frage:** Bei **Aufgaben × Testmodus**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K156-Q5 · Nachbauprüfung

**Frage:** Wie wird **Aufgaben × Testmodus** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

### K156-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Aufgaben × Testmodus** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_09_RESULT.json · screenshots_v21/gate09_tactical_pause_combat_sidequest.png`

## Gate-Entscheidung

Alle 130 relevanten Fragen wurden vor und nach dem Bau beantwortet. Der unmittelbare Playwright-Lauf ist bestanden.

<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_09_FRAGEN_VORHER_NACHHER.md" order="3" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-MOVE-020__K033-Q1_Nachbauprufung.md) · `FW-MOVE-020`
- [Nächster Knoten](FW-MOVE-022__Gate_09_Taktische_Pause_Ausrustung_Kampf_Loot_und_dialogreiche_Nebenquests.md) · `FW-MOVE-022`
- [Themenindex](00_INDEX.md) · `FW-INDEX-MOVE`
- [Verwandt: Abnahmekriterien Bauring 3 und weitere Statusabschnitte](../13_REDTEAM_SIMULATION_TESTS_BELEGE/FW-TEST-008__Abnahmekriterien_Bauring_3_und_weitere_Statusabschnitte.md) · `FW-TEST-008`
- [Verwandt: K045-Q5 · K045 · Fehlurteil × Beziehungen](FW-MOVE-023__K045-Q5_K045_Fehlurteil_Beziehungen.md) · `FW-MOVE-023`
- [Verwandt: F-0678 · TEILWEISE](FW-MOVE-007__F-0678_TEILWEISE.md) · `FW-MOVE-007`
- [Verwandt: F-1853 · TEILWEISE](FW-MOVE-012__F-1853_TEILWEISE.md) · `FW-MOVE-012`
- [Versionsspur v20](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-20__VERSIONSKARTE_V20.md) · `FW-VERSION-20`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
