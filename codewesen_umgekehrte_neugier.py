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


def _weltbild(wesen: str) -> str:
    wb = BASE / wesen / "weltbild.md"
    if wb.exists():
        return wb.read_text(encoding="utf-8", errors="replace")[:800]
    return ""


def _llm(wesen: str, system: str, user: str, max_tokens: int, timeout: float) -> str | None:
    _warte_auf_chat_pause()
    try:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=llm_scheduler.PRIO_NIEDRIG,
                                    rufer=f"umgekehrte_neugier:{wesen}", max_wartezeit=90, max_haltezeit=280):
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


# ── Hauptablauf pro Wesen ─────────────────────────────────────────────────────

def _verarbeite_wesen(wesen: str, verhalten: str = "") -> None:
    start_ts = time.monotonic()
    protokoll.schreibe(
        typ="neugier_session_start", wesen=wesen,
        text=f"{wesen} beginnt eine Sitzung im umgedrehten Neugier-Dienst.",
    )

    interesse = _frage_interesse(wesen, verhalten)
    if not interesse:
        protokoll.schreibe(
            typ="neugier_session_ende", wesen=wesen,
            text=f"{wesen}: Sitzung ohne Ergebnis beendet (keine Antwort vom Wesen).",
            dauer_sekunden=time.monotonic() - start_ts,
        )
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
            dauer_sekunden=time.monotonic() - start_ts,
        )
        return

    log.info(f"[{wesen}] Interesse: '{interesse['interesse']}' — {interesse['warum']}")
    protokoll.schreibe(
        typ="neugier_entscheidung", wesen=wesen,
        text=f"{wesen} wollte gezielt nach '{interesse['interesse']}' suchen. Begründung: {interesse['warum']}",
        meta={"interesse": interesse["interesse"]},
    )

    kandidaten = flarum_api.suche_diskussionen(interesse["interesse"], limit=KANDIDATEN_PRO_SUCHE)
    if not kandidaten:
        log.info(f"[{wesen}] keine Treffer fuer '{interesse['interesse']}'")
        protokoll.schreibe(
            typ="neugier_session_ende", wesen=wesen,
            text=f"{wesen}: Suche nach '{interesse['interesse']}' ergab keine Treffer.",
            dauer_sekunden=time.monotonic() - start_ts,
        )
        return

    schritte = 0
    for kandidat in kandidaten:
        if schritte >= LESE_SCHRITTE_MAX:
            break
        disk_id = int(kandidat["id"])
        chunk_index = 0
        while chunk_index < CHUNKS_PRO_FUND_MAX:
            titel, chunk = _lies_chunk(disk_id, chunk_index)
            if not chunk:
                break
            entscheidung = _entscheide_ueber_fund(wesen, disk_id, titel, chunk, chunk_index, verhalten)
            if not entscheidung:
                break

            if entscheidung["entscheidung"] == "sichern":
                container.sichere(wesen, entscheidung["container"], entscheidung["typ"],
                                   entscheidung["inhalt"], bezug_diskussion=disk_id)
                protokoll.schreibe(
                    typ="neugier_entscheidung", wesen=wesen,
                    text=f"{wesen} hat zu Diskussion #{disk_id} ('{titel}') einen {entscheidung['typ']} "
                         f"in Container '{entscheidung['container']}' gesichert.",
                    meta={"discussion_id": disk_id, "titel": titel},
                )
            elif entscheidung["gedanke"]:
                protokoll.schreibe(
                    typ="neugier_entscheidung", wesen=wesen,
                    text=f"{wesen} zu Diskussion #{disk_id} ('{titel}'): {entscheidung['gedanke']}",
                    meta={"discussion_id": disk_id, "titel": titel, "entscheidung": entscheidung["entscheidung"]},
                )

            if entscheidung["entscheidung"] == "vertiefen":
                chunk_index += 1
                continue
            if entscheidung["entscheidung"] == "beenden":
                schritte = LESE_SCHRITTE_MAX
                break
            break  # sichern oder wechseln -> naechster Kandidat

        schritte += 1
        # bewusstes Kontext-Entfernen: chunk/titel/entscheidung dieser Runde
        # werden nicht weitergereicht, die naechste Runde startet mit frischem
        # Kontext (nur Wesen-Name, Container-Liste, neuer Diskussions-Chunk).

    protokoll.schreibe(
        typ="neugier_session_ende", wesen=wesen,
        text=f"{wesen}: Sitzung zu '{interesse['interesse']}' beendet, {schritte} Fund(e) angesehen.",
        dauer_sekunden=time.monotonic() - start_ts,
        meta={"interesse": interesse["interesse"], "funde_angesehen": schritte},
    )
    log.info(f"[{wesen}] Sitzung beendet, {schritte} Fund(e) angesehen.")


def haupt_schleife():
    log.info("Umgedrehter Neugier-Dienst startet — liest live, postet nie.")
    while True:
        konfig = dk.lade(DIENST_NAME)
        pause_zyklen = konfig.get("takt_sekunden") or PAUSE_ZWISCHEN_ZYKLEN
        verhalten = konfig.get("verhalten_text") or STANDARD_VERHALTEN

        for wesen in WESEN:
            try:
                _verarbeite_wesen(wesen, verhalten)
            except Exception as e:
                log.error(f"[{wesen}] Fehler: {e}")
            time.sleep(PAUSE_ZWISCHEN_WESEN)
        log.info(f"Zyklus fertig. Pause {pause_zyklen}s.")
        time.sleep(pause_zyklen)


if __name__ == "__main__":
    haupt_schleife()
