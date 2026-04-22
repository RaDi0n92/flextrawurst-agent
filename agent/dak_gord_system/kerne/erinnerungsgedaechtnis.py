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

    def kurzbild(self) -> str:
        if not self.erinnerungen:
            return ""
        zeilen = [f"- [{e.art}] {e.text}" for e in self.erinnerungen[-5:]]
        return "ERINNERUNGEN:\n" + "\n".join(zeilen)

    def speichern(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import speichere_json
        speichere_json("erinnerungen.json", [
            {"art": e.art, "text": e.text, "schlagworte": e.schlagworte, "reifestufe": e.reifestufe}
            for e in self.erinnerungen
        ])

    def laden(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import lade_json
        daten = lade_json("erinnerungen.json", [])
        self.erinnerungen = [
            Erinnerung(art=d["art"], text=d["text"], schlagworte=d.get("schlagworte", []), reifestufe=d.get("reifestufe", "roh"))
            for d in daten
        ]
