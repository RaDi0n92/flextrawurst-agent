#!/usr/bin/env python3
"""
RAG-API: HTTP-Endpunkt für die bestehende Ring-1-Retrieval-Logik (rag_retrieve.py).
Wird von api.py importiert via: from rag_api import rag_router

War bisher nur CLI (siehe docs/systemdoku/23_rag_ring1.md, "bekannte Luecken").
Dieser Endpunkt bedient zwei Konsumenten (Daniels Wunsch, 2026-07-21):
  - den neuen RAG-Tab in der Surface (Daniel schaut zu, welche RAG-Treffer ein Wesen bekommt)
  - Wesen selbst, ueber ihren eigenen virtuellen Browser (rag_erkunden-Aktion, browser_agent.py)

Endpunkte:
  GET /rag/suche — hybride Suche, admin- oder entity-authentifiziert
"""

from fastapi import APIRouter, Header, HTTPException, Query

import rag_retrieve

rag_router = APIRouter(prefix="/rag", tags=["rag"])


@rag_router.get("/suche")
def rag_suche(
    anfrage: str = Query(..., max_length=1000),
    wesen: str | None = Query(default=None, max_length=64),
    quelle: str | None = Query(default=None, max_length=64),
    n: int = Query(default=8, ge=1, le=30),
    anlass: str | None = Query(default=None, max_length=100),
    authorization: str | None = Header(default=None),
):
    """Admin sieht jede Wesen-Perspektive (per ?wesen=), ein Wesen sieht nur seine eigene
    (wesen-Filter wird serverseitig auf die eigene entity_id erzwungen, auch wenn ein
    anderer Wert im Query-Parameter steht -- kein Wesen darf RAG-Treffer eines anderen
    Wesens abrufen, indem es einfach den Parameter aendert)."""
    from api import _require_admin_or_entity  # spaeter Import: Zirkularitaet vermeiden (api.py importiert diesen Router)

    claims = _require_admin_or_entity(authorization)
    ist_wesen = claims.get("role") == "entity"
    wesen_filter = claims["user_id"] if ist_wesen else wesen
    wesen_der_anfrage = claims["user_id"] if ist_wesen else None
    anlass_effektiv = anlass or ("browser_agent_erkundung" if ist_wesen else "admin_beobachtung")

    try:
        ergebnisse = rag_retrieve.suche(
            anfrage, wesen=wesen_filter, quelle=quelle, n=n,
            wesen_der_anfrage=wesen_der_anfrage, anlass=anlass_effektiv,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RAG-Suche fehlgeschlagen: {e}")

    return {
        "anfrage": anfrage,
        "wesen": wesen_filter,
        "ergebnisse": [dict(r) for r in ergebnisse],
    }
