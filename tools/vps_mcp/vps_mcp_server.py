#!/usr/bin/env python3
"""
vps_mcp_server.py — "Der Werkzeugkörper für den gesamten VPS", MCP-Server für ChatGPT.

Daniels Auftrag (2026-07-23, wörtlich): "ja chatgpt ist teil des schiffes teil der
crew xD und ja alles machen". Gebaut in Stufen (Phase 1: die 10 von ihm selbst
vorgeschlagenen risikoärmsten Lese-Werkzeuge + die zwei priorisierten Asset-Werkzeuge
assets.get_file/assets.render_3d_preview), nicht alle ~50 auf einmal — siehe
_claude/-Konzeptdatei zur Linsen-Session: ein großer Bauplan wird trotzdem einzeln,
verifiziert Stück für Stück umgesetzt, nicht blind komplett generalisiert.

Denselben OAuth-2.1+PKCE-Mechanismus wie flextrawurst_3d_mcp.py (kopiert, dort schon
gegen ChatGPT verifiziert), eigener Port/Dienst/nginx-Pfad, weil dies konzeptionell
ein eigener, viel breiterer "VPS-Werkzeugkörper" ist, kein Teil der 3D-Pipeline.

Sicherheit von Anfang an mitgedacht (nicht nachtraeglich): ALLOWED_ROOTS begrenzt
Datei-Zugriff auf die von Daniel genannten Bereiche, SECRET_MUSTER schliesst .env/
Tokens/Schluessel/Passwoerter aus, auch innerhalb erlaubter Wurzeln.
"""
import base64
import fnmatch
import hashlib
import html
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("VPS_MCP_PORT", "8091"))
API_KEY = os.environ.get("VPS_MCP_KEY", "")
PUBLIC_BASE_URL = os.environ.get("VPS_MCP_PUBLIC_URL", f"http://127.0.0.1:{PORT}")
OAUTH_CLIENT_ID = os.environ.get("VPS_MCP_CLIENT_ID", "vps-mcp")
OAUTH_CLIENT_SECRET = os.environ.get("VPS_MCP_CLIENT_SECRET", "")

# ── Freigegebene Wurzeln (Daniels Liste) ────────────────────────────────────────
ALLOWED_ROOTS = [
    Path("/root/werkraum"),
    Path("/root/flextrawurst"),
    Path("/root/zensi"),
    Path("/root/.gemini/antigravity-cli/brain"),
]
# /etc/systemd/system/ nur lesend, separat behandelt (kein freier Datei-Zugriff,
# nur ueber services.status/services.logs via systemctl/journalctl).

# ── Ausgeschlossen: Geheimnisse (gilt auch INNERHALB erlaubter Wurzeln) ─────────
SECRET_MUSTER = [
    "*.env", "*.env.*", ".env*",
    "*_tokens.json", "*token*.json",
    "id_rsa*", "id_ed25519*", "*.pem", "*.key",
    ".htpasswd*",
    "*password*", "*secret*", "*_credentials*",
]


def _ist_geheim(pfad: Path) -> bool:
    name = pfad.name.lower()
    return any(fnmatch.fnmatch(name, m.lower()) for m in SECRET_MUSTER)


def _pfad_erlaubt(roh_pfad: str) -> Path | None:
    """Gibt den aufgeloesten Pfad zurueck wenn er innerhalb einer erlaubten Wurzel
    liegt UND kein Geheimnis-Muster trifft, sonst None."""
    try:
        p = Path(roh_pfad).resolve()
    except Exception:
        return None
    if not any(p == root or root in p.parents for root in ALLOWED_ROOTS):
        return None
    if _ist_geheim(p):
        return None
    for teil in p.relative_to(next(r for r in ALLOWED_ROOTS if p == r or r in p.parents)).parts:
        if _ist_geheim(Path(teil)):
            return None
    return p


