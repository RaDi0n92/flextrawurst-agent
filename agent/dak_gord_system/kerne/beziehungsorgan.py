from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Beziehungszustand:
    arbeitsbewegung: str = "offen"
    arbeitsbewegung_verlauf: List[Tuple[str, float]] = field(default_factory=list)
    strukturbedarf: int = 0
    widerspruchsbedarf: int = 0
    resonanzbedarf: int = 0
    schutzbedarf: int = 0
    engagementgrad: int = 0   # wie aktiv das System gerade ist (Marker-Zahl)
    bemerkungen: List[str] = field(default_factory=list)


class Beziehungsorgan:
    def __init__(self) -> None:
        self.zustand = Beziehungszustand()

    def lese_hinweis(self, text: str) -> None:
        """Liest Nutzereingabe und aktualisiert Beziehungszustand."""
        klein = text.lower()

        if any(w in klein for w in ["struktur", "ordnen", "sortieren", "plan"]):
            self.zustand.arbeitsbewegung = "struktur_suchend"
            self.zustand.strukturbedarf += 1

        elif any(w in klein for w in ["zweifel", "unsicher", "weiß nicht", "ahnung"]):
            self.zustand.arbeitsbewegung = "tastend"

        elif any(w in klein for w in ["weiter", "mehr", "tiefer", "genau"]):
            self.zustand.arbeitsbewegung = "vertiefend"

        else:
            self.zustand.arbeitsbewegung = "offen"

        self.zustand.arbeitsbewegung_verlauf.append((self.zustand.arbeitsbewegung, time.time()))
        if len(self.zustand.arbeitsbewegung_verlauf) > 10:
            self.zustand.arbeitsbewegung_verlauf.pop(0)

        if any(w in klein for w in ["widerspruch", "kritik", "gegenhalt", "aber", "stimmt nicht"]):
            self.zustand.widerspruchsbedarf += 1

        if any(w in klein for w in ["resonanz", "fühlen", "zieht", "stimmig", "genau das"]):
            self.zustand.resonanzbedarf += 1

        if any(w in klein for w in ["zu viel", "überfordert", "langsam", "warte", "stopp"]):
            self.zustand.schutzbedarf += 1

    def lese_antwort_hinweis(self, llm_antwort: str) -> None:
        """Feedback-Loop: Liest LLM-Antwort und aktualisiert Zustand.

        Signale: Marker-Dichte → Engagement, Länge → Tiefe, Direktheit → Klarheit.
        """
        marker_count = llm_antwort.count("##")
        self.zustand.engagementgrad = marker_count // 2  # Jeder Marker hat öffnend/schließend

        antwort_laenge = len(llm_antwort)
        if antwort_laenge < 200 and self.zustand.schutzbedarf > 0:
            # Kurze Antwort bei Schutzbedarf → System hält Abstand, korrekt
            self.zustand.schutzbedarf = max(0, self.zustand.schutzbedarf - 1)

        if antwort_laenge > 800 and self.zustand.strukturbedarf > 0:
            # Lange strukturierte Antwort → Strukturbedarf wird bedient
            self.zustand.strukturbedarf = max(0, self.zustand.strukturbedarf - 1)

        # Wenn Widerspruch in der Antwort vorhanden: Bedarf sinkt (wurde bedient)
        if any(w in llm_antwort.lower() for w in ["aber", "allerdings", "im gegensatz", "unterschied"]):
            self.zustand.widerspruchsbedarf = max(0, self.zustand.widerspruchsbedarf - 1)

    def kurzbild(self) -> str:
        verlauf = self.zustand.arbeitsbewegung_verlauf
        if len(verlauf) >= 2:
            trend = " → ".join(v[0] for v in verlauf[-3:])
            teile = [f"arbeitsbewegung={trend}"]
        else:
            teile = [f"arbeitsbewegung={self.zustand.arbeitsbewegung}"]
        if self.zustand.strukturbedarf > 0:
            teile.append(f"strukturbedarf={self.zustand.strukturbedarf}")
        if self.zustand.widerspruchsbedarf > 0:
            teile.append(f"widerspruchsbedarf={self.zustand.widerspruchsbedarf}")
        if self.zustand.resonanzbedarf > 0:
            teile.append(f"resonanzbedarf={self.zustand.resonanzbedarf}")
        if self.zustand.schutzbedarf > 0:
            teile.append(f"schutzbedarf={self.zustand.schutzbedarf}")
        if self.zustand.engagementgrad > 0:
            teile.append(f"engagement={self.zustand.engagementgrad}")
        return ", ".join(teile)
