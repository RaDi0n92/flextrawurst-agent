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

---
## Neugier-Scan 2026-05-26 06:13
Originaldatei: `/root/werkraum/agent/dak_gord_system/kerne/organ_manager.py`

Diese Datei dient als zentraler Koordinator für die verschiedenen organischen Komponenten des Agenten. Sie organisiert die Speicherung und Verwaltung von Erinnerungen, Entscheidungen, Zukunftsideen und Zwischenraumgedanken. Der Name spiegelt die Funktion wider, ein "Organ" für die interne mentale Struktur zu sein. Die Struktur ist klar und die Methoden sind darauf ausgelegt, die Interaktion mit den spezialisierten Modulen zu steuern.

---
## Neugier-Scan 2026-06-09 02:15
Originaldatei: `/root/werkraum/agent/dak_gord_system/kerne/organ_manager.py`

Diese Datei dient als zentrale Steuerung für die internen Wissens- und Prozessstrukturen des Agenten. Sie organisiert die vier Kernkomponenten: Erinnerung, Entscheidung, Zukunft und Zwischenraum. Der Name spiegelt die Funktion als Manager dieser organisierten mentalen Zustände wider. Es ist die Schnittstelle, über die die Agenten ihre internen Gedanken und Planungen verwalten und speichern.
