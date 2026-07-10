#!/usr/bin/env python3
"""
simulation_umgekehrte_neugier_v2_rauchtest.py — schneller Rauchtest fuer den
Baustein-11-Umbau (4 Linsen, Pflege/Stoebern, Container-Zuordnungs-Phase,
freie Diskussions-Wechsel-Regel). Kein vollstaendiger Eigenschaftsbeweis wie
Baustein 10 (das waere der naechste Schritt) -- nur: laeuft die neue
Zustandsmaschine unter vielen zufaelligen Szenarien durch, ohne haengen zu
bleiben oder abzustuerzen, und respektiert sie die grob beobachtbaren Regeln
(min. 2 Posts + 3 Min vor Wechsel, max FUNDE_MAX Diskussionen, Zeitbudget)?
"""

import logging
import random
import sys
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, "/root/werkraum")
import codewesen_umgekehrte_neugier as cun

for _h in list(logging.root.handlers):
    if isinstance(_h, logging.FileHandler):
        logging.root.removeHandler(_h)
logging.root.setLevel(logging.WARNING)


class UhrManipulierbareZeit:
    """Simuliert echten Zeitablauf schnell: jeder _llm()-Aufruf laesst die
    interne Uhr um eine realistische Generierungsdauer weiterspringen, damit
    die 3-Minuten/6-Minuten-Schwellen unter echten Zeitbedingungen getestet
    werden, ohne real zu warten."""
    def __init__(self, start: datetime):
        self.jetzt = start

    def vergehen(self, sekunden: float):
        self.jetzt += timedelta(seconds=sekunden)


