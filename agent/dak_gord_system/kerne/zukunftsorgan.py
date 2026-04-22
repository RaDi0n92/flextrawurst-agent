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

    def kurzbild(self) -> str:
        if not self.keime:
            return ""
        zeilen = [f"- {k.heute} → {k.spaeter}" for k in self.keime[-3:]]
        return "ZUKUNFTSKEIME:\n" + "\n".join(zeilen)

    def speichern(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import speichere_json
        speichere_json("zukunft.json", [
            {"heute": k.heute, "spaeter": k.spaeter, "begruendung": k.begruendung}
            for k in self.keime
        ])

    def laden(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import lade_json
        daten = lade_json("zukunft.json", [])
        self.keime = [
            Zukunftskeim(heute=d["heute"], spaeter=d["spaeter"], begruendung=d.get("begruendung", ""))
            for d in daten
        ]
