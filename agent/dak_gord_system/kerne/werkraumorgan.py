from pathlib import Path
from typing import List


class Werkraumorgan:
    def lese_datei(self, pfad: str) -> str:
        datei = Path(pfad)
        if not datei.exists():
            return ""
        return datei.read_text(encoding="utf-8")

    def finde_dateien(self, wurzel: str, endung: str = ".md") -> List[str]:
        basis = Path(wurzel)
        if not basis.exists():
            return []
        return [str(p) for p in sorted(basis.rglob(f"*{endung}"))]

    def datei_existiert(self, pfad: str) -> bool:
        return Path(pfad).exists()
