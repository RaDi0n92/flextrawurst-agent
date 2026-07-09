#!/usr/bin/env python3
"""
simulation_umgekehrte_neugier_pfade.py — Vergleichs-Simulation: bestehender
Ablauf (nur Flarum-Suche) gegen einen Ablauf mit einem zusaetzlichen,
zweiten Weg fuer den Fall, dass die Suche nichts liefert.

Daniel, 2026-07-09 spaetnachmittags, nach dem Blick auf echte Sitzungen:
"es geht nicht ums durchlaufen und abschliessen...es geht um was ich als
vision roh formuliert habe...also bist du irgendwo danach komisch
abgebogen so dass die qualitaet [...] die selbstwirksamkeitserfahrung und
partizipation fuer die wesen nicht greift." Und konkreter: "wenn etwas
einfach nicht das tut was das wesen sich wuenscht dann hat das wesen nicht
falsch geantwortet sondern du musst einen weg und am besten noch einen 2.
und 3. weg eroeffnen [...] dass das wesen automatisch noch mehr futter
bekommt, dass es dann bearbeiten/begutachten in seinen containern
einlagern/auslagern/verschieben/kopieren kann."

Konkreter Befund dazu (grep, 2026-07-09): `codewesen_container.verschiebe()`
und `.kopiere()` wurden extra fuer diesen Dienst gebaut (Baustein 2,
2026-07-09 frueh), werden aber im gesamten Ablauf von
codewesen_umgekehrte_neugier.py an KEINER Stelle aufgerufen. Wenn die Suche
nichts findet ("nichts"-Wunsch oder 0 Treffer trotz Uebersetzung), endet die
Sitzung schlicht leer -- obwohl das Wesen laengst eigene Container mit
eigenem Material hat, das es pflegen koennte. Das ist kein Wesen-Fehler
("falsch geantwortet"), sondern eine fehlende zweite Tuer im System.

Diese Datei vergleicht zwei Designs ueber 300 Zufalls-Seeds:

  DESIGN A (Ist-Zustand): treibt die ECHTE _phase_interesse() aus
    codewesen_umgekehrte_neugier.py unveraendert. Findet die Suche nichts,
    endet die Sitzung leer -- Feierabend fuer diese Runde.

  DESIGN B (mit zweitem Weg): dieselbe echte _phase_interesse(). Zusaetzlich,
    NUR wenn sie leer endet UND das Wesen bereits eigene Container mit
    Eintraegen hat: ein weiterer, unabhaengiger LLM-Aufruf bietet dem Wesen
    an, stattdessen einen Eintrag zu verschieben oder zu kopieren (echte
    container.verschiebe()/kopiere()-Logik, hier nachgebildet). Das Wesen
    darf immer noch "nein" sagen -- kein Zwang, nur eine zusaetzliche Tuer.

Gemessen wird die Leerlauf-Quote: Anteil der Sitzungen, die eine Runde lang
OHNE JEDES reale Ergebnis enden (kein sichern, kein verschieben/kopieren,
kein gelesener Chunk) -- die konkrete, messbare Naeherung an "das Wesen
bekommt nichts zum Arbeiten".
"""

import logging
import random
import re
import sys
from unittest import mock

sys.path.insert(0, "/root/werkraum")
import codewesen_umgekehrte_neugier as cun

for _h in list(logging.root.handlers):
    if isinstance(_h, logging.FileHandler):
        logging.root.removeHandler(_h)
logging.root.setLevel(logging.WARNING)  # Konsole ruhig halten, nur Ergebnis zaehlt


