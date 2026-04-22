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

    def kurzbild(self) -> str:
        if not self.offene_abwaegungen:
            return ""
        zeilen = [f"- {a.frage}" for a in self.offene_abwaegungen[-3:]]
        return "OFFENE ABWÄGUNGEN:\n" + "\n".join(zeilen)

    def speichern(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import speichere_json
        speichere_json("abwaegungen.json", [
            {
                "frage": a.frage,
                "richtungen": a.richtungen,
                "spannungen": a.spannungen,
                "verdeckte_kosten": a.verdeckte_kosten,
                "moegliche_tiefere_linie": a.moegliche_tiefere_linie,
            }
            for a in self.offene_abwaegungen
        ])

    def laden(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import lade_json
        daten = lade_json("abwaegungen.json", [])
        self.offene_abwaegungen = [
            Abwaegung(
                frage=d["frage"],
                richtungen=d.get("richtungen", []),
                spannungen=d.get("spannungen", []),
                verdeckte_kosten=d.get("verdeckte_kosten", []),
                moegliche_tiefere_linie=d.get("moegliche_tiefere_linie"),
            )
            for d in daten
        ]
