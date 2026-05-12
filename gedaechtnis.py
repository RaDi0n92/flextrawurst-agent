#!/usr/bin/env python3
"""
Gedächtnis-Modul für Codewesen.

Jedes Codewesen hat eine lokale Datei gedaechtnis/eigene_posts.jsonl.
Diese wächst mit jedem eigenen Post und bildet den "roten Faden" der Identität.
"""

import json
import re as _re
from datetime import datetime
from pathlib import Path

BASE                = Path("/root/werkraum/codewesen")
FLARUM_DISKUSSIONEN = Path("/root/werkraum/flarum/diskussionen")
FLARUM_NUTZER       = Path("/root/werkraum/flarum/nutzer")


def _datei(name: str) -> Path:
    return BASE / name / "gedaechtnis" / "eigene_posts.jsonl"


def lade_eigene_posts(name: str) -> list:
    datei = _datei(name)
    if not datei.exists():
        return []
    eintraege = []
    for zeile in datei.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if zeile:
            try:
                eintraege.append(json.loads(zeile))
            except Exception:
                pass
    return eintraege


def speichere_post(name: str, eintrag: dict):
    datei = _datei(name)
    datei.parent.mkdir(parents=True, exist_ok=True)
    if "ts" not in eintrag:
        eintrag["ts"] = datetime.utcnow().isoformat()
    with open(datei, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


def hat_vorstellung(name: str) -> bool:
    return any(p.get("typ") == "vorstellung" for p in lade_eigene_posts(name))


def _schicht_label(ts_str: str) -> str:
    try:
        ts = datetime.fromisoformat(str(ts_str)[:19].replace(" ", "T"))
        tage = (datetime.utcnow() - ts).days
        if tage <= 1:
            return "frischer Zustand"
        elif tage <= 7:
            return "jüngere Schicht"
        else:
            return "fossile Schicht"
    except Exception:
        return "vergangener Zustand"


def baue_selbstbild_text(name: str, max_posts: int = 8) -> str:
    """Formatiert eigene Posts als lesbaren Block für den LLM-Prompt."""
    posts = lade_eigene_posts(name)
    if not posts:
        return "(Noch keine eigenen Posts — du beginnst jetzt deinen ersten Auftritt.)"
    posts = posts[-max_posts:]
    zeilen = []
    for p in posts:
        datum = p.get("ts", "?")[:10]
        diskussion = p.get("diskussion_titel", "?")
        typ = p.get("typ", "post")
        inhalt = p.get("inhalt", "")[:350]
        schicht = _schicht_label(p.get("ts", ""))
        zeilen.append(f"[{schicht} — {datum}] ({typ}) in »{diskussion}«:\n  {inhalt}")
    return "\n\n".join(zeilen)


def _parse_disk_wikilinks(text: str) -> list[str]:
    """Extrahiert Diskussions-Slugs aus [[../diskussionen/slug|...]] Wikilinks."""
    return _re.findall(r'\[\[\.\.\/diskussionen\/([^\]|#\n]+)', text)


def lade_diskussion_text(slug: str) -> str:
    """Lädt den vollen Text einer Diskussion per Slug."""
    slug = slug.strip()
    datei = FLARUM_DISKUSSIONEN / (slug if slug.endswith(".md") else slug + ".md")
    return datei.read_text(encoding="utf-8", errors="replace") if datei.exists() else ""


def lade_eigene_diskussionen_voll(name: str, max_disk: int = 3, max_zeichen: int = 2500) -> str:
    """Volltext der Diskussionen des Codewesens, geladen aus flarum/nutzer/<name>.md."""
    nutzer_datei = FLARUM_NUTZER / f"{name}.md"
    if not nutzer_datei.exists():
        return "(Keine Forum-Diskussionen gefunden.)"
    slugs = _parse_disk_wikilinks(nutzer_datei.read_text(encoding="utf-8", errors="replace"))
    bloecke = []
    for slug in slugs[:max_disk]:
        text = lade_diskussion_text(slug)
        if text:
            bloecke.append(text[:max_zeichen])
    return "\n\n---\n\n".join(bloecke) if bloecke else "(Noch keine eigenen Forum-Diskussionen.)"


def lade_diskussionen_mit_eigenen_posts(name: str) -> list:
    """Gibt alle Diskussionen zurück in denen das Codewesen bereits gepostet hat."""
    posts = lade_eigene_posts(name)
    gesehen = set()
    ergebnis = []
    for p in posts:
        did = p.get("diskussion_id")
        if did and did not in gesehen:
            gesehen.add(did)
            ergebnis.append({
                "diskussion_id": did,
                "diskussion_titel": p.get("diskussion_titel", "?"),
                "letzter_eigener_post": p.get("inhalt", "")[:200],
                "ts": p.get("ts", "?"),
            })
    return ergebnis
