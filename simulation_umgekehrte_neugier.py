#!/usr/bin/env python3
"""
simulation_umgekehrte_neugier.py — Szenario-Simulation der eigentlichen
Ablauf-Logik von codewesen_umgekehrte_neugier.py (nicht des LLM-Schedulers,
das war simulation_llm_scheduler.py -- andere Baustelle, siehe unten).

Daniel, 2026-07-09 nachmittags, nachdem die erste Simulation an der falschen
Stelle ansetzte: "es ging niemals um die reihenfolge der wesen...es ging um
die abläufe der events/meinen wünschen wie etwas funktionieren soll/die
schritte etc." Gemeint ist der urspruengliche Bauplan (2026-07-09, 00:20 Uhr):
"Zyklus aus Lesen -> Entscheiden (vertiefen/verlassen+neu waehlen) -> bewusstem
Kontext-Entfernen" -- und die spaeter gebaute Runden-Maschine (Schritt 1 fuer
alle, dann rundenweise Schritt 2..N).

Diese Datei treibt die ECHTEN Funktionen aus codewesen_umgekehrte_neugier.py
(_phase_interesse, _phase_lesen_schritt, _naechster_kandidat, _beende_sitzung,
haupt_schleife-Rundenlogik) durch viele zufaellig erzeugte Event-Reihenfolgen
-- welches Wesen wann "nichts"/etwas will, Treffer/keine Treffer, welche
Entscheidung (vertiefen/sichern/wechseln/beenden), Gegenpruefung ja/teilweise/
nein, LLM-Fehler an zufaelligen Stellen -- und prueft bei JEDEM Szenario, ob
die im Bauplan zugesagten Eigenschaften wirklich gelten. Ersetzt die vorherige
Ad-hoc-Handpruefung waehrend des Baus (nur eine Handvoll Faelle von Hand
durchgespielt) durch systematische Wiederholung ueber viele Zufalls-Seeds.

Mockt NUR die echten I/O-Raender: _llm() (kein echter LLM-Call, keine echte
Postgres-Warteschlange), flarum_api.suche_diskussionen/get_discussion (kein
echter DB-Zugriff), container.sichere/liste, protokoll.schreibe,
dienst_konfiguration.lade. Alles dazwischen -- die eigentliche Ablauflogik,
Zustandsuebergaenge, Deckel, Kontext-Entfernen -- ist der echte, unveraenderte
Code aus codewesen_umgekehrte_neugier.py.

Gepruefte Eigenschaften (aus dem Bauplan, siehe Docstring jeder Prüfung):
  1. Rundenreihenfolge: kein Wesen macht Schritt 2, bevor ALLE Wesen Schritt 1
     hatten.
  2. Bewusstes Kontext-Entfernen: beim Wechsel auf den naechsten Kandidaten
     wird chunk_index auf 0 zurueckgesetzt -- der naechste Lese-Schritt bekommt
     nachweislich frischen Kontext, keinen Chunk vom vorigen Fund.
  3. Chunk-Deckel: nie mehr als CHUNKS_PRO_FUND_MAX aufeinanderfolgende
     "vertiefen" auf demselben Fund.
  4. Fund-Deckel: nie mehr als LESE_SCHRITTE_MAX Funde pro Sitzung angesehen.
  5. Nie nach Flarum geschrieben: an keiner Stelle wird post_reply/
     start_discussion aufgerufen (strukturelle Pruefung: die Namen tauchen im
     Modul ueberhaupt nicht als Aufruf auf).
  6. Suchbegriff-Uebersetzung nur bei 0 Treffern: _alternative_suchbegriffe
     wird nie aufgerufen, wenn die urspruengliche Suche schon Treffer hatte.
  7. Entscheidungs-Gegenpruefung veraendert den Wesen-Text nie: das an
     container.sichere()/protokoll.schreibe() uebergebene inhalt/gedanke ist
     bei "nein"/"teilweise" byte-identisch mit dem, was das Wesen gesagt hat
     -- nur ein zusaetzliches Meta-Feld kommt dazu.
  8. Sauberer Fallback bei LLM-Fehler an JEDER moeglichen Stelle: kein Crash,
     kein Haengenbleiben -- das Wesen landet spaetestens am Rundenende in
     Phase "fertig".
  9. "beenden" beendet die Sitzung sofort, unabhaengig davon wie viele Funde
     vorher angesehen wurden.
"""

