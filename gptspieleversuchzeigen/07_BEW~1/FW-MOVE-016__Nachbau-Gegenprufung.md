---
id: FW-MOVE-016
status: BESTAETIGT
typ: source
themenraum: MOVE
version: v21
tags: [fahrzeug, fragen, load, move, playwright, redteam, save, test, v20, v21, welt, wesen, zeit]
---

# Nachbau-Gegenprüfung

> **Quellenkörper:** Der Inhalt zwischen den Segmentmarkern ist wortgetreu aus den angegebenen Originalpfaden übernommen.
<!-- SOURCE_SEGMENT_BEGIN source="v21:docs_v21/GATE_02_FRAGEN_VORHER_NACHHER.md" sha256="cd5af55a75e4b17cf2ea75c5043e80ae5c4a8527d477c741a0aef5ccb85247e8" order="2" -->
## Nachbau-Gegenprüfung

Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

### D062-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche Gleiter, Flugzeuge, Lufttaxis, VTOLs und Spezialformen existieren?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Luftfahrzeuge“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Luftfahrzeuge“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Luftfahrzeuge“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Luftfahrzeuge“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Luftfahrzeuge“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Luftfahrzeuge“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D062-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Luftfahrzeuge“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie funktionieren Laufen, Klettern, Springen, Tragen, Schleichen und Sturz?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Bewegung zu Fuß“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Bewegung zu Fuß“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Bewegung zu Fuß“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Bewegung zu Fuß“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Bewegung zu Fuß“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Bewegung zu Fuß“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D067-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Bewegung zu Fuß“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie verändert Können Handlung, Wahrnehmung und Weltzugang?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Meisterschaft“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Meisterschaft“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Meisterschaft“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Meisterschaft“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Meisterschaft“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Meisterschaft“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D090-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Meisterschaft“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche Zustände, Ereignisse und privaten Schichten werden wie gespeichert?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Speichern“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Speichern“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Speichern“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Speichern“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Speichern“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Speichern“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D130-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Speichern“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie werden alle Systeme frei erzeugt, verändert, verglichen und zurückgesetzt?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Testmodus“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Testmodus“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Testmodus“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Testmodus“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Testmodus“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Testmodus“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D134-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Testmodus“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Wie bleiben Testwelten strikt getrennt?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Testisolierung“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Testisolierung“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Testisolierung“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Testisolierung“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Testisolierung“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Testisolierung“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D135-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Testisolierung“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q01 · Nachbauprüfung

**Frage:** Welche genaue, quellenmarkierte Antwort gilt für: Welche echten Spielerpfade werden vollständig automatisiert?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Bewertet wird der reale Gate-Zustand, nicht die Absicht.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q02 · Nachbauprüfung

**Frage:** Welche Teile von „Playwright/Automation“ sind bereits gesetzt, welche nur abgeleitet und welche offen?

**Nachbauantwort:** Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt. Quellenrang: Rohinput und v20-Vertrag vor Ableitung; offene Parameter bleiben markiert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q03 · Nachbauprüfung

**Frage:** Welche konkrete Spielerhandlung beweist „Playwright/Automation“ innerhalb der Welt statt im Menü?

**Nachbauantwort:** Die beweisende Handlung wird im echten Browser ausgeführt, nicht nur als Zustandsmutation. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q04 · Nachbauprüfung

**Frage:** Welche unmittelbare sichtbare Signatur muss nach der Handlung in „Playwright/Automation“ auftreten?

**Nachbauantwort:** Es entsteht eine sichtbare Welt-, Sequenz-, Geometrie- oder UI-Signatur plus persistenter Ereigniseintrag. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q05 · Nachbauprüfung

**Frage:** Welche mindestens drei anderen Systeme reagieren auf „Playwright/Automation“ und wodurch?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q06 · Nachbauprüfung

**Frage:** Welche Spätfolge von „Playwright/Automation“ bleibt nach Speichern, Ortswechsel, Zeitwechsel oder langer Abwesenheit?

**Nachbauantwort:** Der Zustand bleibt nach Save/Load oder Wiederbetreten lesbar. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q07 · Nachbauprüfung

**Frage:** Wie sähe die generische, flache oder falsche Umsetzung von „Playwright/Automation“ aus?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### D136-Q08 · Nachbauprüfung

**Frage:** Welcher Testmodusweg, automatisierte Test und Redteam-Angriff beweisen die richtige Umsetzung von „Playwright/Automation“?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K033-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Luftfahrzeuge** verändern **Recht**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K033-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Luftfahrzeuge** und **Recht** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K033-Q3 · Nachbauprüfung

**Frage:** Bei **Luftfahrzeuge × Recht**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K033-Q4 · Nachbauprüfung

**Frage:** Bei **Luftfahrzeuge × Recht**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K033-Q5 · Nachbauprüfung

**Frage:** Wie wird **Luftfahrzeuge × Recht** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K033-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Luftfahrzeuge × Recht** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K103-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Ökologie** verändern **Luftfahrzeuge**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K103-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Ökologie** und **Luftfahrzeuge** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K103-Q3 · Nachbauprüfung

**Frage:** Bei **Ökologie × Luftfahrzeuge**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K103-Q4 · Nachbauprüfung

**Frage:** Bei **Ökologie × Luftfahrzeuge**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K103-Q5 · Nachbauprüfung

