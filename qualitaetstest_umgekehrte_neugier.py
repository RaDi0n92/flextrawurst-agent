#!/usr/bin/env python3
"""
qualitaetstest_umgekehrte_neugier.py — ECHTE LLM-Aufrufe gegen den
Baustein-11-Code, um Output-QUALITAET zu pruefen statt nur Struktur.

Daniel, 2026-07-09 abends: "wie aussagekraeftig ist deine simulation wenn du
sie nicht auf outputqualitaet hin simuliert hat [...] und falls nicht
entweder an dem input was veraendert hast oder die eher richtigen wege
eroeffnet hast [...] und dann wider simuliert hast und diese schleife
mehrfach durchbist?" Der Rauchtest (simulation_umgekehrte_neugier_v2_
rauchtest.py) mockt _llm() komplett -- validiert nur, dass die Zustands-
maschine nicht abstuerzt, sagt NICHTS ueber die Qualitaet der neuen Prompts.

Dieses Skript ruft echt: _llm() (echter hauhau_client/llm_scheduler-Call,
echte Wartezeit), flarum_api.suche_diskussionen/zufaellige_diskussionen/
get_discussion (echte, nur lesende DB-Zugriffe). Gemockt wird NUR die
Schreib-Seite (protokoll.schreibe, container.sichere/verschiebe/kopiere) --
damit ein Qualitaetstest keine echten Container-Dateien oder Protokoll-
Eintraege eines echten Wesens verschmutzt, aber echte Intelligenz zu sehen
ist statt Platzhaltertext.

Nutzung: python3 qualitaetstest_umgekehrte_neugier.py <wesen> [--zwinge-leere-suche]
Gibt jeden echten Prompt UND die echte Antwort vollstaendig aus, damit
tatsaechlich gelesen (nicht nur gezaehlt) werden kann, ob es gut ist.

--zwinge-leere-suche: Daniel, 2026-07-09 abends: "ich brauch jetzt die
sicherheit dass egal was ein wesen formuliert wir es schaffen flarum
zuzulesen [...] dass es ihnen etwas passendes anbietet". In den ersten drei
echten Laeufen fand die Suche (mit oder ohne Uebersetzung) jedes Mal zufaellig
etwas -- der garantierte Pflege/Stoebern-Weg wurde real nie durchlaufen. Diese
Option zwingt flarum_api.suche_diskussionen() hart auf 0 Treffer (echte
DB-Verbindung bleibt bestehen, nur das Ergebnis wird auf [] gesetzt), damit
der Fallback-Pfad mit Sicherheit statt Zufall real durchlaufen wird --
container.liste()/dateien() und flarum_api.zufaellige_diskussionen() bleiben
komplett echt.
"""

import logging
import sys
from unittest import mock

sys.path.insert(0, "/root/werkraum")
import codewesen_umgekehrte_neugier as cun

# Siehe simulation_umgekehrte_neugier.py: der Modul-Import haengt einen
# FileHandler an den ROOT-Logger, der ungefiltert in die echte Live-Logdatei
# schreibt. Hier besonders wichtig, weil dieses Skript ECHTE _llm()-Aufrufe
# macht und deren log.warning() bei Timeout/Fehler sonst real reinschreiben wuerde.
for _h in list(logging.root.handlers):
    if isinstance(_h, logging.FileHandler):
        logging.root.removeHandler(_h)


def _log_llm_aufrufe():
    """Wrappt cun._llm so, dass jeder ECHTE Prompt+Antwort sichtbar auf der
    Konsole landet -- der Punkt dieses Skripts ist genau das Lesen, nicht
    nur ein Boolean 'hat geantwortet'."""
    original = cun._llm

    def geloggt(wesen, system, user, max_tokens, timeout):
        print("\n" + "=" * 78)
        print(f"PROMPT an {wesen} (max_tokens={max_tokens}):")
        print("-" * 78)
        print(system.strip())
        if user and user != "(bitte jetzt antworten)":
            print("--- USER ---")
            print(user[:1500] + ("..." if len(user) > 1500 else ""))
        print("-" * 78)
        antwort = original(wesen, system, user, max_tokens, timeout)
        print(f"ANTWORT:\n{antwort}")
        print("=" * 78)
        return antwort

    return geloggt


def _protokoll_schreibe(*a, **k):
    pass  # bewusst kein echtes Schreiben waehrend des Qualitaetstests


def _container_sichere(*a, **k):
    print(f"\n[WUERDE SICHERN, hier nur beobachtet:] wesen={a[0]} container={a[1]} typ={a[2]}\n  inhalt={a[3][:200]}")


def _container_verschiebe(*a, **k):
    print(f"\n[WUERDE VERSCHIEBEN, hier nur beobachtet:] {a}")
    return True


def _container_kopiere(*a, **k):
    print(f"\n[WUERDE KOPIEREN, hier nur beobachtet:] {a}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in cun.WESEN:
        print(f"Aufruf: python3 {sys.argv[0]} <wesen> [--zwinge-leere-suche]  ({', '.join(cun.WESEN)})")
        sys.exit(1)
    wesen = sys.argv[1]
    zwinge_leere_suche = "--zwinge-leere-suche" in sys.argv[2:]

    patches = [
        mock.patch.object(cun, "_llm", side_effect=_log_llm_aufrufe()),
        mock.patch.object(cun.protokoll, "schreibe", side_effect=_protokoll_schreibe),
        mock.patch.object(cun.container, "sichere", side_effect=_container_sichere),
        mock.patch.object(cun.container, "verschiebe", side_effect=_container_verschiebe),
        mock.patch.object(cun.container, "kopiere", side_effect=_container_kopiere),
    ]
    if zwinge_leere_suche:
        print("### --zwinge-leere-suche aktiv: flarum_api.suche_diskussionen() liefert hart [] ###\n")
        patches.append(mock.patch.object(cun.flarum_api, "suche_diskussionen", side_effect=lambda *a, **k: []))

    from contextlib import ExitStack
    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        # container.liste()/dateien() bewusst NICHT gemockt -- echte
        # Container-Info im Prompt sehen ist Teil dessen was geprueft wird.
        zustand = {wesen: {"phase": "neu"}}
        print(f"### Qualitaetstest fuer {wesen} — Schritt 1: Interesse ###")
        cun._phase_interesse(wesen, zustand, "")

        print(f"\n### Zustand nach Schritt 1: {zustand[wesen].get('phase')} ###")
        if zustand[wesen].get("phase") == "lesen":
            for i in range(4):
                if zustand[wesen]["phase"] != "lesen":
                    break
                print(f"\n### Lese-Schritt {i+1} ###")
                cun._phase_lesen_schritt(wesen, zustand, "")
            if zustand[wesen]["phase"] == "container_zuordnung":
                print("\n### Container-Zuordnungs-Phase ###")
                cun._phase_container_zuordnung(wesen, zustand)

        print(f"\n### ENDZUSTAND: {zustand[wesen]} ###")