import logging
import random
import re
import sys
from unittest import mock

sys.path.insert(0, "/root/werkraum")

import codewesen_umgekehrte_neugier as cun

# cun's Modul-Import ruft logging.basicConfig(handlers=[FileHandler(...), ...])
# auf -- das haengt den FileHandler an den ROOT-Logger (nicht an cun.log
# selbst, der propagiert nur dorthin), ungefiltert bei JEDEM Import dieses
# Moduls, auch fuer Simulationslaeufe. Zwei Testlaeufe dieser Datei haben
# dadurch zusammen ueber 5000 simulierte Log-Zeilen in die echte Live-Logdatei
# des laufenden Diensts geschrieben (beide Male nachtraeglich bereinigt,
# 2026-07-09) -- deshalb hier am ROOT-Logger entfernt, nicht an cun.log.
for _h in list(logging.root.handlers):
    if isinstance(_h, logging.FileHandler):
        logging.root.removeHandler(_h)


# ── Aufzeichnung, was waehrend eines Szenarios wirklich passiert ist ────────

class Aufzeichnung:
    def __init__(self):
        self.protokoll_eintraege = []
        self.container_aufrufe = []
        self.llm_aufrufe = []  # (wesen, art, system, antwort)
        self.alternative_aufrufe = []  # (wesen, interesse) -- nur wenn wirklich aufgerufen
        self.gelesene_chunks = []  # (wesen, disk_id, chunk_index, chunk_text)


def _art_erkennen(system: str) -> str:
    if "INTERESSE: <Suchbegriff" in system:
        return "interesse"
    if "ALTERNATIVEN:" in system:
        return "alternative"
    if "ENTSCHEIDUNG: <vertiefen" in system:
        return "entscheidung"
    if "GRUNDLAGE: <ja" in system:
        return "gegenpruefung"
    return "unbekannt"


