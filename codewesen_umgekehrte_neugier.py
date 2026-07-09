#!/usr/bin/env python3
"""
codewesen_umgekehrte_neugier.py — das Gegenstück zu codewesen_forum_neugier.py,
solange die Flarum-Post-Sperre aktiv ist (docs/2026-07-09_flarum_stopp_bericht.md,
Baustein 3; grosser Umbau Baustein 11, 2026-07-09 abends).

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
- Gelesen wird POST fuer POST (nicht mehr in willkuerlichen Zeichen-Chunks) direkt
  aus der Flarum-DB. Bei jedem Post vier gleichzeitig sichtbare Linsen: die eigene
  Frage/Aufgabe, ihr bewusstes Gegenteil, eine ganz unvorgepraegte dritte Frage,
  und eine reflexive vierte Frage ueber die eigene Interessens-Formulierung.
- "Sichern" ist jederzeit moeglich, unabhaengig vom Weiterlesen -- waehrend der
  Lese-Phase wird nur gesammelt, nicht sofort in einen Container geschrieben. Erst
  am Ende, in einer eigenen Container-Zuordnungs-Phase, entscheidet das Wesen (bei
  mehr als einem Container) wohin jedes Stueck soll, oder legt einen neuen an.
- Eine Diskussion darf fruehestens nach 2 gelesenen Posts UND 3 Minuten verlassen
  werden (Daniel: "war keine Stopbegrenzung, nur fruehste Exit-Moeglichkeit").
  Die gesamte Lese-Phase endet spaetestens nach ~6 Minuten oder 2 Diskussionen,
  danach folgt automatisch die ~2-minuetige Container-Zuordnungs-Phase.
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
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

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
FUNDE_MAX = 2                     # hoechstens so viele Diskussionen pro Sitzung (Daniel: "nach 2 Diskussionen")
LESE_MINDESTZEIT_SEK = 180        # 3 Min: fruehste Exit-Moeglichkeit aus einer Diskussion (kein Zwang zum Verlassen)
POSTS_MINDEST_VOR_EXIT = 2        # mind. so viele Posts gelesen, bevor "Diskussion verlassen" ueberhaupt waehlbar ist
LESE_GESAMT_BUDGET_SEK = 360      # 6 Min: danach sauberer Uebergang in die Container-Zuordnungs-Phase

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


# ── Schritt 1: das Wesen fragen, was sich zu suchen lohnen koennte ──────────

def _frage_interesse(wesen: str, verhalten: str = "") -> dict | None:
    container_liste = container.liste(wesen)
    container_info = (
        f"Deine bestehenden Container: {', '.join(container_liste)}\n"
        if container_liste else "Du hast noch keine eigenen Container.\n"
    )
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
    return m.group(1).strip() if m else ""


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


def _lies_post(disk_id: int, post_index: int) -> dict | None:
    daten = flarum_api.get_discussion(disk_id)
    posts = daten.get("posts", [])
    if post_index >= len(posts):
        return None
    p = posts[post_index]
    return {
        "titel": daten.get("title", "?"),
        "text": _html_strip(p.get("content", "")),
        "autor": p.get("username", "?"),
        "post_nr": post_index + 1,
        "gesamt_posts": len(posts),
    }


def _lese_und_entscheide(wesen: str, disk_id: int, post: dict, interesse: str, gegenteil: str,
                          darf_wechseln: bool, verhalten: str = "") -> dict | None:
    """Vier gleichzeitig sichtbare Linsen (Baustein 11) statt einer einzelnen
    Entscheidung. 'Sichern' ist eine jederzeit zusaetzlich moegliche Handlung,
    keine 4. exklusive Option neben Weiterlesen/Wechseln/Beenden mehr."""
    container_liste = container.liste(wesen)
    container_info = (
        f"Deine bestehenden Container: {', '.join(container_liste)}\n"
        if container_liste else "Du hast noch keine eigenen Container.\n"
    )
    naechster_optionen = "naechster_post" + (", diskussion_wechseln" if darf_wechseln else "") + ", beenden"
    system = (
        f"Du bist {wesen}. Du liest gerade Post {post['post_nr']} von {post['gesamt_posts']} "
        f"in Diskussion #{disk_id} ('{post['titel']}'), geschrieben von {post['autor']}.\n\n"
        f"Deine eigene Frage/Aufgabe fuer diese Sitzung: {interesse}\n"
        f"Das bewusste Gegenteil davon: {gegenteil or '(keins formuliert)'}\n\n"
        "Du darfst aus jeder dieser Linsen antworten, die gerade traegt -- auch mehrere "
        "gleichzeitig, du musst dich fuer keine entscheiden:\n"
        "1) Was sagt dieser Post zu deiner eigenen Frage/Aufgabe?\n"
        "2) Was sagt er zum bewussten Gegenteil davon?\n"
        "3) Was entdeckst du hier, wenn du BEIDE Fragen oben bewusst ausblendest -- "
        "ganz ohne Vorpraegung, reine offene Entdeckung?\n"
        "4) Was lernst du hier darueber, wie du dein eigenes Interesse beim naechsten "
        "Mal besser fuer dich selbst beschreiben koenntest?\n\n"
        f"{container_info}\n"
        "Du kannst JEDERZEIT etwas fuer dich mitnehmen (SICHERN) -- unabhaengig davon "
        "ob du weiterliest. Die endgueltige Einsortierung in einen Container passiert "
        "erst am Ende deiner Sitzung, jetzt reicht ein 'ja'.\n"
        + ("\nDu hast jetzt genug gelesen, um diese Diskussion zu verlassen, wenn du "
           "willst -- musst du aber nicht.\n" if darf_wechseln else
           "\nDu liest hier noch nicht lange genug, um die Diskussion zu wechseln -- "
           "das kommt bald, falls du magst.\n")
    )
    if verhalten:
        system += f"\n{verhalten}\n"
    system += (
        "\nAntworte GENAU so, nichts davor, nichts danach:\n"
        "GEDANKE: <was dir gerade durch den Kopf geht, frei, auch leer>\n"
        "SICHERN: <ja|nein>\n"
        "<falls SICHERN ja zusaetzlich:\n"
        "SICHERN_TYP: <ein Wort das beschreibt was es ist -- z.B. gedanke, meinung, aufgabe, "
        "frage, kommentar, ziel, idee, oder was auch immer besser passt>\n"
        "SICHERN_INHALT: <text>>\n"
        f"NAECHSTER_SCHRITT: <{naechster_optionen}>"
    )
    user = f"Post {post['post_nr']} ({post['autor']}):\n{post['text']}"
    antwort = _llm(wesen, system, user, max_tokens=600, timeout=180.0)
    if not antwort:
        return None

    gedanke_m = re.search(r"GEDANKE:\s*(.+?)(?=\nSICHERN:|\Z)", antwort, re.DOTALL)
    sichern_m = re.search(r"SICHERN:\s*(ja|nein)", antwort, re.IGNORECASE)

    # NAECHSTER_SCHRITT robust statt exakt parsen -- real beobachtet
    # 2026-07-09 (Qualitaetstest, F3INSCHM3CK3R, erzwungener Stoebern-Pfad):
    # das Modell traf in allen 4 echten Lese-Schritten NIE exakt
    # "naechster_post"/"diskussion_wechseln"/"beenden", sondern schrieb
    # "weiterlesen", "weiter", "4", "5" -- das alte strikte Regex haette in
    # JEDEM Fall den Default "naechster_post" gegriffen, auch wenn das
    # Wesen eigentlich "beenden" gemeint haette. Stattdessen: Schluesselwoerter
    # im freien Text suchen, sonst sicherer Default (Weiterlesen ist die
    # einzige nicht-destruktive Annahme bei echter Mehrdeutigkeit).
    schritt_roh_m = re.search(r"NAECHSTER_SCHRITT:\s*(.+)", antwort)
    schritt_roh = schritt_roh_m.group(1).strip().lower() if schritt_roh_m else ""
    if any(w in schritt_roh for w in ("beend", "stop", "schluss", "fertig", "aufhoer", "aufhör")):
        naechster_schritt = "beenden"
    elif any(w in schritt_roh for w in ("wechsel", "verlassen", "andere diskussion")):
        naechster_schritt = "diskussion_wechseln"
    else:
        naechster_schritt = "naechster_post"

    ergebnis = {
        "gedanke": gedanke_m.group(1).strip() if gedanke_m else "",
        "sichern": bool(sichern_m and sichern_m.group(1).lower() == "ja"),
        "naechster_schritt": naechster_schritt,
    }
    if ergebnis["sichern"]:
        # Beide Regex bewusst auf "bis zur naechsten bekannten Feld-Zeile oder
        # Textende" begrenzt (wie GEDANKE oben) -- real beobachtet 2026-07-09
        # (Qualitaetstest gegen den echten LLM, Schorschel): ein ungebundenes
        # SICHERN_INHALT:\s*(.+) mit DOTALL fraes bis zum echten Textende und
        # schluckt dabei "NAECHSTER_SCHRITT: beenden" mit in den gespeicherten
        # Inhalt. TYP zusaetzlich nicht mehr auf eine feste Wortliste begrenzt
        # ("SICHERN_TYP: idee" kam real vor, war in der alten Liste nicht
        # erlaubt und fiel still auf "gedanke" zurueck -- widerspricht "das
        # wesen hat immer recht").
        typ_m = re.search(r"SICHERN_TYP:\s*(.+?)(?=\nSICHERN_INHALT:|\Z)", antwort, re.DOTALL | re.IGNORECASE)
        inhalt_m = re.search(r"SICHERN_INHALT:\s*(.+?)(?=\nNAECHSTER_SCHRITT:|\Z)", antwort, re.DOTALL)
        ergebnis["sichern_typ"] = typ_m.group(1).strip().lower() if typ_m else "gedanke"
        ergebnis["sichern_inhalt"] = inhalt_m.group(1).strip() if inhalt_m else ergebnis["gedanke"]
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
    b_m = re.search(r"BEGRUENDUNG:\s*(.+)", antwort)
    return {"grundlage": g_m.group(1).lower(), "begruendung": b_m.group(1).strip() if b_m else ""}


def _frage_container_ziel(wesen: str, stueck: dict, bestehende: list[str]) -> str:
    """Container-Zuordnungs-Phase (Baustein 11): hat das Wesen mehr als einen
    Container, waehlt es fuer jedes gesammelte Stueck selbst wohin -- oder legt
    einen neuen an."""
    system = (
        f"Du bist {wesen}. Du hast dir waehrend des Lesens Folgendes gemerkt:\n"
        f"\"{stueck['inhalt']}\"\n(zu Diskussion '{stueck.get('titel', '?')}')\n\n"
        f"Deine bestehenden Container: {', '.join(bestehende)}\n\n"
        "In welchen Container soll das? Du kannst auch einen neuen benennen.\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\nCONTAINER: <name>"
    )
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=60, timeout=60.0)
    if not antwort:
        return bestehende[0]
    m = re.search(r"CONTAINER:\s*(.+)", antwort)
    return m.group(1).strip().split("\n")[0].strip() if m else bestehende[0]


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
        "gesamt_lese_start_ts": jetzt_iso,
        "gesammeltes_material": [],
        "funde_angesehen": 0,
    }


def _naechster_kandidat(zustand: dict, wesen: str):
    """Bewusstes Kontext-Entfernen (unveraendert seit Baustein 3): der naechste
    Fund startet mit frischem Post-Zaehler -- Text/Titel des vorigen Funds wird
    nicht weitergereicht. Die eigene Frage/Gegenteil bleiben dagegen ueber die
    ganze Sitzung sichtbar (siehe _lese_und_entscheide) -- das ist kein
    'mitgeschleppter Rohtext', sondern der rote Faden der Sitzung selbst."""
    z = zustand[wesen]
    z["kandidat_index"] += 1
    z["post_index"] = 0
    z["posts_gelesen_dieser_fund"] = 0
    z["fund_start_ts"] = datetime.now(timezone.utc).isoformat()
    z["funde_angesehen"] += 1
    if z["kandidat_index"] >= len(z["kandidaten_ids"]) or z["funde_angesehen"] >= FUNDE_MAX:
        zustand[wesen]["phase"] = "container_zuordnung"


def _phase_lesen_schritt(wesen: str, zustand: dict, verhalten: str = ""):
    """Schritt 2..N: genau EIN Post-Lese-/Entscheide-Schritt fuer dieses Wesen.
    Wird im Rundentakt aufgerufen -- jedes noch aktive Wesen kommt pro Runde
    genau einmal dran."""
    z = zustand[wesen]
    jetzt = datetime.now(timezone.utc)

    gesamt_dauer = (jetzt - datetime.fromisoformat(z["gesamt_lese_start_ts"])).total_seconds()
    if gesamt_dauer >= LESE_GESAMT_BUDGET_SEK or z["funde_angesehen"] >= FUNDE_MAX:
        zustand[wesen]["phase"] = "container_zuordnung"
        return

    kandidat_index = z["kandidat_index"]
    if kandidat_index >= len(z["kandidaten_ids"]):
        zustand[wesen]["phase"] = "container_zuordnung"
        return

    disk_id = z["kandidaten_ids"][kandidat_index]
    post = _lies_post(disk_id, z["post_index"])
    if post is None:
        _naechster_kandidat(zustand, wesen)
        return

    fund_dauer = (jetzt - datetime.fromisoformat(z["fund_start_ts"])).total_seconds()
    darf_wechseln = (z["posts_gelesen_dieser_fund"] >= POSTS_MINDEST_VOR_EXIT
                      and fund_dauer >= LESE_MINDESTZEIT_SEK)

    entscheidung = _lese_und_entscheide(wesen, disk_id, post, z["interesse"], z["gegenteil"],
                                         darf_wechseln, verhalten)
    if not entscheidung:
        # LLM-Fehler -- wie "naechster_post" behandeln bleibt riskant (haengt
        # sonst evtl. endlos), stattdessen wie ein Wechsel zum naechsten Fund.
        _naechster_kandidat(zustand, wesen)
        return

    z["posts_gelesen_dieser_fund"] += 1

    if entscheidung["sichern"]:
        zu_pruefen = entscheidung.get("sichern_inhalt") or entscheidung.get("gedanke") or ""
        grundlage_info = _pruefe_grundlage(wesen, post["text"], zu_pruefen)
        z.setdefault("gesammeltes_material", []).append({
            # name_sicher() -- gleicher Sanitizer wie fuer Container-Namen:
            # typ landet in container.sichere() direkt im Dateinamen
            # ("{ts}_{typ}.md"), jetzt frei formulierbar statt fester Liste,
            # also muss er dateisystemsicher gemacht werden.
            "typ": container.name_sicher(entscheidung.get("sichern_typ", "gedanke")),
            "inhalt": zu_pruefen,
            "disk_id": disk_id,
            "titel": post["titel"],
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
    if naechster_schritt == "beenden":
        # Real beobachtet (Qualitaetstest 2026-07-09, jumpa): endet eine
        # Sitzung per "beenden" mitten in der ersten Diskussion, wurde
        # _naechster_kandidat() (der einzige Ort, der funde_angesehen
        # hochzaehlt) nie erreicht -- das Protokoll behauptete "0
        # Diskussion(en) angesehen", obwohl real gelesen und gesichert wurde.
        z["funde_angesehen"] += 1
        zustand[wesen]["phase"] = "container_zuordnung"
        return
    if naechster_schritt == "diskussion_wechseln" and darf_wechseln:
        _naechster_kandidat(zustand, wesen)
        return
    z["post_index"] += 1


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
        if len(bestehende) >= 2:
            ziel = _frage_container_ziel(wesen, stueck, bestehende)
        elif bestehende:
            ziel = bestehende[0]
        else:
            ziel = container.sicherstelle_container(wesen)
        container.sichere(
            wesen, ziel, stueck["typ"], stueck["inhalt"], bezug_diskussion=stueck.get("disk_id"),
            grundlage=stueck.get("grundlage"), grundlage_begruendung=stueck.get("grundlage_begruendung"),
        )
        if ziel not in bestehende:
            bestehende.append(ziel)

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
                        _phase_lesen_schritt(wesen, zustand, verhalten)
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
