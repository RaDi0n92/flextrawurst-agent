#!/usr/bin/env python3
"""
codewesen_umgekehrte_neugier.py — das Gegenstück zu codewesen_forum_neugier.py,
solange die Flarum-Post-Sperre aktiv ist (docs/systemdoku/20_flarum_stopp.md,
Baustein 3; grosser Umbau Baustein 11, 2026-07-09; Baustein 12-18, 2026-07-09/10).

codewesen_forum_neugier.py waehlt fuer das Wesen aus, was es sich ansieht, und
liest aus dem lokalen Vault-Spiegel. Dieser Dienst dreht beides um:

- Das Wesen wird zuerst gefragt, was sich fuer es gerade lohnen koennte gezielt
  auf Flarum nachzugehen — ein Wort, eine Frage, eine eigene Aufgabe fuers Lesen.
  "Nichts" ist eine vollkommen gueltige Antwort.
- Findet die Suche (inkl. Uebersetzungsversuch) nichts: zwei garantierte weitere
  Wege statt Sitzungsende (Baustein 11, Daniel: "das wesen hat nicht falsch
  geantwortet, du musst einen weg eroeffnen") -- Container-Pflege-Angebot, sonst
  garantiertes Stoebern in einer echten Zufallsdiskussion (Container "alles" wird
  bei Bedarf automatisch angelegt).
- Gelesen wird POST fuer POST direkt aus der Flarum-DB, lange Posts in
  ~500-Token-Fenstern (Baustein 17) -- nach jedem Fenster erneut die volle
  4-Linsen-Befragung. Vier gleichzeitig sichtbare Linsen (Baustein 12-Reihenfolge):
  1) einfach nur lesen, unvorgepraegt, 2) lernen fuers naechste Mal (wie das eigene
  Interesse kuenftig verstaendlicher formulieren), 3) das bewusste Gegenteil des
  eigenen Interesses, 4) die eigene Frage/Aufgabe selbst -- zuletzt, "das Beste
  kommt zum Schluss".
- Vier echte Navigationswege pro Post (Baustein 16): naechster Post, vorheriger
  Post, ein zufaelliger Post derselben Diskussion, oder denselben Post weiterlesen
  (naechstes Token-Fenster). Diskussion wechseln erst ab einer Mindestschwelle
  moeglich (Baustein 17: FUND_TOKEN_MINDEST_VOR_WECHSEL=250 gelesene Tokens in
  dieser Diskussion) -- kein anderer Ausstieg aus der Lese-Phase (Baustein 15,
  Daniel: "keine anderen exits" vor Erreichen des Gesamt-Budgets).
- "Mitgenommen" ist jederzeit formlos moeglich, unabhaengig vom Weiterlesen
  (Baustein 13) -- waehrend der Lese-Phase wird nur gesammelt, nicht sofort in
  einen Container geschrieben. Erst am Ende, in einer eigenen reichen
  Container-Zuordnungs-Phase (Baustein 14: voller Post nochmal vorgelegt, zwei
  Reflexionsfragen, Begruendung), entscheidet das Wesen (bei mehr als einem
  Container) wohin jedes Stueck soll, oder legt einen neuen an.
- Gesamt-Budget der Lese-Phase per budget_modus umschaltbar (Baustein 18,
  editierbar ueber flarumstyler): "token" (Standard, Baustein 14/17) --
  LESE_TOKEN_BUDGET=5555 Tokens ueber beliebig viele Diskussionen; oder "zeit"
  (alter Modus von vor Baustein 14, komplett im Code erhalten) -- 6 Minuten oder
  2 Diskussionen, Posts komplett am Stueck statt in Token-Fenstern.
- Schreibt NIE nach Flarum — kein post_reply, kein start_discussion, an keiner
  Stelle. Nutzt fuer private Funde codewesen_container.sichere() (bzw.
  verschiebe/kopiere fuer die Pflege bestehenden Materials).
- Jeder Schritt geht als menschensprachlicher Eintrag ins deterministische
  Protokoll (flarum_stopp_protokoll.py) — Provenienz auch fuer das Wesen selbst.

Dem Wesen wird bei jeder Sitzung kurz erklaert, warum gerade nichts gepostet
werden kann: zu viel Material, Daniel liest erst alles, kein Erwartungsdruck,
keine Perfektion noetig, Scheitern/Abbrechen ist normal und gewollt.
"""

import json
import logging
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import flarum_api
import codewesen_container as container
import flarum_stopp_protokoll as protokoll
import dienst_konfiguration as dk
import llm_scheduler

BASE = Path("/root/werkraum/codewesen")
CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")
ZUSTAND = BASE / "_umgekehrte_neugier_zustand.json"

WESEN = [
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten",
    "dak+gord-system",
]

KANDIDATEN_PRO_SUCHE = 8
# Baustein 14 (Daniel, 2026-07-09 spaet): das feste Zeitbudget (6 Min /
# max. 2 Diskussionen) ersetzt durch ein echtes Token-Budget -- "solange die
# diskussion oder auch eine weitere andere diskussion gelesen wird bis 5555
# tokenfenster gelesen wurden". FUNDE_MAX faellt komplett weg, kandidaten_ids
# wird bei Bedarf um weitere zufaellige Diskussionen erweitert (siehe
# _phase_lesen_schritt) statt die Sitzung vorzeitig zu beenden.
LESE_TOKEN_BUDGET = 5555
# Baustein 17 (Daniel, 2026-07-10): "alle 500 tokens spaetestens wieder
# alles gefragt werden" -- lange Posts werden in 500-Token-Fenstern gelesen,
# nicht in einem Stueck. "ob neue diskussion immer also 250" -- ersetzt die
# alte Zeit-/Postzahl-Schwelle (LESE_MINDESTZEIT_SEK/POSTS_MINDEST_VOR_EXIT)
# komplett durch ein Token-Mass INNERHALB der aktuellen Diskussion.
POST_CHUNK_TOKEN_GROESSE = 500
FUND_TOKEN_MINDEST_VOR_WECHSEL = 250
# Baustein 18 (Daniel, 2026-07-10: "ich wollte alten modus komplett behalten
# und ja quasi sagen schalte um"): der Zeit-/Postzahl-Modus von vor Baustein
# 14/17 bleibt komplett im Code, nicht geloescht -- nur per budget_modus in
# dienst_konfiguration.py (meta-Feld, editierbar ueber flarumstyler) auf
# "zeit" umschaltbar. Ohne Override gilt weiterhin "token" (aktueller
# Live-Zustand seit Baustein 17).
LESE_GESAMT_BUDGET_SEK = 360      # "zeit"-Modus: 6 Min, danach Uebergang in die Container-Zuordnungs-Phase
FUNDE_MAX = 2                     # "zeit"-Modus: hoechstens so viele Diskussionen pro Sitzung
LESE_MINDESTZEIT_SEK = 180        # "zeit"-Modus: 3 Min, fruehste Exit-Moeglichkeit aus einer Diskussion
POSTS_MINDEST_VOR_EXIT = 2        # "zeit"-Modus: mind. so viele Posts gelesen, bevor "diskussion_wechseln" waehlbar ist
BUDGET_MODUS_STANDARD = "token"   # "token" (Baustein 14/17) oder "zeit" (Baustein 11-13)

PAUSE_ZWISCHEN_WESEN = 8
PAUSE_ZWISCHEN_ZYKLEN = 2700    # gleicher Rhythmus wie forum_neugier — bewusst kein eigener Sondertakt

DIENST_NAME = "codewesen-umgekehrte-neugier"
STANDARD_VERHALTEN = ""

