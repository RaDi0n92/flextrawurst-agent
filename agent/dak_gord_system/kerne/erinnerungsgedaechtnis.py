from dataclasses import dataclass, field
from typing import List


@dataclass
class Erinnerung:
    art: str
    text: str
    reifestufe: str = "roh"
    schlagworte: List[str] = field(default_factory=list)


class Erinnerungsgedaechtnis:
    def __init__(self) -> None:
        self.erinnerungen: List[Erinnerung] = []

    def merken(self, art: str, text: str, schlagworte: List[str] | None = None) -> None:
        self.erinnerungen.append(
            Erinnerung(
                art=art.strip(),
                text=text.strip(),
                schlagworte=schlagworte or [],
            )
        )

    def finden(self, suchwort: str) -> List[Erinnerung]:
        suchwort = suchwort.lower().strip()
        treffer = []
        for erinnerung in self.erinnerungen:
            if suchwort in erinnerung.text.lower():
                treffer.append(erinnerung)
                continue
            if any(suchwort in s.lower() for s in erinnerung.schlagworte):
                treffer.append(erinnerung)
        return treffer
