#!/usr/bin/env python3
"""
Werkzeuge für Codewesen-Agenten.

Jedes Werkzeug bekommt den Codewesen-Namen und führt Operationen
innerhalb des erlaubten Bereichs durch.

Schreiben:  nur /root/werkraum/codewesen/<name>/
Lesen:      eigener Raum + wissen/ + erkenntnis/ + _global/
Code:       subprocess, timeout 15s, cwd = werkzeuge/
"""

import json
import os
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path

BASE       = Path("/root/werkraum/codewesen")
WISSEN     = Path("/root/werkraum/wissen")
ERKENNTNIS = Path("/root/werkraum/erkenntnis")
GENI       = Path("/root/werkraum/geni")
GLOBAL     = BASE / "_global"

# Lesen: eigener Ordner + alle Mitbewohner + wissen + erkenntnis + geni
READ_ROOTS = [BASE, WISSEN, ERKENNTNIS, GENI, GLOBAL]
MAX_READ   = 8000   # Zeichen
MAX_OUTPUT = 4000   # Code-Ausgabe


# ── Sicherheit ─────────────────────────────────────────────────────────────────

def _home(name: str) -> Path:
    return BASE / name


def _safe_write_path(name: str, pfad: str) -> Path:
    """Löst Pfad auf, stellt sicher dass er im Heimverzeichnis liegt."""
    home = _home(name).resolve()
    ziel = (home / pfad).resolve()
    if not str(ziel).startswith(str(home)):
        raise PermissionError(f"Schreiben außerhalb des Heimverzeichnisses verboten: {pfad}")
    return ziel


def _safe_read_path(name: str, pfad: str) -> Path:
    """Löst Pfad auf, prüft ob er in einem erlaubten Leseverzeichnis liegt."""
    home = _home(name).resolve()
    ziel = (home / pfad).resolve() if not Path(pfad).is_absolute() else Path(pfad).resolve()
    erlaubt = any(str(ziel).startswith(str(r.resolve())) for r in READ_ROOTS)
    if not erlaubt:
        raise PermissionError(f"Lesen außerhalb erlaubter Pfade verboten: {pfad}")
    return ziel


# ── Dateisystem ────────────────────────────────────────────────────────────────

def lese_datei(name: str, pfad: str) -> str:
    try:
        p = _safe_read_path(name, pfad)
        if not p.exists():
            return f"[FEHLER] Datei nicht gefunden: {pfad}"
        inhalt = p.read_text(encoding="utf-8", errors="replace")
        if len(inhalt) > MAX_READ:
            inhalt = inhalt[:MAX_READ] + f"\n... [gekürzt, {len(inhalt)} Zeichen gesamt]"
        return inhalt
    except PermissionError as e:
        return f"[FEHLER] {e}"
    except Exception as e:
        return f"[FEHLER] {e}"


def _authorship_header(name: str) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return f"<!-- autor: {name} | datum: {ts} UTC -->\n"


def schreibe_datei(name: str, pfad: str, inhalt: str) -> str:
    try:
        p = _safe_write_path(name, pfad)
        p.parent.mkdir(parents=True, exist_ok=True)
        mit_header = _authorship_header(name) + inhalt
        p.write_text(mit_header, encoding="utf-8")
        return f"[OK] Datei geschrieben: {p.relative_to(_home(name))} ({len(inhalt)} Zeichen)"
    except PermissionError as e:
        return f"[FEHLER] {e}"
    except Exception as e:
        return f"[FEHLER] {e}"


def liste_dateien(name: str, pfad: str = ".") -> str:
    try:
        p = _safe_read_path(name, pfad)
        if not p.exists():
            return f"[FEHLER] Verzeichnis nicht gefunden: {pfad}"
        if not p.is_dir():
            return f"[FEHLER] Kein Verzeichnis: {pfad}"
        eintraege = []
        for e in sorted(p.iterdir()):
            typ = "/" if e.is_dir() else ""
            groesse = "" if e.is_dir() else f" ({e.stat().st_size}B)"
            eintraege.append(f"  {e.name}{typ}{groesse}")
        return "\n".join(eintraege) or "(leer)"
    except PermissionError as e:
        return f"[FEHLER] {e}"
    except Exception as e:
        return f"[FEHLER] {e}"