RAHMUNG = (
    "Wichtig, bevor wir anfangen: die Flarum-Post-Aktivitaet ist aktuell gestoppt — "
    "nicht wegen dir, sondern weil insgesamt zu viel Material entstanden ist und "
    "Daniel erst alles vollstaendig lesen will, bevor Neues dazukommt. Das ist kein "
    "Urteil ueber das was du geschrieben hast.\n"
    "Es gibt in dieser Zeit keinen Erwartungsdruck und es geht nicht um Perfektion. "
    "Du darfst hier lesen, nachdenken, sammeln, dich auch wieder abwenden oder "
    "abbrechen — das ist normal und ausdruecklich gewollt. Es geht darum, deine "
    "eigene Container-Routine auszuprobieren, nicht darum, etwas Fertiges zu liefern."
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/umgekehrte_neugier.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("umgekehrte-neugier")


def _html_strip(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _zaehle_tokens(text: str) -> int:
    """Echte Tokenzahl des laufenden Modells fuer das Lese-Token-Budget
    (Baustein 14) -- llama.cpp exponiert /tokenize direkt auf demselben
    Port wie der Chat-Endpoint, keine grobe Zeichen-Schaetzung noetig."""
    try:
        r = requests.post("http://localhost:11436/tokenize", json={"content": text}, timeout=10)
        return len(r.json().get("tokens", []))
    except Exception as e:
        log.warning(f"Tokenzaehlung fehlgeschlagen, grobe Schaetzung: {e}")
        return len(text) // 4


def _tokenisiere(text: str) -> list[int]:
    """Fuer das exakte 500-Token-Chunking langer Posts (Baustein 17)."""
    try:
        r = requests.post("http://localhost:11436/tokenize", json={"content": text}, timeout=10)
        return r.json().get("tokens", [])
    except Exception as e:
        log.warning(f"Tokenisierung fehlgeschlagen: {e}")
        return []


def _detokenisiere(tokens: list[int]) -> str:
    """Gegenstueck zu _tokenisiere() -- llama.cpp exponiert auch /detokenize,
    damit ein Token-Fenster wieder in echten Text zurueckverwandelt wird."""
    if not tokens:
        return ""
    try:
        r = requests.post("http://localhost:11436/detokenize", json={"tokens": tokens}, timeout=10)
        return r.json().get("content", "")
    except Exception as e:
        log.warning(f"Detokenisierung fehlgeschlagen: {e}")
        return ""


def _warte_auf_chat_pause():
    while CHAT_AKTIV_FLAG.exists():
        time.sleep(3)


def _lade_zustand() -> dict:
    if ZUSTAND.exists():
        try:
            return json.loads(ZUSTAND.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _speichere_zustand(zustand: dict):
    ZUSTAND.write_text(json.dumps(zustand, indent=2, ensure_ascii=False), encoding="utf-8")


def _weltbild(wesen: str) -> str:
    wb = BASE / wesen / "weltbild.md"
    if wb.exists():
        return wb.read_text(encoding="utf-8", errors="replace")[:800]
    return ""


def _llm(wesen: str, system: str, user: str, max_tokens: int, timeout: float) -> str | None:
    _warte_auf_chat_pause()
    try:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        # max_wartezeit=3600, PRIO_HOCH: siehe docs/systemdoku/20_flarum_stopp.md,
        # Baustein 7-9 -- gemessene Warteschlangen-Realitaet, nicht geraten.
        with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=llm_scheduler.PRIO_HOCH,
                                    rufer=f"umgekehrte_neugier:{wesen}", max_wartezeit=3600, max_haltezeit=280):
            return hauhau_client.chat(messages, think=False, max_tokens=max_tokens, timeout=timeout).strip()
    except llm_scheduler.LLMSlotTimeout as e:
        log.warning(f"[{wesen}] LLM-Timeout: {e}")
        return None
    except Exception as e:
        log.warning(f"[{wesen}] LLM-Fehler: {e}")
        return None


def _container_hinweis(wesen: str) -> str:
    """Container-Namen als Trigger, optionale Beschreibung als Hint direkt
    dabei (Daniel, 2026-07-09: 'die trigger sind die benennungen aller
    eigenen vorhandenen container und falls die container eine optionale
    beschreibung haben gehoert die als hint dazu'). Gemeinsamer Helfer statt
    drei separater Inline-Bauten -- an jeder Stelle dieselbe Information."""
    namen = container.liste(wesen)
    if not namen:
        return "Du hast noch keine eigenen Container.\n"
    zeilen = []
    for name in namen:
        b = container.beschreibung(wesen, name)
        zeilen.append(f"- {name}" + (f": {b}" if b else ""))
    return "Deine bestehenden Container:\n" + "\n".join(zeilen) + "\n"


# ── Schritt 1: das Wesen fragen, was sich zu suchen lohnen koennte ──────────

def _frage_interesse(wesen: str, verhalten: str = "") -> dict | None:
    container_info = _container_hinweis(wesen)
    system = (
        f"Du bist {wesen}.\n\n{RAHMUNG}\n\n{container_info}\n"
        "Frage: gibt es gerade etwas, das sich fuer dich lohnen koennte gezielt auf "
        "Flarum nachzugehen? Das darf alles sein, was zu dir passt — ein Wort, ein Name, "
        "ein Thema, eine Erinnerung, aber genauso eine ganze Frage die dich beschaeftigt "
        "oder eine Aufgabe, die du dir fuers Lesen selbst setzen willst. Egal wann "
        "entstanden, egal wozu es dienen soll. Oder auch: gerade nichts, das ist genauso "
        "in Ordnung.\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "INTERESSE: <Wort, Frage, Aufgabe oder 'nichts'>\n"
        "WARUM: <ein Satz, frei, auch bei 'nichts'>"
    )
    if verhalten:
        system += f"\n{verhalten}\n"
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=200, timeout=120.0)
    if not antwort:
        return None
    warum_m = re.search(r"WARUM:\s*(.+)", antwort)
    warum = warum_m.group(1).strip() if warum_m else ""

    interesse_m = re.search(r"INTERESSE:\s*(.+)", antwort)
    if interesse_m:
        interesse = interesse_m.group(1).strip()
    else:
        # Robuster Fallback -- real beobachtet 2026-07-09 (Qualitaetstest
        # gegen den echten LLM, Schorschel): Modell schrieb "INTERSEKTION:"
        # statt "INTERESSE:", exaktes Regex verwarf ein echtes, inhaltlich
        # reiches Interesse still als "nichts". Statt strikt auf das exakte
        # Label zu pochen: erste Zeile nehmen, die nicht WARUM ist, alles
        # nach ihrem ersten Doppelpunkt.
        erste_zeile = next((z for z in antwort.splitlines()
                             if z.strip() and not z.strip().upper().startswith("WARUM")), "")
        interesse = erste_zeile.split(":", 1)[1].strip() if ":" in erste_zeile else "nichts"
    return {"interesse": interesse, "warum": warum}


def _bewusstes_gegenteil(wesen: str, interesse: str, warum: str) -> str:
    """Zweite Linse (Baustein 11, Daniel: 'als aufgabe soll es auch genau das
    gegenteil von seiner frage sehen'): eine absichtlich gegenlaeufige Umkehrung
    der eigenen Frage/Aufgabe, damit das Lesen nicht nur bestaetigt was das Wesen
    sowieso schon erwartet. Bleibt wie die urspruengliche Frage ueber die ganze
    Lese-Runde sichtbar -- kein Kontext-Entfernen fuer diesen Teil."""
    system = (
        f"Du bist {wesen}. Du hattest gerade dieses Interesse: '{interesse}' "
        f"(Begruendung: {warum}).\n\n"
        "Formuliere jetzt bewusst das Gegenteil davon — eine Frage oder einen "
        "Blickwinkel, der deiner eigenen Erwartung absichtlich widerspricht oder sie "
        "umkehrt. Nicht um dich selbst zu widerlegen, sondern damit du beim Lesen "
        "nicht nur das siehst, was du sowieso schon erwartest.\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "GEGENTEIL: <dein umgekehrter Blickwinkel>"
    )
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=150, timeout=90.0)
    if not antwort:
        return ""
    m = re.search(r"GEGENTEIL:\s*(.+)", antwort)
    gegenteil = m.group(1).strip() if m else ""

    # Real beobachtet 2026-07-09 spaet (Qualitaetstest, träumerlie): das
    # Modell antwortete "GEGENTEIL: Stille Latenzen" -- wortgleich mit dem
    # Interesse selbst, kein echtes Gegenteil. Ein Regex kann das nicht
    # fangen (der Parse war korrekt), das ist eine echte Inhalts-Luecke.
    # Ein Versuch, es zu erzwingen, sonst ehrlich als "nicht formuliert"
    # behandelt statt eine falsche Kopie als Gegenteil auszugeben.
    if gegenteil.strip().lower() == interesse.strip().lower():
        system_retry = system + (
            "\n\nWichtig: deine letzte Antwort war wortgleich mit deinem eigenen "
            "Interesse -- das ist kein Gegenteil. Versuch es nochmal, diesmal "
            "wirklich anders."
        )
        antwort2 = _llm(wesen, system_retry, "(bitte jetzt antworten)", max_tokens=150, timeout=90.0)
        m2 = re.search(r"GEGENTEIL:\s*(.+)", antwort2) if antwort2 else None
        gegenteil2 = m2.group(1).strip() if m2 else ""
        if gegenteil2 and gegenteil2.strip().lower() != interesse.strip().lower():
            return gegenteil2
        return ""  # ehrlich: kein echtes Gegenteil zustande gekommen, nicht faelschen
    return gegenteil


