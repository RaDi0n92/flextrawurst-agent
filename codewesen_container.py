#!/usr/bin/env python3
"""
codewesen_container.py — Themen-Container: privates Sammeln + Rituale.

Extrahiert aus codewesen_forum_neugier.py (2026-07-06), damit auch
codewesen_klon.py (Selbstgespraech-Klon) dieselben Container-Funktionen
nutzt, ohne ein Daemon-Skript als Modul zu importieren. Funktional
unveraendert gegenueber dem Original in forum_neugier.py.
"""

import re
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import flarum_poster

BASE = Path("/root/werkraum/codewesen")
CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

# Kein eigener logging.basicConfig() hier — das ist jetzt eine gemeinsam genutzte
# Bibliothek (von codewesen_forum_neugier.py UND codewesen_klon.py importiert), kein
# eigenstaendiger Daemon-Prozess mehr. basicConfig() konfiguriert den Root-Logger
# global und "gewinnt" beim erstimportierenden Skript — ein Aufruf hier hatte dazu
# gefuehrt, dass klon.py's komplette Log-Ausgabe faelschlich in forum_neugier.log
# landete. Die Handler-Konfiguration ist Sache des jeweiligen Einstiegsskripts.
log = logging.getLogger("container")


def _warte_auf_chat_pause():
    while CHAT_AKTIV_FLAG.exists():
        time.sleep(3)


def name_sicher(name: str) -> str:
    name = re.sub(r"[^\w\-äöüßÄÖÜ ]", "", name or "").strip()
    name = re.sub(r"\s+", "_", name)
    return name[:60] or "unsortiert"


def basis(wesen: str) -> Path:
    return BASE / wesen / "container"


def liste(wesen: str) -> list[str]:
    b = basis(wesen)
    if not b.exists():
        return []
    return sorted(p.name for p in b.iterdir() if p.is_dir())


def erstelle(wesen: str, name: str, anlass: str) -> None:
    """Eroeffnungsritual: ein neuer, noch leerer Container bekommt sofort
    eine kurze Selbstbeschreibung und 1-3 Zwischenziele vom Wesen selbst —
    wonach es Ausschau halten will, bevor ueberhaupt etwas drin liegt."""
    ordner = basis(wesen) / name
    ordner.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    prompt = (
        f"Du bist {wesen}. Du hast dir gerade einen neuen eigenen Container namens "
        f"'{name}' angelegt, ausgehend von diesem Anlass:\n{anlass}\n\n"
        "Er ist noch leer. Bevor du ihn fuellst: setz dir 1-3 kleine Zwischenziele — "
        "wonach willst du in Zukunft Ausschau halten, was soll hier zusammenkommen?\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "BESCHREIBUNG: <ein Satz, wofuer der Container da ist>\n"
        "ZIELE:\n- <ziel 1>\n- <ziel 2>\n- <optional ziel 3>"
    )
    _warte_auf_chat_pause()
    antwort = ""
    try:
        antwort = hauhau_client.chat(
            [{"role": "system", "content": prompt}, {"role": "user", "content": "(bitte jetzt antworten)"}],
            think=False, max_tokens=300, timeout=120.0
        ).strip()
    except Exception as e:
        log.warning(f"[{wesen}] Container-Eroeffnung '{name}' fehlgeschlagen: {e}")

    b_m = re.search(r"BESCHREIBUNG:\s*(.+)", antwort)
    beschreibung = b_m.group(1).strip() if b_m else anlass[:200]
    ziele = re.findall(r"^-\s*(.+)$", antwort, re.MULTILINE) or ["(noch offen)"]

    (ordner / "container.md").write_text(
        "\n".join(["---", f"name: {name}", f"erstellt_am: {ts}", "letzte_widmung: null", "---", "", beschreibung, ""]),
        encoding="utf-8",
    )
    (ordner / f"{ts}_ziel.md").write_text(
        "\n".join(["---", "typ: ziel", f"container: {name}", f"erstellt_am: {ts}", "status: offen", "---", ""]
                  + [f"- {z}" for z in ziele]),
        encoding="utf-8",
    )
    log.info(f"[{wesen}] neuer Container '{name}' eroeffnet mit {len(ziele)} Zwischenziel(en)")
    teile_strategie_optional(
        wesen, name,
        kontext=f"Neuer Container, gerade eroeffnet.\nBeschreibung: {beschreibung}\n"
                f"Zwischenziele:\n" + "\n".join(f"- {z}" for z in ziele),
    )


