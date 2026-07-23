# Exakter Auftragsvertrag

## Verbindliche Reihenfolge

1. Den vollständigen Quellenkörper lesen und inventarisieren.
2. Mindestens alles aus `00_WAS_ES_ALLES_GIBT.md` erfassen und zusätzliche Ideen, Dimensionen, Kollisionen und Rohsetzungen ergänzen.
3. Runde 01: **jedes** Ziel verbessern, die Verbesserung redteamen und reparieren.
4. Runde 02 beginnt auf dem reparierten Gesamtzustand von Runde 01 und bearbeitet erneut **jedes** Ziel.
5. Dies sequenziell bis Runde 66 fortsetzen.
6. Erst danach mehrere Umsetzungsreihenfolgen erzeugen, bewerten und die stärkste auswählen.
7. Für jedes Ziel den vollständigen Bauplan ausschreiben: Schritte, Fragen davor, Gegenprüfung danach, Negativregeln, Abhängigkeiten, Playwright-Gate, Stopkriterien und Beweise.
8. Danach **Stopp**. Keine Spielimplementierung ohne ausdrückliches `Go`.

## Was ausdrücklich nicht als Erfüllung gilt

- 66 verschiedene Vollständigkeitsfragen ohne Zielverbesserungen
- ein globaler Redteamtext, der nicht jedes Ziel berührt
- Rundenzahlen ohne sequenzielle Zustandsübergabe
- 111.111 Varianten als Ersatz für die 66 Vollbestandsrunden
- grobe Phasenübersichten ohne Einzeldossiers
- Playwright als Wort im Plan ohne konkrete Browserhandlung und Assertions
- OUTRO vor dem tatsächlich gebauten Planungskörper