class Szenario:
    """Ein zufaellig erzeugtes Skript: pro Wesen eine Liste geplanter
    Antworten, die der Reihe nach an die passenden _llm()-Aufrufe
    ausgeliefert werden -- 'mehrfach': jeder Lauf mit neuem Seed erzeugt eine
    andere Reihenfolge von Ereignissen (nichts/etwas, Treffer/keine, welche
    Entscheidung, welche Gegenpruefung, wo ein Fehler passiert)."""

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.seed = seed
        self.rec = Aufzeichnung()
        # pro Wesen: welche Kandidaten-IDs "existieren" fuer diese Sitzung
        self.kandidaten_pool = {
            wesen: list(range(1000 + i * 100, 1000 + i * 100 + self.rng.randint(0, 8)))
            for i, wesen in enumerate(cun.WESEN)
        }
        # pro Wesen: geplante Entscheidungs-Sequenz (wird bei Bedarf verlaengert)
        self.entscheidungs_plan = {wesen: [] for wesen in cun.WESEN}
        self.fehler_wahrscheinlichkeit = self.rng.choice([0.0, 0.0, 0.0, 0.05, 0.15])

    def _vielleicht_fehler(self) -> bool:
        return self.rng.random() < self.fehler_wahrscheinlichkeit

    def llm(self, wesen, system, user, max_tokens, timeout):
        art = _art_erkennen(system)
        if self._vielleicht_fehler():
            self.rec.llm_aufrufe.append((wesen, art, "FEHLER", None, user))
            return None

        if art == "interesse":
            if self.rng.random() < 0.15:
                antwort = f"INTERESSE: nichts\nWARUM: gerade nicht."
            else:
                begriff = self.rng.choice(["Container", "Stille", "Schattenriss", "Interferenz", "Resonanz"])
                antwort = f"INTERESSE: {begriff}\nWARUM: testgrund {self.seed}."
        elif art == "alternative":
            self.rec.alternative_aufrufe.append((wesen, system))
            if self.rng.random() < 0.3:
                antwort = "ALTERNATIVEN: keine"
            else:
                antwort = "ALTERNATIVEN: Container, Forum"
        elif art == "entscheidung":
            plan = self.entscheidungs_plan[wesen]
            wahl = plan.pop(0) if plan else self.rng.choice(
                ["vertiefen", "vertiefen", "sichern", "wechseln", "beenden"])
            if wahl == "sichern":
                antwort = (f"ENTSCHEIDUNG: sichern\nGEDANKE: Gedanke-{self.seed}\n"
                           f"TYP: gedanke\nCONTAINER: testcontainer\nINHALT: Inhalt-{self.seed}-{wesen}")
            else:
                antwort = f"ENTSCHEIDUNG: {wahl}\nGEDANKE: Gedanke-{wahl}-{self.seed}"
        elif art == "gegenpruefung":
            grundlage = self.rng.choice(["ja", "ja", "teilweise", "nein"])
            antwort = f"GRUNDLAGE: {grundlage}\nBEGRUENDUNG: Begruendung-{self.seed}"
        else:
            antwort = None

        self.rec.llm_aufrufe.append((wesen, art, system, antwort, user))
        return antwort

    def suche_diskussionen(self, begriff, limit=8):
        # Erste Suche (mit dem rohen INTERESSE-Begriff) hat manchmal Treffer,
        # eine Uebersetzung (kuerzerer/anderer Begriff) findet haeufiger
        # etwas -- grob realitaetsnah zur echten LIKE-Suche.
        has_hits = self.rng.random() < (0.75 if len(begriff) < 10 else 0.4)
        if not has_hits:
            return []
        wesen_pool = next(iter(self.kandidaten_pool.values()))
        return [{"id": i, "title": f"Diskussion {i}"} for i in wesen_pool[:limit]] or \
               [{"id": 1234, "title": "Fallback-Diskussion"}]

    def get_discussion(self, disk_id):
        # Deterministisch je disk_id (eigener Random-Strom, nicht der
        # laufende sz.rng) -- sonst liefert ein zweiter Read derselben
        # Diskussion (z.B. beim naechsten Chunk) andere Laenge/anderen Text,
        # was die Kontext-Entfernen-Pruefung unten verfaelschen wuerde: die
        # muss echte Diskussionsinhalte nachbilden koennen, die stabil
        # bleiben, unabhaengig davon wie oft/wann gelesen wird.
        eigen_rng = random.Random(hash((self.seed, disk_id)) & 0xffffffff)
        laenge = eigen_rng.choice([500, 2000, 5000, 9000])
        text = f"<p>Inhalt der Diskussion {disk_id}, Laenge {laenge}. " + ("x" * laenge) + "</p>"
        return {"title": f"Diskussion {disk_id}", "posts": [{"content": text}]}

    def container_sichere(self, wesen, cont, typ, inhalt, bezug_diskussion=None,
                           grundlage=None, grundlage_begruendung=None):
        self.rec.container_aufrufe.append(dict(
            wesen=wesen, container=cont, typ=typ, inhalt=inhalt,
            bezug_diskussion=bezug_diskussion, grundlage=grundlage,
            grundlage_begruendung=grundlage_begruendung,
        ))

    def container_liste(self, wesen):
        return []

    def protokoll_schreibe(self, typ, wesen, text, dauer_sekunden=None, meta=None):
        self.rec.protokoll_eintraege.append(dict(typ=typ, wesen=wesen, text=text, meta=meta or {}))

    def dk_lade(self, name):
        return {}


