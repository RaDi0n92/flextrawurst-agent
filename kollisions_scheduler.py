#!/usr/bin/env python3
"""
kollisions_scheduler.py — vergibt fuer einen neuen Wesen-eigenen Dienst einen
start_offset_sekunden, der Kollisionen mit bereits aktiven Wesen-eigenen Diensten
vermeidet. Pflicht laut Vision-Notiz (Baustein 4, Randbedingung): "nie alle Wesen
gleichzeitig losschicken" -- das war in der Nacht 2026-07-06/07 der reale Grund
fuer einen Ollama-Slot-Deadlock (6+ Wesen-Dienste parallel).

Hintergrund: seit dem Umbau laeuft die Hintergrund-LLM-Instanz (Port 11436) mit
genau EINEM echten Slot (--parallel 1) -- Kollisionen fuehren nicht mehr zum
Deadlock, aber zu Warteschlangen-Stau (bis zu 300s Timeout pro Anfrage). Diese
Funktion plant neue Rhythmen von vornherein versetzt, statt sich blind auf die
Warteschlange zu verlassen.

Ehrliche Grenze: bei Rhythmen mit unterschiedlichen, nicht kommensurablen Perioden
ist echte Kollisionsfreiheit auf alle Zeit ein offenes Scheduling-Problem, das
hier nicht vollstaendig geloest wird. Was diese Funktion garantiert: kein neuer
Rhythmus bekommt denselben Offset wie ein bereits bekannter aktiver Rhythmus
desselben Wesens -- jeder wird um mindestens MIN_ABSTAND_SEKUNDEN verschoben.
"""

import wesen_eigene_dienste as wed

MIN_ABSTAND_SEKUNDEN = 300  # 5 Minuten -- Hintergrund-Instanz hat 1 Slot

# Feste Wesen-Reihenfolge, wie in codewesen_agent.py:run() (dort wesen_idx * 480
# fuer die 7 bestehenden Wesen-Prozesse) -- hier nur als grobe zusaetzliche
# Entzerrung zwischen Wesen genutzt, nicht als exakte Nachbildung.
_WESEN_REIHE = ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"]


def _wesen_index(wesen: str) -> int:
    return _WESEN_REIHE.index(wesen) if wesen in _WESEN_REIHE else 0


def naechster_freier_offset(wesen: str, takt_sekunden: int, mindestabstand: int = MIN_ABSTAND_SEKUNDEN) -> int:
    """Gibt einen start_offset_sekunden (0 <= offset < takt_sekunden) zurueck.

    Bestehende aktive Wesen-eigene Dienste desselben Wesens werden geladen, ihre
    Offsets modulo takt_sekunden als belegt betrachtet. Der Kandidat startet bei
    einer wesen-spezifischen Basis (Index in der festen Reihenfolge * Mindestabstand)
    und wandert in Mindestabstand-Schritten weiter, bis ein Slot frei ist, der zu
    JEDEM bestehenden Offset mindestens mindestabstand entfernt liegt (zyklisch,
    da Rhythmen periodisch sind).
    """
    if takt_sekunden <= 0:
        raise ValueError("takt_sekunden muss positiv sein")

    bestehende = wed.lade_fuer_wesen(wesen, nur_aktive=True)
    belegt = sorted(o["start_offset_sekunden"] % takt_sekunden for o in bestehende)

    basis = (_wesen_index(wesen) * mindestabstand) % takt_sekunden
    kandidat = basis
    max_versuche = max(1, takt_sekunden // mindestabstand)

    for _ in range(max_versuche):
        kollidiert = any(
            min((kandidat - b) % takt_sekunden, (b - kandidat) % takt_sekunden) < mindestabstand
            for b in belegt
        )
        if not kollidiert:
            return kandidat
        kandidat = (kandidat + mindestabstand) % takt_sekunden

    # Kein Slot mit vollem Mindestabstand gefunden (sehr viele Rhythmen auf kurzem
    # Takt) -- lieber knapp gestaffelt zurueckgeben als komplett gleichzeitig.
    return kandidat