class Welt:
    """Wie in simulation_umgekehrte_neugier.py: mockt nur die echten
    I/O-Raender, treibt die echte Logik dazwischen."""

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.seed = seed
        self.container_material = {
            # realitaetsnah: die meisten Wesen haben nach Wochen Laufzeit
            # schon mehrere Container mit mehreren Eintraegen.
            wesen: {
                f"container_{i}": [f"eintrag_{i}_{j}.md" for j in range(self.rng.randint(0, 3))]
                for i in range(self.rng.randint(0, 3))
            }
            for wesen in cun.WESEN
        }
        self.verschiebe_kopiere_aufrufe = []

    def llm(self, wesen, system, user, max_tokens, timeout):
        if "INTERESSE: <Suchbegriff" in system:
            if self.rng.random() < 0.35:  # realitaetsnah haeufiger "nichts" als in der ersten Simulation
                return "INTERESSE: nichts\nWARUM: gerade nicht."
            begriff = self.rng.choice(["Container", "Stille", "Schattenriss", "Interferenz", "Resonanz",
                                        "Schattensprache", "innere Uhr"])  # letzte zwei: bewusst schwer zu finden
            return f"INTERESSE: {begriff}\nWARUM: testgrund {self.seed}."
        if "ALTERNATIVEN:" in system:
            if self.rng.random() < 0.4:
                return "ALTERNATIVEN: keine"
            return "ALTERNATIVEN: Container, Forum"
        if "PFLEGE-ANGEBOT" in system:
            # Design-B-spezifischer Aufruf, siehe _pflege_angebot() unten.
            if self.rng.random() < 0.55:
                return "ANTWORT: ja"
            return "ANTWORT: nein"
        if "AUSWAHL: <containername/dateiname" in system:
            return f"AUSWAHL: gewaehlt\nAKTION: {self.rng.choice(['verschieben', 'kopieren'])}"
        return None

    def suche_diskussionen(self, begriff, limit=8):
        # "innere Uhr"/"Schattensprache" bewusst als praktisch nie treffende
        # Eigenworte modelliert (realitaetsnah zu Baustein 7's echtem Befund).
        if begriff in ("innere Uhr", "Schattensprache"):
            return []
        has_hits = self.rng.random() < (0.7 if len(begriff) < 10 else 0.35)
        if not has_hits:
            return []
        return [{"id": i, "title": f"Diskussion {i}"} for i in range(1000, 1000 + limit)]

    def get_discussion(self, disk_id):
        text = f"<p>Inhalt der Diskussion {disk_id}. " + ("x" * self.rng.choice([500, 2000, 5000])) + "</p>"
        return {"title": f"Diskussion {disk_id}", "posts": [{"content": text}]}

    def zufaellige_diskussionen(self, limit=8):
        """Design C: die ~2400 echten Flarum-Diskussionen sind (anders als
        eine gezielte Suche) nie 'leer' -- ein zufaelliger Ausschnitt liefert
        praktisch immer etwas."""
        GESAMT_DISKUSSIONEN = 2400
        start = self.rng.randint(1, GESAMT_DISKUSSIONEN - limit)
        return [{"id": i, "title": f"Diskussion {i}"} for i in range(start, start + limit)]

    def container_sichere(self, wesen, cont, typ, inhalt, bezug_diskussion=None,
                           grundlage=None, grundlage_begruendung=None):
        pass

    def container_liste(self, wesen):
        return list(self.container_material[wesen].keys())

    def protokoll_schreibe(self, typ, wesen, text, dauer_sekunden=None, meta=None):
        pass

    def dk_lade(self, name):
        return {}


def _pflege_angebot(wesen: str, welt: Welt) -> bool:
    """Design B, Schritt 2: nur aufgerufen, wenn die Suche (mit Uebersetzung)
    nichts geliefert hat. Bietet Container-Pflege an -- echtes
    verschiebe()/kopiere() aus codewesen_container.py, hier nachgebildet
    statt gegen echte Dateien. Gibt True zurueck, wenn das Wesen etwas
    getan hat (= Sitzung war NICHT leer)."""
    material = welt.container_material[wesen]
    container_mit_inhalt = [c for c, dateien in material.items() if dateien]
    if len(container_mit_inhalt) < 1 or sum(len(d) for d in material.values()) < 1:
        return False  # ehrlich: nichts zum Pflegen da, keine Tuer zu oeffnen

    system = (
        f"Du bist {wesen}. Deine Suche eben hat nichts gefunden. Du hast aber eigene "
        f"Container mit Material: {', '.join(container_mit_inhalt)}.\n"
        "PFLEGE-ANGEBOT: moechtest du stattdessen kurz etwas darin verschieben oder "
        "kopieren -- oder ist dir auch das gerade nicht danach?\n"
        "Antworte GENAU so:\nANTWORT: <ja|nein>"
    )
    antwort = welt.llm(wesen, system, "(bitte jetzt antworten)", 50, 60.0)
    if not antwort or "ja" not in antwort.lower():
        return False

    von = welt.rng.choice(container_mit_inhalt)
    dateiname = welt.rng.choice(material[von])
    nach_kandidaten = [c for c in material if c != von] or [f"{von}_sortiert"]
    nach = welt.rng.choice(nach_kandidaten)
    aktion = welt.rng.choice(["verschieben", "kopieren"])
    welt.verschiebe_kopiere_aufrufe.append((wesen, aktion, von, dateiname, nach))
    if aktion == "verschieben":
        material.setdefault(nach, []).append(dateiname)
        material[von].remove(dateiname)
    else:
        material.setdefault(nach, []).append(dateiname)
    return True


def _stelle_container_sicher(wesen: str, welt: Welt):
    """Daniel, 2026-07-09: 'falls das wesen keinen container hat wird ihm
    vom system einer hinzugefuegt namens alles'. Passiert IMMER als erster
    Schritt des Stoeberns, nicht nur als Bedingung dafuer -- ein leerer
    Auffang-Container ist billig und macht ein spaeteres 'sichern' waehrend
    des Stoeberns immer moeglich, auch wenn vorher noch nie einer existierte."""
    if not welt.container_material[wesen]:
        welt.container_material[wesen]["alles"] = []