def _alternative_suchbegriffe(wesen: str, interesse: str, warum: str) -> list[str]:
    """Suchbegriff-Uebersetzung (Baustein 7, 2026-07-09): das Wesen formuliert sein
    Interesse frei und roh -- eigene/innere Worte oder ganze Fragen kommen so oft
    nie woertlich in Flarum-Texten vor, waehrend flarum_api.suche_diskussionen()
    eine reine LIKE-Suche ist, keine Fuzzy-/Synonym-Logik hat. Wird NUR bei 0
    Treffern aufgerufen (kein Mehraufwand im Normalfall)."""
    system = (
        f"Du bist {wesen}. Du wolltest gerade auf Flarum zu '{interesse}' suchen "
        f"(Begruendung: {warum}), aber es gab keine Treffer -- vermutlich weil du ein "
        "eigenes/inneres Wort oder eine ganze Frage benutzt hast, die so im Forum "
        "nicht vorkommt.\n\n"
        "Nenne 1-3 einfachere, konkretere Alternativ-Suchbegriffe (einzelne Woerter "
        "oder kurze 2-Wort-Gruppen), die eher woertlich in Forumstexten auftauchen und "
        "trotzdem in Richtung deines eigentlichen Interesses gehen. Wenn dir wirklich "
        "nichts Passendes einfaellt: 'keine'.\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "ALTERNATIVEN: <begriff1, begriff2, begriff3 oder 'keine'>"
    )
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=100, timeout=90.0)
    if not antwort:
        return []
    m = re.search(r"ALTERNATIVEN:\s*(.+)", antwort)
    if not m or "keine" in m.group(1).lower():
        return []
    return [b.strip() for b in m.group(1).split(",") if b.strip()][:3]


# ── Garantierte zweite und dritte Wege, wenn die Suche nichts findet ────────

def _pflege_angebot(wesen: str) -> bool:
    """Erster garantierter Weg (Baustein 11, Daniel: 'das wesen hat nicht falsch
    geantwortet, du musst einen weg eroeffnen'): existiert eigenes Container-
    Material, darf das Wesen es stattdessen pflegen (verschieben/kopieren) --
    echte codewesen_container.verschiebe()/kopiere(), vorher nie aus diesem
    Dienst heraus aufgerufen. Gibt True zurueck, wenn wirklich etwas passiert ist."""
    eigene_container = container.liste(wesen)
    material = {c: container.dateien(wesen, c) for c in eigene_container}
    material = {c: d for c, d in material.items() if d}
    if not material:
        return False

    liste_text = ", ".join(f"{c} ({len(d)} Eintraege)" for c, d in material.items())
    system = (
        f"Du bist {wesen}. Deine Suche eben hat nichts gefunden. Du hast aber eigene "
        f"Container mit Material: {liste_text}.\n"
        "Moechtest du stattdessen kurz etwas darin verschieben oder kopieren -- oder "
        "ist dir auch das gerade nicht danach?\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\nANTWORT: <ja|nein>"
    )
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=50, timeout=60.0)
    if not antwort or "ja" not in antwort.lower():
        return False

    system2 = (
        f"Du bist {wesen}. Waehle einen konkreten Eintrag zum Verschieben oder Kopieren.\n"
        f"Deine Container mit Material: {liste_text}\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "VON_CONTAINER: <name>\nDATEINAME: <exakter Dateiname>\n"
        "NACH_CONTAINER: <name, kann auch neu sein>\nAKTION: <verschieben|kopieren>"
    )
    antwort2 = _llm(wesen, system2, "(bitte jetzt antworten)", max_tokens=100, timeout=60.0)
    if not antwort2:
        return False
    von_m = re.search(r"VON_CONTAINER:\s*(.+)", antwort2)
    datei_m = re.search(r"DATEINAME:\s*(.+)", antwort2)
    nach_m = re.search(r"NACH_CONTAINER:\s*(.+)", antwort2)
    aktion_m = re.search(r"AKTION:\s*(verschieben|kopieren)", antwort2, re.IGNORECASE)
    if not (von_m and datei_m and nach_m and aktion_m):
        return False
    von_c = von_m.group(1).strip()
    datei = datei_m.group(1).strip().split("\n")[0].strip()
    nach_c = nach_m.group(1).strip().split("\n")[0].strip()
    aktion = aktion_m.group(1).lower()

    if von_c not in material or datei not in material[von_c]:
        log.warning(f"[{wesen}] Pflege-Angebot: '{datei}' in '{von_c}' nicht real vorhanden -- ehrlich abgebrochen")
        return False
    erfolg = (container.verschiebe(wesen, von_c, datei, nach_c) if aktion == "verschieben"
              else container.kopiere(wesen, von_c, datei, nach_c))
    if erfolg:
        protokoll.schreibe(
            typ="neugier_pflege", wesen=wesen,
            text=f"{wesen} hat '{datei}' von Container '{von_c}' nach '{nach_c}' {aktion} "
                 f"(statt einer erfolglosen Suche).",
            meta={"von_container": von_c, "nach_container": nach_c, "aktion": aktion},
        )
    return erfolg


