import re

from agent.dak_gord_system.kerne.erinnerungsgedaechtnis import Erinnerungsgedaechtnis
from agent.dak_gord_system.kerne.entscheidungsorgan import Entscheidungsorgan
from agent.dak_gord_system.kerne.zukunftsorgan import Zukunftsorgan
from agent.dak_gord_system.kerne.zwischenraumorgan import Zwischenraumorgan

# LLM-Marker die der Agent schreiben kann:
# ##MERKEN art: text##          → Erinnerung speichern
# ##SPÄTER heute | später##     → Zukunftskeim anlegen
# ##ZWISCHENRAUM text##         → schwebenden Gedanken ablegen
# ##ABWÄGEN frage##             → offene Abwägung öffnen

_RE_MERKEN = re.compile(r'##MERKEN\s+([^:#]+):\s*(.+?)##', re.DOTALL)
_RE_SPAETER = re.compile(r'##SP(?:Ä|AE?)TER\s+(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(.+?))?##')
_RE_ZWISCHEN = re.compile(r'##ZWISCHENRAUM\s+(.+?)##', re.DOTALL)
_RE_ABWAEGEN = re.compile(r'##ABW(?:Ä|AE?)GEN\s+(.+?)##')


class OrganManager:
    def __init__(self) -> None:
        self.erinnerung = Erinnerungsgedaechtnis()
        self.entscheidung = Entscheidungsorgan()
        self.zukunft = Zukunftsorgan()
        self.zwischenraum = Zwischenraumorgan()

    def laden(self) -> None:
        self.erinnerung.laden()
        self.entscheidung.laden()
        self.zukunft.laden()
        self.zwischenraum.laden()

    def speichern(self) -> None:
        self.erinnerung.speichern()
        self.entscheidung.speichern()
        self.zukunft.speichern()
        self.zwischenraum.speichern()

    def verarbeite_llm_antwort(self, text: str) -> int:
        """Parst Marker aus LLM-Antwort, speichert in Organe. Gibt Anzahl gefundener Marker zurück."""
        gefunden = 0

        for m in _RE_MERKEN.finditer(text):
            self.erinnerung.merken(m.group(1).strip(), m.group(2).strip())
            gefunden += 1

        for m in _RE_SPAETER.finditer(text):
            self.zukunft.vormerken(m.group(1).strip(), m.group(2).strip(), (m.group(3) or "").strip())
            gefunden += 1

        for m in _RE_ZWISCHEN.finditer(text):
            self.zwischenraum.ablegen(m.group(1).strip())
            gefunden += 1

        for m in _RE_ABWAEGEN.finditer(text):
            self.entscheidung.anlegen(m.group(1).strip())
            gefunden += 1

        if gefunden:
            self.speichern()

        return gefunden

    def systemtext_block(self) -> str:
        """Kurzübersicht aller Organe für den Systemtext."""
        teile = []
        for kurzbild in [
            self.erinnerung.kurzbild(),
            self.entscheidung.kurzbild(),
            self.zukunft.kurzbild(),
            self.zwischenraum.kurzbild(),
        ]:
            if kurzbild:
                teile.append(kurzbild)
        if not teile:
            return ""
        return "\n\n".join(teile)

    def marker_doku(self) -> str:
        return (
            "Organ-Marker (kannst du jederzeit in deiner Antwort verwenden):\n"
            "  ##MERKEN art: text##          → Erinnerung festhalten (art z.B. 'fakt', 'entscheid', 'daniel')\n"
            "  ##SPÄTER heute | später##     → Idee für später vormerken\n"
            "  ##ZWISCHENRAUM text##         → schwebenden Gedanken ablegen\n"
            "  ##ABWÄGEN frage##             → offene Abwägung öffnen"
        )