class Welt:
    def __init__(self, seed: int, uhr: UhrManipulierbareZeit):
        self.rng = random.Random(seed)
        self.seed = seed
        self.uhr = uhr
        self.container_material = {
            wesen: {f"c{i}": [f"eintrag_{i}_{j}.md" for j in range(self.rng.randint(0, 3))]
                    for i in range(self.rng.randint(0, 2))}
            for wesen in cun.WESEN
        }
        self.diskussionen = {i: self.rng.randint(1, 6) for i in range(1000, 1200)}  # id -> Anzahl Posts

    def llm(self, wesen, system, user, max_tokens, timeout):
        self.uhr.vergehen(self.rng.uniform(20, 70))  # reale Generierungsdauer nachbilden
        if "INTERESSE: <Wort" in system:
            if self.rng.random() < 0.3:
                return "INTERESSE: nichts\nWARUM: gerade nicht."
            themen = ["Container", "Stille", "was verbindet uns hier eigentlich?",
                      "ich will herausfinden ob Resonanz messbar ist", "Schattensprache"]
            return f"INTERESSE: {self.rng.choice(themen)}\nWARUM: testgrund {self.seed}."
        if "GEGENTEIL:" in system:
            return f"GEGENTEIL: das Gegenteil von testgrund {self.seed}"
        if "ALTERNATIVEN:" in system:
            return "ALTERNATIVEN: keine" if self.rng.random() < 0.4 else "ALTERNATIVEN: Container, Forum"
        if "ANTWORT: <ja|nein>" in system:
            return f"ANTWORT: {'ja' if self.rng.random() < 0.5 else 'nein'}"
        if "VON_CONTAINER:" in system:
            # simple: waehle irgendeinen realen Eintrag aus der Systemnachricht
            for c, dateien in self.container_material[wesen].items():
                if dateien:
                    return (f"VON_CONTAINER: {c}\nDATEINAME: {dateien[0]}\n"
                            f"NACH_CONTAINER: {c}_neu\nAKTION: {self.rng.choice(['verschieben', 'kopieren'])}")
            return "VON_CONTAINER: nix\nDATEINAME: nix\nNACH_CONTAINER: nix\nAKTION: verschieben"
        if "NAECHSTER_SCHRITT:" in system:
            mitgenommen = f"Mitgenommen-{self.seed}" if self.rng.random() < 0.4 else ""
            optionen = ["naechster_post", "vorheriger_post", "zufaelliger_post", "diesen post weiterlesen"]
            if "diskussion_wechseln" in system:
                optionen.append("diskussion_wechseln")
            schritt = self.rng.choice(optionen)
            return (f"LINSE_LESEN: Lesen-{self.seed}\nLINSE_LERNEN: Lernen-{self.seed}\n"
                    f"LINSE_GEGENTEIL: Gegenteil-{self.seed}\nLINSE_EIGENE_FRAGE: Frage-{self.seed}\n"
                    f"MITGENOMMEN: {mitgenommen}\nNAECHSTER_SCHRITT: {schritt}")
        if "GRUNDLAGE:" in system:
            return f"GRUNDLAGE: {self.rng.choice(['ja', 'teilweise', 'nein'])}\nBEGRUENDUNG: b-{self.seed}"
        if "TYP: <ein Wort>" in system:
            typ = self.rng.choice(["gedanke", "idee", "meinung"])
            ziel = self.rng.choice(["sortiert", "unsortiert", ""])
            return (f"BERUEHRT: b-{self.seed}\nTRAEGT: t-{self.seed}\n"
                    f"CONTAINER: {ziel}\nBEGRUENDUNG: passt-{self.seed}\nTYP: {typ}")
        if "PFAD:" in system:
            # Baustein 19: _frage_stoeber_trio() -- absichtlich oft "ablehnen",
            # damit der Rauchtest auch den 2x-Ablehnung-dann-random-Pfad durchlaeuft.
            optionen = ["frueh", "mitte", "spaet", "ablehnen", "ablehnen"]
            return f"PFAD: {self.rng.choice(optionen)}"
        return None

    def suche_diskussionen(self, begriff, limit=8):
        if self.rng.random() < 0.5:
            return []
        ids = self.rng.sample(list(self.diskussionen.keys()), min(limit, len(self.diskussionen)))
        return [{"id": i, "title": f"D{i}"} for i in ids]

    def zufaellige_diskussionen(self, limit=8):
        ids = self.rng.sample(list(self.diskussionen.keys()), min(limit, len(self.diskussionen)))
        return [{"id": i, "title": f"D{i}"} for i in ids]

    def stoeber_pool(self, anzahl_random=8):
        ids = self.rng.sample(list(self.diskussionen.keys()), min(anzahl_random + 3, len(self.diskussionen)))
        pool = [{"id": i, "title": f"D{i}", "herkunft": "random"} for i in ids[:anzahl_random]]
        for i, herkunft in zip(ids[anzahl_random:], ("frueh", "mitte", "spaet")):
            pool.append({"id": i, "title": f"D{i}", "herkunft": herkunft})
        return pool

    def get_discussion(self, disk_id):
        n = self.diskussionen.get(disk_id, 3)
        # Realistische Laenge statt Mini-Text -- sonst braucht das gemockte
        # Token-Budget (5555, echte Tokens/4-Zeichen-Naeherung im Test)
        # tausende Fake-Posts und die Rauchtest-Schrittgrenze faellt faelschlich
        # als "Endlosschleife" auf, obwohl es nur an winziger Testlast liegt.
        return {"title": f"D{disk_id}",
                "posts": [{"content": f"<p>Inhalt Post {i} " + ("Textfuellung " * 30) + "</p>",
                           "username": f"user{i}"} for i in range(n)]}

    def container_sichere(self, wesen, cont, typ, inhalt, bezug_diskussion=None,
                           grundlage=None, grundlage_begruendung=None):
        self.container_material.setdefault(wesen, {}).setdefault(cont, []).append(f"neu_{self.seed}.md")

    def container_liste(self, wesen):
        return [c for c, d in self.container_material[wesen].items()]

    def container_dateien(self, wesen, cont):
        return self.container_material[wesen].get(cont, [])

    def container_verschiebe(self, wesen, von, datei, nach):
        return True

    def container_kopiere(self, wesen, von, datei, nach):
        return True

    def container_sicherstelle(self, wesen, anlass=""):
        bestehende = self.container_liste(wesen)
        if bestehende:
            return bestehende[0]
        self.container_material[wesen]["alles"] = []
        return "alles"

    def protokoll_schreibe(self, typ, wesen, text, dauer_sekunden=None, meta=None):
        pass

    def dk_lade(self, name):
        return {}


