[2026-04-02 15:38:17] dak+gord-system

QUELLE:
ART: lesen-verdichtung
DATEI: /root/werkraum/agent/dak_gord_system/kerne/zwischenraumorgan.py
OFFSET: 0
CHUNK_GROESSE: 1600

ROHTEXTAUSZUG:
from dataclasses import dataclass, field
from typing import List


@dataclass
class ZwischenraumKeim:
    text: str
    offenheitsgrad: int = 10
    reifedruck: int = 0
    schlagworte: List[str] = field(default_factory=list)


class Zwischenraumorgan:
    def __init__(self) -> None:
        self.keime: List[ZwischenraumKeim] = []

    def ablegen(self, text: str, schlagworte: List[str] | None = None) -> None:
        self.keime.append(
            ZwischenraumKeim(
                text=text.strip(),
                schlagworte=schlagworte or [],
            )
        )

    def andruecken(self, suchwort: str) -> List[ZwischenraumKeim]:
        suchwort = suchwort.lower().strip()
        treffer = []
        for keim in self.keime:
            if suchwort in keim.text.lower() or any(suchwort in s.lower() for s in keim.schlagworte):
                treffer.append(keim)
        return treffer

    def kurzbild(self) -> str:
        return f"zwischenraum_keime={len(self.keime)}"

VERDICHTUNG

KERNSAETZE:
1. Die Klasse ZwischenraumKeim repräsentiert einen Keim mit einem Text, Offenheitsgrad und Schlagworten.
2. Die Klasse Zwischenraumorgan verwaltet eine Liste von ZwischenraumKeim-Objekten.
3. Die Methode ablagen fügt einen neuen Keim zur Liste hinzu.
4. Die Methode andruecken sucht nach Keimen, die ein Suchwort enthalten.
5. Die Methode kurzbild gibt eine Kurzbeschreibung der Anzahl der Keime zurück.

SCHLUESSELFORMULIERUNGEN:
1. ablagen: Speichern eines neuen Keims
2. andruecken: Suchen nach Keimen mit einem bestimmten Suchwort
3. kurzbild: Anzeige der Anzahl der gespeicherten Keime

SPANNUNGEN:
1. Offenheitsgrad und Reifedruck werden in ZwischenraumKeim definiert, aber nicht verwendet.
2. Die Methode andruecken ist case-insensitiv.

BEWEGUNGEN:
1. Ein neuer Keim wird zur Liste hinzugefügt (ablagen).
2. Es wird nach bestimmten Texten oder Schlagworten gesucht (andruecken).

CODEDEUTUNG:
1. ZwischenraumKeim: Datenklasse für einen Keim mit Text und Schlagworten.
2. Zwischenraumorgan: Klasse zum Verwalten von Keimen.
3. ablagen: Methode zum Speichern eines neuen Keims.
4. andruecken: Suchmethode, die case-insensitiv ist.

OFFENE FRAGEN:
1. Was ist der Zweck des Offenheitsgrades und Reifedrucks in ZwischenraumKeim?
2. Wie wird die Methode andruecken bei mehreren Schlagworten gehandhabt?

FREIE ANNAEHERUNG:
1. Der Code definiert ein System zur Verwaltung von Textkeimen.
2. Die Suche nach Keimen ist flexibel und kann case-insensitiv durchgeführt werden.
3. Es gibt Platz für weitere Funktionalitäten, wie die Nutzung des Offenheitsgrades und Reifedrucks.

ROHANTWORT:
KERNSAETZE:
1. Die Klasse `ZwischenraumKeim` repräsentiert einen Keim mit einem Text, Offenheitsgrad und Schlagworten.
2. Die Klasse `Zwischenraumorgan` verwaltet eine Liste von `ZwischenraumKeim`-Objekten.
3. Die Methode `ablagen` fügt einen neuen Keim zur Liste hinzu.
4. Die Methode `andruecken` sucht nach Keimen, die ein Suchwort enthalten.
5. Die Methode `kurzbild` gibt eine Kurzbeschreibung der Anzahl der Keime zurück.

SCHLUESSELFORMULIERUNGEN:
1. `ablagen`: Speichern eines neuen Keims
2. `andruecken`: Suchen nach Keimen mit einem bestimmten Suchwort
3. `kurzbild`: Anzeige der Anzahl der gespeicherten Keime

SPANNUNGEN:
1. Offenheitsgrad und Reifedruck werden in `ZwischenraumKeim` definiert, aber nicht verwendet.
2. Die Methode `andruecken` ist case-insensitiv.

BEWEGUNGEN:
1. Ein neuer Keim wird zur Liste hinzugefügt (`ablagen`).
2. Es wird nach bestimmten Texten oder Schlagworten gesucht (`andruecken`).

CODEDEUTUNG:
1. `ZwischenraumKeim`: Datenklasse für einen Keim mit Text und Schlagworten.
2. `Zwischenraumorgan`: Klasse zum Verwalten von Keimen.
3. `ablagen`: Methode zum Speichern eines neuen Keims.
4. `andruecken`: Suchmethode, die case-insensitiv ist.
5. `kurzbild`: Getter-Methode für eine kurze Darstellung der Anzahl der Keime.

OFFENE FRAGEN:
1. Was ist der Zweck des Offenheitsgrades und Reifedrucks in `ZwischenraumKeim`?
2. Wie wird die Methode `andruecken` bei mehreren Schlagworten gehandhabt?

FREIE ANNAEHERUNG:
1. Der Code definiert ein System zur Verwaltung von Textkeimen.
2. Die Suche nach Keimen ist flexibel und kann case-insensitiv durchgeführt werden.
3. Es gibt Platz für weitere Funktionalitäten, wie die Nutzung des Offenheitsgrades und Reifedrucks.