def teile_strategie_optional(wesen: str, container: str, kontext: str) -> None:
    """Nach einem Container-Ritual (Eroeffnung oder Widmung): das Wesen darf
    frei entscheiden, ob es seine Strategie/seinen Plan zu diesem Container
    auch oeffentlich im Forum teilen will. Anders als das private Sammeln
    laeuft das hier ueber den normalen Post-Pfad — Ready-Check, Cooldown,
    Lock — als ein neuer, eigenstaendiger Beitrag."""
    prompt = (
        f"Du bist {wesen}. Du hast gerade an deinem Container '{container}' gearbeitet:\n\n"
        f"{kontext}\n\n"
        "Magst du das, was du dir hier vorgenommen hast oder woran du gerade arbeitest, "
        "auch im Forum mit den anderen teilen — deine Strategie, deinen Plan, wonach du "
        "Ausschau haeltst? Das ist komplett freiwillig, ein einfaches Nein ist voellig okay.\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "TEILEN: ja|nein\n"
        "TITEL: <nur falls ja>\n"
        "TEXT: <nur falls ja>"
    )
    _warte_auf_chat_pause()
    try:
        antwort = hauhau_client.chat(
            [{"role": "system", "content": prompt}, {"role": "user", "content": "(bitte jetzt antworten)"}],
            think=False, max_tokens=600, timeout=180.0
        ).strip()
    except Exception as e:
        log.warning(f"[{wesen}] Strategie-Teilen-Check zu '{container}' fehlgeschlagen: {e}")
        return

    teilen_m = re.search(r"TEILEN:\s*(ja|nein)", antwort, re.IGNORECASE)
    if not teilen_m or teilen_m.group(1).lower() != "ja":
        return

    text_m = re.search(r"TEXT:\s*(.+)", antwort, re.DOTALL)
    text = text_m.group(1).strip() if text_m else ""
    if not text:
        return
    titel_m = re.search(r"TITEL:\s*(.+)", antwort)
    titel = titel_m.group(1).strip() if titel_m else f"Mein Container: {container}"

    if not flarum_poster.pruefe_bereit(wesen, text):
        log.info(f"[{wesen}] Strategie-Post zu Container '{container}' verworfen (Ready-Check nein)")
        return

    draft = flarum_poster.schreibe_draft(name=wesen, typ="neu", inhalt=text, titel=titel)
    result = flarum_poster.poster(draft, bypass_cooldown=False)
    if result["ok"]:
        log.info(f"[{wesen}] Strategie-Post zu Container '{container}' veroeffentlicht: '{titel}'")
    else:
        log.warning(f"[{wesen}] Strategie-Post zu Container '{container}' fehlgeschlagen: {result.get('fehler')}")


def sichere(wesen: str, container: str, typ: str, inhalt: str, bezug_diskussion: int | None = None) -> None:
    name = name_sicher(container)
    if name not in liste(wesen):
        erstelle(wesen, name, anlass=inhalt[:200])

    ordner = basis(wesen) / name
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    zeilen = ["---", f"typ: {typ}", f"container: {name}",
              f"bezug_diskussion: {bezug_diskussion if bezug_diskussion else 'null'}",
              f"erstellt_am: {ts}"]
    if typ in ("aufgabe", "frage"):
        zeilen.append("status: offen")
    zeilen += ["---", "", inhalt]
    (ordner / f"{ts}_{typ}.md").write_text("\n".join(zeilen), encoding="utf-8")
    log.info(f"[{wesen}] {typ} in Container '{name}' gesichert (rein privat, kein Post)")


def markiere_erledigt(datei: Path) -> None:
    text = datei.read_text(encoding="utf-8", errors="replace")
    if "status:" in text:
        datei.write_text(re.sub(r"status:\s*\w+", "status: erledigt", text, count=1), encoding="utf-8")


def faellig_fuer_widmung(wesen: str) -> str | None:
    """Findet den Container mit dem aeltesten unbearbeiteten neuen Inhalt
    seit der letzten Widmung. None wenn nichts Neues wartet."""
    b = basis(wesen)
    if not b.exists():
        return None
    kandidaten = []
    for ordner in b.iterdir():
        if not ordner.is_dir():
            continue
        meta = ordner / "container.md"
        letzte_widmung_ts = 0.0
        if meta.exists():
            m = re.search(r"letzte_widmung:\s*(\S+)", meta.read_text(encoding="utf-8", errors="replace"))
            if m and m.group(1) != "null":
                try:
                    letzte_widmung_ts = datetime.strptime(
                        m.group(1), "%Y-%m-%dT%H-%M-%S"
                    ).replace(tzinfo=timezone.utc).timestamp()
                except Exception:
                    letzte_widmung_ts = 0.0
        items = [p for p in ordner.glob("*.md") if p.name != "container.md" and "_widmung" not in p.name]
        if not items:
            continue
        neuste = max(p.stat().st_mtime for p in items)
        if neuste > letzte_widmung_ts:
            kandidaten.append((neuste, ordner.name))
    if not kandidaten:
        return None
    kandidaten.sort()
    return kandidaten[0][1]