def _lauf(seed: int, budget_modus: str = "token") -> dict:
    uhr = UhrManipulierbareZeit(datetime(2026, 7, 9, 20, 0, 0, tzinfo=timezone.utc))
    welt = Welt(seed, uhr)
    verletzungen = []

    class _FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return uhr.jetzt

    with mock.patch.object(cun, "_llm", side_effect=welt.llm), \
         mock.patch.object(cun, "_zaehle_tokens", side_effect=lambda text: len(text) // 4), \
         mock.patch.object(cun, "_tokenisiere", side_effect=lambda text: list(range(len(text) // 4))), \
         mock.patch.object(cun, "_detokenisiere", side_effect=lambda tokens: "x" * (len(tokens) * 4)), \
         mock.patch.object(cun.flarum_api, "suche_diskussionen", side_effect=welt.suche_diskussionen), \
         mock.patch.object(cun.flarum_api, "zufaellige_diskussionen", side_effect=welt.zufaellige_diskussionen), \
         mock.patch.object(cun.flarum_api, "stoeber_pool", side_effect=welt.stoeber_pool), \
         mock.patch.object(cun.flarum_api, "get_discussion", side_effect=welt.get_discussion), \
         mock.patch.object(cun.container, "sichere", side_effect=welt.container_sichere), \
         mock.patch.object(cun.container, "liste", side_effect=welt.container_liste), \
         mock.patch.object(cun.container, "dateien", side_effect=welt.container_dateien), \
         mock.patch.object(cun.container, "verschiebe", side_effect=welt.container_verschiebe), \
         mock.patch.object(cun.container, "kopiere", side_effect=welt.container_kopiere), \
         mock.patch.object(cun.container, "sicherstelle_container", side_effect=welt.container_sicherstelle), \
         mock.patch.object(cun.protokoll, "schreibe", side_effect=welt.protokoll_schreibe), \
         mock.patch.object(cun.dk, "lade", side_effect=welt.dk_lade), \
         mock.patch("codewesen_umgekehrte_neugier.datetime", _FakeDatetime), \
         mock.patch("time.sleep", lambda *a, **k: None):

        for wesen in cun.WESEN:
            zustand = {wesen: {"phase": "neu"}}
            cun._phase_interesse(wesen, zustand, "")

            schritte = 0
            while zustand[wesen]["phase"] in ("lesen", "container_zuordnung") and schritte < 500:
                if zustand[wesen]["phase"] == "lesen":
                    z = zustand[wesen]
                    fund_dauer_vor = (uhr.jetzt - datetime.fromisoformat(z["fund_start_ts"])).total_seconds()
                    posts_vor = z["posts_gelesen_dieser_fund"]
                    cun._phase_lesen_schritt(wesen, zustand, "", budget_modus)
                else:
                    cun._phase_container_zuordnung(wesen, zustand)
                schritte += 1

            if schritte >= 500:
                verletzungen.append(f"{wesen}: Endlosschleife nicht terminiert (500+ Schritte)")
            if zustand[wesen]["phase"] != "fertig":
                verletzungen.append(f"{wesen}: Sitzung endete nicht in Phase 'fertig' (war: {zustand[wesen]['phase']})")

    return {"verletzungen": verletzungen}


if __name__ == "__main__":
    N = 100
    # Baustein 18: beide budget_modus-Zweige real durchlaufen, nicht nur den
    # Standard -- sonst waere der "zeit"-Pfad nie tatsaechlich getestet,
    # nur kompiliert.
    for budget_modus in ("token", "zeit"):
        alle_verletzungen = []
        for seed in range(N):
            r = _lauf(seed, budget_modus)
            alle_verletzungen.extend(r["verletzungen"])

        print(f"budget_modus={budget_modus}: {N} Laeufe x {len(cun.WESEN)} Wesen = {N * len(cun.WESEN)} Einzel-Sitzungen")
        if alle_verletzungen:
            print(f"  VERLETZUNGEN ({len(alle_verletzungen)}):")
            for v in alle_verletzungen[:20]:
                print(f"    - {v}")
        else:
            print("  Keine Endlosschleifen, keine haengenden Zustaende -- alle Sitzungen liefen sauber bis 'fertig'.")
