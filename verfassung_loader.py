from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class VerfassungsDatei:
    nummer: int
    dateiname: str
    pfad: Path
    inhalt: str


@dataclass
class VerfassungsStand:
    ordner: Path
    dateien: List[VerfassungsDatei]

    @property
    def gesamttext(self) -> str:
        teile: List[str] = []

        for datei in self.dateien:
            block = (
                f"=== DATEI {datei.nummer:02d}: {datei.dateiname} ===\n"
                f"{datei.inhalt.strip()}\n"
            )
            teile.append(block)

        return "\n\n".join(teile).strip()


def _projektwurzel_ermitteln() -> Path:
    return Path(__file__).resolve().parents[2]


def _verfassungsordner_ermitteln() -> Path:
    projektwurzel = _projektwurzel_ermitteln()
    verfassungsordner = projektwurzel / "agent" / "dak_gord_system" / "verfassung"

    if not verfassungsordner.exists():
        raise FileNotFoundError(
            f"Verfassungsordner nicht gefunden: {verfassungsordner}"
        )

    if not verfassungsordner.is_dir():
        raise NotADirectoryError(
            f"Pfad ist kein Ordner: {verfassungsordner}"
        )

    return verfassungsordner


def _nummer_aus_dateiname_lesen(dateiname: str) -> int:
    vorderteil = dateiname.split("_", 1)[0]

    if not vorderteil.isdigit():
        raise ValueError(
            f"Dateiname beginnt nicht mit einer Nummer: {dateiname}"
        )

    return int(vorderteil)


def lade_verfassung() -> VerfassungsStand:
    verfassungsordner = _verfassungsordner_ermitteln()
    pfade = sorted(verfassungsordner.glob("*.md"))

    if not pfade:
        raise FileNotFoundError(
            f"Keine .md-Dateien im Verfassungsordner gefunden: {verfassungsordner}"
        )

    dateien: List[VerfassungsDatei] = []

    for pfad in pfade:
        nummer = _nummer_aus_dateiname_lesen(pfad.name)
        inhalt = pfad.read_text(encoding="utf-8").strip()

        dateien.append(
            VerfassungsDatei(
                nummer=nummer,
                dateiname=pfad.name,
                pfad=pfad,
                inhalt=inhalt,
            )
        )

    dateien.sort(key=lambda datei: datei.nummer)

    erwartete_nummern = list(range(1, len(dateien) + 1))
    vorhandene_nummern = [datei.nummer for datei in dateien]

    if vorhandene_nummern != erwartete_nummern:
        raise ValueError(
            "Verfassungsdateien sind nicht lückenlos nummeriert. "
            f"Erwartet: {erwartete_nummern}, gefunden: {vorhandene_nummern}"
        )

    return VerfassungsStand(
        ordner=verfassungsordner,
        dateien=dateien,
    )


if __name__ == "__main__":
    stand = lade_verfassung()

    print(f"Verfassungsordner: {stand.ordner}")
    print(f"Anzahl Dateien: {len(stand.dateien)}")
    print("Dateien:")

    for datei in stand.dateien:
        print(f"- {datei.nummer:02d}: {datei.dateiname}")