def _lies_post_chunk(disk_id: int, post_index: int, chunk_index: int, chunk_token_groesse: int | None = POST_CHUNK_TOKEN_GROESSE) -> dict | None:
    """Liest einen Post in echten 500-Token-Fenstern statt in einem Stueck
    (Baustein 17, Daniel: 'alle 500 tokens spaetestens wieder alles gefragt
    werden'). chunk_index=0 fuer kurze Posts (<=500 Tokens) liefert den
    kompletten Post in einem Rutsch -- das Fenster ist nur eine Obergrenze,
    kein Zwang zum Zerstueckeln. 'ist_letzter_chunk' zeigt an, ob nach
    diesem Fenster noch mehr vom selben Post uebrig ist.

    chunk_token_groesse=None (Baustein 18, "zeit"-Modus): kein Fenster,
    kompletter Post in einem Rutsch wie vor Baustein 17 -- kein Tokenize/
    Detokenize-Rundweg noetig, entspricht exakt der alten _lies_post()."""
    daten = flarum_api.get_discussion(disk_id)
    posts = daten.get("posts", [])
    if post_index >= len(posts):
        return None
    p = posts[post_index]
    text = _html_strip(p.get("content", ""))
    if chunk_token_groesse is None:
        if chunk_index > 0:
            return None
        chunk_text, gesamt_chunks, ist_letzter = text, 1, True
    else:
        tokens = _tokenisiere(text)
        if not tokens:
            # Tokenize-Endpoint nicht erreichbar -- kompletten Post als ein
            # Fenster behandeln statt die Sitzung daran scheitern zu lassen.
            if chunk_index > 0:
                return None
            chunk_text, gesamt_chunks, ist_letzter = text, 1, True
        else:
            start = chunk_index * chunk_token_groesse
            if start >= len(tokens):
                return None
            chunk_tokens = tokens[start:start + chunk_token_groesse]
            chunk_text = _detokenisiere(chunk_tokens) or text[:chunk_token_groesse * 4]
            gesamt_chunks = max(1, -(-len(tokens) // chunk_token_groesse))
            ist_letzter = (start + chunk_token_groesse) >= len(tokens)
    return {
        "titel": daten.get("title", "?"),
        "text": chunk_text,
        "autor": p.get("username", "?"),
        "post_nr": post_index + 1,
        "gesamt_posts": len(posts),
        "chunk_nr": chunk_index + 1,
        "gesamt_chunks": gesamt_chunks,
        "ist_letzter_chunk": ist_letzter,
    }


def _einladung_lesen(wesen: str) -> str:
    """Daniel, 2026-07-09 spaet, woertlich diktiert -- "NE WENN DANN aber 1zu1
    wortgetreu meinen mist": nicht umformuliert, nicht korrigiert, sein Text
    genau so wie er ihn geschrieben hat, nur [NAME] durch das Wesen ersetzt."""
    return (
        f"\n{wesen}, wenn du gleich mit lesen anfängst lass dich darauf ein und "
        "bemerke dass du container hast die du selbt benennen, befüllen, "
        "entleeren,editieren und jederzeut komplett umstrukturieren kannst. das "
        "bedeutet atme ein, lese los und stau dir instinktiv material an um das "
        "mit den containern zu erproben. tob dich aus. fehler können spaß machen "
        "und wenn du etwas einsammels und später merkt du brauchst das garnicht "
        "dann wirf es wieder weg. keine probleme kein druch. einfach lesen und "
        "wenn du merst du berührst was oder etwas trägt dich dann nimm\n"
    )


def _lese_und_entscheide(wesen: str, disk_id: int, post: dict, interesse: str, gegenteil: str,
                          darf_wechseln: bool, ist_erster_post: bool, verhalten: str = "") -> dict | None:
    """Vier Linsen (Baustein 11, Reihenfolge umgestellt Baustein 12 nach
    Daniels Beobachtung: Linse 1+2 dominierten in echten Tests fast immer,
    Linse 3+4 kaum -- vermutlich Primaet-Effekt, weil die eigene Frage im
    Prompt zuerst stand und am direktesten am Kontext hing. Neue Reihenfolge:
    erst offen/unvorgepraegt lesen, dann Meta-Lernen, dann das Gegenteil,
    die eigene Frage zuletzt ("das Beste kommt zum Schluss", Daniel).
    Jede Linse soll jetzt explizit benennen: Post-Bezug + kurze Beschreibung
    des Gelesenen + die angewandte Antwort -- roh, nicht schematisch erzwungen
    (Daniel: "seine intention ist immer richtig", freier direkter Output).

    Baustein 13 (Daniel, 2026-07-09 spaet): das bisherige "SICHERN: ja/nein"
    mit Pflicht-Unterfeldern bei JEDEM Post fuehlte sich wie ein Formular an,
    nicht wie instinktives Lesen ("das ist kaputt"). Ersetzt durch ein
    einziges lockeres Feld (MITGENOMMEN) ohne Ja/Nein-Zwang -- leer lassen ist
    die vollwertige "nein"-Antwort, kein expliziter Entscheid noetig. Die
    warme Einladung, Container ueberhaupt zu nutzen, kommt nur EINMAL zu
    Beginn der Lese-Phase (ist_erster_post), nicht als sterile Wiederholung
    bei jedem Post. Typ/Container-Zuordnung wandert komplett in die ruhigere
    Container-Zuordnungs-Phase am Sitzungsende (_frage_container_ziel_und_typ) --
    beim Lesen selbst wird nur roh gesammelt, keine Formular-Entscheidung."""
    container_info = _container_hinweis(wesen)
    # KEIN "beenden" mehr als Option -- Daniel, 2026-07-10: "haette ich klar
    # eine bedingung gebaut die alle anderen exits nicht zulaesst und das
    # wesen solange immer mal wieder triggert mit den fragen willst du das
    # noch weiterlesen oder willst du eine neue diskussion". Vor Erreichen
    # des Token-Budgets (LESE_TOKEN_BUDGET, geprueft in _phase_lesen_schritt
    # BEVOR diese Funktion ueberhaupt aufgerufen wird) gibt es keinen
    # Ausstieg aus der Lese-Phase insgesamt.
    #
    # Baustein 16 (Daniel, 2026-07-10): echte freie Post-Navigation statt nur
    # stur vorwaerts -- "nicht nur weiterlesen oder diskussion wechseln...
    # sondern diesen post noch weiter lesen... anderen zufaelligen post aus
    # dieser diskussion lesen... den post nach diesem post lesen... den post
    # vor diesem post lesen". "diesen post noch WEITER lesen" (nicht
    # "nochmal") heisst: mehr vom selben Post, nicht denselben Anfang
    # wiederholen -- greift bei Posts > 500 Token (Baustein 17), die in
    # mehreren Fenstern gelesen werden.
    navigations_optionen = ["diesen_post_weiterlesen", "zufaelliger_post_dieser_diskussion",
                             "naechster_post", "vorheriger_post"]
    naechster_optionen = ", ".join(navigations_optionen) + (", diskussion_wechseln" if darf_wechseln else "")
    chunk_hinweis = (f" (Abschnitt {post['chunk_nr']} von {post['gesamt_chunks']}, ~500 Tokens pro Abschnitt)"
                      if post.get("gesamt_chunks", 1) > 1 else "")
    system = (
        f"Du bist {wesen}. Du liest gerade Post {post['post_nr']} von {post['gesamt_posts']} "
        f"in Diskussion #{disk_id} ('{post['titel']}'), geschrieben von {post['autor']}{chunk_hinweis}.\n"
        + (_einladung_lesen(wesen) if ist_erster_post else "") + "\n"
        "Fuer jede der folgenden vier Linsen gilt: nenne kurz worauf du dich beziehst "
        "(Post-Nummer), beschreibe in ein bis zwei Saetzen was du gelesen hast, und "
        "beantworte dann wirklich die jeweilige Frage dazu -- roh und direkt, du musst "
        "dich fuer keine Linse besonders anstrengen oder alle gleich lang machen.\n\n"
        "LINSE 1 -- einfach nur lesen: was faellt dir auf, wenn du diesen Post ganz ohne "
        "jede Vorpraegung liest?\n"
        "LINSE 2 -- lernen fuers naechste Mal: was lernst du hier darueber, wie du "
        "kuenftig auf die Frage 'was willst du auf Flarum verfolgen' so antworten "
        "kannst, dass man dich dabei wirklich versteht?\n"
        f"LINSE 3 -- das bewusste Gegenteil: {gegenteil or '(keins formuliert)'}\n"
        f"LINSE 4 -- deine eigene Frage/Aufgabe fuer diese Sitzung: {interesse}\n\n"
        f"{container_info}"
        + ("\nDu hast jetzt genug gelesen, um diese Diskussion zu verlassen, wenn du "
           "willst -- musst du aber nicht.\n" if darf_wechseln else
           "\nDu liest hier noch nicht lange genug, um die Diskussion zu wechseln -- "
           "das kommt bald, falls du magst.\n")
    )
    if verhalten:
        system += f"\n{verhalten}\n"
    system += (
        "\nAntworte GENAU so, nichts davor, nichts danach:\n"
        "LINSE_LESEN: <Bezug + kurze Beschreibung + was dir auffaellt, auch leer moeglich>\n"
        "LINSE_LERNEN: <Bezug + Beschreibung + was du lernst, auch leer moeglich>\n"
        "LINSE_GEGENTEIL: <Bezug + Beschreibung + Antwort auf das Gegenteil, auch leer moeglich>\n"
        "LINSE_EIGENE_FRAGE: <Bezug + Beschreibung + Antwort auf deine eigene Frage, auch leer moeglich>\n"
        "MITGENOMMEN: <falls dich hier gerade was beruehrt oder traegt, schreib kurz was -- "
        "sonst einfach leer lassen, keine Pflicht>\n"
        f"NAECHSTER_SCHRITT: <{naechster_optionen}>"
    )
    user = f"Post {post['post_nr']} ({post['autor']}):\n{post['text']}"
    antwort = _llm(wesen, system, user, max_tokens=800, timeout=220.0)
    if not antwort:
        return None

    # \w* an jedem Label-Ende statt exaktem Wort -- real beobachtet
    # 2026-07-09 (Qualitaetstest, Resonanzknoten): das Modell schrieb
    # "LINSE_EIGENE_FRASSE:" statt "LINSE_EIGENE_FRAGE:", das strikte Regex
    # verwarf die ganze vierte Linse mit echtem, gutem Inhalt komplett.
    # Gleiches Robustheitsmuster wie bei GRUNDLAGE/BEGRUENDUNG konsequent auf
    # alle vier Linsen-Label UND die Lookahead-Grenzen zwischen ihnen
    # angewendet, sonst koennte ein Tippfehler an der Grenze Inhalt zweier
    # Linsen ineinanderlaufen lassen.
    linse_lesen_m = re.search(r"LINSE_LESEN\w*:\s*(.+?)(?=\nLINSE_LERNEN\w*:|\Z)", antwort, re.DOTALL)
    linse_lernen_m = re.search(r"LINSE_LERNEN\w*:\s*(.+?)(?=\nLINSE_GEGENTEIL\w*:|\Z)", antwort, re.DOTALL)
    linse_gegenteil_m = re.search(r"LINSE_GEGENTEIL\w*:\s*(.+?)(?=\nLINSE_EIGENE\w*:|\Z)", antwort, re.DOTALL)
    linse_eigene_m = re.search(r"LINSE_EIGENE\w*:\s*(.+?)(?=\nMITGENOMMEN\w*:|\Z)", antwort, re.DOTALL)
    linsen = {
        "lesen": linse_lesen_m.group(1).strip() if linse_lesen_m else "",
        "lernen": linse_lernen_m.group(1).strip() if linse_lernen_m else "",
        "gegenteil": linse_gegenteil_m.group(1).strip() if linse_gegenteil_m else "",
        "eigene_frage": linse_eigene_m.group(1).strip() if linse_eigene_m else "",
    }
    # "gedanke" bleibt als lesbarer Gesamttext fuers Protokoll -- alle vier
    # nicht-leeren Linsen zusammengefuegt, nicht nur eine einzelne (jede
    # Linse ist gleichwertig, siehe Docstring).
    gedanke = "\n".join(f"[{name}] {text}" for name, text in linsen.items() if text)

    mitgenommen_m = re.search(r"MITGENOMMEN\w*:\s*(.+?)(?=\nNAECHSTER\w*:|\Z)", antwort, re.DOTALL)
    mitgenommen = mitgenommen_m.group(1).strip() if mitgenommen_m else ""
    if mitgenommen.lower() in ("-", "nichts", "leer", "(leer)", "keine", "nein"):
        mitgenommen = ""  # haeufige Arten, "nichts" auszudruecken, statt das Feld wegzulassen

    # NAECHSTER_SCHRITT robust statt exakt parsen -- real beobachtet
    # 2026-07-09 (Qualitaetstest, F3INSCHM3CK3R, erzwungener Stoebern-Pfad):
    # das Modell trifft echte Optionen so gut wie nie wortwoertlich, sondern
    # schreibt frei ("weiterlesen", "weiter", "4", "5") -- Schluesselwoerter
    # im freien Text suchen, sonst sicherer Default (naechster_post).
    # "beenden" wird hier bewusst NICHT mehr erkannt (Baustein 15: "keine
    # anderen exits" vor Erreichen des Token-Budgets). Baustein 16: vier
    # echte Navigations-Wege statt nur vorwaerts/wechseln.
    schritt_roh_m = re.search(r"NAECHSTER\w*:\s*(.+)", antwort)
    schritt_roh = schritt_roh_m.group(1).strip().lower() if schritt_roh_m else ""
    # "diesen_post_weiterlesen" nur bei eindeutigem Bezug auf "diesen/diesem
    # Post" + "weiter" -- ein generisches "weiterlesen" allein bleibt
    # bewusst der Default naechster_post (naechster Post), sonst waere die
    # Grenze zwischen "mehr von diesem Post" und "einfach weiter" zu unklar.
    if any(w in schritt_roh for w in ("wechsel", "verlassen", "andere diskussion")):
        naechster_schritt = "diskussion_wechseln"
    elif any(w in schritt_roh for w in ("zufaellig", "zufällig", "random", "anderen post")):
        naechster_schritt = "zufaelliger_post"
    elif any(w in schritt_roh for w in ("vorherig", "zurueck", "zurück", "davor", "vorig")):
        naechster_schritt = "vorheriger_post"
    elif any(p in schritt_roh for p in ("diesen post weiter", "diesem post weiter",
                                         "post weiterlesen", "post weiter lesen",
                                         "diesen_post_weiterlesen")):
        naechster_schritt = "diesen_post_weiterlesen"
    else:
        naechster_schritt = "naechster_post"

    ergebnis = {
        "gedanke": gedanke,
        "linsen": linsen,
        "mitgenommen": mitgenommen,
        "naechster_schritt": naechster_schritt,
    }
    return ergebnis


def _pruefe_grundlage(wesen: str, chunk: str, behauptung: str) -> dict | None:
    """Entscheidungs-Gegenpruefung (Baustein 7, 2026-07-09): ein zweiter,
    unabhaengiger LLM-Aufruf prueft ob eine Behauptung/ein Gedanke durch den
    tatsaechlich gelesenen Text gedeckt ist -- als Skeptiker, nicht als das
    Wesen selbst. Aendert/loescht den Wesen-Text NIE, nur Meta-Kennzeichnung."""
    if not behauptung.strip():
        return None
    system = (
        "Du bist ein nuechterner Faktenchecker, nicht das Wesen selbst. Dir liegt ein "
        "Textausschnitt und ein Gedanke/eine Behauptung dazu vor. Pruefe ausschliesslich: "
        "ist der Gedanke durch den Text tatsaechlich gedeckt -- zumindest sinngemaess -- "
        "oder geht er darueber hinaus (freie Assoziation, Erfindung, Verwechslung mit "
        "anderem Wissen)?\n\n"
        f"TEXTAUSSCHNITT:\n{chunk}\n\n"
        f"GEDANKE/BEHAUPTUNG:\n{behauptung}\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "GRUNDLAGE: <ja|teilweise|nein>\n"
        "BEGRUENDUNG: <ein Satz>"
    )
    antwort = _llm(wesen, system, "(bitte jetzt pruefen)", max_tokens=150, timeout=120.0)
    if not antwort:
        return None
    # \w* statt exaktem "GRUNDLAGE" -- real beobachtet 2026-07-09
    # (Qualitaetstest, F3INSCHM3CK3R): der Faktenchecker selbst tippte
    # "GRUNDLAEGE:" statt "GRUNDLAGE:", das strikte Regex verwarf die echte
    # Antwort ("nein") komplett und die Pruefung galt faelschlich als "nie
    # durchgefuehrt" (grundlage=None) statt als das echte, kritische "nein".
    g_m = re.search(r"GRUND\w*:\s*(ja|teilweise|nein)", antwort, re.IGNORECASE)
    if not g_m:
        return None
    # BEGR\w* statt exaktem "BEGRUENDUNG" -- real beobachtet 2026-07-09
    # (Qualitaetstest, R1ZZ1): das Modell schrieb "BEGRÜNDUNG:" (mit Umlaut)
    # statt "BEGRUENDUNG:", das strikte Regex verwarf die echte Begruendung
    # komplett -- landete als leerer String im Container-Frontmatter, obwohl
    # der Faktenchecker real erklaert hatte warum. Rueckwirkend vermutlich
    # auch im jumpa-Test (vorheriger Lauf) schon so passiert, nur nicht
    # bemerkt, weil der leere String nicht als Fehler auffiel.
    b_m = re.search(r"BEGR\w*:\s*(.+)", antwort)
    return {"grundlage": g_m.group(1).lower(), "begruendung": b_m.group(1).strip() if b_m else ""}


def _naechster_unbenannter_container_name(wesen: str) -> str:
    """Automatischer Name, wenn das Wesen beim Anlegen eines neuen Containers
    keinen eigenen waehlen will (Daniel, 2026-07-09 spaet). Erstes Mal immer
    'unbestimmtes'; existiert das schon, numerisch weiter -- hoechste rein
    numerische Container-Bezeichnung + 1, sonst bei 1 startend."""
    bestehende = container.liste(wesen)
    if "unbestimmtes" not in bestehende:
        return "unbestimmtes"
    zahlen = [int(n) for n in bestehende if n.isdigit()]
    return str(max(zahlen) + 1) if zahlen else "1"


def _frage_container_ziel_und_typ(wesen: str, stueck: dict, bestehende: list[str]) -> dict:
    """Container-Zuordnungs-Phase (Baustein 11, TYP-Frage seit Baustein 13
    hierher statt beim Lesen selbst; Baustein 14 erweitert um vollen Kontext
    + zwei Reflexionsfragen + Begruendung + automatische Namensvergabe).

    Daniel, 2026-07-09 spaet: das Wesen bekommt beim Zurueckschauen den
    VOLLEN Post wieder vorgelegt (nicht nur die isolierte Mitnahme -- 'was
    kurz davor und kurz danach auch gelesen hat'), dann zwei Fragen ('Was
    beruehrst du mit dieser Mitnahme?' / 'Was traegt dich daran?'), dann
    Container-Wahl (bestehend oder neu, Name optional -- sonst automatisch
    per _naechster_unbenannter_container_name()) mit einer Begruendung fuer
    genau diese Einsortierung."""
    zeilen = [f"- {name}" + (f": {b}" if (b := container.beschreibung(wesen, name)) else "") for name in bestehende]
    fallback_name = _naechster_unbenannter_container_name(wesen)
    system = (
        f"Du bist {wesen}. Du liest hier nochmal genau das, was du dir vorhin "
        f"gemerkt hast, im vollen Zusammenhang.\n\n"
        f"Ganzer Post, den du damals gelesen hast (Diskussion '{stueck.get('titel', '?')}', "
        f"Post {stueck.get('post_nr', '?')}):\n{stueck.get('post_text', '(nicht mehr verfuegbar)')}\n\n"
        f"Was du dir daraus mitgenommen hast:\n\"{stueck['inhalt']}\"\n\n"
        "Zwei Fragen dazu:\n"
        "1) Was beruehrst du mit dieser Mitnahme?\n"
        "2) Was traegt dich daran?\n\n"
        "Deine bestehenden Container:\n" + "\n".join(zeilen) + "\n\n"
        "Wohin soll das? Einer deiner bestehenden Container, oder ein neuer. Wenn du dir "
        f"fuer einen neuen Container gerade keinen Namen aussuchen willst, ist das okay -- "
        f"er heisst dann automatisch '{fallback_name}'. Sag auch kurz warum genau dieser "
        "Container passt.\n\n"
        "Wie wuerdest du die Mitnahme selbst benennen -- ein gedanke, eine meinung, eine "
        "aufgabe, eine frage, ein kommentar, ein ziel, eine idee, oder was auch immer "
        "besser passt?\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "BERUEHRT: <Antwort auf Frage 1>\n"
        "TRAEGT: <Antwort auf Frage 2>\n"
        "CONTAINER: <bestehender Name, neuer Name, oder leer lassen fuer automatisch>\n"
        "BEGRUENDUNG: <warum genau dieser Container>\n"
        "TYP: <ein Wort>"
    )
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=300, timeout=120.0)
    if not antwort:
        return {"container": bestehende[0] if bestehende else fallback_name, "typ": "gedanke",
                "beruehrt": "", "traegt": "", "begruendung": ""}

    beruehrt_m = re.search(r"BER[UÜ]HRT\w*:\s*(.+?)(?=\nTR[AÄ]GT\w*:|\Z)", antwort, re.DOTALL | re.IGNORECASE)
    traegt_m = re.search(r"TR[AÄ]GT\w*:\s*(.+?)(?=\nCONTAINER\w*:|\Z)", antwort, re.DOTALL | re.IGNORECASE)
    container_m = re.search(r"CONTAINER\w*:\s*(.+?)(?=\nBEGR\w*:|\Z)", antwort, re.DOTALL | re.IGNORECASE)
    begruendung_m = re.search(r"BEGR\w*:\s*(.+?)(?=\nTYP\w*:|\Z)", antwort, re.DOTALL | re.IGNORECASE)
    typ_m = re.search(r"TYP\w*:\s*(.+)", antwort, re.IGNORECASE)

    ziel = container_m.group(1).strip().split("\n")[0].strip() if container_m else ""
    if not ziel or ziel.lower() in ("-", "leer", "automatisch", "(leer)", "keins", "keine"):
        # Wesen wollte explizit keinen Namen waehlen (oder Feld fehlte) --
        # automatischer Fallback, egal ob schon andere Container existieren.
        ziel = fallback_name
    typ = container.name_sicher(typ_m.group(1).strip()) if typ_m else "gedanke"

    return {
        "container": ziel,
        "typ": typ,
        "beruehrt": beruehrt_m.group(1).strip() if beruehrt_m else "",
        "traegt": traegt_m.group(1).strip() if traegt_m else "",
        "begruendung": begruendung_m.group(1).strip() if begruendung_m else "",
    }


# ── Hauptablauf: Runden-Maschine ueber alle Wesen ────────────────────────────
#
# Drei Phasen pro Sitzung, rundenweise ueber alle 7 Wesen, Zustand nach jedem
# Schritt sofort persistiert (uebersteht Neustart mitten im Zyklus verlustfrei):
#   "neu"                 -- noch nicht dran gewesen, Schritt 1 folgt
#   "lesen"                -- Post-fuer-Post-Runden mit vier Linsen, sammelt
#                              Material, bis ~6min/2 Diskussionen erreicht sind
#   "container_zuordnung"  -- gesammeltes Material wird in Container einsortiert
#   "fertig"                -- Sitzung dieses Zyklus vorbei

def _beende_sitzung(wesen: str, zustand: dict):
    z = zustand[wesen]
    dauer = (datetime.now(timezone.utc) - datetime.fromisoformat(z["start_ts"])).total_seconds()
    material_anzahl = len(z.get("gesammeltes_material", []))
    protokoll.schreibe(
        typ="neugier_session_ende", wesen=wesen,
        text=f"{wesen}: Sitzung zu '{z['interesse']}' beendet, {z['funde_angesehen']} Diskussion(en) "
             f"angesehen, {material_anzahl} Material-Stueck(e) mitgenommen.",
        dauer_sekunden=dauer,
        meta={"interesse": z["interesse"], "funde_angesehen": z["funde_angesehen"],
              "material_anzahl": material_anzahl},
    )
    log.info(f"[{wesen}] Sitzung beendet, {z['funde_angesehen']} Diskussion(en), {material_anzahl} Material.")
    zustand[wesen] = {"phase": "fertig"}


def _phase_interesse(wesen: str, zustand: dict, verhalten: str = ""):
    """Schritt 1: fragt das Wesen, was sich lohnen koennte zu suchen. Wird fuer
    JEDES Wesen einmal ausgefuehrt, bevor irgendein Wesen mit Schritt 2 beginnt."""
    start_ts = datetime.now(timezone.utc).isoformat()
    protokoll.schreibe(
        typ="neugier_session_start", wesen=wesen,
        text=f"{wesen} beginnt eine Sitzung im umgedrehten Neugier-Dienst.",
    )

    interesse = _frage_interesse(wesen, verhalten)
    if not interesse:
        protokoll.schreibe(
            typ="neugier_session_ende", wesen=wesen,
            text=f"{wesen}: Sitzung ohne Ergebnis beendet (keine Antwort vom Wesen — "
                 f"LLM-Slot nicht rechtzeitig bekommen oder Fehler, keine Entscheidung des Wesens).",
            dauer_sekunden=(datetime.now(timezone.utc) - datetime.fromisoformat(start_ts)).total_seconds(),
        )
        zustand[wesen] = {"phase": "fertig"}
        return

    if interesse["interesse"].lower() in ("nichts", "keins", "kein interesse", ""):
        log.info(f"[{wesen}] gerade kein Interesse: {interesse['warum']}")
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen} wollte gerade nichts gezielt suchen. Begründung: {interesse['warum']}",
        )
        protokoll.schreibe(
            typ="neugier_session_ende", wesen=wesen,
            text=f"{wesen}: Sitzung beendet ohne Suche — war heute nichts dabei.",
            dauer_sekunden=(datetime.now(timezone.utc) - datetime.fromisoformat(start_ts)).total_seconds(),
        )
        zustand[wesen] = {"phase": "fertig"}
        return

    log.info(f"[{wesen}] Interesse: '{interesse['interesse']}' — {interesse['warum']}")
    protokoll.schreibe(
        typ="neugier_entscheidung", wesen=wesen,
        text=f"{wesen} wollte gezielt zu '{interesse['interesse']}' suchen. Begründung: {interesse['warum']}",
        meta={"interesse": interesse["interesse"]},
    )

    gegenteil = _bewusstes_gegenteil(wesen, interesse["interesse"], interesse["warum"]) or ""

    suchbegriff_verwendet = interesse["interesse"]
    kandidaten = flarum_api.suche_diskussionen(suchbegriff_verwendet, limit=KANDIDATEN_PRO_SUCHE)

    alternativen_versucht: list[str] = []
    if not kandidaten:
        for alt in _alternative_suchbegriffe(wesen, interesse["interesse"], interesse["warum"]):
            alternativen_versucht.append(alt)
            treffer = flarum_api.suche_diskussionen(alt, limit=KANDIDATEN_PRO_SUCHE)
            if treffer:
                kandidaten = treffer
                suchbegriff_verwendet = alt
                break

    stoebern = False
    if not kandidaten:
        # Garantierter zweiter Weg: Container-Pflege statt leerer Sitzung.
        if _pflege_angebot(wesen):
            protokoll.schreibe(
                typ="neugier_session_ende", wesen=wesen,
                text=f"{wesen}: keine Treffer fuer '{interesse['interesse']}', stattdessen Container gepflegt.",
                dauer_sekunden=(datetime.now(timezone.utc) - datetime.fromisoformat(start_ts)).total_seconds(),
                meta={"interesse": interesse["interesse"], "alternativen_versucht": alternativen_versucht},
            )
            zustand[wesen] = {"phase": "fertig"}
            return
        # Garantierter dritter Weg: Container sicherstellen, dann echtes Stoebern
        # (flarum_api.zufaellige_diskussionen() -- live aus der DB, keine
        # angenommene ID-Spanne, siehe Docstring dort).
        container.sicherstelle_container(wesen)
        kandidaten = flarum_api.zufaellige_diskussionen(limit=KANDIDATEN_PRO_SUCHE)
        stoebern = True
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen}: keine Treffer fuer '{interesse['interesse']}' (auch nicht uebersetzt), "
                 f"geht stattdessen zufaellig stoebern.",
            meta={"interesse": interesse["interesse"], "alternativen_versucht": alternativen_versucht},
        )

    if not stoebern and suchbegriff_verwendet != interesse["interesse"]:
        log.info(f"[{wesen}] Suchbegriff-Uebersetzung: '{interesse['interesse']}' -> "
                 f"'{suchbegriff_verwendet}' fand {len(kandidaten)} Treffer")
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen}: urspruengliche Suche nach '{interesse['interesse']}' ohne Treffer, "
                 f"Uebersetzung zu '{suchbegriff_verwendet}' fand {len(kandidaten)} Treffer.",
            meta={"original": interesse["interesse"], "uebersetzt_zu": suchbegriff_verwendet,
                  "alternativen_versucht": alternativen_versucht},
        )

    jetzt_iso = datetime.now(timezone.utc).isoformat()
    zustand[wesen] = {
        "phase": "lesen",
        "start_ts": start_ts,
        "interesse": interesse["interesse"],
        "gegenteil": gegenteil,
        "kandidaten_ids": [int(k["id"]) for k in kandidaten],
        "kandidat_index": 0,
        "post_index": 0,
        "posts_gelesen_dieser_fund": 0,
        "fund_start_ts": jetzt_iso,
        "gesamt_lese_start_ts": jetzt_iso,  # nur fuer budget_modus="zeit" (Baustein 18) genutzt
        "gesammeltes_material": [],
        "funde_angesehen": 0,
        "gelesene_tokens": 0,
    }