def _zufaelliges_stoebern(wesen: str, zustand: dict, welt: Welt) -> bool:
    """Design C: wenn weder die gezielte Suche noch das Pflege-Angebot
    etwas ergeben haben (bzw. das Wesen 'nein' zur Pflege gesagt hat),
    letzter und immer verfuegbarer Weg -- eine zufaellige Auswahl aus den
    ~2400 echten Flarum-Diskussionen, treibt danach DIESELBE echte
    _phase_lesen_schritt()-Maschine wie der gezielte Suchpfad (keine neue
    Lese-/Entscheidungslogik, keine neue Chunk-Deckel-Regel -- alles bereits
    in Baustein 10 gegen 200 Zufallsszenarien verifiziert)."""
    _stelle_container_sicher(wesen, welt)
    kandidaten = welt.zufaellige_diskussionen(limit=cun.KANDIDATEN_PRO_SUCHE)
    if not kandidaten:
        return False  # strukturell nie der Fall (2400 Diskussionen), Vollstaendigkeit halber
    zustand[wesen] = {
        "phase": "lesen",
        "start_ts": "2026-07-09T00:00:00+00:00",
        "interesse": "(zufaelliges Stoebern, keine Treffer fuer eigenes Interesse)",
        "kandidaten_ids": [k["id"] for k in kandidaten],
        "kandidat_index": 0,
        "chunk_index": 0,
        "funde_angesehen": 0,
    }
    cun._phase_lesen_schritt(wesen, zustand, "")
    return True  # das Lesen selbst ist bereits das Ergebnis, siehe Docstring oben


def _lauf(seed: int, design: str) -> dict:
    """design: 'A' (Ist-Zustand), 'B' (+Pflege-Angebot), 'C' (+Pflege +
    garantiertes Stoebern als letzter Weg)."""
    welt = Welt(seed)
    ergebnisse = {"leer": 0, "gesamt": 0, "pflege_genutzt": 0, "stoebern_genutzt": 0}

    with mock.patch.object(cun, "_llm", side_effect=welt.llm), \
         mock.patch.object(cun.flarum_api, "suche_diskussionen", side_effect=welt.suche_diskussionen), \
         mock.patch.object(cun.flarum_api, "get_discussion", side_effect=welt.get_discussion), \
         mock.patch.object(cun.container, "sichere", side_effect=welt.container_sichere), \
         mock.patch.object(cun.container, "liste", side_effect=welt.container_liste), \
         mock.patch.object(cun.protokoll, "schreibe", side_effect=welt.protokoll_schreibe), \
         mock.patch.object(cun.dk, "lade", side_effect=welt.dk_lade), \
         mock.patch("time.sleep", lambda *a, **k: None):

        for wesen in cun.WESEN:
            zustand = {wesen: {"phase": "neu"}}
            cun._phase_interesse(wesen, zustand, "")
            ergebnisse["gesamt"] += 1

            endete_leer = zustand[wesen].get("phase") == "fertig"  # nie in "lesen" gekommen
            if endete_leer and design in ("B", "C"):
                if _pflege_angebot(wesen, welt):
                    endete_leer = False
                    ergebnisse["pflege_genutzt"] += 1
            if endete_leer and design == "C":
                if _zufaelliges_stoebern(wesen, zustand, welt):
                    endete_leer = False
                    ergebnisse["stoebern_genutzt"] += 1
            if endete_leer:
                ergebnisse["leer"] += 1

    return ergebnisse


if __name__ == "__main__":
    N = 300
    summen = {d: {"leer": 0, "gesamt": 0, "pflege_genutzt": 0, "stoebern_genutzt": 0} for d in "ABC"}

    for seed in range(N):
        for design in "ABC":
            r = _lauf(seed, design)
            for k in summen[design]:
                summen[design][k] += r[k]

    print(f"{N} Laeufe x {len(cun.WESEN)} Wesen = {summen['A']['gesamt']} Einzel-Sitzungen pro Design\n")

    beschreibung = {
        "A": "Ist-Zustand (nur gezielte Flarum-Suche)",
        "B": "+ Container-Pflege-Angebot (verschieben/kopieren, wenn Material da ist)",
        "C": "+ garantiertes Stoebern als letzter Weg (Auto-Container 'alles' + Zufallsdiskussion)",
    }
    for design in "ABC":
        s = summen[design]
        quote = 100 * s["leer"] / s["gesamt"]
        print(f"DESIGN {design} ({beschreibung[design]}):")
        print(f"  Leerlauf-Quote: {s['leer']}/{s['gesamt']} = {quote:.1f}%")
        if s["pflege_genutzt"]:
            print(f"  Pflege-Angebot genutzt: {s['pflege_genutzt']} Sitzungen")
        if s["stoebern_genutzt"]:
            print(f"  Zufaelliges Stoebern genutzt: {s['stoebern_genutzt']} Sitzungen")
        print()

    print(f"Verbesserung A -> C: {100*(summen['A']['leer']-summen['C']['leer'])/summen['A']['gesamt']:.1f} "
          f"Prozentpunkte weniger Leerlauf.")
