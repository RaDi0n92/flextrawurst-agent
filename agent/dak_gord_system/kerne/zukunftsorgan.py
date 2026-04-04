from dataclasses import dataclass, field
from typing import List


@dataclass
class Zukunftskeim:
    heute: str
    spaeter: str
    begruendung: str = ""


class Zukunftsorgan:
    def __init__(self) -> None:
        self.keime: List[Zukunftskeim] = []

    def vormerken(self, heute: str, spaeter: str, begruendung: str = "") -> None:
        self.keime.append(
            Zukunftskeim(
                heute=heute.strip(),
                spaeter=spaeter.strip(),
                begruendung=begruendung.strip(),
            )
        )