**Frage:** Wie wird **Ökologie × Luftfahrzeuge** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K103-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Ökologie × Luftfahrzeuge** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K112-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Versorgungsnetze** verändern **Luftfahrzeuge**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K112-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Versorgungsnetze** und **Luftfahrzeuge** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K112-Q3 · Nachbauprüfung

**Frage:** Bei **Versorgungsnetze × Luftfahrzeuge**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K112-Q4 · Nachbauprüfung

**Frage:** Bei **Versorgungsnetze × Luftfahrzeuge**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K112-Q5 · Nachbauprüfung

**Frage:** Wie wird **Versorgungsnetze × Luftfahrzeuge** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K112-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Versorgungsnetze × Luftfahrzeuge** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K120-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Luftfahrzeuge** verändern **Körper**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K120-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Luftfahrzeuge** und **Körper** in Konflikt?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K120-Q3 · Nachbauprüfung

**Frage:** Bei **Luftfahrzeuge × Körper**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Technische Möglichkeit ersetzt weder Zustimmung noch Besitzrecht. Eigenständige Wesen- und Provenienzgrenzen haben Vorrang und Ablehnung wird gespeichert.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K120-Q4 · Nachbauprüfung

**Frage:** Bei **Luftfahrzeuge × Körper**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Emergenz muss aus gespeichertem Zustand und Systemkopplung entstehen, nicht aus beliebigem Zufallstext. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K120-Q5 · Nachbauprüfung

**Frage:** Wie wird **Luftfahrzeuge × Körper** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K120-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Luftfahrzeuge × Körper** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K188-Q1 · Nachbauprüfung

**Frage:** Welche Zustände von **Testmodus** verändern **Luftfahrzeuge**, und welche Rückwirkung entsteht?

**Nachbauantwort:** Darstellung, Weltzustand, Chronik/Speicherung und mindestens ein Nachbarsystem reagieren. Sichtbares Seil, Zugkraft, Pendel, Schwung, Fallschirmauftrieb und gemeinsame Nutzung sind direkt im Browser bestätigt.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K188-Q2 · Nachbauprüfung

**Frage:** Welche Rechte, Ressourcen, Räume, Daten oder Zeitstände geraten zwischen **Testmodus** und **Luftfahrzeuge** in Konflikt?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K188-Q3 · Nachbauprüfung

**Frage:** Bei **Testmodus × Luftfahrzeuge**: Welche Regel besitzt Vorrang, wer entscheidet das und wie wird die Entscheidung sichtbar?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K188-Q4 · Nachbauprüfung

**Frage:** Bei **Testmodus × Luftfahrzeuge**: Welche emergente Geschichte kann aus der Kollision entstehen, ohne Zufallstext zu sein?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K188-Q5 · Nachbauprüfung

**Frage:** Wie wird **Testmodus × Luftfahrzeuge** im Testmodus deterministisch erzeugt und nach Speichern/Laden geprüft?

**Nachbauantwort:** Playwright prüft Normalpfad, isolierte Test-Fork, Sichtbarkeit, Zustand, Save/Load und Fehler. Beleg: tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`

### K188-Q6 · Nachbauprüfung

**Frage:** Wie versucht das Redteam, **Testmodus × Luftfahrzeuge** zu einer bloßen Zahl, UI-Meldung oder Feature-Entfernung zu verflachen?

**Nachbauantwort:** Falsch wäre ein Toast, Menüeintrag, bloßer Zähler, Teleport oder nicht gespeicherter Effekt ohne verkörperte Weltwirkung.

**Beleg:** `tests_v21/GATE_02_RESULT.json · screenshots_v21/gate02_grapple_parachute.png`


<!-- SOURCE_SEGMENT_END source="v21:docs_v21/GATE_02_FRAGEN_VORHER_NACHHER.md" order="2" -->

---

## Vernetzung

- [Vorheriger Knoten](FW-MOVE-015__Gate_02_Krallenhaken_Fallschirm_und_physikgekoppeltes_Traversal.md) · `FW-MOVE-015`
- [Nächster Knoten](FW-MOVE-017__D062-Q05_Nachbauprufung.md) · `FW-MOVE-017`
- [Themenindex](00_INDEX.md) · `FW-INDEX-MOVE`
- [Verwandt: Gate 05 · Fahrzeugfamilien und räumliche Fahrzeug-Testzone](FW-MOVE-018__Gate_05_Fahrzeugfamilien_und_raumliche_Fahrzeug-Testzone.md) · `FW-MOVE-018`
- [Verwandt: Gate 09 · Taktische Pause, Ausrüstung, Kampf, Loot und dialogreiche Nebenquests](FW-MOVE-022__Gate_09_Taktische_Pause_Ausrustung_Kampf_Loot_und_dialogreiche_Nebenquests.md) · `FW-MOVE-022`
- [Verwandt: D054-Q08 · Nachbauprüfung](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-019__D054-Q08_Nachbauprufung.md) · `FW-BUILD-019`
- [Verwandt: D134-Q05 · D134 · Testmodus](../08_BAUEN_HANDWERK_MODULARITAET/FW-BUILD-020__D134-Q05_D134_Testmodus.md) · `FW-BUILD-020`
- [Versionsspur v20](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-20__VERSIONSKARTE_V20.md) · `FW-VERSION-20`
- [Versionsspur v21](../03_SESSION_UND_VERSIONENSPUR/FW-VERSION-21__VERSIONSKARTE_V21.md) · `FW-VERSION-21`