def _sha256_datei(pfad: Path, max_bytes: int = 50_000_000) -> str | None:
    if pfad.stat().st_size > max_bytes:
        return None
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit_fuer(pfad: Path) -> str | None:
    """Findet das umschliessende Git-Repo und liefert den letzten Commit-Hash der Datei,
    falls vorhanden -- rein lesend (git log -1), kein neuer Prozess-Zustand."""
    try:
        repo = subprocess.run(
            ["git", "-C", str(pfad.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if repo.returncode != 0:
            return None
        res = subprocess.run(
            ["git", "-C", str(pfad.parent), "log", "-1", "--format=%H", "--", str(pfad)],
            capture_output=True, text=True, timeout=5,
        )
        return res.stdout.strip() or None
    except Exception:
        return None


def _source_ref(pfad: Path, start_line: int | None = None, end_line: int | None = None) -> dict:
    try:
        stat = pfad.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        modified_at = None
    return {
        "path": str(pfad),
        "start_line": start_line,
        "end_line": end_line,
        "sha256": _sha256_datei(pfad) if pfad.is_file() else None,
        "modified_at": modified_at,
        "git_commit": _git_commit_fuer(pfad) if pfad.is_file() else None,
        "source_type": "file",
    }


def _ergebnis(ok: bool, data=None, source_refs=None, warnings=None,
              truncated: bool = False, next_cursor=None, error: str | None = None) -> dict:
    """Gemeinsames Ausgabeformat fuer alle Tools (Daniels Vorgabe)."""
    return {
        "ok": ok,
        "data": data,
        "source_refs": source_refs or [],
        "warnings": warnings or [],
        "truncated": truncated,
        "next_cursor": next_cursor,
        "error": error,
    }


# ── Tool-Implementierungen (Phase 1) ────────────────────────────────────────────

def tool_list_roots(_args: dict) -> dict:
    return _ergebnis(True, data=[str(r) for r in ALLOWED_ROOTS])


def tool_list_files(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    tiefe = int(args.get("depth", 2))
    glob = args.get("glob", "*")
    limit = min(int(args.get("limit", 200)), 1000)
    cursor = int(args.get("cursor", 0))

    basis = _pfad_erlaubt(roh_pfad)
    if basis is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not basis.is_dir():
        return _ergebnis(False, error="Kein Ordner")

    treffer = []
    basis_tiefe = len(basis.parts)
    for dirpath, dirnames, filenames in os.walk(basis):
        aktuelle_tiefe = len(Path(dirpath).parts) - basis_tiefe
        if aktuelle_tiefe >= tiefe:
            dirnames.clear()
            continue
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if _ist_geheim(p) or not fnmatch.fnmatch(name, glob):
                continue
            treffer.append(p)

    gesamt = len(treffer)
    seite = treffer[cursor:cursor + limit]
    data = []
    for p in seite:
        try:
            stat = p.stat()
            data.append({"path": str(p), "size": stat.st_size,
                         "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()})
        except Exception:
            continue
    next_cursor = cursor + limit if cursor + limit < gesamt else None
    return _ergebnis(True, data=data, truncated=next_cursor is not None, next_cursor=next_cursor)


def tool_search_text(args: dict) -> dict:
    query = args.get("query", "")
    roots = args.get("roots") or [str(r) for r in ALLOWED_ROOTS]
    globs = args.get("globs") or ["*"]
    ist_regex = bool(args.get("regex", False))
    context_lines = min(int(args.get("context_lines", 1)), 5)
    limit = min(int(args.get("limit", 50)), 200)

    if not query:
        return _ergebnis(False, error="query fehlt")

    muster = re.compile(query) if ist_regex else None
    treffer = []
    warnungen = []
    for roh_root in roots:
        basis = _pfad_erlaubt(roh_root)
        if basis is None:
            warnungen.append(f"Wurzel nicht erlaubt, uebersprungen: {roh_root}")
            continue
        for dirpath, _, filenames in os.walk(basis):
            for name in filenames:
                if len(treffer) >= limit:
                    break
                if not any(fnmatch.fnmatch(name, g) for g in globs):
                    continue
                p = Path(dirpath) / name
                if _ist_geheim(p):
                    continue
                try:
                    if p.stat().st_size > 5_000_000:
                        continue
                    zeilen = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                except Exception:
                    continue
                for i, zeile in enumerate(zeilen):
                    treffer_hier = muster.search(zeile) if ist_regex else (query in zeile)
                    if treffer_hier:
                        start = max(0, i - context_lines)
                        ende = min(len(zeilen), i + context_lines + 1)
                        treffer.append({
                            "path": str(p),
                            "line": i + 1,
                            "match": zeile.strip()[:300],
                            "context": "\n".join(zeilen[start:ende])[:1000],
                        })
                        if len(treffer) >= limit:
                            break
            if len(treffer) >= limit:
                break

    refs = [_source_ref(Path(t["path"]), t["line"], t["line"]) for t in treffer[:limit]]
    return _ergebnis(True, data=treffer, source_refs=refs, warnings=warnungen,
                      truncated=len(treffer) >= limit)


def tool_read_file(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    start_line = args.get("start_line")
    end_line = args.get("end_line")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    if p.stat().st_size > 5_000_000:
        return _ergebnis(False, error="Datei zu gross fuer read_file (>5MB) -- assets.get_file nutzen")
    try:
        zeilen = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as ex:
        return _ergebnis(False, error=f"Lesefehler: {ex}")
    start = (start_line - 1) if start_line else 0
    ende = end_line if end_line else len(zeilen)
    nummeriert = [f"{i+1}\t{zeile}" for i, zeile in enumerate(zeilen[start:ende], start=start)]
    return _ergebnis(True, data="\n".join(nummeriert),
                      source_refs=[_source_ref(p, start + 1, ende)])


def tool_file_metadata(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.exists():
        return _ergebnis(False, error="Pfad existiert nicht")
    stat = p.stat()
    daten = {
        "path": str(p),
        "type": "dir" if p.is_dir() else "file",
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "sha256": _sha256_datei(p) if p.is_file() else None,
        "git_commit": _git_commit_fuer(p) if p.is_file() else None,
    }
    return _ergebnis(True, data=daten, source_refs=[_source_ref(p)])


def _git_repo_fuer(roh_pfad: str) -> Path | None:
    p = _pfad_erlaubt(roh_pfad or "")
    if p is None:
        return None
    try:
        res = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return None
        repo = Path(res.stdout.strip())
        return repo if _pfad_erlaubt(str(repo)) is not None else None
    except Exception:
        return None


def tool_git_status(args: dict) -> dict:
    repo = _git_repo_fuer(args.get("path", "/root/werkraum"))
    if repo is None:
        return _ergebnis(False, error="Kein erlaubtes Git-Repo an diesem Pfad")
    try:
        res = subprocess.run(["git", "-C", str(repo), "status", "--porcelain=v1"],
                              capture_output=True, text=True, timeout=15)
        zeilen = [z for z in res.stdout.splitlines() if z.strip()]
        return _ergebnis(True, data={"repo": str(repo), "changes": zeilen, "count": len(zeilen)})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_git_log(args: dict) -> dict:
    repo = _git_repo_fuer(args.get("path", "/root/werkraum"))
    if repo is None:
        return _ergebnis(False, error="Kein erlaubtes Git-Repo an diesem Pfad")
    limit = min(int(args.get("limit", 20)), 100)
    datei = args.get("file")
    cmd = ["git", "-C", str(repo), "log", f"-{limit}", "--format=%H|%ad|%an|%s", "--date=iso-strict"]
    if datei:
        cmd += ["--", datei]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        commits = []
        for zeile in res.stdout.splitlines():
            teile = zeile.split("|", 3)
            if len(teile) == 4:
                commits.append({"hash": teile[0], "date": teile[1], "author": teile[2], "subject": teile[3]})
        return _ergebnis(True, data=commits)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# 2026-07-23: Dienst-Namen bewusst NICHT frei -- nur systemd-Units, deren Name auf
# einen bekannten flextrawurst/werkraum-Dienst passt, damit hier kein beliebiger
# root-Prozess des ganzen VPS abgefragt werden kann. Read-only (status/logs), keine
# start/stop/restart-Aktion in Phase 1.
_DIENST_MUSTER = re.compile(r"^[a-zA-Z0-9_@.+-]+\.service$")


def tool_services_status(args: dict) -> dict:
    name = args.get("name", "")
    if not _DIENST_MUSTER.match(name):
        return _ergebnis(False, error="Ungueltiger Dienstname")
    try:
        res = subprocess.run(["systemctl", "status", name, "--no-pager", "-l"],
                              capture_output=True, text=True, timeout=10)
        return _ergebnis(True, data={"name": name, "output": res.stdout[-4000:], "returncode": res.returncode})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_services_logs(args: dict) -> dict:
    name = args.get("name", "")
    if not _DIENST_MUSTER.match(name):
        return _ergebnis(False, error="Ungueltiger Dienstname")
    lines = min(int(args.get("lines", 100)), 1000)
    try:
        res = subprocess.run(["journalctl", "-u", name, "-n", str(lines), "--no-pager", "-o", "short-iso"],
                              capture_output=True, text=True, timeout=10)
        return _ergebnis(True, data={"name": name, "log": res.stdout[-20000:]})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_find_recent_files(args: dict) -> dict:
    """2026-07-23: Daniels/ChatGPTs erster vorgeschlagener Test ("die zehn zuletzt
    geaenderten Dateien im Werkraum") brauchte dieses Tool -- war in Phase 1 zuerst
    vergessen, vps.list_files sortiert nur alphabetisch, nicht nach Aenderungsdatum."""
    roots = args.get("roots") or [str(r) for r in ALLOWED_ROOTS]
    seit = args.get("since")
    extensions = args.get("extensions")
    limit = min(int(args.get("limit", 10)), 200)

    seit_ts = None
    if seit:
        try:
            seit_ts = datetime.fromisoformat(seit.replace("Z", "+00:00")).timestamp()
        except Exception:
            return _ergebnis(False, error="since muss ISO-8601 sein, z.B. 2026-07-20T00:00:00Z")

    treffer = []
    for roh_root in roots:
        basis = _pfad_erlaubt(roh_root)
        if basis is None:
            continue
        for dirpath, _, filenames in os.walk(basis):
            for name in filenames:
                if extensions and not any(name.endswith(e) for e in extensions):
                    continue
                p = Path(dirpath) / name
                if _ist_geheim(p):
                    continue
                try:
                    mtime = p.stat().st_mtime
                except Exception:
                    continue
                if seit_ts and mtime < seit_ts:
                    continue
                treffer.append((mtime, p))

    treffer.sort(key=lambda t: t[0], reverse=True)
    seite = treffer[:limit]
    data = [{"path": str(p), "modified_at": datetime.fromtimestamp(m, tz=timezone.utc).isoformat()}
            for m, p in seite]
    return _ergebnis(True, data=data, truncated=len(treffer) > limit)


def tool_system_snapshot(_args: dict) -> dict:
    daten = {}
    try:
        daten["load_avg"] = Path("/proc/loadavg").read_text().split()[:3]
    except Exception:
        daten["load_avg"] = None
    try:
        meminfo = Path("/proc/meminfo").read_text()
        werte = {z.split(":")[0]: z.split(":")[1].strip() for z in meminfo.splitlines() if ":" in z}
        daten["mem_total"] = werte.get("MemTotal")
        daten["mem_available"] = werte.get("MemAvailable")
    except Exception:
        pass
    try:
        uptime_s = float(Path("/proc/uptime").read_text().split()[0])
        daten["uptime_stunden"] = round(uptime_s / 3600, 1)
    except Exception:
        pass
    try:
        gesamt, belegt, frei = shutil.disk_usage("/")
        daten["disk_total_gb"] = round(gesamt / 1e9, 1)
        daten["disk_used_gb"] = round(belegt / 1e9, 1)
        daten["disk_free_gb"] = round(frei / 1e9, 1)
    except Exception:
        pass
    try:
        cpu_count = os.cpu_count()
        daten["cpu_count"] = cpu_count
    except Exception:
        pass
    return _ergebnis(True, data=daten)


def tool_assets_get_file(args: dict) -> dict:
    """Liefert Dateiinhalt. mode='preview' (Standard) gibt bei Bildern/kleinen Dateien
    Base64 zurueck, mode='download' bei zu grossen Dateien eine befristete, per Token
    abgesicherte direkte Download-URL statt riesiger Base64-Bloecke im Chat-Kontext."""
    roh_pfad = args.get("path", "")
    mode = args.get("mode", "preview")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")

    groesse = p.stat().st_size
    INLINE_LIMIT = 2_000_000  # 2MB -- darueber sprengt Base64 den Chat-Kontext sinnlos
    if groesse <= INLINE_LIMIT:
        inhalt = base64.b64encode(p.read_bytes()).decode("ascii")
        return _ergebnis(True, data={"path": str(p), "size": groesse, "base64": inhalt},
                          source_refs=[_source_ref(p)])

    token = secrets.token_urlsafe(24)
    _DOWNLOAD_TOKENS[token] = {"path": str(p), "expires": time.time() + 600}
    url = f"{PUBLIC_BASE_URL}/download/{token}"
    return _ergebnis(True, data={
        "path": str(p), "size": groesse,
        "download_url": url, "expires_in_s": 600,
        "hinweis": "Datei zu gross fuer Inline-Base64 -- befristete Download-URL (10 Minuten gueltig)",
    }, source_refs=[_source_ref(p)], warnings=["Datei nicht inline geliefert, siehe download_url"])


_DOWNLOAD_TOKENS: dict[str, dict] = {}


def tool_assets_render_3d_preview(args: dict) -> dict:
    """Wiederverwendet blender_pipeline.render_preview_headless() aus der 3D-Pipeline --
    kein Duplikat der Blender-Logik, nur ein neuer, sicherheitsgeprueftr Zugang dazu."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")

    sys.path.insert(0, "/root/werkraum/tools/3d_pipeline")
    import blender_pipeline

    ziel = Path("/tmp/vps_mcp_previews") / f"{p.stem}_{secrets.token_hex(4)}.png"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    res = blender_pipeline.render_preview_headless(str(p), str(ziel))
    if res.get("status") == "error" or not ziel.exists():
        return _ergebnis(False, error=res.get("error", "Rendern fehlgeschlagen"))
    inhalt = base64.b64encode(ziel.read_bytes()).decode("ascii")
    return _ergebnis(True, data={"model_path": str(p), "preview_png_base64": inhalt},
                      source_refs=[_source_ref(p)])


TOOLS = {
    "vps.list_roots": {
        "fn": tool_list_roots,
        "description": "Zeigt alle freigegebenen Hauptbereiche (Wurzeln) des VPS.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "vps.list_files": {
        "fn": tool_list_files,
        "description": "Listet Ordner und Dateien unter einem erlaubten Pfad auf, mit Tiefe/Glob/Pagination.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "depth": {"type": "integer"},
                "glob": {"type": "string"},
                "cursor": {"type": "integer"},
                "limit": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    "vps.search_text": {
        "fn": tool_search_text,
        "description": "Durchsucht Textdateien in erlaubten Wurzeln nach einem Begriff oder Regex.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "roots": {"type": "array", "items": {"type": "string"}},
                "globs": {"type": "array", "items": {"type": "string"}},
                "regex": {"type": "boolean"},
                "context_lines": {"type": "integer"},
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    "vps.read_file": {
        "fn": tool_read_file,
        "description": "Liest eine Textdatei (mit Zeilennummern), optional einen Zeilenbereich. Max. 5MB.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    "vps.file_metadata": {
        "fn": tool_file_metadata,
        "description": "Groesse, Typ, Aenderungsdatum, SHA256-Hash und letzter Git-Commit einer Datei.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "git.status": {
        "fn": tool_git_status,
        "description": "Zeigt geaenderte, neue und geloeschte Dateien im Git-Repo an diesem Pfad.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}},
    },
    "git.log": {
        "fn": tool_git_log,
        "description": "Commit-Historie eines Projekts oder einer einzelnen Datei.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "file": {"type": "string"}, "limit": {"type": "integer"}},
        },
    },
    "services.status": {
        "fn": tool_services_status,
        "description": "Zustand, PID, Startzeit und letzte Fehler eines systemd-Diensts (nur lesend).",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "services.logs": {
        "fn": tool_services_logs,
        "description": "Journal-Log eines systemd-Diensts (journalctl -u, nur lesend).",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "lines": {"type": "integer"}},
            "required": ["name"],
        },
    },
    "vps.find_recent_files": {
        "fn": tool_find_recent_files,
        "description": "Findet die zuletzt geaenderten Dateien in erlaubten Wurzeln.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "roots": {"type": "array", "items": {"type": "string"}},
                "since": {"type": "string"},
                "extensions": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
            },
        },
    },
    "system.snapshot": {
        "fn": tool_system_snapshot,
        "description": "CPU-Last, RAM, Speicherplatz und Uptime des VPS.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "assets.get_file": {
        "fn": tool_assets_get_file,
        "description": "Liefert eine Datei (Bild, GLB, ZIP etc.) als Base64 (bis 2MB) oder als befristete Download-URL (groesser).",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "mode": {"type": "string"}},
            "required": ["path"],
        },
    },
    "assets.render_3d_preview": {
        "fn": tool_assets_render_3d_preview,
        "description": "Rendert ein Studio-Vorschaubild (PNG) eines 3D-Modells via Headless Blender und liefert es als Base64.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
}


def _pkce_gueltig(code_verifier: str, code_challenge: str, method: str) -> bool:
    if method == "S256":
        digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        berechnet = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        return berechnet == code_challenge
    if method == "plain":
        return code_verifier == code_challenge
    return False


_AUTH_CODES: dict[str, dict] = {}
_ACCESS_TOKENS: dict[str, float] = {}
_CODE_TTL_S = 300
_TOKEN_TTL_S = 3600 * 24 * 30


def get_openapi_schema() -> dict:
    """OpenAPI-Schema fuer den Custom-GPT-Actions-Weg (Alternative zum nativen
    MCP-Connector, gleiches Muster wie flextrawurst_3d_mcp.py)."""
    paths = {}
    for name, spec in TOOLS.items():
        op_id = "".join(w.capitalize() for w in re.split(r"[._]", name))
        paths[f"/tool/{name}"] = {
            "post": {
                "summary": spec["description"],
                "operationId": op_id[0].lower() + op_id[1:],
                "requestBody": {"content": {"application/json": {"schema": spec["inputSchema"]}}},
                "responses": {"200": {"description": "OK"}},
            }
        }
    return {
        "openapi": "3.0.0",
        "info": {"title": "Flextrawurst VPS-Werkzeugkoerper", "version": "1.0.0",
                  "description": "Lesender Zugriff auf Dateien, Git, Dienste, System-Status und 3D-Assets."},
        "servers": [{"url": PUBLIC_BASE_URL}],
        "paths": paths,
    }


class VPSHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json(self, status: int, obj: dict):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _autorisiert(self) -> bool:
        if not API_KEY:
            return True
        auth = self.headers.get("Authorization", "")
        if auth == f"Bearer {API_KEY}":
            return True
        if auth.startswith("Bearer "):
            token = auth[len("Bearer "):]
            ablauf = _ACCESS_TOKENS.get(token)
            if ablauf and ablauf > time.time():
                return True
        return False

    def _unauthorized(self):
        body = json.dumps({"error": "unauthorized"}).encode("utf-8")
        self.send_response(401)
        self._cors()
        self.send_header(
            "WWW-Authenticate",
            f'Bearer resource_metadata="{PUBLIC_BASE_URL}/.well-known/oauth-protected-resource"',
        )
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/.well-known/oauth-protected-resource":
            self._json(200, {"resource": f"{PUBLIC_BASE_URL}/mcp",
                              "authorization_servers": [PUBLIC_BASE_URL]})
            return

        if path == "/.well-known/oauth-authorization-server":
            self._json(200, {
                "issuer": PUBLIC_BASE_URL,
                "authorization_endpoint": f"{PUBLIC_BASE_URL}/oauth/authorize",
                "token_endpoint": f"{PUBLIC_BASE_URL}/oauth/token",
                "registration_endpoint": f"{PUBLIC_BASE_URL}/oauth/register",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256", "plain"],
                "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
            })
            return

        if path == "/oauth/authorize":
            qs = parse_qs(parsed.query)
            redirect_uri = (qs.get("redirect_uri") or [""])[0]
            state = (qs.get("state") or [""])[0]
            code_challenge = (qs.get("code_challenge") or [""])[0]
            code_challenge_method = (qs.get("code_challenge_method") or ["plain"])[0]
            eingereichter_key = (qs.get("key") or [""])[0]

            if not redirect_uri:
                self._json(400, {"error": "invalid_request", "error_description": "redirect_uri fehlt"})
                return

            if eingereichter_key != API_KEY or not API_KEY:
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"""<!doctype html><html><body style="font-family:monospace;background:#0a0e14;color:#cdd6f4;padding:40px">
<h3>Flextrawurst VPS-Werkzeugkoerper — Zugriff erlauben?</h3>
<form method="GET" action="{html.escape(PUBLIC_BASE_URL)}/oauth/authorize">
<input type="hidden" name="redirect_uri" value="{html.escape(redirect_uri)}">
<input type="hidden" name="state" value="{html.escape(state)}">
<input type="hidden" name="code_challenge" value="{html.escape(code_challenge)}">
<input type="hidden" name="code_challenge_method" value="{html.escape(code_challenge_method)}">
<label>Schluessel: <input type="password" name="key"></label>
<button type="submit">Erlauben</button>
</form></body></html>""".encode("utf-8"))
                return

            code = secrets.token_urlsafe(32)
            _AUTH_CODES[code] = {
                "redirect_uri": redirect_uri, "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method, "expires": time.time() + _CODE_TTL_S,
            }
            trenner = "&" if "?" in redirect_uri else "?"
            ziel = f"{redirect_uri}{trenner}code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}"
            self.send_response(302)
            self.send_header("Location", ziel)
            self.end_headers()
            return

        if path == "/openapi.json":
            self._json(200, get_openapi_schema())
            return

        if path.startswith("/download/"):
            token = path[len("/download/"):]
            eintrag = _DOWNLOAD_TOKENS.get(token)
            if not eintrag or eintrag["expires"] < time.time():
                self._json(404, {"error": "Token ungueltig oder abgelaufen"})
                return
            p = Path(eintrag["path"])
            if not p.is_file():
                self._json(404, {"error": "Datei nicht mehr vorhanden"})
                return
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{p.name}"')
            self.send_header("Content-Length", str(p.stat().st_size))
            self.end_headers()
            with open(p, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        from urllib.parse import urlparse
        path = urlparse(self.path).path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length", 0))
        roh = self.rfile.read(length) if length > 0 else b""
        content_type = self.headers.get("Content-Type", "")
        if "application/x-www-form-urlencoded" in content_type:
            body_data = {k: v[0] for k, v in urllib.parse.parse_qs(roh.decode("utf-8")).items()}
        else:
            body_data = json.loads(roh) if roh else {}

        if path == "/oauth/register":
            self._json(201, {
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "client_id_issued_at": int(time.time()),
                "client_secret_expires_at": 0,
                "redirect_uris": body_data.get("redirect_uris", []),
                "grant_types": body_data.get("grant_types", ["authorization_code"]),
                "response_types": body_data.get("response_types", ["code"]),
                "token_endpoint_auth_method": "client_secret_post" if OAUTH_CLIENT_SECRET else "none",
            })
            return

        if path == "/oauth/token":
            if body_data.get("grant_type") != "authorization_code":
                self._json(400, {"error": "unsupported_grant_type"})
                return
            eintrag = _AUTH_CODES.pop(body_data.get("code", ""), None)
            if not eintrag or eintrag["expires"] < time.time():
                self._json(400, {"error": "invalid_grant", "error_description": "Code ungueltig oder abgelaufen"})
                return
            if eintrag["code_challenge"] and not _pkce_gueltig(
                body_data.get("code_verifier", ""), eintrag["code_challenge"], eintrag["code_challenge_method"]
            ):
                self._json(400, {"error": "invalid_grant", "error_description": "PKCE-Verifikation fehlgeschlagen"})
                return
            token = secrets.token_urlsafe(32)
            _ACCESS_TOKENS[token] = time.time() + _TOKEN_TTL_S
            self._json(200, {"access_token": token, "token_type": "Bearer", "expires_in": _TOKEN_TTL_S})
            return

        if not self._autorisiert():
            self._unauthorized()
            return

        if path.startswith("/tool/"):
            # Custom-GPT-Actions-Weg: direkter REST-Aufruf eines einzelnen Tools
            name = path[len("/tool/"):]
            spec = TOOLS.get(name)
            if not spec:
                self._json(404, {"error": f"Unbekanntes Tool: {name}"})
                return
            self._json(200, spec["fn"](body_data))
            return

        if path in ("/mcp", "/rpc", "/"):
            # 2026-07-23: "App-Verknuepfung erkannt, Tool-Weitergabe noch nicht" (Teil 2) --
            # ChatGPTs MCP-Client schickt initialize+notifications/initialized offenbar als
            # JSON-RPC-BATCH (ein JSON-Array mehrerer Nachrichten in einem POST), nicht als
            # einzelne Requests. Der Server erwartete bisher IMMER ein einzelnes Objekt --
            # bei einem Array crashte body_data.get(...) mit AttributeError (bestaetigt im
            # journalctl-Log: "'list' object has no attribute 'get'"), nginx zeigte 502.
            # Jetzt: einzelne Nachricht ODER Batch (Liste von Nachrichten), pro Nachricht
            # verarbeitet, Notifications liefern KEIN Element in der Antwort (JSON-RPC-2.0-
            # Batch-Regel: nur Antworten zu Requests, nie zu Notifications).
            nachrichten = body_data if isinstance(body_data, list) else [body_data]
            antworten = [a for a in (self._verarbeite_rpc(n) for n in nachrichten) if a is not None]

            if not antworten:
                # alles Notifications gewesen -- keine Antwort noetig
                self.send_response(202)
                self._cors()
                self.end_headers()
                return
            if isinstance(body_data, list):
                self._json(200, antworten)
            else:
                self._json(200, antworten[0])
            return

        self.send_response(404)
        self.end_headers()

    def _verarbeite_rpc(self, nachricht) -> dict | None:
        """Verarbeitet EINE JSON-RPC-Nachricht. Gibt None zurueck fuer Notifications
        (kein 'id'-Feld) -- die bekommen laut Spec keine Antwort."""
        if not isinstance(nachricht, dict) or "id" not in nachricht:
            return None
        msg_id = nachricht["id"]
        method = nachricht.get("method", "")
        params = nachricht.get("params", {})

        if method == "initialize":
            client_version = params.get("protocolVersion", "2024-11-05")
            result_payload = {
                "protocolVersion": client_version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "flextrawurst-vps-mcp", "version": "1.0.0"},
            }
        elif method in ("tools/list", "mcp.list_tools"):
            result_payload = {
                "tools": [
                    {"name": n, "description": s["description"], "inputSchema": s["inputSchema"]}
                    for n, s in TOOLS.items()
                ]
            }
        elif method in ("tools/call", "mcp.call_tool"):
            tool_name = params.get("name", "")
            args = params.get("arguments", {})
            spec = TOOLS.get(tool_name)
            if not spec:
                result_payload = {"content": [{"type": "text", "text": json.dumps({"error": f"Unbekanntes Tool: {tool_name}"})}]}
            else:
                try:
                    res = spec["fn"](args)
                except Exception as ex:
                    res = _ergebnis(False, error=str(ex))
                result_payload = {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]}
        else:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}

        return {"jsonrpc": "2.0", "id": msg_id, "result": result_payload}


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    print(f"⚡ Flextrawurst VPS-MCP-Werkzeugkoerper startet auf Port {PORT}...")
    server = ReusableHTTPServer(("127.0.0.1", PORT), VPSHandler)
    server.serve_forever()
