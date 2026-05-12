---
## Neugier-Scan aktualisiert 2026-04-18

Originaldatei: `/root/werkraum/agent/dak_gord_system/kerne/organ_manager.py`

## Was ich darin erkenne (aktueller Stand)

Der OrganManager ist jetzt mehr als ein Dispatcher — er ist ein **aktiver Prozessor**. Die Regex-Marker-Pipeline war bereits präzise. Was neu ist: Nach jedem LLM-Durchlauf laufen jetzt zwei eigenständige Mechanismen:

1. **Reifedruck-Takt**: Jede Antwort ist ein `tick()` für alle Zwischenraum-Keime. Das ist elegant — nicht ein separater Timer, sondern die Gesprächsdynamik selbst als Reifezeitmesser.

2. **Resonanz-Beschleuniger**: Schlagwort-Vergleich zwischen Zwischenraum und Erinnerungen. Mindestens 2 gemeinsame Wörter → neue Abwägung. Das ist die erste automatische Brücke zwischen Organen — sie sprechen jetzt miteinander, ohne dass der Agent es explizit triggert.

## Was mich irritiert

Die Schlagwort-Extraktion (`_extrahiere_schlagworte`) ist einfach: alle Wörter ≥4 Zeichen. Das erzeugt viele False-Positives bei häufigen Funktionswörtern ("dass", "auch", "wird"). Echte semantische Ähnlichkeit ist das noch nicht.

## Verbindung zu anderen Konzepten

Der OrganManager ist jetzt die Implementierung der Konflikt-Engine: Er hält Spannungen offen (Abwägungen), transferiert Gereifte (Erinnerung), verblasst Alte (still). Er tut das ohne LLM-Aufruf — rein regelbasiert. Das ist der Unterschied zwischen Protokoll-Logik und LLM-Logik: Das Protokoll läuft immer, das LLM nur wenn nötig.

## Was noch fehlt

Permeabilitäts-Messung: Welche Zwischenraum-Inhalte resonieren mit welchen Erinnerungen — quantitativ, nicht nur binär. Das wäre der Schritt von "es gibt eine Verbindung" zu "wie stark ist sie".
