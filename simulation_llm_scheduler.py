#!/usr/bin/env python3
"""
simulation_llm_scheduler.py — Diskrete-Ereignis-Simulation der gemeinsamen
"hintergrund"-LLM-Warteschlange (N_SLOTS=1, echtes Modell aus llm_scheduler.py:
Prioritaet+FIFO, nicht-praeemptiv, jeder Aufrufer gibt nach eigenem
max_wartezeit sauber auf).

Zweck (Daniel, 2026-07-09 nachmittags, nach der PRIO_HOCH-Anhebung von
codewesen_umgekehrte_neugier.py per Live-Test+Rueckfrage): "entwickle ein
System das mein System wirklich ermoeglicht, simuliere alle deine Ideen
durch, aendere Reihenfolgen meines Systems dabei mehrfach" -- statt jede
Konfiguration einzeln stundenlang live zu testen, viele Konfigurationen in
Sekunden durchspielen und mit echten Zahlen vergleichen. Direkter
Nachfolger der Simulation vom 2026-07-07 (docs/systemdoku/19_llm_scheduler.md),
die explizit als offene Luecke vermerkt war: "eine neue Simulation mit
N_SLOTS=1 waere noetig, um die reale Erfolgsquote/Wartezeit unter der
jetzigen Deckelung einzuschaetzen."

Datengrundlage:
  GEMESSEN (nicht geschaetzt):
    - Ankunftsraten: Live-Sampling von `llm_warteschlange` am 2026-07-09,
      ca. 16:40-16:42 Uhr, 40x im 3s-Abstand (21 distinkte Eintraege im
      118.8s-Fenster) -- siehe _claude/notizen/2026-07-09.md, "Sechste Session".
      Waehrend dieses Fensters war die Flarum-Post-Sperre aktiv, die
      Entwurfs-Erzeugung (batch_generator/forum_neugier/aufgabenchats) daher
      strukturell nahezu inaktiv -- das ist der reale AKTUELLE Zustand,
      nicht der theoretische Vollausbau.
    - Prioritaeten/max_wartezeit/max_haltezeit: echte Konstanten aus dem
      Code, per grep ueber alle `llm_scheduler.LLMSlot(...)`-Aufrufer
      (2026-07-09).
    - Bedienzeiten umgekehrte_neugier: real gemessen, siehe
      docs/2026-07-09_flarum_stopp_bericht.md
      (_frage_interesse: 8.9-69.7s, _entscheide_ueber_fund: 28.2-71.4s, Ø 54.3s).
  GESCHAETZT (klar markiert, keine Einzelmessung vorhanden):
    - Bedienzeiten der uebrigen Dienste (reaktion/agent/engagement/
      lg_daemon/weltbild): als Gleichverteilung 10-90s angenommen, angelehnt
      an die gemessene umgekehrte_neugier-Spanne als naechstliegende reale
      Referenz im selben System (gleiche Modell-Generierungsgeschwindigkeit).
    - ready_check (flarum_poster.pruefe_bereit): sehr kurz angenommen
      (2-8s), weil max_tokens=10 im echten Aufruf (kurze Ja/Nein-Antwort).

Modell entspricht 1:1 der echten Logik in llm_scheduler.py::LLMSlot.__enter__:
nicht-praeemptiv (laufender Halter wird nie unterbrochen), beim Freiwerden
gewinnt der wartende Eintrag mit kleinster (prioritaet, angefragt_um).
"""

import random
import statistics
from dataclasses import dataclass

PRIO_HOCH, PRIO_NORMAL, PRIO_NIEDRIG = 0, 1, 2
PRIO_NAME = {0: "HOCH", 1: "NORMAL", 2: "NIEDRIG"}

SIM_STUNDEN = 4.0
SIM_SEK = SIM_STUNDEN * 3600


@dataclass
class Rolle:
    name: str
    prioritaet: int
    rate_pro_std: float          # Ankunftsrate (Poisson)
    service_min: float
    service_max: float
    max_wartezeit: float
    gemessen: bool                # True = Ankunft/Bedienzeit real gemessen, False = geschaetzt


@dataclass
class Ankunft:
    zeit: float
    rolle: str
    prioritaet: int
    max_wartezeit: float
    service: float


def _exponential_ankuenfte(rate_pro_std: float, dauer_sek: float, rng: random.Random):
    if rate_pro_std <= 0:
        return []
    zeiten = []
    t = 0.0
    lam = rate_pro_std / 3600.0
    while True:
        t += rng.expovariate(lam)
        if t > dauer_sek:
            break
        zeiten.append(t)
    return zeiten