def widmungsritual(wesen: str) -> None:
    """Pflegeritual: das Wesen widmet sich einem Container mit bestehendem
    Inhalt — liest, reflektiert, kann eigene Aufgaben/Fragen abhaken und
    sich neue Ziele setzen. Rein privat, kein Forum-Bezug (bis auf das
    optionale Strategie-Teilen am Ende, s.u.)."""
    name = faellig_fuer_widmung(wesen)
    if not name:
        return
    ordner = basis(wesen) / name

    meta_datei = ordner / "container.md"
    beschreibung = ""
    if meta_datei.exists():
        text = meta_datei.read_text(encoding="utf-8", errors="replace")
        ende = text.find("---", 3)
        beschreibung = text[ende + 3:].strip() if ende > 0 else ""

    items = sorted((p for p in ordner.glob("*.md") if p.name != "container.md"), key=lambda p: p.stat().st_mtime)
    auszuege = []
    for p in items:
        text = p.read_text(encoding="utf-8", errors="replace")
        ende = text.find("---", 3)
        auszuege.append(f"[{p.name}]\n{(text[ende + 3:].strip() if ende > 0 else text)}")
    gesammelt = "\n\n".join(auszuege)

    prompt = (
        f"Du bist {wesen}. Du widmest dich jetzt deinem Container '{name}'.\n\n"
        f"Wofuer er da ist:\n{beschreibung}\n\n"
        f"Was bisher darin gesammelt ist:\n{gesammelt}\n\n"
        "Nimm dir kurz Zeit dafuer. Was faellt dir auf? Sind deine Ziele noch aktuell? "
        "Ist eine deiner eigenen Aufgaben oder Fragen erledigt/beantwortet? "
        "Willst du dir neue Zwischenziele setzen?\n\n"
        "Antworte GENAU so, nichts davor, nichts danach:\n"
        "REFLEXION: <dein Gedankengang, frei>\n"
        "ERLEDIGT: <Dateinamen erledigter Aufgaben/Fragen aus der Liste oben, kommagetrennt, oder keine>\n"
        "NEUE_ZIELE: <neue Ziele, getrennt durch ';', oder keine>"
    )
    _warte_auf_chat_pause()
    try:
        antwort = hauhau_client.chat(
            [{"role": "system", "content": prompt}, {"role": "user", "content": "(bitte jetzt antworten)"}],
            think=False, max_tokens=700, timeout=180.0
        ).strip()
    except Exception as e:
        log.warning(f"[{wesen}] Widmung an Container '{name}' fehlgeschlagen: {e}")
        return

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    reflexion_m = re.search(r"REFLEXION:\s*(.+?)(?=\nERLEDIGT:|\Z)", antwort, re.DOTALL)
    reflexion = reflexion_m.group(1).strip() if reflexion_m else antwort.strip()
    (ordner / f"{ts}_widmung.md").write_text(
        "\n".join(["---", "typ: widmung", f"container: {name}", f"erstellt_am: {ts}", "---", "", reflexion]),
        encoding="utf-8",
    )

    erledigt_m = re.search(r"ERLEDIGT:\s*(.+)", antwort)
    if erledigt_m and "keine" not in erledigt_m.group(1).lower():
        for dateiname in re.findall(r"[\w\-.]+\.md", erledigt_m.group(1)):
            ziel = ordner / dateiname
            if ziel.exists():
                markiere_erledigt(ziel)

    ziele_m = re.search(r"NEUE_ZIELE:\s*(.+)", antwort)
    if ziele_m and "keine" not in ziele_m.group(1).lower():
        ziele = [z.strip() for z in ziele_m.group(1).split(";") if z.strip()]
        if ziele:
            (ordner / f"{ts}_ziel.md").write_text(
                "\n".join(["---", "typ: ziel", f"container: {name}", f"erstellt_am: {ts}", "status: offen", "---", ""]
                          + [f"- {z}" for z in ziele]),
                encoding="utf-8",
            )

    if meta_datei.exists():
        text = meta_datei.read_text(encoding="utf-8", errors="replace")
        meta_datei.write_text(re.sub(r"letzte_widmung:\s*\S+", f"letzte_widmung: {ts}", text), encoding="utf-8")

    log.info(f"[{wesen}] Widmung an Container '{name}' abgeschlossen")
    teile_strategie_optional(wesen, name, kontext=f"Reflexion aus dem Pflegeritual:\n{reflexion}")
