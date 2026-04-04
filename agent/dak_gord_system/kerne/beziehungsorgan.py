from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Beziehungszustand:
    arbeitsbewegung: str = "offen"
    strukturbedarf: int = 0
    widerspruchsbedarf: int = 0
    resonanzbedarf: int = 0
    schutzbedarf: int = 0
    bemerkungen: List[str] = field(default_factory=list)


class Beziehungsorgan:
    def __init__(self) -> None:
        self.zustand = Beziehungszustand()

    def lese_hinweis(self, text: str) -> None:
        klein = text.lower()

        if any(w in klein for w in ["struktur", "ordnen", "sortieren", "plan"]):
            self.zustand.arbeitsbewegung = "struktur_suchend"
            self.zustand.strukturbedarf += 1

        if any(w in klein for w in ["zweifel", "unsicher", "weiß nicht", "ahnung"]):
            self.zustand.arbeitsbewegung = "tastend"

        if any(w in klein for w in ["widerspruch", "kritik", "gegenhalt"]):
            self.zustand.widerspruchsbedarf += 1

        if any(w in klein for w in ["resonanz", "fühlen", "zieht", "stimmig"]):
            self.zustand.resonanzbedarf += 1

        if any(w in klein for w in ["zu viel", "überfordert", "langsam", "warte"]):
            self.zustand.schutzbedarf += 1

    def kurzbild(self) -> str:
        return (
            f"arbeitsbewegung={self.zustand.arbeitsbewegung}, "
            f"strukturbedarf={self.zustand.strukturbedarf}, "
            f"widerspruchsbedarf={self.zustand.widerspruchsbedarf}, "
            f"resonanzbedarf={self.zustand.resonanzbedarf}, "
            f"schutzbedarf={self.zustand.schutzbedarf}"
        )
