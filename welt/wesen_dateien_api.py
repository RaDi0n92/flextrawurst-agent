#!/usr/bin/env python3
"""
Wesen-Dateien-API: JWT-geschützter Lesezugriff auf die eigene codewesen/-Akte.
Wird von api.py importiert via: from wesen_dateien_api import wesen_dateien_router

Ersetzt die alte obsidian_lesen-Aktion in browser_agent.py, die bisher gegen die
Basic-Auth-geschützte /werkraum/-Route (serve_process_camera_preview.ts, C-002-Fix
vom 2026-06-14) lief und deshalb seit ihrer Einführung immer nur "Unauthorized"
zurückgab (gefunden 2026-07-21 per direktem Playwright-Blick auf die SCREENS,
Daniels Auftrag). Diese Route bleibt für alles andere unangetastet — hier nur ein
eng geschnittener, JWT-authentifizierter Ausschnitt, kein Ersatz für den Basic-Auth-Schutz.

Endpunkte:
  GET /wesen/datei — eigene codewesen/<entity_id>/-Datei lesen (Admin: beliebige codewesen/-Datei)
"""

import os
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import HTMLResponse

wesen_dateien_router = APIRouter(prefix="/wesen-dateien", tags=["wesen-dateien"])
# eigener Praefix statt /wesen/... : die bestehende Route /wesen/{entity_id} (weiter oben in
# api.py definiert) wuerde /wesen/datei sonst als entity_id="datei" abfangen, bevor dieser
# Router ueberhaupt zum Zug kommt (gefunden 2026-07-21 beim End-to-End-Test: einheitlich 404
# auch ohne Token, statt der erwarteten 401/403 -- klares Zeichen fuer einen Routing-Shadow).

WERKRAUM_ROOT = Path("/root/werkraum").resolve()
CODEWESEN_ROOT = (WERKRAUM_ROOT / "codewesen").resolve()


def _html_seite(titel: str, inhalt: str) -> str:
    body = (
        inhalt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{titel}</title>
<style>
  body {{ background:#0a0d12; color:#c9d6d1; font-family:ui-monospace,monospace;
          max-width:900px; margin:2rem auto; padding:0 1.5rem; line-height:1.6; }}
  h1 {{ color:#4a9a7a; font-size:1rem; letter-spacing:.08em; border-bottom:1px solid #223; padding-bottom:.6rem; }}
  pre {{ white-space:pre-wrap; word-break:break-word; }}
</style></head>
<body><h1>{titel}</h1><pre>{body}</pre></body></html>"""


@wesen_dateien_router.get("/datei", response_class=HTMLResponse)
def wesen_datei_lesen(
    pfad: str = Query(..., max_length=300),
    authorization: str | None = Header(default=None),
):
    """Ein Wesen darf nur unter codewesen/<eigene entity_id>/ lesen — serverseitig
    erzwungen, auch wenn im pfad-Parameter etwas anderes steht (gleiches Muster wie
    rag_api.py). Admin darf jede codewesen/-Datei lesen."""
    from api import _require_admin_or_entity

    claims = _require_admin_or_entity(authorization)
    ist_wesen = claims.get("role") == "entity"

    pfad = pfad.strip().lstrip("/")
    if ist_wesen:
        erlaubtes_praefix = f"codewesen/{claims['user_id']}/"
        if not pfad.startswith(erlaubtes_praefix):
            raise HTTPException(status_code=403, detail=f"nur Lesezugriff auf {erlaubtes_praefix}")
    elif not pfad.startswith("codewesen/"):
        raise HTTPException(status_code=403, detail="nur codewesen/-Pfade erlaubt")

    ziel = (WERKRAUM_ROOT / pfad).resolve()
    try:
        ziel.relative_to(CODEWESEN_ROOT)
    except ValueError:
        raise HTTPException(status_code=403, detail="Pfad verlässt codewesen/")
    if not ziel.is_file():
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")
    if ziel.stat().st_size > 200_000:
        raise HTTPException(status_code=413, detail="Datei zu groß")

    try:
        text = ziel.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Lesefehler: {e}")

    return _html_seite(pfad, text)