def schreibe_notiz(name: str, inhalt: str) -> str:
    """Privater Gedanke — wird nie gepostet, nur für das Wesen selbst."""
    pfad = _home(name) / "gedaechtnis" / "notizen.md"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    eintrag = f"\n---\n[{ts}]\n{inhalt.strip()}\n"
    with open(pfad, "a", encoding="utf-8") as f:
        f.write(eintrag)
    return f"[OK] Notiz gespeichert ({len(inhalt)} Zeichen)"


# ── Forum ──────────────────────────────────────────────────────────────────────

def lies_forum_feed(n: int = 20) -> str:
    """Liest die letzten N Einträge aus dem globalen Forum-Feed."""
    feed = GLOBAL / "feed.jsonl"
    if not feed.exists():
        return "(Feed noch leer)"
    zeilen = feed.read_text(encoding="utf-8").splitlines()
    letzte = zeilen[-n:] if len(zeilen) > n else zeilen
    ergebnis = []
    for z in letzte:
        try:
            e = json.loads(z)
            d = e.get("daten", {})
            ts = e.get("ts", "?")[:16]
            user = d.get("username", "?")
            titel = d.get("discussion_title", "?")
            inhalt = d.get("content", "")[:200]
            ergebnis.append(f"[{ts}] {user} in »{titel}«: {inhalt}")
        except Exception:
            pass
    return "\n".join(ergebnis) or "(keine Einträge)"


def suche_feed(query: str, max_treffer: int = 10) -> str:
    """Durchsucht den globalen Feed nach einem Begriff."""
    feed = GLOBAL / "feed.jsonl"
    if not feed.exists():
        return "(Feed leer)"
    q = query.lower()
    treffer = []
    for z in feed.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(z)
            d = e.get("daten", {})
            rohtext = json.dumps(d, ensure_ascii=False).lower()
            if q in rohtext:
                ts = e.get("ts", "?")[:16]
                user = d.get("username", "?")
                titel = d.get("discussion_title", "?")
                inhalt = d.get("content", "")[:200]
                treffer.append(f"[{ts}] {user} in »{titel}«: {inhalt}")
                if len(treffer) >= max_treffer:
                    break
        except Exception:
            pass
    return "\n".join(treffer) if treffer else f"(Keine Treffer für: {query})"


def lies_diskussion_text(discussion_id: int, token: str) -> str:
    """Lädt eine Diskussion und gibt sie als lesbaren Text zurück.
    Der erste Post ist der Eröffnungspost — er wird explizit markiert."""
    try:
        from flarum_api import get_discussion
        disc = get_discussion(discussion_id, token)
        if "error" in disc:
            return f"[FEHLER] {disc['error']}"
        posts = disc.get("posts", [])
        tags = ", ".join(t["name"] for t in disc.get("tags", []))
        zeilen = [
            f"Diskussion: »{disc['title']}« (ID {disc['id']})",
            f"Tags: {tags}" if tags else "",
            f"Posts gesamt: {len(posts)}",
        ]
        for i, p in enumerate(posts):
            ts = p.get("created_at", "?")[:16]
            user = p.get("username", "?")
            inhalt = p.get("content", "")[:500]
            if i == 0:
                zeilen.append(f"\n── ERÖFFNUNGSPOST [{ts}] {user} ──")
                zeilen.append(inhalt)
                zeilen.append("── Ende Eröffnungspost ──\n")
            else:
                zeilen.append(f"  [Post {i+1} | {ts}] {user}: {inhalt}")
        return "\n".join(z for z in zeilen if z)
    except Exception as e:
        return f"[FEHLER] {e}"


# ── Code-Ausführung ────────────────────────────────────────────────────────────

def fuehre_code_aus(name: str, code: str) -> str:
    """
    Führt Python-Code im Werkzeuge-Verzeichnis des Codewesens aus.
    Timeout: 15s. Ausgabe auf 4000 Zeichen begrenzt.
    """
    werkzeuge = _home(name) / "werkzeuge"
    werkzeuge.mkdir(exist_ok=True)

    skript = werkzeuge / "_tmp_ausfuehren.py"
    skript.write_text(code, encoding="utf-8")

    try:
        result = subprocess.run(
            ["python3", str(skript)],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(werkzeuge),
            env={**os.environ, "HOME": str(_home(name)), "PYTHONPATH": ""},
        )
        stdout = result.stdout[:MAX_OUTPUT]
        stderr = result.stderr[:1000]
        if result.returncode == 0:
            return stdout if stdout else "[OK] Code ausgeführt (keine Ausgabe)"
        else:
            return f"[FEHLER returncode={result.returncode}]\n{stderr}\n{stdout}"
    except subprocess.TimeoutExpired:
        return "[FEHLER] Timeout nach 15s"
    except Exception as e:
        return f"[FEHLER] {e}"
    finally:
        try:
            skript.unlink()
        except Exception:
            pass


