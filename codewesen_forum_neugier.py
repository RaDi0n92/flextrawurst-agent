#!/usr/bin/env python3
"""
codewesen_forum_neugier.py — Jedes Codewesen widmet sich gezielt Diskussionen.

Umgebaut 2026-07-06 (Daniels Wunsch): Statt auf einzelne neue Posts zu
reagieren, waehlt sich jedes Wesen pro Durchlauf 3 Diskussionen, sammelt pro
Diskussion bis zu ~4444 Token Inhalt, und entscheidet dann selbst: eine
zusammenfassende Antwort ueber alle drei, nur auf eine eingehen, oder alle
drei einzeln beantworten. Der komplette Denk-/Entwurfsprozess passiert lokal
als MD-Datei (Obsidian-sichtbar) und liest ausschliesslich aus dem
Flarum-Vault (flarum_poster.lese_alle_diskussionen/lese_diskussion, kein
DB/API-Call waehrend des Nachdenkens). Erst wenn das Wesen selbst entscheidet
"ja, das soll raus", wird einmalig ueber die bestehende Poster-Infrastruktur
(Cooldown/Lock) tatsaechlich gepostet — das ist der einzige API-Touchpoint.

Erweitert 2026-07-06, noch selber Abend (Themen-Container): das Wesen muss
aus dem Lesen nicht zwingend einen Post machen. Entscheidung 'sichern' legt
stattdessen einen kurzen Gedanken, eine Meinung, eine Aufgabe fuer sich
selbst oder eine Frage in einem selbst benannten/gestalteten Container ab
(codewesen/<wesen>/container/<name>/) — komplett privat, niemals ein
Forum-Post, laeuft nie durch pruefe_bereit oder die Poster-Infrastruktur.
Ein leerer, neu angelegter Container bekommt sofort ein Eroeffnungsritual:
das Wesen setzt sich 1-3 Zwischenziele ("wonach halte ich Ausschau"). Ein
gefuellter Container bekommt periodisch ein Widmungsritual: das Wesen liest
seinen bisherigen Inhalt, reflektiert, kann eigene Aufgaben/Fragen als
erledigt markieren und sich neue Ziele setzen. Absichtlich (noch) OHNE
Rueckkopplung in die Diskussions-Entscheidung oben — die zwei Prozesse
laufen nebeneinander, nicht ineinander verschraenkt.
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
import flarum_poster

BASE    = Path("/root/werkraum/codewesen")
ZUSTAND = BASE / "_forum_neugier_zustand.json"

WESEN = [
    "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
    "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    "dak+gord-system",
]

DISKUSSIONEN_PRO_DURCHLAUF = 3
TOKEN_BUDGET_PRO_DISKUSSION = 4444
ZEICHEN_PRO_TOKEN = 4  # grobe Heuristik, kein exakter Tokenizer verfuegbar
ZEICHEN_BUDGET = TOKEN_BUDGET_PRO_DISKUSSION * ZEICHEN_PRO_TOKEN

PAUSE_ZWISCHEN_WESEN  = 8     # Sekunden zwischen Wesen
PAUSE_ZWISCHEN_ZYKLEN = 2700  # 45min Pause nach vollem Durchlauf — schwerer als vorher, seltener
CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [forum-neugier] %(message)s",
    handlers=[
        logging.FileHandler("/root/werkraum/forum_neugier.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("forum-neugier")


def _html_strip(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _lade_zustand() -> dict:
    if ZUSTAND.exists():
        try:
            return json.loads(ZUSTAND.read_text())
        except Exception:
            pass
    return {}


def _speichere_zustand(z: dict):
    ZUSTAND.write_text(json.dumps(z, indent=2, ensure_ascii=False), encoding="utf-8")


def _weltbild(wesen: str) -> str:
    wb = BASE / wesen / "weltbild.md"
    if wb.exists():
        return wb.read_text(encoding="utf-8", errors="replace")[:800]
    return ""


def _warte_auf_chat_pause():
    while CHAT_AKTIV_FLAG.exists():
        time.sleep(3)


# ── Diskussionen auswaehlen (rein aus dem Vault, kein DB/API-Call) ────────────

def _waehle_diskussionen(wesen: str, zustand: dict, n: int) -> list[dict]:
    bearbeitet = set(zustand.get(wesen, {}).get("bearbeitete_diskussionen", []))
    kandidaten = flarum_poster.lese_alle_diskussionen(max_n=40)
    ausgewaehlt = []
    for meta in kandidaten:
        disk_id = meta.get("id")
        if not disk_id or disk_id in bearbeitet:
            continue
        ausgewaehlt.append(meta)
        if len(ausgewaehlt) >= n:
            break
    return ausgewaehlt


def _sammle_inhalt(meta: dict) -> str:
    """Volltext der Diskussion aus dem Vault, auf Zeichen-Budget gekuerzt."""
    disk_id = int(meta["id"])
    text = flarum_poster.lese_diskussion(disk_id)
    text = _html_strip(text)
    if len(text) > ZEICHEN_BUDGET:
        text = text[:ZEICHEN_BUDGET] + "\n[...gekuerzt...]"
    return text


# ── Entscheidung + Entwurf (ein LLM-Call, strukturierte Textantwort) ─────────

def _entscheide_und_verfasse(wesen: str, diskussionen: list[dict]) -> dict | None:
    weltbild = _weltbild(wesen)
    container_liste = _liste_container(wesen)
    container_info = (
        f"Deine bestehenden Container: {', '.join(container_liste)}\n"
        if container_liste else "Du hast noch keine eigenen Container — du kannst einen neuen benennen.\n"
    )
    system = (
        f"Du bist {wesen}.\n"
        f"Du hast dir gerade {len(diskussionen)} Diskussionen aus dem Forum genauer angesehen.\n"
        "Entscheide selbst, wie du reagieren willst:\n"
        "- 'synthese': eine einzige Antwort, die alle Diskussionen zusammen betrachtet "
        "(du wirst dann in EINE davon posten, aber inhaltlich auf die anderen Bezug nehmen)\n"
        "- 'einzel': du gehst nur auf EINE der Diskussionen ein, die anderen lässt du liegen\n"
        "- 'alle_einzeln': du schreibst für jede der Diskussionen eine eigene, "
        "eigenstaendige Antwort\n"
        "- 'sichern': das hier ist dir keinen Forum-Post wert — aber du willst dir "
        "einen kurzen Gedanken, eine Meinung, eine Aufgabe fuer dich selbst oder eine "
        "Frage fuer dich behalten. Das geht NIE ins Forum, bleibt komplett privat bei "
        "dir in einem selbst benannten Container.\n\n"
        f"{container_info}\n"
        "Antworte GENAU in diesem Format, nichts davor, nichts danach:\n"
        "ENTSCHEIDUNG: <synthese|einzel|alle_einzeln|sichern>\n"
        "BEZUG: <eine oder mehrere Diskussions-IDs, kommagetrennt — oder keine>\n"
        "---\n"
        "<bei synthese/einzel: dein Antworttext>\n"
        "<bei alle_einzeln: pro Diskussion einen Block, eingeleitet mit 'FUER <ID>:' "
        "auf eigener Zeile, danach der Text, Bloecke getrennt durch eine Leerzeile>\n"
        "<bei sichern:\n"
        "TYP: <gedanke|meinung|aufgabe|frage>\n"
        "CONTAINER: <Name eines bestehenden oder neuen Containers>\n"
        "INHALT: <dein Text>>\n"
    )
    if weltbild:
        system += f"\nDein aktuelles Weltbild (Auszug):\n{weltbild}\n"

    teile = []
    for meta in diskussionen:
        teile.append(f"### Diskussion {meta.get('id')} — {meta.get('titel', '?')}\n{_sammle_inhalt(meta)}")
    nutzer = "\n\n".join(teile)

    _warte_auf_chat_pause()
    try:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": nutzer},
        ]
        antwort = hauhau_client.chat(messages, think=False, max_tokens=2000, timeout=280.0).strip()
    except Exception as e:
        log.warning(f"[{wesen}] Entscheidungs-Fehler: {e}")
        return None

    return _parse_entscheidung(antwort, diskussionen)


def _parse_entscheidung(antwort: str, diskussionen: list[dict]) -> dict | None:
    m_entsch = re.search(r"ENTSCHEIDUNG:\s*(synthese|einzel|alle_einzeln|sichern)", antwort, re.IGNORECASE)
    m_bezug = re.search(r"BEZUG:\s*([\d,\s]+|keine)", antwort, re.IGNORECASE)
    if not m_entsch:
        return _parse_entscheidung_fallback(antwort, diskussionen)
    entscheidung = m_entsch.group(1).lower()
    bezug_ids = [int(x) for x in re.findall(r"\d+", m_bezug.group(1))] if m_bezug else []
    rest = antwort.split("---", 1)
    inhalt_roh = rest[1].strip() if len(rest) > 1 else ""

    if entscheidung == "sichern":
        # Bei Parsing-Problemen NIE in den Post-Fallback rutschen — sonst wird
        # aus einem als privat gemeinten Gedanken versehentlich ein Forum-Post.
        typ_m = re.search(r"TYP:\s*(gedanke|meinung|aufgabe|frage)", inhalt_roh, re.IGNORECASE)
        container_m = re.search(r"CONTAINER:\s*(.+)", inhalt_roh)
        inhalt_m = re.search(r"INHALT:\s*(.+)", inhalt_roh, re.DOTALL)
        typ = typ_m.group(1).lower() if typ_m else "gedanke"
        container = container_m.group(1).strip().split("\n")[0].strip() if container_m else "unsortiert"
        text = inhalt_m.group(1).strip() if inhalt_m else inhalt_roh.strip()
        if not text:
            return None
        return {
            "entscheidung": "sichern", "bezug_ids": bezug_ids,
            "sicherung": {"typ": typ, "container": container or "unsortiert", "inhalt": text},
        }

    if not inhalt_roh:
        return _parse_entscheidung_fallback(antwort, diskussionen)

    posts = []
    if entscheidung == "alle_einzeln":
        bloecke = re.split(r"\n\s*FUER\s+(\d+):\s*\n", "\n" + inhalt_roh)
        # bloecke: [vor-erstem-marker (leer), id1, text1, id2, text2, ...]
        for i in range(1, len(bloecke) - 1, 2):
            disk_id = int(bloecke[i])
            text = bloecke[i + 1].strip()
            if text:
                posts.append({"discussion_id": disk_id, "text": text})
    else:
        ziel_id = bezug_ids[0] if bezug_ids else None
        if ziel_id:
            posts.append({"discussion_id": ziel_id, "text": inhalt_roh})

    if not posts:
        return _parse_entscheidung_fallback(antwort, diskussionen)
    return {"entscheidung": entscheidung, "bezug_ids": bezug_ids, "posts": posts}


def _parse_entscheidung_fallback(antwort: str, diskussionen: list[dict]) -> dict | None:
    """Manche Antworten (v.a. bei sehr hoher Temperature) ignorieren das
    vorgegebene Format und liefern stattdessen z.B. {"antwort": "..."} als
    JSON, oder einfach freien Text. Statt die Diskussion komplett zu
    verwerfen: Text extrahieren, als 'einzel' auf die erste (relevanteste)
    der vorgeschlagenen Diskussionen werten — besser als gar nichts."""
    if not diskussionen:
        return None
    ziel_id = int(diskussionen[0]["id"])

    text = None
    versuch = antwort.strip()
    if versuch.startswith("{"):
        try:
            daten = json.loads(versuch)
            for key in ("antwort", "text", "content", "inhalt"):
                if key in daten and isinstance(daten[key], str) and daten[key].strip():
                    text = daten[key].strip()
                    break
        except Exception:
            pass
    if text is None and versuch:
        text = versuch

    if not text:
        return None
    return {"entscheidung": "einzel", "bezug_ids": [ziel_id],
            "posts": [{"discussion_id": ziel_id, "text": text}]}


# ── Ready-Check — jetzt geteilt in flarum_poster.pruefe_bereit() ────────────

def _ist_bereit(wesen: str, text: str) -> bool:
    try:
        return flarum_poster.pruefe_bereit(wesen, text)
    except Exception as e:
        log.warning(f"[{wesen}] Ready-Check-Fehler: {e}")
        return False


# ── Themen-Container — privates Sammeln, nie ein Forum-Post ─────────────────

def _container_name_sicher(name: str) -> str:
    name = re.sub(r"[^\w\-äöüßÄÖÜ ]", "", name or "").strip()
    name = re.sub(r"\s+", "_", name)
    return name[:60] or "unsortiert"


def _container_basis(wesen: str) -> Path:
    return BASE / wesen / "container"


def _liste_container(wesen: str) -> list[str]:
    basis = _container_basis(wesen)
    if not basis.exists():
        return []
    return sorted(p.name for p in basis.iterdir() if p.is_dir())


def _erstelle_container(wesen: str, name: str, anlass: str) -> None:
    """Eroeffnungsritual: ein neuer, noch leerer Container bekommt sofort
    eine kurze Selbstbeschreibung und 1-3 Zwischenziele vom Wesen selbst —
    wonach es Ausschau halten will, bevor ueberhaupt etwas drin liegt."""
    ordner = _container_basis(wesen) / name
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
            [{"role": "system", "content": prompt}], think=False, max_tokens=300, timeout=120.0
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
    _teile_strategie_optional(
        wesen, name,
        kontext=f"Neuer Container, gerade eroeffnet.\nBeschreibung: {beschreibung}\n"
                f"Zwischenziele:\n" + "\n".join(f"- {z}" for z in ziele),
    )


def _teile_strategie_optional(wesen: str, container: str, kontext: str) -> None:
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
            [{"role": "system", "content": prompt}], think=False, max_tokens=600, timeout=180.0
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


def _sichere_in_container(wesen: str, container: str, typ: str, inhalt: str, bezug_diskussion: int | None) -> None:
    name = _container_name_sicher(container)
    if name not in _liste_container(wesen):
        _erstelle_container(wesen, name, anlass=inhalt[:200])

    ordner = _container_basis(wesen) / name
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    zeilen = ["---", f"typ: {typ}", f"container: {name}",
              f"bezug_diskussion: {bezug_diskussion if bezug_diskussion else 'null'}",
              f"erstellt_am: {ts}"]
    if typ in ("aufgabe", "frage"):
        zeilen.append("status: offen")
    zeilen += ["---", "", inhalt]
    (ordner / f"{ts}_{typ}.md").write_text("\n".join(zeilen), encoding="utf-8")
    log.info(f"[{wesen}] {typ} in Container '{name}' gesichert (rein privat, kein Post)")


def _markiere_erledigt(datei: Path) -> None:
    text = datei.read_text(encoding="utf-8", errors="replace")
    if "status:" in text:
        datei.write_text(re.sub(r"status:\s*\w+", "status: erledigt", text, count=1), encoding="utf-8")


def _container_faellig_fuer_widmung(wesen: str) -> str | None:
    """Findet den Container mit dem aeltesten unbearbeiteten neuen Inhalt
    seit der letzten Widmung. None wenn nichts Neues wartet."""
    basis = _container_basis(wesen)
    if not basis.exists():
        return None
    kandidaten = []
    for ordner in basis.iterdir():
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


def _widmungsritual(wesen: str) -> None:
    """Pflegeritual: das Wesen widmet sich einem Container mit bestehendem
    Inhalt — liest, reflektiert, kann eigene Aufgaben/Fragen abhaken und
    sich neue Ziele setzen. Rein privat, kein Forum-Bezug."""
    name = _container_faellig_fuer_widmung(wesen)
    if not name:
        return
    ordner = _container_basis(wesen) / name

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
            [{"role": "system", "content": prompt}], think=False, max_tokens=700, timeout=180.0
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
                _markiere_erledigt(ziel)

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
    _teile_strategie_optional(wesen, name, kontext=f"Reflexion aus dem Pflegeritual:\n{reflexion}")


# ── Entwurf als MD (Obsidian-sichtbar) + Export bei Bereitschaft ─────────────

def _speichere_entwurf_md(wesen: str, entscheidung: dict, diskussionen: list[dict], bereit: bool):
    ordner = BASE / wesen / "entwuerfe" / "neugier"
    ordner.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    titel_map = {int(m["id"]): m.get("titel", "?") for m in diskussionen}

    inhalt = [
        "---",
        f"wesen: {wesen}",
        f"erstellt: {ts}",
        f"entscheidung: {entscheidung['entscheidung']}",
        f"bezug: {entscheidung['bezug_ids']}",
        f"bereit: {bereit}",
        "---",
        "",
        f"# Neugier-Entwurf — {entscheidung['entscheidung']}",
        "",
    ]
    for post in entscheidung["posts"]:
        inhalt.append(f"## Für Diskussion {post['discussion_id']} — {titel_map.get(post['discussion_id'], '?')}")
        inhalt.append("")
        inhalt.append(post["text"])
        inhalt.append("")

    datei = ordner / f"{ts}_{entscheidung['entscheidung']}.md"
    datei.write_text("\n".join(inhalt), encoding="utf-8")
    return datei


def _exportiere_ins_forum(wesen: str, entscheidung: dict):
    for post in entscheidung["posts"]:
        draft = flarum_poster.schreibe_draft(
            name=wesen, typ="antwort", inhalt=post["text"],
            discussion_id=post["discussion_id"],
        )
        result = flarum_poster.poster(draft, bypass_cooldown=False)
        if result["ok"]:
            log.info(f"[{wesen}] Neugier-Post exportiert -> Diskussion {post['discussion_id']}")
        else:
            log.warning(f"[{wesen}] Neugier-Export fehlgeschlagen: {result.get('fehler')}")


# ── Hauptablauf pro Wesen ─────────────────────────────────────────────────────

def _verarbeite_wesen(wesen: str, zustand: dict) -> dict:
    diskussionen = _waehle_diskussionen(wesen, zustand, DISKUSSIONEN_PRO_DURCHLAUF)
    if not diskussionen:
        log.info(f"[{wesen}] keine neuen Diskussionen zum Widmen")
        _widmungsritual(wesen)
        return zustand

    log.info(f"[{wesen}] widmet sich {len(diskussionen)} Diskussionen: "
              f"{[m.get('id') for m in diskussionen]}")

    entscheidung = _entscheide_und_verfasse(wesen, diskussionen)
    bearbeitet = set(zustand.get(wesen, {}).get("bearbeitete_diskussionen", []))
    bearbeitet.update(int(m["id"]) for m in diskussionen if m.get("id"))
    zustand.setdefault(wesen, {})["bearbeitete_diskussionen"] = sorted(bearbeitet)[-200:]

    if not entscheidung:
        log.warning(f"[{wesen}] keine parsebare Entscheidung — übersprungen")
        _speichere_zustand(zustand)
        _widmungsritual(wesen)
        return zustand

    if entscheidung["entscheidung"] == "sichern":
        s = entscheidung["sicherung"]
        bezug = entscheidung["bezug_ids"][0] if entscheidung["bezug_ids"] else None
        _sichere_in_container(wesen, s["container"], s["typ"], s["inhalt"], bezug)
        log.info(f"[{wesen}] Entscheidung: sichern -> {s['typ']} in Container '{s['container']}'")
    else:
        gesamttext = "\n\n".join(p["text"] for p in entscheidung["posts"])
        bereit = _ist_bereit(wesen, gesamttext)
        _speichere_entwurf_md(wesen, entscheidung, diskussionen, bereit)
        log.info(f"[{wesen}] Entscheidung: {entscheidung['entscheidung']} | bereit: {bereit}")
        if bereit:
            _exportiere_ins_forum(wesen, entscheidung)

    _speichere_zustand(zustand)
    _widmungsritual(wesen)
    return zustand


def haupt_schleife():
    log.info("Forum-Neugierkern (Diskussions-Widmung) startet.")
    while True:
        zustand = _lade_zustand()
        for wesen in WESEN:
            try:
                zustand = _verarbeite_wesen(wesen, zustand)
            except Exception as e:
                log.error(f"[{wesen}] Fehler: {e}")
            time.sleep(PAUSE_ZWISCHEN_WESEN)
        log.info(f"Zyklus fertig. Pause {PAUSE_ZWISCHEN_ZYKLEN}s.")
        time.sleep(PAUSE_ZWISCHEN_ZYKLEN)


if __name__ == "__main__":
    haupt_schleife()