def baue_ankuenfte(rollen: list[Rolle], rng: random.Random) -> list[Ankunft]:
    ankuenfte = []
    for rolle in rollen:
        for zeit in _exponential_ankuenfte(rolle.rate_pro_std, SIM_SEK, rng):
            service = rng.uniform(rolle.service_min, rolle.service_max)
            ankuenfte.append(Ankunft(zeit, rolle.name, rolle.prioritaet, rolle.max_wartezeit, service))
    ankuenfte.sort(key=lambda a: a.zeit)
    return ankuenfte


def simuliere(rollen: list[Rolle], seed: int) -> dict:
    """Ereignisgesteuerte Simulation der echten LLMSlot-Logik: 1 Slot,
    nicht-praeemptiv, Auswahl beim Freiwerden nach (prioritaet, angefragt_um),
    jeder Wartende gibt nach seiner eigenen max_wartezeit auf."""
    rng = random.Random(seed)
    ankuenfte = baue_ankuenfte(rollen, rng)

    warteschlange: list[Ankunft] = []
    ergebnisse = {r.name: {"erfolg": 0, "timeout": 0, "wartezeiten": []} for r in rollen}

    ai = 0
    n = len(ankuenfte)
    aktueller_halter_ende = 0.0  # Zeitpunkt, ab dem der Slot als naechstes frei wird

    def slot_leeren(bis_zeit: float):
        """Vergibt den Slot so lange weiter, wie er vor `bis_zeit` frei wird
        (nicht-praeemptiv: laeuft der aktuelle Halter ueber `bis_zeit` hinaus,
        bleibt er unangetastet bis zu seinem eigenen Ende). `max()` ist der
        eigentliche Fix ggue. der ersten Fassung: ein Wartender kann fruehestens
        bei seiner eigenen Ankunftszeit bedient werden, auch wenn der Slot
        schon vorher leer stand."""
        nonlocal aktueller_halter_ende, warteschlange
        while warteschlange and aktueller_halter_ende <= bis_zeit:
            noch_wartend = []
            for w in warteschlange:
                gewartet = aktueller_halter_ende - w.zeit
                if gewartet > w.max_wartezeit:
                    ergebnisse[w.rolle]["timeout"] += 1
                else:
                    noch_wartend.append(w)
            warteschlange = noch_wartend
            if not warteschlange:
                return
            warteschlange.sort(key=lambda w: (w.prioritaet, w.zeit))
            gewinner = warteschlange.pop(0)
            start = max(aktueller_halter_ende, gewinner.zeit)
            wartezeit = start - gewinner.zeit
            ergebnisse[gewinner.rolle]["erfolg"] += 1
            ergebnisse[gewinner.rolle]["wartezeiten"].append(wartezeit)
            aktueller_halter_ende = start + gewinner.service

    while ai < n:
        neu = ankuenfte[ai]
        ai += 1
        slot_leeren(neu.zeit)
        warteschlange.append(neu)

    # Restliche Warteschlange bis zum echten Ende durchspielen (kein
    # Randeffekt mehr: derselbe Mechanismus, bis nichts mehr wartet oder
    # alle per eigener max_wartezeit aufgegeben haben).
    slot_leeren(float("inf"))
    for w in warteschlange:
        ergebnisse[w.rolle]["timeout"] += 1

    # Zusammenfassen
    zusammenfassung = {}
    for name, d in ergebnisse.items():
        gesamt = d["erfolg"] + d["timeout"]
        quote = d["erfolg"] / gesamt if gesamt else float("nan")
        wz = sorted(d["wartezeiten"])
        mittel = statistics.mean(wz) if wz else float("nan")
        p95 = wz[int(0.95 * (len(wz) - 1))] if wz else float("nan")
        zusammenfassung[name] = dict(gesamt=gesamt, erfolg=d["erfolg"], timeout=d["timeout"],
                                      quote=quote, mittel_wartezeit=mittel, p95_wartezeit=p95,
                                      wartezeiten=wz)
    return zusammenfassung


# ── Reale, gemessene Basis-Konfiguration (2026-07-09, Sperre aktiv) ────────

