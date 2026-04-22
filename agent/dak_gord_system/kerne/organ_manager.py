from __future__ import annotations

import re

from agent.dak_gord_system.kerne.erinnerungsgedaechtnis import Erinnerungsgedaechtnis
from agent.dak_gord_system.kerne.entscheidungsorgan import Entscheidungsorgan
from agent.dak_gord_system.kerne.zukunftsorgan import Zukunftsorgan
from agent.dak_gord_system.kerne.zwischenraumorgan import ZwischenraumKeim, Zwischenraumorgan

# LLM-Marker die der Agent schreiben kann:
# ##MERKEN art: text##          → Erinnerung speichern
# ##SPÄTER heute | später##     → Zukunftskeim anlegen
# ##ZWISCHENRAUM text##         → schwebenden Gedanken ablegen
# ##ABWÄGEN frage##             → offene Abwägung öffnen

_RE_MERKEN = re.compile(r'##MERKEN\s+([^:#]+):\s*(.+?)##', re.DOTALL)
_RE_SPAETER = re.compile(r'##SP(?:Ä|AE?)TER\s+(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(.+?))?##')
_RE_ZWISCHEN = re.compile(r'##ZWISCHENRAUM\s+(.+?)##', re.DOTALL)
_RE_ABWAEGEN = re.compile(r'##ABW(?:Ä|AE?)GEN\s+(.+?)##')

_RESONANZ_WORTLAENGE = 4  # Minimale Wortlänge für Schlagwort-Extraktion


def _extrahiere_schlagworte(text: str) -> set[str]:
    """Einfache Schlagwort-Extraktion: alle Wörter ≥ 4 Zeichen, lowercase."""
    return {w.lower() for w in re.findall(r'\w+', text) if len(w) >= _RESONANZ_WORTLAENGE}


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

        # Reifedruck-Takt: jede Antwort ist ein Tick für alle Zwischenraum-Keime
        self.zwischenraum.tick()
        self._verarbeite_reife()

        # Resonanz-Beschleuniger: nach jeder Antwort auf Paare prüfen
        self._resonanz_beschleuniger()

        if gefunden or self.zwischenraum.keime:
            self.speichern()

        return gefunden

    def _verarbeite_reife(self) -> None:
        """Transferiert reife Zwischenraum-Keime ins Erinnerungsorgan, protokolliert verblasste."""
        transfer_kandidaten, verblasste = self.zwischenraum.pruefe_reife()

        for keim in transfer_kandidaten:
            # Transfer: Zwischenraum → Erinnerung (art: "zwischenraum")
            self.erinnerung.merken(
                art="zwischenraum",
                text=keim.text,
                schlagworte=keim.schlagworte,
            )
            self.zwischenraum.entferne(keim)

        if verblasste:
            self._protokolliere_verblassen(verblasste)

    def _protokolliere_verblassen(self, verblasste) -> None:
        """Schreibt verblasste Keime ins Verblassen-Log statt sie still zu entfernen."""
        import datetime
        from agent.dak_gord_system.kerne.gedaechtnisspeicher import lade_json, speichere_json

        log = lade_json("verblassen_log.json", [])
        jetzt = datetime.datetime.now().isoformat(timespec="minutes")
        for keim in verblasste:
            log.append({
                "zeitpunkt": jetzt,
                "text": keim.text,
                "reifedruck_bei_verblassen": keim.reifedruck,
                "schlagworte": keim.schlagworte,
            })
        speichere_json("verblassen_log.json", log)

    def _resonanz_beschleuniger(self) -> None:
        """Sucht Paare (Zwischenraum ↔ Erinnerung) mit gemeinsamen Schlagworten.
        Legt für jedes neue Paar eine offene Abwägung an.
        """
        if not self.zwischenraum.keime or not self.erinnerung.erinnerungen:
            return

        bereits_abgewogen = {a.frage for a in self.entscheidung.offene_abwaegungen}

        for keim in self.zwischenraum.keime:
            keim_woerter = _extrahiere_schlagworte(keim.text)
            if not keim_woerter:
                continue

            for erinnerung in self.erinnerung.erinnerungen[-10:]:  # Nur letzte 10
                er_woerter = _extrahiere_schlagworte(erinnerung.text)
                gemeinsame = keim_woerter & er_woerter

                if len(gemeinsame) >= 2:  # Mindestens 2 gemeinsame Schlagworte
                    paar_frage = (
                        f"Spannung: [{keim.text[:60]}] ↔ [{erinnerung.text[:60]}]"
                    )
                    if paar_frage not in bereits_abgewogen:
                        self.entscheidung.anlegen(paar_frage)
                        bereits_abgewogen.add(paar_frage)

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