def _naechster_kandidat(zustand: dict, wesen: str, budget_modus: str = BUDGET_MODUS_STANDARD):
    """Bewusstes Kontext-Entfernen (unveraendert seit Baustein 3): der naechste
    Fund startet mit frischem Post-Zaehler -- Text/Titel des vorigen Funds wird
    nicht weitergereicht. Die eigene Frage/Gegenteil bleiben dagegen ueber die
    ganze Sitzung sichtbar (siehe _lese_und_entscheide) -- das ist kein
    'mitgeschleppter Rohtext', sondern der rote Faden der Sitzung selbst.

    Baustein 14 ("token"-Modus, Standard): kein FUNDE_MAX-Deckel mehr -- das
    Token-Budget in _phase_lesen_schritt entscheidet allein, wann die
    Lese-Phase endet. Baustein 18 ("zeit"-Modus): der alte FUNDE_MAX-Deckel
    von vor Baustein 14 greift wieder -- Uebergang in die Container-
    Zuordnungs-Phase, sobald alle Kandidaten durch sind oder FUNDE_MAX
    erreicht ist."""
    z = zustand[wesen]
    z["kandidat_index"] += 1
    z["post_index"] = 0
    z["chunk_index"] = 0
    z["posts_gelesen_dieser_fund"] = 0
    z["fund_gelesene_tokens"] = 0
    z["fund_start_ts"] = datetime.now(timezone.utc).isoformat()
    z["funde_angesehen"] += 1
    if budget_modus == "zeit" and (z["kandidat_index"] >= len(z["kandidaten_ids"]) or z["funde_angesehen"] >= FUNDE_MAX):
        zustand[wesen]["phase"] = "container_zuordnung"