def basis_rollen(neugier_prio: int, neugier_service_min=8.9, neugier_service_max=71.4) -> list[Rolle]:
    return [
        Rolle("reaktion", PRIO_NORMAL, 302.9, 10, 90, 90, gemessen=True),
        Rolle("agent", PRIO_NORMAL, 90.9, 10, 90, 90, gemessen=True),
        Rolle("engagement", PRIO_NIEDRIG, 90.9, 10, 90, 90, gemessen=True),
        Rolle("lg_daemon", PRIO_NIEDRIG, 60.6, 10, 90, 90, gemessen=True),
        Rolle("weltbild", PRIO_NIEDRIG, 30.3, 10, 90, 90, gemessen=True),
        Rolle("ready_check", PRIO_HOCH, 60.6, 2, 8, 90, gemessen=True),
        Rolle("umgekehrte_neugier", neugier_prio, 7 * (60 / 90), neugier_service_min, neugier_service_max,
              3600, gemessen=True),
        # ANNAHME (Sperre aktuell aktiv, daher aktuell ~0 real beobachtet):
        # falls die Sperre aufgehoben wird, kommt zusaetzliche Last dazu --
        # separat unten als eigenes Szenario, nicht in der Basis-Konfiguration.
    ]


def rollen_mit_entwurfslast(neugier_prio: int) -> list[Rolle]:
    r = basis_rollen(neugier_prio)
    # ANNAHME, nicht gemessen (Sperre war waehrend der Live-Messung aktiv):
    # grobe Ordnung anhand der Poll-Intervalle im Code (PAUSE_NACH_CALL=5s
    # batch_generator, PAUSE_ZWISCHEN_WESEN=8s forum_neugier) als vorsichtige
    # Naeherung, deutlich als Schaetzung markiert.
    r.append(Rolle("batch_generator", PRIO_NORMAL, 40.0, 10, 90, 90, gemessen=False))
    r.append(Rolle("forum_neugier", PRIO_NIEDRIG, 20.0, 10, 90, 90, gemessen=False))
    r.append(Rolle("aufgabenchats", PRIO_NIEDRIG, 5.0, 10, 90, 90, gemessen=False))
    return r


if __name__ == "__main__":
    print(f"Diskrete-Ereignis-Simulation, {SIM_STUNDEN:.0f}h simulierte Zeit, {30} Seeds pro Konfiguration\n")

    konfigurationen = [
        ("A: umgekehrte_neugier PRIO_NIEDRIG (Ausgangszustand vor heute)", PRIO_NIEDRIG),
        ("B: umgekehrte_neugier PRIO_NORMAL", PRIO_NORMAL),
        ("C: umgekehrte_neugier PRIO_HOCH (aktuell live, seit 16:26 Uhr)", PRIO_HOCH),
    ]

    for label, prio in konfigurationen:
        print(f"=== {label} ===")
        ergebnisse_pro_seed = [simuliere(basis_rollen(prio), seed) for seed in range(30)]
        namen = ergebnisse_pro_seed[0].keys()
        for name in namen:
            quoten = [e[name]["quote"] for e in ergebnisse_pro_seed if e[name]["gesamt"] > 0]
            wz_mittel = [e[name]["mittel_wartezeit"] for e in ergebnisse_pro_seed if e[name]["erfolg"] > 0]
            quote_pct = statistics.mean(quoten) * 100 if quoten else float("nan")
            wz = statistics.mean(wz_mittel) if wz_mittel else float("nan")
            marker = " <-- unter Test" if name == "umgekehrte_neugier" else ""
            print(f"  {name:20s} prio={PRIO_NAME.get([r for r in basis_rollen(prio) if r.name==name][0].prioritaet):8s}"
                  f" Erfolgsquote={quote_pct:5.1f}%  mittl.Wartezeit={wz:6.1f}s{marker}")
        print()

    print("=== D: umgekehrte_neugier PRIO_HOCH, ABER mit Entwurfslast (Sperre aufgehoben) ===")
    ergebnisse_pro_seed = [simuliere(rollen_mit_entwurfslast(PRIO_HOCH), seed) for seed in range(30)]
    namen = ergebnisse_pro_seed[0].keys()
    for name in namen:
        quoten = [e[name]["quote"] for e in ergebnisse_pro_seed if e[name]["gesamt"] > 0]
        wz_mittel = [e[name]["mittel_wartezeit"] for e in ergebnisse_pro_seed if e[name]["erfolg"] > 0]
        quote_pct = statistics.mean(quoten) * 100 if quoten else float("nan")
        wz = statistics.mean(wz_mittel) if wz_mittel else float("nan")
        print(f"  {name:20s} Erfolgsquote={quote_pct:5.1f}%  mittl.Wartezeit={wz:6.1f}s")
