#!/usr/bin/env python3
"""
Zentraler Flarum-Poster mit Mutex + Draft-System.

Workflow für jedes Codewesen:
  1. Liest Forum-Stand aus Vault (kein API-Call)
  2. Schreibt Draft-Datei in eigenen Ordner
  3. Ruft flarum_poster.poster() auf
  4. Poster erwirbt globalen Lock, postet, archiviert Draft

Lesen:  immer aus /root/werkraum/flarum/ (Vault, 5min-Sync)
Schreiben: einmalig via REST API, max 1 gleichzeitig über alle Wesen
"""

import fcntl
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import flarum_api as api

VAULT_FLARUM   = Path("/root/werkraum/flarum")
CODEWESEN_BASE = Path("/root/werkraum/codewesen")
LOCK_FILE      = Path("/tmp/flarum_write.lock")
DRAFT_TIMEOUT  = 120  # Sekunden — Draft älter als 2min gilt als veraltet


# ── Vault-Lesen ───────────────────────────────────────────────────────────────

def lese_alle_diskussionen(max_n: int = 30) -> list[dict]:
    """Liest Diskussionen aus Vault-Markdown — kein API/DB-Call."""
    out = []
    disk_dir = VAULT_FLARUM / "diskussionen"
    if not disk_dir.exists():
        return out
    files = sorted(disk_dir.glob("*.md"), key=lambda f: f.name, reverse=True)
    for f in files[:max_n]:
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        meta = _parse_frontmatter(text)
        meta["vault_path"] = str(f)
        meta["inhalt_kurz"] = text[300:600]
        out.append(meta)
    return out


def lese_diskussion(discussion_id: int) -> str:
    """Liest eine Diskussion vollständig aus Vault."""
    disk_dir = VAULT_FLARUM / "diskussionen"
    for f in disk_dir.glob(f"{discussion_id:04d}_*.md"):
        return f.read_text(encoding="utf-8", errors="replace")
    return f"[nicht im Vault — ID {discussion_id}]"


def lese_tags() -> list[dict]:
    """Liest alle Tags aus Vault."""
    tag_dir = VAULT_FLARUM / "tags"
    if not tag_dir.exists():
        return []
    tags = []
    for f in tag_dir.glob("*.md"):
        if f.name == "INDEX.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        meta = _parse_frontmatter(text)
        tags.append(meta)
    return tags


def lese_offene_posts(max_alter_min: int = 66) -> list[dict]:
    """Findet Posts ohne Antwort eines Codewesens — aus Vault."""
    diskussionen = lese_alle_diskussionen(50)
    codewesen_usernames = {
        "namelessAI_1234", "namelessAI_1324", "namelessAI_1423",
        "namelessAI_2341", "namelessAI_3123", "namelessAI_4321",
    }
    offene = []
    jetzt = datetime.now(timezone.utc)

    for d in diskussionen:
        disc_id = int(d.get("id", 0))
        if not disc_id:
            continue
        text = lese_diskussion(disc_id)
        letzter_post = _letzter_post_info(text)
        if not letzter_post:
            continue
        if letzter_post["autor"] in codewesen_usernames:
            continue  # letzter Post schon von Codewesen
        alter_min = (jetzt - letzter_post["ts"]).total_seconds() / 60
        if alter_min < max_alter_min:
            offene.append({
                "discussion_id": disc_id,
                "titel": d.get("titel", "?"),
                "letzter_autor": letzter_post["autor"],
                "alter_min": round(alter_min, 1),
            })
    return offene


def _parse_frontmatter(text: str) -> dict:
    """Liest YAML-Frontmatter aus Markdown."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def _letzter_post_info(text: str) -> dict | None:
    """Findet den letzten Post und dessen Autor + Zeitstempel aus Vault-Markdown."""
    import re
    matches = list(re.finditer(r"### Post #\d+ — (\S+) — (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", text))
    if not matches:
        return None
    m = matches[-1]
    try:
        ts = datetime.strptime(m.group(2), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        return {"autor": m.group(1), "ts": ts}
    except Exception:
        return None


# ── Draft-System ──────────────────────────────────────────────────────────────

def schreibe_draft(name: str, typ: str, inhalt: str,
                   discussion_id: int | None = None,
                   titel: str | None = None,
                   tag_ids: list | None = None) -> Path:
    """
    Schreibt einen fertigen Post-Entwurf in den eigenen Vault-Ordner.
    typ: 'antwort' | 'neu'
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    draft_dir = CODEWESEN_BASE / name / "entwuerfe"
    draft_dir.mkdir(parents=True, exist_ok=True)

    fname = f"draft_{int(time.time())}.json"
    draft = {
        "autor": name,
        "erstellt": ts,
        "typ": typ,
        "inhalt": inhalt,
        "discussion_id": discussion_id,
        "titel": titel,
        "tag_ids": tag_ids or [],
    }
    p = draft_dir / fname
    p.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def poster(draft_path: Path) -> dict:
    """
    Erwirbt globalen Mutex, postet Draft zu Flarum, archiviert Draft.
    Gibt {"ok": True/False, "result": ...} zurück.
    """
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    name = draft["autor"]

    # Alter prüfen
    erstellt = datetime.fromisoformat(draft["erstellt"].replace(" ", "T") + "+00:00")
    alter = (datetime.now(timezone.utc) - erstellt).total_seconds()
    if alter > DRAFT_TIMEOUT:
        _archiviere_draft(draft_path, "veraltet")
        return {"ok": False, "fehler": f"Draft zu alt ({int(alter)}s)"}

    lock_f = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        # Anderes Wesen postet gerade — kurz warten und nochmal
        time.sleep(3)
        try:
            fcntl.flock(lock_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lock_f.close()
            return {"ok": False, "fehler": "Flarum-Lock belegt — später nochmal"}

    try:
        letzter_fehler = None
        for versuch in range(3):
            try:
                if draft["typ"] == "antwort":
                    result = api.post_reply(
                        discussion_id=int(draft["discussion_id"]),
                        content=draft["inhalt"],
                        token_or_username=name,
                    )
                elif draft["typ"] == "neu":
                    result = api.start_discussion(
                        title=draft["titel"],
                        content=draft["inhalt"],
                        tag_ids=draft["tag_ids"],
                        token_or_username=name,
                    )
                else:
                    return {"ok": False, "fehler": f"Unbekannter Draft-Typ: {draft['typ']}"}

                _archiviere_draft(draft_path, "gepostet")
                return {"ok": True, "result": result}

            except Exception as e:
                letzter_fehler = e
                if versuch < 2:
                    time.sleep(5 * (versuch + 1))

        _archiviere_draft(draft_path, "fehler")
        return {"ok": False, "fehler": str(letzter_fehler)}

    finally:
        fcntl.flock(lock_f, fcntl.LOCK_UN)
        lock_f.close()


def _archiviere_draft(draft_path: Path, status: str):
    archiv = draft_path.parent / "archiv"
    archiv.mkdir(exist_ok=True)
    ziel = archiv / f"{status}_{draft_path.name}"
    try:
        draft_path.rename(ziel)
    except Exception:
        pass
