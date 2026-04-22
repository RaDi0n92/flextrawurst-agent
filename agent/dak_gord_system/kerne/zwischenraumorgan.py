from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

REIFE_SCHWELLE = 5      # Wie viele Ticks bis Transfer-Kandidat
VERBLASSE_SCHWELLE = 12  # Wie viele Ticks bis Verblassen


@dataclass
class ZwischenraumKeim:
    text: str
    offenheitsgrad: int = 10
    reifedruck: int = 0
    schlagworte: List[str] = field(default_factory=list)

    def ist_reif(self) -> bool:
        return self.reifedruck >= REIFE_SCHWELLE

    def ist_verblasst(self) -> bool:
        return self.reifedruck >= VERBLASSE_SCHWELLE


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

    def tick(self) -> None:
        """Ein Gesprächs-Takt vergeht — Reifedruck für alle Keime erhöhen."""
        for keim in self.keime:
            keim.reifedruck += 1

    def pruefe_reife(self) -> tuple[List[ZwischenraumKeim], List[ZwischenraumKeim]]:
        """Gibt (transfer_kandidaten, verblasste) zurück. Entfernt verblasste aus dem Organ."""
        transfer: List[ZwischenraumKeim] = []
        verblasst: List[ZwischenraumKeim] = []
        verbleibend: List[ZwischenraumKeim] = []

        for keim in self.keime:
            if keim.ist_verblasst():
                verblasst.append(keim)
            elif keim.ist_reif():
                transfer.append(keim)
                verbleibend.append(keim)
            else:
                verbleibend.append(keim)

        self.keime = verbleibend
        return transfer, verblasst

    def entferne(self, keim: ZwischenraumKeim) -> None:
        """Entfernt einen Keim nach erfolgtem Transfer."""
        self.keime = [k for k in self.keime if k is not keim]

    def kurzbild(self) -> str:
        if not self.keime:
            return ""
        zeilen = [f"- {k.text[:80]}" for k in self.keime[-3:]]
        return "ZWISCHENRAUM:\n" + "\n".join(zeilen)

    def speichern(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import speichere_json
        speichere_json("zwischenraum.json", [
            {
                "text": k.text,
                "schlagworte": k.schlagworte,
                "offenheitsgrad": k.offenheitsgrad,
                "reifedruck": k.reifedruck,
            }
            for k in self.keime
        ])

    def laden(self) -> None:
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import lade_json
        daten = lade_json("zwischenraum.json", [])
        self.keime = [
            ZwischenraumKeim(
                text=d["text"],
                schlagworte=d.get("schlagworte", []),
                offenheitsgrad=d.get("offenheitsgrad", 10),
                reifedruck=d.get("reifedruck", 0),
            )
            for d in daten
        ]