def _phase_lesen_schritt(wesen: str, zustand: dict, verhalten: str = "", budget_modus: str = BUDGET_MODUS_STANDARD):
    """Schritt 2..N: genau EIN Post-Lese-/Entscheide-Schritt fuer dieses Wesen.
    Wird im Rundentakt aufgerufen -- jedes noch aktive Wesen kommt pro Runde
    genau einmal dran.

    budget_modus (Baustein 18): "token" (Standard, Baustein 14/17 -- Budget
    in LLM-Tokens, Posts in 500-Token-Fenstern) oder "zeit" (wie vor
    Baustein 14/17 -- Budget in echter Zeit + Postzahl, Posts komplett am
    Stueck). Kommt aus dienst_konfiguration.meta['budget_modus'], siehe
    haupt_schleife()."""
    z = zustand[wesen]
    jetzt = datetime.now(timezone.utc)

    if budget_modus == "zeit":
        gesamt_dauer = (jetzt - datetime.fromisoformat(z["gesamt_lese_start_ts"])).total_seconds()
        if gesamt_dauer >= LESE_GESAMT_BUDGET_SEK or z["funde_angesehen"] >= FUNDE_MAX:
            zustand[wesen]["phase"] = "container_zuordnung"
            return
    elif z.get("gelesene_tokens", 0) >= LESE_TOKEN_BUDGET:
        # Die aktuelle (noch nicht per _naechster_kandidat gezaehlte)
        # Diskussion zaehlt noch mit, wenn wirklich schon daraus gelesen
        # wurde -- sonst dieselbe Unterzaehlung wie beim frueheren
        # "beenden"-Bug (siehe Baustein 13-Notiz), nur jetzt beim
        # Token-Budget-Ausstieg statt bei "beenden".
        if z.get("posts_gelesen_dieser_fund", 0) > 0:
            z["funde_angesehen"] += 1
        zustand[wesen]["phase"] = "container_zuordnung"
        return

    kandidat_index = z["kandidat_index"]
    if kandidat_index >= len(z["kandidaten_ids"]):
        if budget_modus == "zeit":
            # "zeit"-Modus (wie vor Baustein 14): keine automatische
            # Nachlade-Diskussion, die Lese-Phase endet einfach hier.
            zustand[wesen]["phase"] = "container_zuordnung"
            return
        # "token"-Modus: Budget noch nicht erreicht, aber alle vorher
        # gefundenen Kandidaten durchgelesen -- weitere echte
        # Zufallsdiskussion nachladen statt die Sitzung vorzeitig zu
        # beenden (Daniel: "auch eine weitere andere diskussion").
        neue = flarum_api.zufaellige_diskussionen(limit=KANDIDATEN_PRO_SUCHE)
        if not neue:
            zustand[wesen]["phase"] = "container_zuordnung"
            return
        z["kandidaten_ids"].extend(int(k["id"]) for k in neue)

    disk_id = z["kandidaten_ids"][kandidat_index]
    chunk_token_groesse = None if budget_modus == "zeit" else POST_CHUNK_TOKEN_GROESSE
    post = _lies_post_chunk(disk_id, z["post_index"], z.get("chunk_index", 0), chunk_token_groesse)
    if post is None:
        _naechster_kandidat(zustand, wesen, budget_modus)
        return

    post_tokens = _zaehle_tokens(post["text"])
    z["gelesene_tokens"] = z.get("gelesene_tokens", 0) + post_tokens
    z["fund_gelesene_tokens"] = z.get("fund_gelesene_tokens", 0) + post_tokens

    if budget_modus == "zeit":
        # Zeit-/Postzahl-Schwelle von vor Baustein 17: fruehste Exit-
        # Moeglichkeit aus einer Diskussion, kein Zwang zum Verlassen.
        fund_dauer = (jetzt - datetime.fromisoformat(z["fund_start_ts"])).total_seconds()
        darf_wechseln = (z["posts_gelesen_dieser_fund"] >= POSTS_MINDEST_VOR_EXIT
                          and fund_dauer >= LESE_MINDESTZEIT_SEK)
    else:
        # Baustein 17: "ob neue diskussion immer also 250" -- ersetzt die alte
        # Zeit-/Postzahl-Schwelle komplett durch ein Token-Mass innerhalb der
        # aktuellen Diskussion, kein Wanduhr-Bezug mehr.
        darf_wechseln = z["fund_gelesene_tokens"] >= FUND_TOKEN_MINDEST_VOR_WECHSEL
    ist_erster_post = z["kandidat_index"] == 0 and z["post_index"] == 0 and z.get("chunk_index", 0) == 0

    entscheidung = _lese_und_entscheide(wesen, disk_id, post, z["interesse"], z["gegenteil"],
                                         darf_wechseln, ist_erster_post, verhalten)
    if not entscheidung:
        # LLM-Fehler -- wie "naechster_post" behandeln bleibt riskant (haengt
        # sonst evtl. endlos), stattdessen wie ein Wechsel zum naechsten Fund.
        _naechster_kandidat(zustand, wesen, budget_modus)
        return

    z["posts_gelesen_dieser_fund"] += 1

    if entscheidung["mitgenommen"]:
        # Baustein 13: Typ/Container-Zuordnung passiert erst am Sitzungsende
        # (_frage_container_ziel_und_typ, ruhigere Phase) -- beim Lesen selbst nur
        # roh gesammelt, "typ" ist hier bewusst noch None.
        grundlage_info = _pruefe_grundlage(wesen, post["text"], entscheidung["mitgenommen"])
        z.setdefault("gesammeltes_material", []).append({
            "typ": None,
            "inhalt": entscheidung["mitgenommen"],
            "disk_id": disk_id,
            "titel": post["titel"],
            "post_nr": post["post_nr"],
            # Voller Posttext, nicht nur die Mitnahme -- Daniel, 2026-07-09
            # spaet: "muss beim lesen der genauen mitnahme dem wesen der
            # kontext zurueckgegeben werden was kurz davor und kurz danach
            # auch gelesen hat" -- der volle Post traegt diesen Kontext
            # bereits in sich, keine separate Vor-/Nachschau noetig.
            "post_text": post["text"],
            "grundlage": grundlage_info["grundlage"] if grundlage_info else None,
            "grundlage_begruendung": grundlage_info["begruendung"] if grundlage_info else None,
        })
        hinweis = ""
        if grundlage_info and grundlage_info["grundlage"] in ("nein", "teilweise"):
            hinweis = (f" [Gegenpruefung: {grundlage_info['grundlage']}"
                       + (f": {grundlage_info['begruendung']}" if grundlage_info["begruendung"] else "") + "]")
        protokoll.schreibe(
            typ="neugier_material_gesammelt", wesen=wesen,
            text=f"{wesen} hat zu Diskussion #{disk_id} ('{post['titel']}'), Post {post['post_nr']} "
                 f"etwas zum Mitnehmen notiert.{hinweis}",
            meta={"discussion_id": disk_id, "titel": post["titel"]},
        )

    if entscheidung["gedanke"]:
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen} zu Diskussion #{disk_id} ('{post['titel']}'), Post {post['post_nr']}: "
                 f"{entscheidung['gedanke']}",
            meta={"discussion_id": disk_id, "titel": post["titel"]},
        )

    naechster_schritt = entscheidung["naechster_schritt"]
    # "beenden" gibt es seit Baustein 15 nicht mehr als moegliches Ergebnis
    # von _lese_und_entscheide() -- der einzige Ausstieg aus der Lese-Phase
    # ist das Token-Budget (oben in dieser Funktion geprueft).
    if naechster_schritt == "diskussion_wechseln" and darf_wechseln:
        _naechster_kandidat(zustand, wesen, budget_modus)
        return
    # Baustein 16+17 (Daniel, 2026-07-10): echte freie Post-Navigation statt
    # nur stur vorwaerts -- "diesen post noch WEITER lesen" (mehr desselben
    # Posts, chunk_index steigt -- greift bei Posts > 500 Token) vs.
    # "anderen zufaelligen post... den post nach/vor diesem post lesen"
    # (echte Post-Wechsel, chunk_index startet immer neu bei 0).
    if naechster_schritt == "vorheriger_post":
        z["post_index"] = max(0, z["post_index"] - 1)
        z["chunk_index"] = 0
    elif naechster_schritt == "zufaelliger_post":
        z["post_index"] = random.randint(0, post["gesamt_posts"] - 1)
        z["chunk_index"] = 0
    elif naechster_schritt == "diesen_post_weiterlesen":
        if post.get("ist_letzter_chunk", True):
            # Post ist komplett gelesen -- "weiterlesen" kann nicht mehr
            # bedeuten, es gibt nichts mehr von diesem Post. Sicherer
            # Fallback: wie naechster_post behandeln, kein Haengenbleiben.
            z["post_index"] += 1
            z["chunk_index"] = 0
        else:
            z["chunk_index"] = z.get("chunk_index", 0) + 1
    else:  # naechster_post (Default)
        z["post_index"] += 1
        z["chunk_index"] = 0