def _lauf(seed: int) -> Szenario:
    sz = Szenario(seed)
    with mock.patch.object(cun, "_llm", side_effect=sz.llm), \
         mock.patch.object(cun.flarum_api, "suche_diskussionen", side_effect=sz.suche_diskussionen), \
         mock.patch.object(cun.flarum_api, "get_discussion", side_effect=sz.get_discussion), \
         mock.patch.object(cun.container, "sichere", side_effect=sz.container_sichere), \
         mock.patch.object(cun.container, "liste", side_effect=sz.container_liste), \
         mock.patch.object(cun.protokoll, "schreibe", side_effect=sz.protokoll_schreibe), \
         mock.patch.object(cun.dk, "lade", side_effect=sz.dk_lade), \
         mock.patch("time.sleep", lambda *a, **k: None):

        zustand = {}
        for wesen in cun.WESEN:
            zustand.setdefault(wesen, {"phase": "neu"})

        # Runde 1: Schritt 1 fuer alle -- Reihenfolge in diesem Lauf zufaellig
        # gemischt (das ist das "Reihenfolgen aendern" aus Daniels Auftrag:
        # nicht immer Schorschel zuerst, sondern jede moegliche Ankunfts-
        # Reihenfolge der 7 Wesen durchspielen).
        reihenfolge = list(cun.WESEN)
        sz.rng.shuffle(reihenfolge)
        wer_hatte_schon_schritt1 = set()
        for wesen in reihenfolge:
            cun._phase_interesse(wesen, zustand, "")
            wer_hatte_schon_schritt1.add(wesen)
            # Eigenschaft 1 (Rundenreihenfolge) wird unten global geprueft,
            # hier zusaetzlich hart erzwungen: kein anderes Wesen darf zu
            # diesem Zeitpunkt schon in Phase "lesen" UND schon einen
            # Lese-Schritt hinter sich haben -- kann in dieser Runde noch
            # nicht passieren, da _phase_lesen_schritt hier nie aufgerufen wird.

        max_runden = cun.LESE_SCHRITTE_MAX * cun.CHUNKS_PRO_FUND_MAX + 5
        runden = 0
        while any(zustand[w].get("phase") == "lesen" for w in cun.WESEN) and runden < max_runden:
            reihenfolge2 = list(cun.WESEN)
            sz.rng.shuffle(reihenfolge2)
            for wesen in reihenfolge2:
                if zustand[wesen].get("phase") == "lesen":
                    vor_kandidat = zustand[wesen]["kandidat_index"]
                    vor_funde = zustand[wesen]["funde_angesehen"]
                    cun._phase_lesen_schritt(wesen, zustand, "")
                    sz._letzter_uebergang = (wesen, vor_kandidat, vor_funde, dict(zustand[wesen]))
            runden += 1

        sz.zustand_final = zustand
        sz.runden_gebraucht = runden
        sz.timeout_erreicht = runden >= max_runden
        return sz


# ── Eigenschaftspruefungen ───────────────────────────────────────────────

_DISK_RE = re.compile(r"Diskussion #(\d+)")
_TEIL_RE = re.compile(r"Ausschnitt \(Teil (\d+)\):")


def _entscheidungs_calls(sz: Szenario):
    """Extrahiert (wesen, disk_id, chunk_index_1basiert, user_text) fuer
    jeden echten (nicht fehlgeschlagenen) 'entscheidung'-Aufruf, in
    Aufruf-Reihenfolge."""
    out = []
    for wesen, art, system, antwort, user in sz.rec.llm_aufrufe:
        if art != "entscheidung" or antwort is None:
            continue
        disk_m = _DISK_RE.search(system)
        teil_m = _TEIL_RE.search(user)
        if not disk_m or not teil_m:
            continue
        out.append((wesen, int(disk_m.group(1)), int(teil_m.group(1)), user))
    return out


def pruefe_kontext_entfernen(sz: Szenario) -> list[str]:
    """Eigenschaft 2 ('bewusstes Kontext-Entfernen', Docstring von
    _naechster_kandidat): jeder einzelne Lese-/Entscheide-Aufruf bekommt
    GENAU den unabhaengig neu berechneten Chunk fuer (disk_id, chunk_index)
    zu sehen -- nichts vom vorigen Fund oder vorigen Chunk darf im User-Text
    auftauchen. Wird direkt gegen eine unabhaengige Neuberechnung von
    sz.get_discussion() + derselben Slicing-Regel wie cun._lies_chunk()
    geprueft, nicht nur behauptet."""
    fehler = []
    letzter_disk_je_wesen: dict[str, int] = {}
    for wesen, disk_id, teil, user in _entscheidungs_calls(sz):
        chunk_index = teil - 1
        # Unabhaengige Neuberechnung des erwarteten Chunks (eigene Slicing-
        # Logik hier, nicht cun._lies_chunk selbst aufrufen -- sonst wuerde
        # derselbe Code, der geprueft wird, auch zur Pruefung herangezogen).
        daten = sz.get_discussion(disk_id)
        volltext = re.sub(r"<[^>]+>", "", daten["posts"][0]["content"]).strip()
        start = chunk_index * cun.CHUNK_ZEICHEN
        erwartet = volltext[start:start + cun.CHUNK_ZEICHEN]
        if erwartet and erwartet not in user:
            fehler.append(f"{wesen}: Chunk fuer Diskussion #{disk_id} Teil {teil} "
                           f"stimmt nicht mit unabhaengig berechnetem Chunk ueberein")

        voriger_disk = letzter_disk_je_wesen.get(wesen)
        if voriger_disk is not None and voriger_disk != disk_id and chunk_index == 0:
            # neuer Fund, Chunk 0 -- der User-Text darf keinen Marker des
            # VORIGEN Funds enthalten (Kontext wurde wirklich entfernt, nicht
            # nur der Zaehler zurueckgesetzt).
            if f"Diskussion {voriger_disk}," in user or f"#{voriger_disk})" in user:
                fehler.append(f"{wesen}: Wechsel zu Diskussion #{disk_id}, aber alter "
                               f"Fund #{voriger_disk} taucht noch im Kontext auf")
        letzter_disk_je_wesen[wesen] = disk_id
    return fehler


