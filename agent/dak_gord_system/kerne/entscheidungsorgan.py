from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Abwaegung:
    frage: str
    richtungen: List[str] = field(default_factory=list)
    spannungen: List[str] = field(default_factory=list)
    verdeckte_kosten: List[str] = field(default_factory=list)
    moegliche_tiefere_linie: Optional[str] = None


class Entscheidungsorgan:
    def __init__(self) -> None:
        self.offene_abwaegungen: List[Abwaegung] = []

    def anlegen(self, frage: str) -> Abwaegung:
        abwaegung = Abwaegung(frage=frage.strip())
        self.offene_abwaegungen.append(abwaegung)
        return abwaegung

    def richtung_hinzufuegen(self, abwaegung: Abwaegung, richtung: str) -> None:
        abwaegung.richtungen.append(richtung.strip())

    def spannung_hinzufuegen(self, abwaegung: Abwaegung, spannung: str) -> None:
        abwaegung.spannungen.append(spannung.strip())

    def kosten_hinzufuegen(self, abwaegung: Abwaegung, kosten: str) -> None:
        abwaegung.verdeckte_kosten.append(kosten.strip())