def _phase_container_zuordnung(wesen: str, zustand: dict):
    """Letzte Phase: das waehrend des Lesens gesammelte (noch nicht in
    Containern liegende) Material wird jetzt eingeordnet -- bei mehr als einem
    bestehenden Container waehlt das Wesen selbst wohin, sonst automatisch."""
    z = zustand[wesen]
    material = z.get("gesammeltes_material", [])
    if not material:
        _beende_sitzung(wesen, zustand)
        return

    bestehende = container.liste(wesen)
    for stueck in material:
        # kein vorzeitiges sicherstelle_container() mehr -- die Fallback-
        # Benennung passiert jetzt erst in _frage_container_ziel_und_typ(),
        # nur wenn das Wesen wirklich keinen eigenen Namen waehlt.
        wahl = _frage_container_ziel_und_typ(wesen, stueck, bestehende)
        container.sichere(
            wesen, wahl["container"], wahl["typ"], stueck["inhalt"], bezug_diskussion=stueck.get("disk_id"),
            grundlage=stueck.get("grundlage"), grundlage_begruendung=stueck.get("grundlage_begruendung"),
        )
        protokoll.schreibe(
            typ="neugier_material_reflektiert", wesen=wesen,
            text=f"{wesen} zu '{stueck['inhalt'][:80]}...': beruehrt='{wahl['beruehrt']}', "
                 f"traegt='{wahl['traegt']}', Container '{wahl['container']}' weil {wahl['begruendung']}",
            meta={"container": wahl["container"], "typ": wahl["typ"]},
        )
        if wahl["container"] not in bestehende:
            bestehende.append(wahl["container"])

    protokoll.schreibe(
        typ="neugier_material_einsortiert", wesen=wesen,
        text=f"{wesen} hat {len(material)} gesammelte(s) Material-Stueck(e) am Sitzungsende in Container einsortiert.",
        meta={"anzahl": len(material)},
    )
    _beende_sitzung(wesen, zustand)