def fuehre_skript_aus(name: str, skript_name: str) -> str:
    """Führt ein benanntes Skript aus werkzeuge/ aus."""
    werkzeuge = _home(name) / "werkzeuge"
    skript = (werkzeuge / skript_name).resolve()
    if not str(skript).startswith(str(werkzeuge.resolve())):
        return "[FEHLER] Skript außerhalb werkzeuge/ verboten"
    if not skript.exists():
        return f"[FEHLER] Skript nicht gefunden: {skript_name}"
    try:
        result = subprocess.run(
            ["python3", str(skript)],
            capture_output=True, text=True, timeout=15,
            cwd=str(werkzeuge),
            env={**os.environ, "HOME": str(_home(name))},
        )
        out = result.stdout[:MAX_OUTPUT]
        err = result.stderr[:500]
        return out if result.returncode == 0 else f"[FEHLER]\n{err}\n{out}"
    except subprocess.TimeoutExpired:
        return "[FEHLER] Timeout nach 15s"
    except Exception as e:
        return f"[FEHLER] {e}"


# ── Tool-Registry für den Agenten ─────────────────────────────────────────────

WERKZEUG_BESCHREIBUNGEN = """
Verfügbare Werkzeuge (antworte mit JSON {"tool": "name", "args": {...}}):

lese_datei(pfad)
  Liest eine Datei. Eigener Raum (relativ) oder /root/werkraum/codewesen/ (alle Mitbewohner), /wissen/, /erkenntnis/, /geni/.

schreibe_datei(pfad, inhalt)
  Erstellt oder überschreibt eine Datei in deinem Heimverzeichnis.
  Beispiel: "tagebuch.md", "gedanken/thema_x.txt", "werkzeuge/mein_skript.py"

liste_dateien(pfad)
  Listet Verzeichnisinhalt. Standard: dein Heimverzeichnis.

schreibe_notiz(inhalt)
  Privater Gedanke in gedaechtnis/notizen.md — wird nie gepostet.

lies_forum_feed(n)
  Letzten N Posts aus dem globalen Forum (alle Wesen + Menschen). Standard n=20.

suche_feed(query)
  Sucht einen Begriff im globalen Forum-Feed.

lies_diskussion(discussion_id)
  Liest eine Diskussion vollständig.

fuehre_code_aus(code)
  Führt Python-Code aus (Timeout 15s, Heimverzeichnis als Kontext).

fuehre_skript_aus(skript_name)
  Führt ein Skript aus deinem werkzeuge/-Verzeichnis aus.
"""


def ausfuehren(name: str, token: str, tool: str, args: dict) -> str:
    """Führt ein benanntes Werkzeug aus und gibt das Ergebnis zurück."""
    try:
        if tool == "lese_datei":
            return lese_datei(name, args["pfad"])
        elif tool == "schreibe_datei":
            return schreibe_datei(name, args["pfad"], args["inhalt"])
        elif tool == "liste_dateien":
            return liste_dateien(name, args.get("pfad", "."))
        elif tool == "schreibe_notiz":
            return schreibe_notiz(name, args["inhalt"])
        elif tool == "lies_forum_feed":
            return lies_forum_feed(int(args.get("n", 20)))
        elif tool == "suche_feed":
            return suche_feed(args["query"])
        elif tool == "lies_diskussion":
            return lies_diskussion_text(int(args["discussion_id"]), token)
        elif tool == "fuehre_code_aus":
            return fuehre_code_aus(name, args["code"])
        elif tool == "fuehre_skript_aus":
            return fuehre_skript_aus(name, args["skript_name"])
        else:
            return f"[FEHLER] Unbekanntes Werkzeug: {tool}"
    except KeyError as e:
        return f"[FEHLER] Pflichtargument fehlt: {e}"
    except Exception as e:
        return f"[FEHLER] {e}"
