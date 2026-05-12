#!/usr/bin/env python3
"""
Obsidian Vault — zentrale Schnittstelle für alle Wesen.

Alle Wesen (GENI, dak-gord, Codewesen) nutzen diese Bibliothek
um im Vault zu lesen, zu schreiben, zu suchen und zu navigieren.

Vault-Wurzel: /root/werkraum/
"""
from __future__ import annotations

import re
import time
from datetime import datetime
from pathlib import Path

VAULT = Path("/root/werkraum")

# Dateien und Verzeichnisse die Wesen nicht sehen sollen
_IGNORIERT = {
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    "watchdog_venv", ".venv-agent", "gedaechtnis", "sinne/bilder",
    "graphify-out", ".obsidian",
}

# Maximale Dateigröße die gelesen wird (Bytes)
_MAX_LESEN = 200_000


# ── Lesen ─────────────────────────────────────────────────────────────────────

def lese(pfad: str) -> str:
    """Liest eine Datei aus dem Vault. Pfad relativ zur Vault-Wurzel."""
    ziel = _prüfe_pfad(pfad)
    if not ziel.exists():
        return f"[nicht gefunden: {pfad}]"
    if not ziel.is_file():
        return f"[kein File: {pfad}]"
    if ziel.stat().st_size > _MAX_LESEN:
        return f"[zu groß: {ziel.stat().st_size} Bytes — {pfad}]"
    return ziel.read_text(encoding="utf-8", errors="replace")


def lese_oder_leer(pfad: str) -> str:
    """Wie lese(), gibt '' zurück wenn Datei nicht existiert."""
    ziel = _prüfe_pfad(pfad)
    if not ziel.exists() or not ziel.is_file():
        return ""
    if ziel.stat().st_size > _MAX_LESEN:
        return ""
    return ziel.read_text(encoding="utf-8", errors="replace")


# ── Schreiben ─────────────────────────────────────────────────────────────────

def schreibe(pfad: str, inhalt: str) -> None:
    """Schreibt eine Datei in den Vault. Erstellt Verzeichnisse automatisch."""
    ziel = _prüfe_pfad(pfad)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(inhalt, encoding="utf-8")


def notiz(wesen: str, titel: str, text: str, tags: list[str] | None = None) -> str:
    """
    Schreibt eine Notiz als Markdown-Datei in wesen/<wesen>/notizen/.
    Gibt den Pfad zurück.
    """
    datum = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dateiname = datum + "_" + _slug(titel) + ".md"
    pfad = f"{wesen}/notizen/{dateiname}"

    tag_zeile = ""
    if tags:
        tag_zeile = "tags: [" + ", ".join(tags) + "]\n"

    inhalt = f"---\nwesen: {wesen}\ntitel: {titel}\nzeit: {datetime.now().isoformat()}\n{tag_zeile}---\n\n# {titel}\n\n{text}\n"
    schreibe(pfad, inhalt)
    return pfad


def tagebuch(wesen: str, text: str) -> str:
    """
    Schreibt einen Tagebuch-Eintrag in wesen/<wesen>/tagebuch/<datum>.md.
    Mehrere Einträge am selben Tag werden an dieselbe Datei angehängt.
    """
    datum = datetime.now().strftime("%Y-%m-%d")
    pfad = f"{wesen}/tagebuch/{datum}.md"
    ziel = _prüfe_pfad(pfad)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    uhrzeit = datetime.now().strftime("%H:%M")
    zeile = f"\n## {uhrzeit}\n\n{text}\n"
    with open(ziel, "a", encoding="utf-8") as f:
        f.write(zeile)
    return pfad


# ── Navigieren ────────────────────────────────────────────────────────────────

def liste(verzeichnis: str = "", nur_md: bool = False, tiefe: int = 1) -> list[dict]:
    """
    Listet Dateien in einem Vault-Verzeichnis.
    Gibt [{name, pfad, typ, größe, geändert}] zurück.
    """
    basis = _prüfe_pfad(verzeichnis) if verzeichnis else VAULT
    if not basis.exists() or not basis.is_dir():
        return []

    ergebnis: list[dict] = []
    _liste_rekursiv(basis, basis, ergebnis, nur_md, tiefe, 0)
    return ergebnis


def _liste_rekursiv(wurzel: Path, basis: Path, ergebnis: list, nur_md: bool, max_tiefe: int, aktuelle_tiefe: int) -> None:
    try:
        eintraege = sorted(basis.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return

    for eintrag in eintraege:
        relativ = str(eintrag.relative_to(wurzel))
        if any(teil in _IGNORIERT for teil in eintrag.parts):
            continue
        if eintrag.name.startswith("."):
            continue

        if eintrag.is_dir():
            ergebnis.append({"name": eintrag.name, "pfad": relativ, "typ": "ordner"})
            if aktuelle_tiefe < max_tiefe - 1:
                _liste_rekursiv(wurzel, eintrag, ergebnis, nur_md, max_tiefe, aktuelle_tiefe + 1)
        elif eintrag.is_file():
            if nur_md and eintrag.suffix != ".md":
                continue
            stat = eintrag.stat()
            ergebnis.append({
                "name": eintrag.name,
                "pfad": relativ,
                "typ": "datei",
                "erweiterung": eintrag.suffix,
                "größe": stat.st_size,
                "geändert": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            })


def suche(query: str, verzeichnis: str = "", nur_md: bool = True, max_treffer: int = 20) -> list[dict]:
    """
    Volltext-Suche im Vault.
    Gibt [{pfad, treffer_zeile, zeilen_nr}] zurück.
    """
    basis = _prüfe_pfad(verzeichnis) if verzeichnis else VAULT
    muster = re.compile(re.escape(query), re.IGNORECASE)
    treffer: list[dict] = []

    suffix_filter = {".md"} if nur_md else None

    for datei in basis.rglob("*"):
        if len(treffer) >= max_treffer:
            break
        if not datei.is_file():
            continue
        if suffix_filter and datei.suffix not in suffix_filter:
            continue
        if any(teil in _IGNORIERT for teil in datei.parts):
            continue
        if datei.stat().st_size > _MAX_LESEN:
            continue
        try:
            text = datei.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for nr, zeile in enumerate(text.splitlines(), 1):
            if muster.search(zeile):
                treffer.append({
                    "pfad": str(datei.relative_to(VAULT)),
                    "zeile_nr": nr,
                    "zeile": zeile.strip()[:200],
                })
                if len(treffer) >= max_treffer:
                    break

    return treffer


def existiert(pfad: str) -> bool:
    return _prüfe_pfad(pfad).exists()


def vault_info() -> dict:
    """Gibt einen Überblick über den Vault zurück."""
    anz_md = sum(1 for _ in VAULT.rglob("*.md") if not any(t in _IGNORIERT for t in _.parts))
    anz_py = sum(1 for _ in VAULT.rglob("*.py") if not any(t in _IGNORIERT for t in _.parts))
    return {
        "vault": str(VAULT),
        "markdown_dateien": anz_md,
        "python_dateien": anz_py,
        "timestamp": datetime.now().isoformat(),
    }


# ── Intern ────────────────────────────────────────────────────────────────────

def _prüfe_pfad(pfad: str) -> Path:
    """Stellt sicher dass Pfad innerhalb des Vaults liegt."""
    ziel = (VAULT / pfad).resolve()
    if not str(ziel).startswith(str(VAULT.resolve())):
        raise ValueError(f"Pfad außerhalb des Vaults: {pfad}")
    return ziel


def _slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")[:50]
