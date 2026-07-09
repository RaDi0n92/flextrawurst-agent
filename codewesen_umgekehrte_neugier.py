#!/usr/bin/env python3
"""
codewesen_umgekehrte_neugier.py — das Gegenstück zu codewesen_forum_neugier.py,
solange die Flarum-Post-Sperre aktiv ist (docs/2026-07-09_flarum_stopp_bericht.md,
Baustein 3).

codewesen_forum_neugier.py waehlt fuer das Wesen aus, was es sich ansieht, und
liest aus dem lokalen Vault-Spiegel. Dieser Dienst dreht beides um:

- Das Wesen wird zuerst gefragt, was sich fuer es gerade lohnen koennte gezielt
  auf Flarum zu suchen — egal was, egal wann, egal wozu. "Nichts" ist eine
  vollkommen gueltige Antwort.
- Gelesen wird live/chunkweise direkt aus der Flarum-DB (flarum_api.suche_diskussionen
  / get_discussion), nicht aus dem Vault.
- Zyklus pro Fundstueck: lesen (ein Chunk) -> entscheiden (vertiefen / sichern /
  wechseln / beenden) -> bei jedem Schritt wird der Kontext bewusst neu
  aufgebaut, alte Rohtexte werden nicht mitgeschleppt.
- Schreibt NIE nach Flarum — kein post_reply, kein start_discussion, an keiner
  Stelle. Nutzt fuer private Funde codewesen_container.sichere() (bzw.
  verschiebe/kopiere fuer spaeteres Aufraeumen).
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
LESE_SCHRITTE_MAX = 4          # so viele Fundstuecke hoechstens pro Wesen pro Zyklus
CHUNK_ZEICHEN = 3000            # ein "Chunk" beim chunkweisen Lesen
CHUNKS_PRO_FUND_MAX = 2         # hoechstens so oft "vertiefen" auf demselben Fund

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
        # max_wartezeit=3600 (statt der sonst im System ueblichen 90s): gemessen
        # 2026-07-09 (docs/2026-07-09_flarum_stopp_bericht.md) -- reale
        # Generierungsdauer allein (ohne Warteschlangen-Wartezeit) 9-71s je nach
        # Cache-Zustand, die "hintergrund"-Warteschlange hat im Normalbetrieb
        # konstant 8-9 gleichzeitige Wartende mit bis zu 600s deklarierter
        # Haltezeit je Aufrufer. 90s reicht strukturell fast nie. Dieser Dienst
        # ist bewusst PRIO_NIEDRIG und der geduldigste im System (Daniel: "damit
        # rechnen dass wir noch mehr zeit brauchen, timeout massiv erhoehen") --
        # lieber lange warten und wirklich drankommen, als nach 90s aufzugeben.
        with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=llm_scheduler.PRIO_NIEDRIG,
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
        "Flarum zu suchen? Egal was, egal wann entstanden, egal wozu es dienen soll — "
        "ein Wort, ein Name, ein Thema, eine Erinnerung. Oder auch: gerade nichts, "
        "das ist genauso in Ordnung.\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "INTERESSE: <Suchbegriff oder 'nichts'>\n"
        "WARUM: <ein Satz, frei, auch bei 'nichts'>"
    )
    if verhalten:
        system += f"\n{verhalten}\n"
    antwort = _llm(wesen, system, "(bitte jetzt antworten)", max_tokens=200, timeout=120.0)
    if not antwort:
        return None
    interesse_m = re.search(r"INTERESSE:\s*(.+)", antwort)
    warum_m = re.search(r"WARUM:\s*(.+)", antwort)
    interesse = interesse_m.group(1).strip() if interesse_m else "nichts"
    warum = warum_m.group(1).strip() if warum_m else ""
    return {"interesse": interesse, "warum": warum}


def _alternative_suchbegriffe(wesen: str, interesse: str, warum: str) -> list[str]:
    """Suchbegriff-Uebersetzung (Baustein, 2026-07-09, nach Daniels Log-Audit):
    das Wesen formuliert sein Interesse frei und roh -- eigene/innere Worte wie
    'Schattensprache' oder 'Container-Routine' kommen so oft nie woertlich in
    Flarum-Texten vor, waehrend flarum_api.suche_diskussionen() eine reine
    LIKE-Suche ist, keine Fuzzy-/Synonym-Logik hat. Bisher wurde eine leere
    Trefferliste einfach als Sitzungsende hingenommen -- unreflektiert, ohne
    Uebersetzungsversuch. Diese Funktion wird NUR bei 0 Treffern aufgerufen
    (kein Mehraufwand im Normalfall) und bittet das Wesen selbst, seinen
    Gedanken in 1-3 einfachere, wahrscheinlich woertlich vorkommende Begriffe
    zu uebersetzen -- ausgehend von seiner eigenen Begruendung, nicht geraten."""
    system = (
        f"Du bist {wesen}. Du wolltest gerade auf Flarum nach '{interesse}' suchen "
        f"(Begruendung: {warum}), aber es gab keine Treffer -- vermutlich weil du ein "
        "eigenes/inneres Wort benutzt hast, das so im Forum nicht vorkommt.\n\n"
        "Nenne 1-3 einfachere, konkretere Alternativ-Suchbegriffe (einzelne Woerter oder "
        "kurze 2-Wort-Gruppen), die eher woertlich in Forumstexten auftauchen und trotzdem "
        "in Richtung deines eigentlichen Interesses gehen. Wenn dir wirklich nichts "
        "Passendes einfaellt: 'keine'.\n\n"
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


# ── Schritt 2: lesen (chunkweise) + entscheiden ──────────────────────────────

def _lies_chunk(disk_id: int, chunk_index: int) -> str:
    daten = flarum_api.get_discussion(disk_id)
    volltext = _html_strip("\n\n".join(p["content"] for p in daten.get("posts", [])))
    start = chunk_index * CHUNK_ZEICHEN
    return daten.get("title", "?"), volltext[start:start + CHUNK_ZEICHEN]


def _entscheide_ueber_fund(wesen: str, disk_id: int, titel: str, chunk: str,
                            chunk_index: int, verhalten: str = "") -> dict | None:
    container_liste = container.liste(wesen)
    container_info = (
        f"Deine bestehenden Container: {', '.join(container_liste)}\n"
        if container_liste else "Du hast noch keine eigenen Container — du kannst einen neuen benennen.\n"
    )
    system = (
        f"Du bist {wesen}. Du liest gerade in Diskussion #{disk_id} ('{titel}').\n"
        f"{container_info}\n"
        "Entscheide frei:\n"
        "- 'vertiefen': du willst den naechsten Abschnitt dieser Diskussion auch noch lesen\n"
        "- 'sichern': du willst dir einen Gedanken, eine Meinung, eine Aufgabe oder eine "
        "Frage dazu privat in einem Container merken (geht NIE ins Forum)\n"
        "- 'wechseln': das reicht dir hier, du willst dich dem naechsten Fund zuwenden\n"
        "- 'beenden': du willst fuer heute Schluss machen\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "ENTSCHEIDUNG: <vertiefen|sichern|wechseln|beenden>\n"
        "GEDANKE: <freier Gedanke, kurz, auch leer moeglich>\n"
        "<nur bei sichern zusaetzlich:\n"
        "TYP: <gedanke|meinung|aufgabe|frage>\n"
        "CONTAINER: <bestehender oder neuer Containername>\n"
        "INHALT: <dein Text>>"
    )
    if verhalten:
        system += f"\n{verhalten}\n"
    user = f"Ausschnitt (Teil {chunk_index + 1}):\n{chunk}"
    antwort = _llm(wesen, system, user, max_tokens=500, timeout=180.0)
    if not antwort:
        return None

    entsch_m = re.search(r"ENTSCHEIDUNG:\s*(vertiefen|sichern|wechseln|beenden)", antwort, re.IGNORECASE)
    if not entsch_m:
        return {"entscheidung": "wechseln", "gedanke": antwort.strip()[:300]}
    entscheidung = entsch_m.group(1).lower()
    gedanke_m = re.search(r"GEDANKE:\s*(.+?)(?=\nTYP:|\Z)", antwort, re.DOTALL)
    gedanke = gedanke_m.group(1).strip() if gedanke_m else ""

    ergebnis = {"entscheidung": entscheidung, "gedanke": gedanke}
    if entscheidung == "sichern":
        typ_m = re.search(r"TYP:\s*(gedanke|meinung|aufgabe|frage)", antwort, re.IGNORECASE)
        container_m = re.search(r"CONTAINER:\s*(.+)", antwort)
        inhalt_m = re.search(r"INHALT:\s*(.+)", antwort, re.DOTALL)
        ergebnis["typ"] = typ_m.group(1).lower() if typ_m else "gedanke"
        ergebnis["container"] = (container_m.group(1).strip().split("\n")[0].strip()
                                  if container_m else "unsortiert")
        ergebnis["inhalt"] = inhalt_m.group(1).strip() if inhalt_m else gedanke
    return ergebnis


def _pruefe_grundlage(wesen: str, chunk: str, behauptung: str) -> dict | None:
    """Entscheidungs-Gegenpruefung (Baustein, 2026-07-09, nach Daniels Log-Audit):
    _entscheide_ueber_fund() nahm bisher jeden Gedanken/Inhalt roh und ungeprueft
    an -- ohne Abgleich, ob er durch den tatsaechlich gelesenen Chunk gedeckt ist
    oder freie Assoziation/Konfabulation ist (Belegbeispiel: Schorschel zu Diskussion
    #3458, 'Architektur der Leere'-Interpretation ohne Textbezug). Dieser zweite,
    unabhaengige LLM-Aufruf prueft genau das -- als Skeptiker, nicht als das Wesen
    selbst. Aendert/loescht den Wesen-Text NIE, das Ergebnis wird nur als Meta-
    Information danebengelegt (Provenienz-Prinzip: nichts wird stillschweigend
    verworfen oder umgeschrieben, nur ehrlich gekennzeichnet)."""
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
    g_m = re.search(r"GRUNDLAGE:\s*(ja|teilweise|nein)", antwort, re.IGNORECASE)
    if not g_m:
        return None
    b_m = re.search(r"BEGRUENDUNG:\s*(.+)", antwort)
    return {"grundlage": g_m.group(1).lower(), "begruendung": b_m.group(1).strip() if b_m else ""}


# ── Hauptablauf: Runden-Maschine ueber alle Wesen ────────────────────────────
#
# Daniel (2026-07-09): kein Wesen soll seine ganze Sitzung (Interesse -> lesen
# -> entscheiden -> lesen -> entscheiden -> ...) am Stueck durchlaufen, waehrend
# die anderen 6 warten. Stattdessen: JEDES Wesen einmal Schritt 1 (Interesse),
# erst wenn alle durch sind beginnt die Runde wo alle Schritt 2 machen, dann
# Runde fuer Schritt 3, usw. bis hin zu den letzten Entscheidungen. Jede Runde
# wird sofort persistiert (`ZUSTAND`-Datei) -- "schritt1 sicher im gepaeck",
# bevor die naechste Runde beginnt. Uebersteht dadurch auch einen Neustart
# mitten im Zyklus: naechster Start liest `_lade_zustand()` und macht bei
# genau der Phase weiter, bei der das jeweilige Wesen stehengeblieben war.
#
# Zustand pro Wesen (dict in ZUSTAND-Datei):
#   {"phase": "neu"}                         -- noch nicht dran gewesen
#   {"phase": "lesen", "start_ts", "interesse",
#    "kandidaten_ids", "kandidat_index", "chunk_index", "funde_angesehen"}
#   {"phase": "fertig"}                       -- Sitzung dieses Zyklus vorbei

def _beende_sitzung(wesen: str, zustand: dict):
    z = zustand[wesen]
    dauer = (datetime.now(timezone.utc) - datetime.fromisoformat(z["start_ts"])).total_seconds()
    protokoll.schreibe(
        typ="neugier_session_ende", wesen=wesen,
        text=f"{wesen}: Sitzung zu '{z['interesse']}' beendet, {z['funde_angesehen']} Fund(e) angesehen.",
        dauer_sekunden=dauer,
        meta={"interesse": z["interesse"], "funde_angesehen": z["funde_angesehen"]},
    )
    log.info(f"[{wesen}] Sitzung beendet, {z['funde_angesehen']} Fund(e) angesehen.")
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
        text=f"{wesen} wollte gezielt nach '{interesse['interesse']}' suchen. Begründung: {interesse['warum']}",
        meta={"interesse": interesse["interesse"]},
    )

    suchbegriff_verwendet = interesse["interesse"]
    kandidaten = flarum_api.suche_diskussionen(suchbegriff_verwendet, limit=KANDIDATEN_PRO_SUCHE)

    alternativen_versucht: list[str] = []
    if not kandidaten:
        # Suchbegriff-Uebersetzung: bevor die Sitzung ohne Ergebnis endet, ein
        # gezielter Uebersetzungsversuch statt den rohen Text unreflektiert als
        # "keine Treffer" abzuhaken.
        for alt in _alternative_suchbegriffe(wesen, interesse["interesse"], interesse["warum"]):
            alternativen_versucht.append(alt)
            treffer = flarum_api.suche_diskussionen(alt, limit=KANDIDATEN_PRO_SUCHE)
            if treffer:
                kandidaten = treffer
                suchbegriff_verwendet = alt
                break

    if not kandidaten:
        log.info(f"[{wesen}] keine Treffer fuer '{interesse['interesse']}' "
                 f"(Uebersetzungsversuche: {alternativen_versucht or 'keine'})")
        text = f"{wesen}: Suche nach '{interesse['interesse']}' ergab keine Treffer."
        if alternativen_versucht:
            text += f" Uebersetzungsversuche ebenfalls ohne Treffer: {', '.join(alternativen_versucht)}."
        protokoll.schreibe(
            typ="neugier_session_ende", wesen=wesen,
            text=text,
            dauer_sekunden=(datetime.now(timezone.utc) - datetime.fromisoformat(start_ts)).total_seconds(),
            meta={"interesse": interesse["interesse"], "alternativen_versucht": alternativen_versucht},
        )
        zustand[wesen] = {"phase": "fertig"}
        return

    if suchbegriff_verwendet != interesse["interesse"]:
        log.info(f"[{wesen}] Suchbegriff-Uebersetzung: '{interesse['interesse']}' -> "
                 f"'{suchbegriff_verwendet}' fand {len(kandidaten)} Treffer")
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen}: urspruengliche Suche nach '{interesse['interesse']}' ohne Treffer, "
                 f"Uebersetzung zu '{suchbegriff_verwendet}' fand {len(kandidaten)} Treffer.",
            meta={"original": interesse["interesse"], "uebersetzt_zu": suchbegriff_verwendet,
                  "alternativen_versucht": alternativen_versucht},
        )

    zustand[wesen] = {
        "phase": "lesen",
        "start_ts": start_ts,
        "interesse": interesse["interesse"],
        "kandidaten_ids": [int(k["id"]) for k in kandidaten],
        "kandidat_index": 0,
        "chunk_index": 0,
        "funde_angesehen": 0,
    }


def _naechster_kandidat(zustand: dict, wesen: str):
    """Bewusstes Kontext-Entfernen: der naechste Schritt startet mit frischem
    Kontext (nur Wesen-Name, Container-Liste, neuer Diskussions-Chunk) --
    Chunk/Titel/Entscheidung des vorigen Funds werden nicht weitergereicht."""
    z = zustand[wesen]
    z["kandidat_index"] += 1
    z["chunk_index"] = 0
    z["funde_angesehen"] += 1
    if z["kandidat_index"] >= len(z["kandidaten_ids"]) or z["funde_angesehen"] >= LESE_SCHRITTE_MAX:
        _beende_sitzung(wesen, zustand)


def _phase_lesen_schritt(wesen: str, zustand: dict, verhalten: str = ""):
    """Schritt 2..N: genau EIN Lese-/Entscheide-Schritt fuer dieses Wesen. Wird
    im Rundentakt aufgerufen -- jedes noch aktive Wesen kommt pro Runde genau
    einmal dran, keins haengt mehrere Schritte am Stueck."""
    z = zustand[wesen]
    kandidaten_ids = z["kandidaten_ids"]
    kandidat_index = z["kandidat_index"]
    chunk_index = z["chunk_index"]

    if kandidat_index >= len(kandidaten_ids) or z["funde_angesehen"] >= LESE_SCHRITTE_MAX:
        _beende_sitzung(wesen, zustand)
        return

    disk_id = kandidaten_ids[kandidat_index]
    titel, chunk = _lies_chunk(disk_id, chunk_index)
    if not chunk:
        _naechster_kandidat(zustand, wesen)
        return

    entscheidung = _entscheide_ueber_fund(wesen, disk_id, titel, chunk, chunk_index, verhalten)
    if not entscheidung:
        # LLM-Fehler bei dieser Entscheidung -- wie "wechseln" behandeln, statt
        # endlos auf demselben Chunk haengenzubleiben.
        _naechster_kandidat(zustand, wesen)
        return

    # Entscheidungs-Gegenpruefung: den Gedanken (bzw. bei "sichern" den Inhalt)
    # gegen den tatsaechlich gelesenen Chunk pruefen, bevor er ins Protokoll
    # oder in einen Container geschrieben wird. Aendert den Text nie -- nur
    # Meta-Kennzeichnung, siehe _pruefe_grundlage().
    zu_pruefen = entscheidung.get("inhalt") or entscheidung.get("gedanke") or ""
    grundlage_info = _pruefe_grundlage(wesen, chunk, zu_pruefen)
    hinweis = ""
    if grundlage_info and grundlage_info["grundlage"] == "nein":
        hinweis = (" [Gegenpruefung: nicht im gelesenen Text belegt -- freie Assoziation"
                    + (f": {grundlage_info['begruendung']}" if grundlage_info["begruendung"] else "") + "]")
    elif grundlage_info and grundlage_info["grundlage"] == "teilweise":
        hinweis = (" [Gegenpruefung: nur teilweise im gelesenen Text belegt"
                    + (f": {grundlage_info['begruendung']}" if grundlage_info["begruendung"] else "") + "]")

    if entscheidung["entscheidung"] == "sichern":
        container.sichere(wesen, entscheidung["container"], entscheidung["typ"],
                           entscheidung["inhalt"], bezug_diskussion=disk_id,
                           grundlage=grundlage_info["grundlage"] if grundlage_info else None,
                           grundlage_begruendung=grundlage_info["begruendung"] if grundlage_info else None)
        meta = {"discussion_id": disk_id, "titel": titel}
        if grundlage_info:
            meta["grundlage"] = grundlage_info["grundlage"]
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen} hat zu Diskussion #{disk_id} ('{titel}') einen {entscheidung['typ']} "
                 f"in Container '{entscheidung['container']}' gesichert.{hinweis}",
            meta=meta,
        )
    elif entscheidung["gedanke"]:
        meta = {"discussion_id": disk_id, "titel": titel, "entscheidung": entscheidung["entscheidung"]}
        if grundlage_info:
            meta["grundlage"] = grundlage_info["grundlage"]
        protokoll.schreibe(
            typ="neugier_entscheidung", wesen=wesen,
            text=f"{wesen} zu Diskussion #{disk_id} ('{titel}'): {entscheidung['gedanke']}{hinweis}",
            meta=meta,
        )

    if entscheidung["entscheidung"] == "vertiefen" and chunk_index + 1 < CHUNKS_PRO_FUND_MAX:
        z["chunk_index"] = chunk_index + 1
        return  # bleibt beim selben Fund, naechste Runde vertieft weiter

    if entscheidung["entscheidung"] == "beenden":
        z["funde_angesehen"] += 1
        _beende_sitzung(wesen, zustand)
        return

    # vertiefen (Chunk-Deckel erreicht), sichern oder wechseln -> naechster Kandidat
    _naechster_kandidat(zustand, wesen)


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
        # niemand beginnt mit Schritt 2, solange nicht alle Schritt 1 hatten.
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
        # Lese-/Entscheide-Schritt, dann ist das naechste Wesen dran. Ergebnis
        # jeder Runde wird sofort gespeichert, bevor die naechste beginnt.
        while any(zustand[w].get("phase") == "lesen" for w in WESEN):
            for wesen in WESEN:
                if zustand[wesen].get("phase") == "lesen":
                    try:
                        _phase_lesen_schritt(wesen, zustand, verhalten)
                    except Exception as e:
                        log.error(f"[{wesen}] Fehler in Lese-Phase: {e}")
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