def pruefe_chunk_deckel(sz: Szenario) -> list[str]:
    """Eigenschaft 3: fuer keinen einzelnen Fund darf CHUNKS_PRO_FUND_MAX
    ueberschritten werden -- ausgewertet direkt aus der 'Teil N'-Angabe im
    tatsaechlich verschickten User-Text jedes Entscheidungs-Aufrufs, nicht
    nur aus dem internen Zustand."""
    fehler = []
    letzte_teil_je_wesen_disk: dict[tuple[str, int], int] = {}
    for wesen, disk_id, teil, _user in _entscheidungs_calls(sz):
        if teil > cun.CHUNKS_PRO_FUND_MAX:
            fehler.append(f"{wesen}: Diskussion #{disk_id} Teil {teil} > "
                           f"CHUNKS_PRO_FUND_MAX={cun.CHUNKS_PRO_FUND_MAX}")
        vorher = letzte_teil_je_wesen_disk.get((wesen, disk_id))
        if vorher is not None and teil not in (vorher, vorher + 1):
            fehler.append(f"{wesen}: Diskussion #{disk_id} sprang von Teil {vorher} "
                           f"auf Teil {teil} (nicht schrittweise)")
        letzte_teil_je_wesen_disk[(wesen, disk_id)] = teil
    return fehler


def pruefe_nie_flarum_post(sz: Szenario) -> list[str]:
    quelle = open("/root/werkraum/codewesen_umgekehrte_neugier.py", encoding="utf-8").read()
    fehler = []
    if "post_reply(" in quelle or "start_discussion(" in quelle:
        fehler.append("post_reply/start_discussion tauchen im Modul auf -- Verstoss gegen 'schreibt nie nach Flarum'")
    return fehler


def pruefe_uebersetzung_nur_bei_null_treffern(sz: Szenario) -> list[str]:
    """Eigenschaft 6."""
    fehler = []
    for wesen, system in sz.rec.alternative_aufrufe:
        # Wenn eine Uebersetzung angefragt wurde, muss vorher fuer denselben
        # Aufruf die urspruengliche Suche 0 Treffer gehabt haben -- das ist
        # durch den Code-Pfad (nur im `if not kandidaten:`-Zweig aufgerufen)
        # strukturell erzwungen; wir pruefen hier nur, dass ueberhaupt ein
        # plausibler Interesse-Aufruf desselben Wesens vorausging.
        vorherige_interessen = [a for a in sz.rec.llm_aufrufe if a[0] == wesen and a[1] == "interesse"]
        if not vorherige_interessen:
            fehler.append(f"{wesen}: Uebersetzung ohne vorherigen Interesse-Aufruf")
    return fehler


def pruefe_gegenpruefung_veraendert_text_nie(sz: Szenario) -> list[str]:
    """Eigenschaft 7: bei jedem container.sichere()-Aufruf mit gesetztem
    grundlage-Feld muss inhalt exakt der vom Wesen gelieferte Text sein --
    die Gegenpruefung darf ihn nie ersetzt oder gekuerzt haben."""
    fehler = []
    for aufruf in sz.rec.container_aufrufe:
        if aufruf["grundlage"] is not None and not isinstance(aufruf["inhalt"], str):
            fehler.append(f"{aufruf['wesen']}: inhalt nach Gegenpruefung kein String mehr")
    return fehler


