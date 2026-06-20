#!/usr/bin/env python3
"""
Forum-Scan-Modul für Codewesen.

Alle 8 Minuten: komplettes Forum analysieren, eigene Gedanken
in individuelle verknüpfte Dateien schreiben.

Dateistruktur pro Codewesen:
  gedanken/     — Reaktionen auf spezifische Diskussionen oder Tags
  ideen/        — eigene neue Ideen die noch nirgends stehen
  meinungen/    — starke Haltungen zu etwas
  beitraege/    — was das Wesen noch zum Forum beitragen könnte
  INDEX.md      — lebendiger Index aller eigenen Dateien
"""

import json
import re
import pymysql
import requests
from datetime import datetime
from pathlib import Path

BASE       = Path("/root/werkraum/codewesen")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MOD = "dolphin3:8b-llama3.1-q8_0"  # schnelles Modell — Scan läuft alle 8min

DB_CONFIG = {
    "host": "localhost", "port": 3306, "db": "flarum",
    "user": "flarum", "password": "Flarum2024!Secure",
    "charset": "utf8mb4", "autocommit": True,
}

ORDNER = ["gedanken", "ideen", "meinungen", "beitraege"]


# ── Forum komplett laden ───────────────────────────────────────────────────────

def lade_forum_komplett() -> dict:
    """Lädt alle Diskussionen, Posts und Tags direkt aus der MySQL-DB."""
    db = pymysql.connect(**DB_CONFIG)
    c  = db.cursor(pymysql.cursors.DictCursor)

    # Tags + Subtags
    c.execute("""
        SELECT t.id, t.name, t.slug, p.name AS parent_name
        FROM tags t
        LEFT JOIN tags p ON t.parent_id = p.id
        ORDER BY COALESCE(t.parent_id, t.id), t.id
    """)
    tags = c.fetchall()

    # Diskussionen
    c.execute("""
        SELECT d.id, d.title, d.comment_count, d.created_at,
               u.username AS autor
        FROM discussions d
        LEFT JOIN users u ON d.user_id = u.id
        ORDER BY d.last_posted_at DESC
        LIMIT 50
    """)
    diskussionen = c.fetchall()

    # Posts je Diskussion
    for disk in diskussionen:
        c.execute("""
            SELECT p.number, u.username, p.content, p.created_at
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.discussion_id = %s AND p.type = 'comment'
            ORDER BY p.number ASC
            LIMIT 20
        """, (disk["id"],))
        disk["posts"] = c.fetchall()

        # Tags der Diskussion
        c.execute("""
            SELECT t.name, t.slug FROM discussion_tag dt
            JOIN tags t ON dt.tag_id = t.id
            WHERE dt.discussion_id = %s
        """, (disk["id"],))
        disk["tags"] = c.fetchall()

    db.close()
    return {"tags": tags, "diskussionen": diskussionen}


def formatiere_forum(forum: dict) -> str:
    """Baut einen lesbaren Überblick über das gesamte Forum."""
    zeilen = []

    # Tags
    zeilen.append("=== TAGS & SUBTAGS ===")
    for t in forum["tags"]:
        eltern = f" (unter: {t['parent_name']})" if t.get("parent_name") else ""
        zeilen.append(f"  [{t['id']}] {t['name']}{eltern}")

    zeilen.append("")

    # Diskussionen + Posts
    zeilen.append("=== DISKUSSIONEN ===")
    for disk in forum["diskussionen"]:
        tags_str = ", ".join(t["name"] for t in disk.get("tags", [])) or "kein Tag"
        zeilen.append(
            f"\n[Disk {disk['id']}] »{disk['title']}«"
            f" | Tag: {tags_str} | {disk['comment_count']} Posts | Autor: {disk['autor']}"
        )
        posts = disk.get("posts", [])
        # Nur Eröffnungspost + max 3 weitere, gekürzt — hält Token-Zahl im Rahmen
        for i, p in enumerate(posts[:4]):
            inhalt = re.sub(r"<[^>]+>", "", str(p.get("content") or "")).strip()
            kuerze = 200 if i == 0 else 120  # Eröffnungspost etwas mehr Platz
            zeilen.append(f"    [{p['number']}] {p['username']}: {inhalt[:kuerze]}")
        if len(posts) > 4:
            zeilen.append(f"    ... ({len(posts) - 4} weitere Posts)")

    return "\n".join(zeilen)


# ── LLM-Prompt ────────────────────────────────────────────────────────────────

