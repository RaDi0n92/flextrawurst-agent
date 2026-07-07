#!/usr/bin/env python3
"""
GENI Muster-Scanner — erkennt Muster, Meta-Muster, blinde Flecken.
Läuft alle 2h via systemd timer.

Was es tut:
  1. Scannt Knoten der letzten 48h → dominante Tags + Themen
  2. Findet Ko-Okkurrenz: welche Themen immer zusammen auftreten
  3. Findet Blinde Flecken: tiefe≥2 Knoten die lange nicht resoniert wurden
  4. Schreibt Muster-Knoten (wenn signifikantes Muster da)
  5. Scannt Muster-Knoten der letzten 4 Wochen → Meta-Muster
  6. GENI liest den neuesten Muster-Knoten im System-Prompt
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

GENI_ROOT   = Path("/root/werkraum/geni")
KNOTEN_DIR  = GENI_ROOT / "gedaechtnis" / "knoten"
KANTEN_DIR  = GENI_ROOT / "gedaechtnis" / "kanten"
MUSTER_DIR  = GENI_ROOT / "spiegel" / "muster"

_id_lock = threading.Lock()

STOPWORDS = frozenset([
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "einem",
    "eines", "ist", "sind", "war", "wird", "hat", "haben", "hatte", "habe",
    "und", "oder", "nicht", "auch", "noch", "dann", "aber", "wenn", "wie",
    "was", "wer", "wessen", "wo", "wohin", "in", "an", "auf", "für", "von",
    "mit", "zu", "aus", "bei", "nach", "seit", "vor", "über", "unter", "als",
    "am", "im", "ins", "ans", "zum", "zur", "ich", "du", "er", "sie", "es",
    "wir", "ihr", "mir", "dir", "ihm", "uns", "euch", "ihnen", "mich", "dich",
    "sich", "sehr", "mehr", "nur", "ja", "nein", "alle", "alles", "kann",
    "will", "soll", "muss", "darf", "wurden", "wurde", "werden", "wurden",
    "geändert", "erstellt", "gelöscht", "datei", "file", "pfad", "path",
    "neue", "neuer", "neues", "neuen", "dieser", "diese", "dieses", "diesen",
    "beim", "diesem", "welche", "welcher", "welchen", "welches", "durch",
    "keine", "keiner", "keinem", "keines", "ohne", "damit", "daran", "darin",
    "schon", "hier", "dort", "jetzt", "dann", "immer", "noch", "schreiben",
    "lesen", "sehen", "gehen", "kommen", "haben", "sein", "werden", "bleiben",
])

# Tags die für Muster-Analyse irrelevant sind
TAG_FILTER = frozenset([
    "muster", "auto", "dialog", "eingabe", "antwort", "datei", "geändert",
    "erstellt", "gelöscht", "bild", "upload", "sinn", "sinn_visuell", "visuell",
    "direktchat", "gespräch", "web",
])


# ── Lade-Funktionen ───────────────────────────────────────────────────────────

# Frueher stat()'te lade_alle_knoten() JEDE Datei im Verzeichnis (Kommentar ging
# noch von "~10M Dateien" aus -- inzwischen 18.9 Mio), nur um die paar Tausend der
# letzten 30 Tage zu finden. Genau das war der Grund fuer den 5h-Haenger vom
# 2026-07-07 (Prozess steckte im 'D'-Status/disk-sleep exakt in dieser Funktion
# fest, System swappte massiv). Eine Knoten-Datei wird nach dem Schreiben nie
# wieder veraendert -- ist ihr mtime einmal bekannt, muss sie nie wieder gestat't
# werden. _SCAN_CACHE_FILE merkt sich das dauerhaft: "ausgeschlossen" fuer Dateien
# die sicher aelter als das 30-Tage-Fenster sind (nur die ID, kein Inhalt -- haelt
# die Cache-Datei klein), "aktuell" fuer die wenigen, die gerade im Fenster liegen.
# Jeder folgende Lauf muss dann nur noch Dateien stat'en, die seit dem letzten Lauf
# neu dazugekommen sind, nicht mehr alle.
_SCAN_CACHE_FILE = MUSTER_DIR / "_scan_cache.json"


def _lade_scan_cache() -> dict:
    try:
        daten = json.loads(_SCAN_CACHE_FILE.read_text())
        return {
            "ausgeschlossen": set(daten.get("ausgeschlossen", [])),
            "aktuell": daten.get("aktuell", {}),
        }
    except Exception:
        return {"ausgeschlossen": set(), "aktuell": {}}


def _speichere_scan_cache(cache: dict) -> None:
    try:
        MUSTER_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _SCAN_CACHE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps({
            "ausgeschlossen": sorted(cache["ausgeschlossen"]),
            "aktuell": cache["aktuell"],
        }), encoding="utf-8")
        tmp.replace(_SCAN_CACHE_FILE)
    except Exception:
        pass


def lade_alle_knoten() -> list[dict]:
    # Lädt nur Knoten die in den letzten 30 Tagen geändert wurden.
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
    cache = _lade_scan_cache()
    ausgeschlossen = cache["ausgeschlossen"]
    aktuell = cache["aktuell"]

    # Aus dem Fenster gefallene Eintraege endgueltig ausschliessen -- mtime
    # aendert sich nie, der Ausschluss gilt damit ab jetzt fuer immer.
    veraendert = False
    for kid, eintrag in list(aktuell.items()):
        if eintrag["mtime"] < cutoff:
            del aktuell[kid]
            ausgeschlossen.add(kid)
            veraendert = True  # sonst wird die Verkleinerung von "aktuell" nie gespeichert

    knoten = []
    try:
        with os.scandir(KNOTEN_DIR) as it:
            for entry in it:
                if not entry.name.endswith(".json") or entry.name == "schema.json":
                    continue
                kid = entry.name[:-5]
                if kid in ausgeschlossen:
                    continue
                bekannt = aktuell.get(kid)
                if bekannt is not None:
                    knoten.append(bekannt["knoten"])
                    continue
                # Neue oder noch nie gesehene Datei -- einmalig stat'en.
                try:
                    mtime = entry.stat().st_mtime
                except Exception:
                    continue
                veraendert = True
                if mtime < cutoff:
                    ausgeschlossen.add(kid)
                    continue
                try:
                    inhalt = json.loads(Path(entry.path).read_text())
                except Exception:
                    continue  # evtl. noch im Schreibvorgang -- naechstes Mal erneut versuchen
                aktuell[kid] = {"mtime": mtime, "knoten": inhalt}
                knoten.append(inhalt)
    except Exception:
        pass

    if veraendert:
        _speichere_scan_cache({"ausgeschlossen": ausgeschlossen, "aktuell": aktuell})
    return knoten


def signifikante_worte(text: str) -> list[str]:
    return [
        w.lower() for w in re.findall(r'\b\w{4,}\b', text)
        if w.lower() not in STOPWORDS and not w.isdigit()
    ]


# ── Schreib-Funktionen ────────────────────────────────────────────────────────

def schreibe_muster_knoten(inhalt: str, tags: list[str]) -> str:
    # War frueher ein KNOTEN_DIR.glob("*.json") + max(int(...)) ueber alle Dateien --
    # bei 18.9 Mio Dateien einer der beiden Gruende fuer den 5h-Haenger vom 2026-07-07
    # (der andere war lade_alle_knoten()). gedaechtnis_ops.naechste_id() haelt denselben
    # Counter bereits O(1) via _counter.json (wird von hoerer.py/dialog.py/aktion.py
    # aktiv gepflegt) -- muster.py nutzte das bisher nur fuer knoten_max_id(), nicht
    # fuer die eigene ID-Vergabe.
    from gedaechtnis_ops import naechste_id as _naechste_id
    with _id_lock:
        naechste = _naechste_id(KNOTEN_DIR)
        k = {
            "id": naechste,
            "typ": "muster",
            "inhalt": inhalt,
            "zeitstempel": datetime.now(timezone.utc).isoformat(),
            "quelle": "geni_muster",
            "zugriffsschicht": 1,
            "verbindungen": [],
            "gewicht": 1.0,
            "tiefe": 1,
            "verblasst": False,
            "tags": ["muster", "auto"] + [t for t in tags if t not in TAG_FILTER],
        }
        (KNOTEN_DIR / f"{naechste}.json").write_text(
            json.dumps(k, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return naechste


# ── Scan-Funktionen ───────────────────────────────────────────────────────────

def scan_48h(alle: list[dict]) -> dict | None:
    """Analysiert Knoten der letzten 48h auf dominante Themen."""
    jetzt = datetime.now(timezone.utc)
    grenze = (jetzt - timedelta(hours=48)).isoformat()

    recent = [
        k for k in alle
        if k.get("zeitstempel", "") >= grenze and k.get("typ") != "muster"
    ]

    if len(recent) < 8:
        return None

    tag_counter: Counter = Counter()
    for k in recent:
        for t in k.get("tags", []):
            if t not in TAG_FILTER:
                tag_counter[t] += 1

    wort_counter: Counter = Counter()
    for k in recent:
        for w in signifikante_worte(k.get("inhalt", "")):
            wort_counter[w] += 1

    # Ko-Okkurrenz: welche Tags erscheinen im selben Knoten
    top_tags = {t for t, _ in tag_counter.most_common(12)}
    ko: dict[str, Counter] = defaultdict(Counter)
    for k in recent:
        ktags = {t for t in k.get("tags", []) if t in top_tags}
        for t1 in ktags:
            for t2 in ktags:
                if t2 != t1:
                    ko[t1][t2] += 1

    quellen: Counter = Counter(k.get("quelle", "?") for k in recent)

    return {
        "knoten_anzahl": len(recent),
        "top_tags": tag_counter.most_common(8),
        "top_worte": wort_counter.most_common(12),
        "ko": {t: v.most_common(3) for t, v in ko.items() if sum(v.values()) >= 2},
        "quellen": dict(quellen),
    }


def scan_blinde_flecken(alle: list[dict]) -> list[dict]:
    """Findet tiefe≥2 Knoten die seit >7 Tagen keine Resonanz hatten."""
    grenze = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    # Letzte Resonanz-Kante pro Knoten
    letzte_resonanz: dict[str, str] = {}
    for f in KANTEN_DIR.glob("*.json"):
        if f.stem == "schema":
            continue
        try:
            kante = json.loads(f.read_text())
            if kante.get("typ") == "resonanz":
                nach = kante.get("nach")
                ts = kante.get("zeitstempel", "")
                if nach and ts:
                    if nach not in letzte_resonanz or ts > letzte_resonanz[nach]:
                        letzte_resonanz[nach] = ts
        except Exception:
            pass

    blinde = []
    for k in alle:
        if k.get("tiefe", 0) >= 2 and k.get("typ") not in ("muster",):
            kid = k["id"]
            letzte = letzte_resonanz.get(kid, k.get("zeitstempel", ""))
            if letzte < grenze:
                blinde.append({
                    "id": kid,
                    "inhalt": k.get("inhalt", "")[:80],
                    "tiefe": k.get("tiefe", 0),
                    "letzte_resonanz": letzte[:16],
                    "tags": k.get("tags", []),
                })

    blinde.sort(key=lambda x: x["tiefe"], reverse=True)
    return blinde[:6]


def scan_meta_muster(alle: list[dict]) -> list[str]:
    """
    Schaut auf alle Muster-Knoten der letzten 4 Wochen.
    Wörter die in ≥3 Muster-Knoten vorkommen = Meta-Muster.
    """
    grenze = (datetime.now(timezone.utc) - timedelta(days=28)).isoformat()

    muster_knoten = [
        k for k in alle
        if k.get("typ") == "muster" and k.get("zeitstempel", "") >= grenze
    ]

    if len(muster_knoten) < 3:
        return []

    wort_counter: Counter = Counter()
    for k in muster_knoten:
        worte = set(signifikante_worte(k.get("inhalt", "")))
        for w in worte:
            wort_counter[w] += 1

    # Nur Wörter die in ≥3 verschiedenen Muster-Knoten vorkommen
    return [w for w, c in wort_counter.most_common(15) if c >= 3][:8]


def scan_zeitrhythmus(alle: list[dict]) -> str | None:
    """Erkennt temporale Muster: zu welchen Tageszeiten ist Daniel aktiv?"""
    daniel_knoten = [
        k for k in alle
        if k.get("quelle") == "daniel" and k.get("zeitstempel")
    ]
    if len(daniel_knoten) < 10:
        return None

    stunden: Counter = Counter()
    for k in daniel_knoten:
        try:
            stunde = int(k["zeitstempel"][11:13])
            stunden[stunde] += 1
        except Exception:
            pass

    if not stunden:
        return None

    peak = stunden.most_common(1)[0][0]
    if peak < 6:
        tageszeit = "nachts"
    elif peak < 12:
        tageszeit = "morgens"
    elif peak < 17:
        tageszeit = "nachmittags"
    elif peak < 21:
        tageszeit = "abends"
    else:
        tageszeit = "spätabends"

    return f"Daniel ist am häufigsten {tageszeit} aktiv (Peak: {peak:02d}:00 Uhr)"


# ── Formatierung ──────────────────────────────────────────────────────────────

def formattiere_muster_text(
    analyse: dict | None,
    blinde: list[dict],
    meta: list[str],
    rhythmus: str | None,
) -> str:
    teile = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    teile.append(f"Muster-Scan {ts}")

    if analyse:
        n = analyse["knoten_anzahl"]
        top_t = [t for t, c in analyse["top_tags"][:5] if c >= 2]
        top_w = [w for w, c in analyse["top_worte"][:6] if c >= 2]

        if top_t:
            teile.append(f"48h / {n} Knoten — Dominierende Tags: {', '.join(top_t)}")
        if top_w:
            teile.append(f"Häufige Themen: {', '.join(top_w)}")

        # Stärkste Ko-Okkurrenz
        konn = []
        for tag, pairs in analyse["ko"].items():
            if pairs and pairs[0][1] >= 3:
                konn.append(f"{tag}↔{pairs[0][0]}")
        if konn:
            teile.append(f"Verbundene Themen: {', '.join(konn[:3])}")

    if rhythmus:
        teile.append(rhythmus)

    if blinde:
        texte = [f"[{b['id']},{b['tiefe']}t] {b['inhalt'][:40]}" for b in blinde[:3]]
        teile.append(f"Blinde Flecken (still seit >7 Tagen): {' | '.join(texte)}")

    if meta:
        teile.append(f"Meta-Muster (4 Wochen, wiederkehrend): {', '.join(meta[:6])}")

    return " — ".join(teile)


def formattiere_markdown(
    analyse: dict | None,
    blinde: list[dict],
    meta: list[str],
    rhythmus: str | None,
    kid: str,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"---\ntyp: muster\nzeitstempel: {ts}\nknoten_id: {kid}\n---\n\n"
    md += f"# Muster-Scan — {ts}\n\n"

    if analyse:
        md += f"## Aktivität (48h)\n"
        md += f"**Knoten**: {analyse['knoten_anzahl']}\n"
        md += f"**Quellen**: {', '.join(f'{q}({n})' for q,n in sorted(analyse['quellen'].items(), key=lambda x:-x[1]))}\n\n"
        md += f"**Top-Tags**: {', '.join(f'{t}({c})' for t,c in analyse['top_tags'][:8])}\n\n"
        md += f"**Häufige Wörter**: {', '.join(f'{w}({c})' for w,c in analyse['top_worte'][:12])}\n\n"
        if analyse["ko"]:
            md += "**Ko-Okkurrenz** (Themen die zusammen auftreten):\n"
            for tag, pairs in list(analyse["ko"].items())[:5]:
                if pairs:
                    md += f"- {tag} → {', '.join(f'{p}({c})' for p,c in pairs[:3])}\n"
            md += "\n"

    if rhythmus:
        md += f"## Zeitrhythmus\n{rhythmus}\n\n"

    if blinde:
        md += "## Blinde Flecken\n"
        md += "*tiefe≥2 Knoten die seit >7 Tagen keine Resonanz hatten:*\n\n"
        for b in blinde:
            md += f"- **[{b['id']}]** tiefe={b['tiefe']} | {b['inhalt']}\n"
            md += f"  letzte Resonanz: {b['letzte_resonanz']}\n"
        md += "\n"

    if meta:
        md += f"## Meta-Muster (4 Wochen)\n"
        md += f"Wiederkehrend: **{', '.join(meta)}**\n\n"

    return md


# ── Hauptfunktion ─────────────────────────────────────────────────────────────

def muster_scan_ausfuehren(stumm: bool = False) -> str | None:
    MUSTER_DIR.mkdir(parents=True, exist_ok=True)

    alle = lade_alle_knoten()

    analyse = scan_48h(alle)
    blinde = scan_blinde_flecken(alle)
    meta = scan_meta_muster(alle)
    rhythmus = scan_zeitrhythmus(alle)

    # Abbrechen wenn nichts Signifikantes
    hat_inhalt = (
        (analyse and (analyse["top_tags"] or analyse["top_worte"])) or
        blinde or
        meta
    )
    if not hat_inhalt:
        if not stumm:
            print("[muster] zu wenig Material — kein Knoten geschrieben")
        return None

    inhalt = formattiere_muster_text(analyse, blinde, meta, rhythmus)
    tags = [t for t, _ in (analyse["top_tags"][:3] if analyse else [])]
    kid = schreibe_muster_knoten(inhalt, tags)

    # Markdown-Datei für Obsidian
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    md = formattiere_markdown(analyse, blinde, meta, rhythmus, kid)
    (MUSTER_DIR / f"{ts}.md").write_text(md, encoding="utf-8")

    if not stumm:
        print(f"[muster] Knoten {kid} geschrieben")
        print(f"[muster] {inhalt[:200]}")

    return kid


_muster_cache: tuple[str, str] | None = None  # (zeitstempel, inhalt)
_muster_cache_lock = threading.Lock()


def _muster_max_id() -> int:
    """Liest die höchste Knoten-ID — ohne alle Dateien zu laden."""
    from gedaechtnis_ops import knoten_max_id as _kid
    return _kid()


def neuester_muster_text() -> str:
    """Gibt den Text des neuesten Muster-Knotens zurück (Cache, 30min TTL)."""
    global _muster_cache
    import time as _time
    now = _time.time()

    with _muster_cache_lock:
        if _muster_cache is not None:
            cached_ts, cached_text, cached_at = _muster_cache  # type: ignore[misc]
            if now - cached_at < 1800:  # 30-Minuten-Cache
                return cached_text

    # Scan rückwärts ab max_id — stoppt beim ersten Treffer
    try:
        max_id = _muster_max_id()
    except Exception:
        return ""

    for i in range(max_id, max(1, max_id - 2000), -1):
        f = KNOTEN_DIR / f"{i}.json"
        if not f.exists():
            continue
        try:
            k = json.loads(f.read_text())
            if k.get("typ") == "muster":
                text = k.get("inhalt", "")
                with _muster_cache_lock:
                    _muster_cache = (k.get("zeitstempel", ""), text, now)  # type: ignore[assignment]
                return text
        except Exception:
            pass
    with _muster_cache_lock:
        _muster_cache = ("", "", now)  # type: ignore[assignment]
    return ""


if __name__ == "__main__":
    muster_scan_ausfuehren()