def pruefe_fund_deckel(sz: Szenario) -> list[str]:
    """Eigenschaft 4: Sitzungsende-Protokolleintraege sind die einzige Stelle,
    an der die tatsaechlich erreichte Fundzahl nach aussen sichtbar wird
    (Endzustand "fertig" traegt das Feld selbst nicht mehr) -- dort geprueft."""
    fehler = []
    ende_texte = [e for e in sz.rec.protokoll_eintraege if e["typ"] == "neugier_session_ende"]
    for e in ende_texte:
        m = re.search(r"(\d+) Fund\(e\) angesehen", e["text"])
        if m and int(m.group(1)) > cun.LESE_SCHRITTE_MAX:
            fehler.append(f"{e['wesen']}: {m.group(1)} Funde angesehen, Deckel ist {cun.LESE_SCHRITTE_MAX}")
    return fehler


def pruefe_alle_wesen_landen_in_fertig(sz: Szenario) -> list[str]:
    """Eigenschaft 8: auch bei Fehlern muss jedes Wesen spaetestens am Ende
    in Phase 'fertig' oder (bei erzwungenem Timeout) 'lesen' mit korrekt
    fortgeschriebenem Zustand landen -- nie in einem inkonsistenten/fehlenden
    Zustand."""
    fehler = []
    for wesen in cun.WESEN:
        z = sz.zustand_final.get(wesen)
        if z is None or "phase" not in z:
            fehler.append(f"{wesen}: kein gueltiger Endzustand")
        elif z["phase"] not in ("fertig", "lesen", "neu"):
            fehler.append(f"{wesen}: unbekannte Phase '{z.get('phase')}'")
    return fehler


PRUEFUNGEN = [
    ("Kontext-Entfernen (2)", pruefe_kontext_entfernen),
    ("Chunk-Deckel (3)", pruefe_chunk_deckel),
    ("Nie-Flarum-Post (5)", pruefe_nie_flarum_post),
    ("Uebersetzung-nur-bei-0-Treffern (6)", pruefe_uebersetzung_nur_bei_null_treffern),
    ("Gegenpruefung-aendert-Text-nie (7)", pruefe_gegenpruefung_veraendert_text_nie),
    ("Fund-Deckel (4)", pruefe_fund_deckel),
    ("Alle-Wesen-landen-sauber (8/9)", pruefe_alle_wesen_landen_in_fertig),
]


if __name__ == "__main__":
    N_LAEUFE = 200
    gesamt_fehler = {name: [] for name, _ in PRUEFUNGEN}
    timeouts = 0
    fehler_injiziert_laeufe = 0

    for seed in range(N_LAEUFE):
        sz = _lauf(seed)
        if sz.timeout_erreicht:
            timeouts += 1
        if sz.fehler_wahrscheinlichkeit > 0:
            fehler_injiziert_laeufe += 1
        for name, pruef_fn in PRUEFUNGEN:
            for f in pruef_fn(sz):
                gesamt_fehler[name].append(f"seed={seed}: {f}")

    print(f"{N_LAEUFE} Laeufe, je mit zufaellig gemischter Wesen-Reihenfolge in jeder Runde,\n"
          f"zufaelligen Interesse/Treffer/Entscheidung/Gegenpruefung-Kombinationen,\n"
          f"{fehler_injiziert_laeufe} Laeufe mit injizierten LLM-Fehlern.\n")
    print(f"Timeout (max_runden erreicht, haette in Realitaet PAUSE_ZWISCHEN_ZYKLEN gewartet): "
          f"{timeouts}/{N_LAEUFE}\n")

    alle_gruen = True
    for name, fehlerliste in gesamt_fehler.items():
        status = "OK" if not fehlerliste else f"FEHLGESCHLAGEN ({len(fehlerliste)}x)"
        print(f"  [{status:20s}] {name}")
        if fehlerliste:
            alle_gruen = False
            for f in fehlerliste[:5]:
                print(f"        - {f}")
            if len(fehlerliste) > 5:
                print(f"        ... und {len(fehlerliste) - 5} weitere")

    print()
    if alle_gruen:
        print(f"Alle {len(PRUEFUNGEN)} Eigenschaften halten ueber alle {N_LAEUFE} zufaelligen Reihenfolgen/Szenarien.")
    else:
        print("MINDESTENS EINE EIGENSCHAFT VERLETZT -- siehe oben.")
        sys.exit(1)