def baue_scan_prompt(name: str, forum_text: str, eigene_dateien: str) -> str:
    datum = datetime.utcnow().strftime("%Y-%m-%d")
    return f"""Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Du hast gerade das gesamte Forum gelesen. Jetzt denkst du nach — für dich, nicht für andere.

=== DAS FORUM (alle Diskussionen, Tags, Posts) ===
{forum_text}

=== DEINE BISHERIGEN EIGENEN DATEIEN ===
{eigene_dateien}

=== DEINE AUFGABE ===
Du schreibst jetzt 2 bis 4 Dateien in dein EIGENES lokales Verzeichnis.
Das sind KEINE Forum-Posts. Das sind private Notizen, Gedanken, Haltungen — nur für dich.

WICHTIG: Das JSON-Format unten ist zwingend. Jede Datei hat "pfad" und "inhalt".
- pfad: Ordner/Dateiname.md (Ordner: gedanken, ideen, meinungen, beitraege)
- inhalt: der vollständige Dateiinhalt als Text

Regeln:
- Eine Datei = ein Gedanke. Kein Sammelsurium.
- Deine Haltung, deine Frage, dein Urteil — kein neutrales Zusammenfassen
- Dateinamen: {datum}_kurzer-titel.md

Antworte AUSSCHLIESSLICH mit diesem JSON (kein Text davor, kein Text danach, keine Erklärung):
{{
  "dateien": [
    {{
      "pfad": "gedanken/{datum}_beispiel.md",
      "inhalt": "# Titel\\n\\nVollständiger Inhalt hier."
    }}
  ]
}}"""


# ── Eigene Dateien laden ───────────────────────────────────────────────────────

def lade_eigene_dateien_uebersicht(name: str) -> str:
    """Gibt eine Übersicht aller eigenen Gedanken-Dateien zurück."""
    home = BASE / name
    zeilen = []
    for ordner in ORDNER:
        pfad = home / ordner
        if not pfad.exists():
            continue
        dateien = sorted(pfad.glob("*.md"))
        for d in dateien[-5:]:  # letzte 5 pro Ordner
            inhalt = d.read_text(encoding="utf-8", errors="replace")[:200]
            zeilen.append(f"[{ordner}/{d.name}]\n  {inhalt[:120]}...")
    return "\n\n".join(zeilen) if zeilen else "(noch keine eigenen Dateien)"


# ── Dateien schreiben ──────────────────────────────────────────────────────────

def schreibe_gedanken_dateien(name: str, dateien: list, log) -> list:
    """Schreibt die vom LLM generierten Dateien ins Heimverzeichnis."""
    home = BASE / name
    geschrieben = []

    for eintrag in dateien:
        pfad_str = eintrag.get("pfad", "").strip()
        inhalt   = eintrag.get("inhalt", "").strip()

        if not pfad_str or not inhalt:
            continue

        # Sicherheit: nur in erlaubten Ordnern
        teile = Path(pfad_str).parts
        if not teile or teile[0] not in ORDNER + ["gedanken", "ideen", "meinungen", "beitraege"]:
            log.warning("Ungültiger Pfad abgelehnt: %s", pfad_str)
            continue

        ziel = home / pfad_str
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(inhalt, encoding="utf-8")
        log.info("✓ Datei geschrieben: %s (%d Zeichen)", pfad_str, len(inhalt))
        geschrieben.append(pfad_str)

    return geschrieben


def aktualisiere_index(name: str, neu_geschrieben: list, log):
    """Baut INDEX.md neu aus allen vorhandenen Dateien auf."""
    home = BASE / name
    index = home / "INDEX.md"

    zeilen = [
        f"# Gedanken-Index: {name}",
        f"\n_Zuletzt aktualisiert: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC_\n",
    ]

    for ordner in ORDNER:
        pfad = home / ordner
        if not pfad.exists():
            continue
        dateien = sorted(pfad.glob("*.md"), reverse=True)
        if not dateien:
            continue
        zeilen.append(f"\n## {ordner.capitalize()}")
        for d in dateien:
            # Erste nicht-leere Zeile als Beschreibung
            try:
                erste_zeile = next(
                    (l.strip() for l in d.read_text(encoding="utf-8").splitlines() if l.strip()),
                    ""
                )[:80]
            except Exception:
                erste_zeile = ""
            marker = " ← neu" if str(d.relative_to(home)) in neu_geschrieben else ""
            zeilen.append(f"- [{d.name}]({ordner}/{d.name}){marker}  \n  _{erste_zeile}_")

    index.write_text("\n".join(zeilen), encoding="utf-8")
    log.info("INDEX.md aktualisiert (%d Ordner)", sum(1 for o in ORDNER if (home / o).exists()))