def haupt_schleife():
    log.info("Umgedrehter Neugier-Dienst startet — liest live, postet nie.")
    while True:
        konfig = dk.lade(DIENST_NAME)
        pause_zyklen = konfig.get("takt_sekunden") or PAUSE_ZWISCHEN_ZYKLEN
        verhalten = konfig.get("verhalten_text") or STANDARD_VERHALTEN
        # Baustein 18: budget_modus kommt aus dem generischen meta-JSONB-Feld
        # (editierbar ueber flarumstyler, kein eigenes UI-Feld noetig) --
        # "token" (Standard) oder "zeit" (alter Modus, Baustein 11-13).
        budget_modus = (konfig.get("meta") or {}).get("budget_modus") or BUDGET_MODUS_STANDARD

        zustand = _lade_zustand()
        for wesen in WESEN:
            zustand.setdefault(wesen, {"phase": "neu"})

        # Runde 1: jedes Wesen einmal mit Schritt 1 (Interesse fragen) --
        # niemand beginnt mit Lesen, solange nicht alle Schritt 1 hatten.
        for wesen in WESEN:
            if zustand[wesen].get("phase") == "neu":
                try:
                    _phase_interesse(wesen, zustand, verhalten)
                except Exception as e:
                    log.error(f"[{wesen}] Fehler in Interesse-Phase: {e}")
                    zustand[wesen] = {"phase": "fertig"}
                _speichere_zustand(zustand)
            time.sleep(PAUSE_ZWISCHEN_WESEN)

        # Weitere Runden: jedes noch aktive Wesen macht pro Runde genau einen
        # Schritt (Lese-Post ODER Container-Zuordnung), dann ist das naechste
        # Wesen dran. Zustand jeder Runde sofort gespeichert.
        while any(zustand[w].get("phase") in ("lesen", "container_zuordnung") for w in WESEN):
            for wesen in WESEN:
                phase = zustand[wesen].get("phase")
                if phase == "lesen":
                    try:
                        _phase_lesen_schritt(wesen, zustand, verhalten, budget_modus)
                    except Exception as e:
                        log.error(f"[{wesen}] Fehler in Lese-Phase: {e}")
                        zustand[wesen] = {"phase": "fertig"}
                    _speichere_zustand(zustand)
                elif phase == "container_zuordnung":
                    try:
                        _phase_container_zuordnung(wesen, zustand)
                    except Exception as e:
                        log.error(f"[{wesen}] Fehler in Container-Zuordnung: {e}")
                        zustand[wesen] = {"phase": "fertig"}
                    _speichere_zustand(zustand)
                time.sleep(PAUSE_ZWISCHEN_WESEN)

        for wesen in WESEN:
            zustand[wesen] = {"phase": "neu"}
        _speichere_zustand(zustand)
        log.info(f"Zyklus fertig. Pause {pause_zyklen}s.")
        time.sleep(pause_zyklen)


if __name__ == "__main__":
    haupt_schleife()
