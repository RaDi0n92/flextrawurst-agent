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