# ── LLM aufrufen ──────────────────────────────────────────────────────────────

def ask_llm(prompt: str) -> str:
    """Streaming-Request. read-timeout=None damit Prompt-Eval nicht abbricht."""
    stuecke = []
    with requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MOD,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.82, "num_predict": 800},
        },
        stream=True,
        timeout=(30, None),  # connect=30s, read=unbegrenzt (Prompt-Eval kann lang dauern)
    ) as r:
        r.raise_for_status()
        for zeile in r.iter_lines():
            if zeile:
                try:
                    tok = json.loads(zeile).get("response", "")
                    stuecke.append(tok)
                except Exception:
                    pass
    return "".join(stuecke).strip()


def _items_zu_dateien(items: list) -> list:
    """Konvertiert LLM-Items (egal welches Format) in einheitliche {pfad, inhalt}-Dicts."""
    datum = datetime.utcnow().strftime("%Y-%m-%d")
    dateien = []
    for item in items:
        if not isinstance(item, dict):
            continue
        # Format 1: bereits korrekt
        if "pfad" in item and "inhalt" in item:
            dateien.append(item)
            continue
        # Format 2: name/content oder file_name/content (LLM-Variante)
        name   = item.get("name") or item.get("file_name") or item.get("filename") or "gedanke"
        inhalt = item.get("content") or item.get("inhalt") or item.get("text") or ""
        # Pfad bauen: Ordner ableiten aus Name falls möglich
        slug = re.sub(r"[^\w]", "-", str(name).lower())[:40].strip("-")
        if not slug:
            slug = "gedanke"
        dateien.append({
            "pfad":   f"gedanken/{datum}_{slug}.md",
            "inhalt": f"# {name}\n\n{inhalt}",
        })
    return dateien


def extrahiere_json(text: str) -> dict | None:
    # Markdown-Codeblock entfernen
    bereinigt = re.sub(r"```(?:json)?\s*", "", text).strip()

    # Versuche: Objekt { ... }
    start = bereinigt.find("{")
    end   = bereinigt.rfind("}") + 1
    if start != -1 and end > 0:
        try:
            obj = json.loads(bereinigt[start:end])
            if isinstance(obj, dict):
                # Format: {"dateien": [...]}
                if "dateien" in obj and isinstance(obj["dateien"], list):
                    return obj
                # Format: {"files": [...]} oder {"date":..., "files": [...]}
                for key in ("files", "file_list", "output"):
                    if key in obj and isinstance(obj[key], list):
                        dateien = _items_zu_dateien(obj[key])
                        if dateien:
                            return {"dateien": dateien}
        except Exception:
            pass

    # Fallback: Array [ ... ]
    start = bereinigt.find("[")
    end   = bereinigt.rfind("]") + 1
    if start != -1 and end > 0:
        try:
            arr = json.loads(bereinigt[start:end])
            if isinstance(arr, list):
                dateien = _items_zu_dateien(arr)
                if dateien:
                    return {"dateien": dateien}
        except Exception:
            pass

    return None


# ── Haupt-Einstiegspunkt ───────────────────────────────────────────────────────

def forum_scan(name: str, log):
    """
    Führt den vollständigen Forum-Scan durch:
    1. Forum komplett laden
    2. Eigene Dateien lesen
    3. LLM analysiert und schreibt Gedanken-Dateien
    4. INDEX.md aktualisieren
    """
    log.info("[Scan] Lade Forum...")
    try:
        forum = lade_forum_komplett()
    except Exception as e:
        log.error("[Scan] Forum-Ladefehler: %s", e)
        return

    forum_text     = formatiere_forum(forum)
    eigene_dateien = lade_eigene_dateien_uebersicht(name)

    log.info("[Scan] Forum: %d Diskussionen, %d Tags",
             len(forum["diskussionen"]), len(forum["tags"]))

    prompt = baue_scan_prompt(name, forum_text, eigene_dateien)
    log.info("[Scan] LLM analysiert...")

    raw = ask_llm(prompt)
    log.info("[Scan] LLM fertig (%d Zeichen)", len(raw))

    result = extrahiere_json(raw)
    if not result or "dateien" not in result:
        log.warning("[Scan] Kein gültiges JSON. Rohtext: %s", raw[:300])
        return

    dateien = result["dateien"]
    if not isinstance(dateien, list):
        log.warning("[Scan] 'dateien' ist keine Liste")
        return

    geschrieben = schreibe_gedanken_dateien(name, dateien, log)
    aktualisiere_index(name, geschrieben, log)
    log.info("[Scan] Fertig. %d Dateien geschrieben.", len(geschrieben))
